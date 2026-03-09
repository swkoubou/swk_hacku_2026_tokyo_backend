from fastapi import FastAPI
from janome.tokenizer import Tokenizer
from datetime import datetime, timedelta
import re
#  curl "http://127.0.0.1:8000/sentence_to_json?sentence=今日から3月11日はきっといい日になる"
t = Tokenizer()
app = FastAPI()

@app.get("/sentence_to_json")
def sentence_to_json(sentence: str):
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
    start_date=date_list[0]
    if len(date_list)==1:
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
    return({
                "start_date": f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}",
                "start_time": start_time,
                "end_date": f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}",
                "event_name": event_name
            })