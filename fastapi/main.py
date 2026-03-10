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
#run uvicorn demo:app --host 0.0.0.0 --port 8888 --reload
#sample user_uuid 3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12
t = Tokenizer()
app = FastAPI()
openai.api_key = os.getenv("OPENAI_API_KEY")

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
    if user_uuid != "3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12":
        return JSONResponse(
            status_code=401,
            content={"detail": "unauthorized user_uuid"},
        )
    return await call_next(request)


# ===== リクエストボディ定義 =====

class MessageBody(BaseModel):
    message: str

class DefEventBody(BaseModel):
    start_date: str
    start_time: str
    end_date: str
    event_name: str

class GetMonthEventsBody(BaseModel):
    year: str
    month: str

class UpdateEventBody(BaseModel):
    task_uuid: str
    new_start_date: str
    new_start_time: str
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
    return {
                "lv": 3,
                "message": body.message,
                "start_date": "2026-03-09",
                "start_time": "10:45:00",
                "end_date": "2026-03-10",
                "event_name": "マイケルと旅行"
            }

@app.post("/def_event") #リクエストB
def def_event(request: Request, body: DefEventBody):
    return {
                "success": True
            }

@app.post("/get_month_events") #リクエストC
def get_month_events(request: Request, body: GetMonthEventsBody):
    return [
            {
                "user_uuid": "3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12",
                "task_uuid": "fbcf83d0-13e6-419f-83eb-661ea656d7b1",
                "start_date": "2026-03-09",
                "start_time": "10:40:00",
                "end_date": "2026-03-15",
                "event_name": "旅行1"
            },
            {
                "user_uuid": "3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12",
                "task_uuid": "c8681580-e36d-448d-9752-b9fc49c2e393",
                "start_date": "2026-03-19",
                "start_time": "8:40:00",
                "end_date": "2026-03-22",
                "event_name": "旅行2"
            },
            {
                "user_uuid": "3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12",
                "task_uuid": "60193e10-35c3-497c-a4d5-08a1267b9f73",
                "start_date": "2026-04-09",
                "start_time": "10:40:00",
                "end_date": "2026-04-10",
                "event_name": "旅行3"
            },
            {
                "user_uuid": "3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12",
                "task_uuid": "9c41ce15-89f7-4ffd-a632-721e0186c611",
                "start_date": "2026-04-19",
                "start_time": None,
                "end_date": "2026-05-10",
                "event_name": "旅行4"
            },
        ]

@app.post("/update_event") #リクエストD
def update_event(request: Request, body: UpdateEventBody):
    return {
                "success": True
            }

@app.post("/delete_event") #リクエストE
def delete_event(request: Request, body: TaskBody):
    return {
                "success": True
            }

@app.post("/get_today_events") #リクエストX
def get_today_events(request: Request):
    return [
            {
                "user_uuid": "3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12",
                "task_uuid": "fbcf83d0-13e6-419f-83eb-661ea656d7b1",
                "start_date": "2026-03-10",
                "start_time": "10:40:00",
                "end_date": "2026-03-15",
                "event_name": "旅行1",
                "done": True
            },
            {
                "user_uuid": "3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12",
                "task_uuid": "c8681580-e36d-448d-9752-b9fc49c2e393",
                "start_date": "2026-03-10",
                "start_time": "8:40:00",
                "end_date": "2026-03-22",
                "event_name": "旅行2",
                "done": True
            },
            {
                "user_uuid": "3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12",
                "task_uuid": "60193e10-35c3-497c-a4d5-08a1267b9f73",
                "start_date": "2026-03-10",
                "start_time": "10:40:00",
                "end_date": "2026-04-10",
                "event_name": "旅行3",
                "done": True
            },
            {
                "user_uuid": "3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12",
                "task_uuid": "9c41ce15-89f7-4ffd-a632-721e0186c611",
                "start_date": "2026-03-10",
                "start_time": None,
                "end_date": "2026-05-10",
                "event_name": "旅行4",
                "done": True
            },
        ]

@app.post("/do_today_event") #リクエストY
def do_today_event(request: Request, body: TaskBody):
    return {
                "success": True
            }

@app.post("/rollback_today_event") #リクエストZ
def rollback_today_event(request: Request, body: TaskBody):
    return {
                "success": True
            }

@app.post("/gen_uuid") #リクエスト FOR DEBUG
def gen_uuid():
    return {"user_uuid": str(uuid.uuid4())}
