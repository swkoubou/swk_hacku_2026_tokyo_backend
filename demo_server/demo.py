from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uuid
#run uvicorn demo:app --host 0.0.0.0 --port 8888 --reload
#とりあえずフロントに渡すAPIモックデモサーバー
#sample user_uuid 3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12

app = FastAPI()

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

class GetYearEventsBody(BaseModel):
    year: str

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
    return {
                "lv": 1,
                "message": body.message,
                "start_date": "2026-03-09",
                "start_time": "10:40:00",
                "end_date": "2026-03-10",
                "event_name": "旅行"
            }

@app.post("/lv2") #リクエストA lv2
def lv2(request: Request, body: MessageBody):
    return {
                "lv": 2,
                "message": body.message,
                "start_date": "2026-03-09",
                "start_time": None,
                "end_date": "2026-03-10",
                "event_name": "旅行"
            }

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

@app.post("/get_year_events") #リクエストC
def get_year_events(request: Request, body: GetYearEventsBody):
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
