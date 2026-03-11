from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uuid
from janome.tokenizer import Tokenizer
from datetime import datetime, timedelta
import re
import os
import openai
import json
import psycopg2
import redis

from psycopg2.extras import RealDictCursor
#run uvicorn demo:app --host 0.0.0.0 --port 8888 --reload
#sample user_uuid 3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12

r = redis.Redis(host="redis", port=6379, decode_responses=True)
t = Tokenizer()
app = FastAPI()
openai.api_key = os.getenv("OPENAI_API_KEY")
connection = psycopg2.connect("host=postgres dbname=calendar user=app password=app")
cursor = connection.cursor(cursor_factory=RealDictCursor)


@app.middleware("http")
async def require_user_uuid(request: Request, call_next):
    user_uuid = request.headers.get("user_uuid")
    if request.url.path == "/gen_uuid":
        return await call_next(request)
    if not user_uuid:
        return JSONResponse(
            status_code=400,
            content={"detail": "missing required header: user_uuid"},
        ) 
    redis_key = f"user_uuid:{user_uuid}" #目標をセンターに入れて代入
    try:
        if r.getex(redis_key, ex=3600): #通ってもいいですか
            #print("redis認証")
            return await call_next(request) #ああ、いいよ
    except Exception: #redisはもう、死んでいる
        pass  # なんとかなる！

    try: 
        cursor.execute(
            "SELECT 1 FROM users WHERE user_uuid = %s",
            (user_uuid,)
        )
        query_result = cursor.fetchone()
    except Exception:
        return JSONResponse( #
            status_code=500,
            content={"detail": "database error"},
        )
    if query_result: #dbから読み込みしてあったら
            try:
                r.set(redis_key, 'active', ex=3600) #redisに追加、次からショートカットどうぞ
            except Exception: #redis dead!
                pass
            #print("db認証")
            return await call_next(request) #ああ、いいよ
    else: #君はこれ以上進めない
        return JSONResponse(
            status_code=401,
            content={"detail": "unauthorized user_uuid"},
        )

# ===== リクエストボディ定義 =====

class MessageBody(BaseModel):
    message: str

class DefEventBody(BaseModel):
    start_date: str
    start_time: Optional[str] = None  # nullを許容
    end_date: str
    event_name: str

class GetYearEventsBody(BaseModel):
    year: str

class UpdateEventBody(BaseModel):
    task_uuid: str
    new_start_date: str
    new_start_time: Optional[str] = None  # nullを許容
    new_end_date: str
    new_event_name: str

class TaskBody(BaseModel):
    task_uuid: str


# ===== エンドポイント =====

@app.post("/lv1") #リクエストA lv1
def lv1(request: Request, body: MessageBody):
    sentence=body.message
    start_date=""
    start_time=None
    end_date=""
    event_name=""
    #ここから前処理
    if "今日" in sentence:
        sentence = sentence.replace("今日", datetime.now().strftime("%Y%m%d")) #今日の日付
    if "明日" in sentence:
        sentence = sentence.replace("明日", (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")) #明日の日付
    if "明後日" in sentence:
        sentence = sentence.replace("明後日", (datetime.now() + timedelta(days=2)).strftime("%Y%m%d")) #明後日の日付
    if "今週" in sentence:
        sentence = sentence.replace("今週", datetime.now().strftime("%Y%m%d")) #今日の日付
    if "今月" in sentence:
        sentence = sentence.replace("今月", datetime.now().strftime("%Y%m%d")) #今日の日付
    if "今年" in sentence:
        sentence = sentence.replace("今年", datetime.now().strftime("%Y%m%d")) #今日の日付
    if ("月" in sentence) or ("日" in sentence):
        year = datetime.now().year
        sentence = re.sub(
                        r'(\d{1,2})月(\d{1,2})日',
                        lambda m: datetime(year, int(m.group(1)), int(m.group(2))).strftime("%Y%m%d"),
                        sentence
                    )
    #前処理終了
    word_list = []
    for token in t.tokenize(sentence):
        word_list.append({
            "word":token.surface,
            "type":token.part_of_speech.split(',')
            })
    #print(word_list)
    date_list=[]
    noun_list=[]
    for word in word_list:
        try: #日付を数える
            datetime.strptime(word["word"], "%Y%m%d")
            date_list.append(word["word"])
            #print(word["word"])
        except ValueError:
            if word["type"][0]=="名詞": #マイケルやテニスなどのevent情報
                event_name+=word["word"]
            if word["type"][0]=="助詞" and word["type"][1]=="格助詞": #から と といった日付間の条件等
                #print(word["word"])
                noun_list.append(word["word"])
    if len(date_list)==0:
        start_date=datetime.now().strftime("%Y%m%d")
    else:
        start_date=date_list[0]
    #print(date_list)
    if len(date_list)<2:
        end_date=start_date
    else:
        end_date=date_list[1]
    #print(date_list)
    time=re.findall(r'(\d{1,2})時(?:\s*(\d{1,2})分)?', sentence)
    #print("time",time)
    if time != []:
        if time[0][1]=="": #分情報がなかったら
            start_time=time[0][0]+":00:00"
        else: #分情報があったら
            start_time=time[0][0]+":"+time[0][1]+":00"
    return{
                "lv": 1,
                "message": body.message,
                "start_date": f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}",
                "start_time": start_time,
                "end_date": f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}",
                "event_name": event_name
            }

@app.post("/lv2") #リクエストA lv2
def lv2(request: Request, body: MessageBody):
    response = openai.chat.completions.create(
    model="gpt-4.1-nano",
    messages=[
        {"role": "system", "content": f"""
        レスポンスは必ずJSONで返してください。
        今日の日付は{datetime.now().strftime("%Y%m%d")}です
        あなたは会話から得られた情報を元に、適切な返答を生成してください。
        以下がサンプルです
        {{
            "start_date": "2026-03-09",
            "start_time": "10:40:00",
            "end_date": "2026-03-10",
            "event_name": "旅行"
        }}
        "start_time"は必ずHH:MM:00の形式で返してください。
        秒数の情報はひつようありませんので
        また、n時などの明確な時間の指定がされてない場合はNULLを返してください。
        以下がNULLを返すサンプルです
        {{
            "start_date": "2026-03-09",
            "start_time": null,
            "end_date": "2026-03-10",
            "event_name": "旅行"
        }}
        開始日と終了日が不明な場合は本日の日付を使用してください。
        """},
        {"role": "user", "content": body.message}
    ]
    )
    data = json.loads(response.choices[0].message.content)
    print(data)
    return {
                "lv": 2,
                "message": body.message,
            }|data

@app.post("/lv3") #リクエストA lv3
def lv3(request: Request, body: MessageBody):
    response = openai.chat.completions.create(
    model="gpt-5-mini",
    messages=[
        {"role": "system", "content": f"""
        レスポンスは必ずJSONで返してください。
        今日の日付は{datetime.now().strftime("%Y%m%d")}です
        あなたは会話から得られた情報を元に、適切な返答を生成してください。
        ユーザーがなにを求めているかある程度察してstart_dateとend_dateとevent_nameを設定してください
        無理にstart_timeは推測しないでください
        以下がサンプルです
        {{
            "start_date": "2026-03-09",
            "start_time": "10:40:00",
            "end_date": "2026-03-10",
            "event_name": "旅行"
        }}
        "start_time"は必ずHH:MM:00の形式で返してください。
        秒数の情報はひつようありませんので
        また、n時などの明確な時間の指定がされてない場合はNULLを返してください。
        以下がNULLを返すサンプルです
        {{
            "start_date": "2026-03-09",
            "start_time": null,
            "end_date": "2026-03-10",
            "event_name": "旅行"
        }}
        開始日と終了日が不明な場合は本日の日付を使用してください。
        """},
        {"role": "user", "content": body.message}
    ]
    )
    data = json.loads(response.choices[0].message.content)
    print(data)
    return {
                "lv": 3,
                "message": body.message,
            }|data

@app.post("/def_event") #リクエストB
def def_event(request: Request, body: DefEventBody):
    sql = "INSERT INTO events (task_id, user_uuid, start_date, start_time, end_date, event_name) VALUES (%s, %s, %s, %s, %s, %s)"
    task_id=str(uuid.uuid4())
    try:
        cursor.execute(sql, (
            task_id,
            request.headers.get("user_uuid"),
            body.start_date,
            body.start_time,
            body.end_date,
            body.event_name
            ))
        connection.commit()
    except psycopg2.Error as e:
        connection.rollback()
        return JSONResponse(
                            status_code=500,
                            content={"detail": f"Database error: {e.pgerror}"}
                            )
    if body.start_date==datetime.now().strftime("%Y-%m-%d"):
        data={
            "user_uuid": task_id,
            "task_uuid": request.headers.get("user_uuid"),
            "start_date": body.start_date,
            "start_time": body.start_time,
            "end_date": body.end_date,
            "event_name": body.event_name,
            "done":False
        }
        now = datetime.now()
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_until_end_of_day = int((tomorrow - now).total_seconds())
        r.set(f"event:{request.headers.get('user_uuid')}:{task_id}", json.dumps(data), ex=seconds_until_end_of_day)
    return {
                "success": True
            }

@app.post("/get_year_events") #リクエストC
def get_year_events(request: Request, body: GetYearEventsBody):
    try: 
        cursor.execute(
            """
        SELECT
            task_id,
            user_uuid,
            TO_CHAR(start_date, 'YYYY-MM-DD') as start_date,
            TO_CHAR(start_time, 'HH24:MI:SS') as start_time,
            TO_CHAR(end_date, 'YYYY-MM-DD') as end_date,
            event_name
        FROM events
        WHERE user_uuid = %s
        AND EXTRACT(YEAR FROM start_date) = %s
    """,
    (request.headers.get("user_uuid"), int(body.year))
        )
        query_result = cursor.fetchall()
    except Exception as e:
        print(e)
        return JSONResponse( #
            status_code=500,
            content={"detail": "database error"},
        )
    result=[]
    for event in query_result:
        result.append({
            "user_uuid": event["user_uuid"],
            "task_uuid": event["task_id"],
            "start_date": event["start_date"],
            "start_time": event["start_time"],
            "end_date": event["end_date"],
            "event_name": event["event_name"]
        })
    #print(event)
    return result

@app.post("/update_event") #リクエストD
def update_event(request: Request, body: UpdateEventBody):
    sql = """
    UPDATE events
    SET
        start_date = %s,
        start_time = %s,
        end_date = %s,
        event_name = %s
    WHERE
        task_id = %s
    AND
        user_uuid = %s;
    """
    try:
        cursor.execute(sql, (
            body.new_start_date,
            body.new_start_time,
            body.new_end_date,
            body.new_event_name,
            body.task_uuid,
            request.headers.get("user_uuid"),
            ))
        connection.commit()
    except psycopg2.Error as e:
        connection.rollback()
        return JSONResponse(
                            status_code=500,
                            content={"detail": f"Database error: {e.pgerror}"}
                            )
    if cursor.rowcount == 0:
        return JSONResponse(
            status_code=404,
            content={"detail": "task not found"}
        )
    r.delete(f"event:{request.headers.get('user_uuid')}:{body.task_uuid}")
    if body.new_start_date==datetime.now().strftime("%Y-%m-%d"):
        data={
            "user_uuid": body.task_uuid,
            "task_uuid": request.headers.get("user_uuid"),
            "start_date": body.new_start_date,
            "start_time": body.new_start_time,
            "end_date": body.new_end_date,
            "event_name": body.new_event_name,
            "done":False
        }
        now = datetime.now()
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_until_end_of_day = int((tomorrow - now).total_seconds())
        r.set(f"event:{request.headers.get('user_uuid')}:{body.task_uuid}", json.dumps(data), ex=seconds_until_end_of_day)
    return {
                "success": True
            }

@app.post("/delete_event") #リクエストE
def delete_event(request: Request, body: TaskBody):
    sql = """
    DELETE FROM events
    WHERE task_id = %s
    AND user_uuid = %s;
    """
    try:
        cursor.execute(sql, (
            body.task_uuid,
            request.headers.get("user_uuid"),
            ))
        connection.commit()
    except psycopg2.Error as e:
        connection.rollback()
        return JSONResponse(
                            status_code=500,
                            content={"detail": f"Database error: {e.pgerror}"}
                            )
    if cursor.rowcount == 0:
        return JSONResponse(
            status_code=404,
            content={"detail": "task not found"}
        )
    r.delete(f"event:{request.headers.get('user_uuid')}:{body.task_uuid}")
    return {
                "success": True
            }

@app.post("/get_today_events") #リクエストX
def get_today_events(request: Request):
    keys = []
    for key in r.scan_iter(f"event:{request.headers.get('user_uuid')}:*"):
        keys.append(key)
    pipe = r.pipeline()
    for key in keys:
        pipe.get(key)
    result = pipe.execute()
    events = []
    for x in result:
        if x:
            events.append(json.loads(x))
    return events

@app.post("/do_today_event") #リクエストY
def do_today_event(request: Request, body: TaskBody):
    key = f"event:{request.headers.get('user_uuid')}:{body.task_uuid}"
    value = r.get(key)
    if value:
        data = json.loads(value)
        data["done"]=True
        r.set(key, json.dumps(data), keepttl=True)
        return {
            "success": True
        }
    return JSONResponse(
            status_code=404,
            content={"detail": "task not found"}
        )

@app.post("/rollback_today_event") #リクエストZ
def rollback_today_event(request: Request, body: TaskBody):
    key = f"event:{request.headers.get('user_uuid')}:{body.task_uuid}"
    value = r.get(key)
    if value:
        data = json.loads(value)
        data["done"]=False
        r.set(key, json.dumps(data), keepttl=True)
        return {
            "success": True
        }
    return JSONResponse(
            status_code=404,
            content={"detail": "task not found"}
        )

@app.post("/gen_uuid") #リクエスト FOR DEBUG
def gen_uuid():
    new_uuid=str(uuid.uuid4())
    sql = "INSERT INTO users (user_uuid) VALUES (%s)"
    try:
        cursor.execute(sql, (new_uuid,))
        connection.commit()
    except psycopg2.Error as e:
        connection.rollback()
        return JSONResponse(
                            status_code=500,
                            content={"detail": f"Database error: {e.pgerror}"}
                            )
    return {"user_uuid": new_uuid}