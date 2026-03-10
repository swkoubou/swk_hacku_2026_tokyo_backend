# カレンダーAPI仕様書

**ベースURL:** `http://localhost:8888`  
**認証方式:** リクエストヘッダーに `user_uuid` を付与  
**サンプル user_uuid:** `3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12`

---

## 認証について

`/gen_uuid` を除くすべてのエンドポイントは、リクエストヘッダーに `user_uuid` が必要です。  
未指定の場合は `400`、不正な値の場合は `401` が返ります。

---

## リクエスト形式

- `user_uuid` は **リクエストヘッダー** で送ります
- それ以外のパラメータはすべて **JSON Body** で送ります
- Bodyを送る場合は `-H "Content-Type: application/json"` が必要です
- 必須フィールドが欠けている場合は **422 Unprocessable Entity** が返ります

---

## エンドポイント一覧

| メソッド | パス | 概要 |
|--------|------|------|
| POST | `/gen_uuid` | UUID発行（認証不要） |
| POST | `/lv1` | イベント解析 lv1 |
| POST | `/lv2` | イベント解析 lv2 |
| POST | `/lv3` | イベント解析 lv3 |
| POST | `/def_event` | イベント登録 |
| POST | `/get_month_events` | 月別イベント取得 |
| POST | `/update_event` | イベント更新 |
| POST | `/delete_event` | イベント削除 |
| POST | `/get_today_events` | 本日のイベント取得 |
| POST | `/do_today_event` | イベントを完了にする |
| POST | `/rollback_today_event` | イベントの完了を取り消す |

---

## 各エンドポイント詳細

### POST `/gen_uuid`
**認証:** 不要

UUIDを新規発行します。デバッグ・初期登録用途。

**レスポンス例:**
```json
{
  "user_uuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

**curlサンプル:**
```cmd
curl -s -X POST http://localhost:8888/gen_uuid
```

---

### POST `/lv1`
**認証:** 必要

**リクエストヘッダー:**

| ヘッダー名 | 必須 | 説明 |
|-----------|------|------|
| `user_uuid` | ✅ | ユーザーID |

**リクエストBody:**

| フィールド名 | 必須 | 説明 |
|------------|------|------|
| `message` | ✅ | 解析するメッセージ文字列 |

メッセージからイベント情報を解析して返します（lv1: 開始時刻あり）。

**レスポンス例:**
```json
{
  "lv": 1,
  "message": "明日の10時40分から旅行",
  "start_date": "2026-03-09",
  "start_time": "10:40:00",
  "end_date": "2026-03-10",
  "event_name": "旅行"
}
```

**curlサンプル:**
```cmd
curl -s -X POST http://localhost:8888/lv1 -H "user_uuid: 3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12" -H "Content-Type: application/json" -d "{\"message\": \"明日の10時40分から旅行\"}"
```

---

### POST `/lv2`
**認証:** 必要

**リクエストヘッダー:**

| ヘッダー名 | 必須 | 説明 |
|-----------|------|------|
| `user_uuid` | ✅ | ユーザーID |

**リクエストBody:**

| フィールド名 | 必須 | 説明 |
|------------|------|------|
| `message` | ✅ | 解析するメッセージ文字列 |

lv1と同様ですが、`start_time` が `null` になるケース（時刻不明）を想定。

**レスポンス例:**
```json
{
  "lv": 2,
  "message": "明日から旅行",
  "start_date": "2026-03-09",
  "start_time": null,
  "end_date": "2026-03-10",
  "event_name": "旅行"
}
```

**curlサンプル:**
```cmd
curl -s -X POST http://localhost:8888/lv2 -H "user_uuid: 3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12" -H "Content-Type: application/json" -d "{\"message\": \"明日から旅行\"}"
```

---

### POST `/lv3`
**認証:** 必要

**リクエストヘッダー:**

| ヘッダー名 | 必須 | 説明 |
|-----------|------|------|
| `user_uuid` | ✅ | ユーザーID |

**リクエストBody:**

| フィールド名 | 必須 | 説明 |
|------------|------|------|
| `message` | ✅ | 解析するメッセージ文字列 |

人名などを含む詳細なイベント名が返るケース。

**レスポンス例:**
```json
{
  "lv": 3,
  "message": "マイケルと明日10時45分から旅行",
  "start_date": "2026-03-09",
  "start_time": "10:45:00",
  "end_date": "2026-03-10",
  "event_name": "マイケルと旅行"
}
```

**curlサンプル:**
```cmd
curl -s -X POST http://localhost:8888/lv3 -H "user_uuid: 3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12" -H "Content-Type: application/json" -d "{\"message\": \"マイケルと明日10時45分から旅行\"}"
```

---

### POST `/def_event`
**認証:** 必要

**リクエストヘッダー:**

| ヘッダー名 | 必須 | 説明 |
|-----------|------|------|
| `user_uuid` | ✅ | ユーザーID |

**リクエストBody:**

| フィールド名 | 必須 | 説明 |
|------------|------|------|
| `start_date` | ✅ | 開始日 (例: `2026-03-09`) |
| `start_time` | ✅ | 開始時刻 (例: `10:40:00`) |
| `end_date` | ✅ | 終了日 (例: `2026-03-10`) |
| `event_name` | ✅ | イベント名 |

新規イベントを登録します。

**レスポンス例 (200 OK):**
```json
{
  "success": true
}
```

**curlサンプル:**
```cmd
curl -s -X POST http://localhost:8888/def_event -H "user_uuid: 3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12" -H "Content-Type: application/json" -d "{\"start_date\": \"2026-03-09\", \"start_time\": \"10:40:00\", \"end_date\": \"2026-03-10\", \"event_name\": \"旅行\"}"
```

---

### POST `/get_month_events`
**認証:** 必要

**リクエストヘッダー:**

| ヘッダー名 | 必須 | 説明 |
|-----------|------|------|
| `user_uuid` | ✅ | ユーザーID |

**リクエストBody:**

| フィールド名 | 必須 | 説明 |
|------------|------|------|
| `year` | ✅ | 取得する年 (例: `"2026"`) |
| `month` | ✅ | 取得する月 (例: `"3"`) |

指定した年月のイベント一覧を返します。`start_time` が `null` のイベントも含まれます。

**レスポンス例:**
```json
[
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
    "task_uuid": "9c41ce15-89f7-4ffd-a632-721e0186c611",
    "start_date": "2026-04-19",
    "start_time": null,
    "end_date": "2026-05-10",
    "event_name": "旅行4"
  }
]
```

**curlサンプル:**
```cmd
curl -s -X POST http://localhost:8888/get_month_events -H "user_uuid: 3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12" -H "Content-Type: application/json" -d "{\"year\": \"2026\", \"month\": \"3\"}"
```

---

### POST `/update_event`
**認証:** 必要

**リクエストヘッダー:**

| ヘッダー名 | 必須 | 説明 |
|-----------|------|------|
| `user_uuid` | ✅ | ユーザーID |

**リクエストBody:**

| フィールド名 | 必須 | 説明 |
|------------|------|------|
| `task_uuid` | ✅ | 更新対象のイベントID |
| `new_start_date` | ✅ | 新しい開始日 |
| `new_start_time` | ✅ | 新しい開始時刻 |
| `new_end_date` | ✅ | 新しい終了日 |
| `new_event_name` | ✅ | 新しいイベント名 |

既存イベントの情報を更新します。

**レスポンス例 (200 OK):**
```json
{
  "success": true
}
```

**curlサンプル:**
```cmd
curl -s -X POST http://localhost:8888/update_event -H "user_uuid: 3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12" -H "Content-Type: application/json" -d "{\"task_uuid\": \"fbcf83d0-13e6-419f-83eb-661ea656d7b1\", \"new_start_date\": \"2026-03-10\", \"new_start_time\": \"09:00:00\", \"new_end_date\": \"2026-03-16\", \"new_event_name\": \"旅行（更新）\"}"
```

---

### POST `/delete_event`
**認証:** 必要

**リクエストヘッダー:**

| ヘッダー名 | 必須 | 説明 |
|-----------|------|------|
| `user_uuid` | ✅ | ユーザーID |

**リクエストBody:**

| フィールド名 | 必須 | 説明 |
|------------|------|------|
| `task_uuid` | ✅ | 削除対象のイベントID |

イベントを削除します。

**レスポンス例 (200 OK):**
```json
{
  "success": true
}
```

**curlサンプル:**
```cmd
curl -s -X POST http://localhost:8888/delete_event -H "user_uuid: 3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12" -H "Content-Type: application/json" -d "{\"task_uuid\": \"fbcf83d0-13e6-419f-83eb-661ea656d7b1\"}"
```

---

### POST `/get_today_events`
**認証:** 必要

**リクエストヘッダー:**

| ヘッダー名 | 必須 | 説明 |
|-----------|------|------|
| `user_uuid` | ✅ | ユーザーID |

**リクエストBody:** なし

本日のイベント一覧を返します。各イベントには `done`（完了フラグ）が含まれます。

**レスポンス例:**
```json
[
  {
    "user_uuid": "3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12",
    "task_uuid": "fbcf83d0-13e6-419f-83eb-661ea656d7b1",
    "start_date": "2026-03-10",
    "start_time": "10:40:00",
    "end_date": "2026-03-15",
    "event_name": "旅行1",
    "done": true
  },
  {
      "user_uuid": "3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12",
      "task_uuid": "c8681580-e36d-448d-9752-b9fc49c2e393",
      "start_date": "2026-03-10",
      "start_time": "8:40:00",
      "end_date": "2026-03-22",
      "event_name": "旅行2",
      "done": false
  }
]
```

**curlサンプル:**
```cmd
curl -s -X POST http://localhost:8888/get_today_events -H "user_uuid: 3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12"
```

---

### POST `/do_today_event`
**認証:** 必要

**リクエストヘッダー:**

| ヘッダー名 | 必須 | 説明 |
|-----------|------|------|
| `user_uuid` | ✅ | ユーザーID |

**リクエストBody:**

| フィールド名 | 必須 | 説明 |
|------------|------|------|
| `task_uuid` | ✅ | 完了にするイベントID |

本日のイベントを「完了」状態にします。

**レスポンス例 (200 OK):**
```json
{
  "success": true
}
```

**curlサンプル:**
```cmd
curl -s -X POST http://localhost:8888/do_today_event -H "user_uuid: 3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12" -H "Content-Type: application/json" -d "{\"task_uuid\": \"fbcf83d0-13e6-419f-83eb-661ea656d7b1\"}"
```

---

### POST `/rollback_today_event`
**認証:** 必要

**リクエストヘッダー:**

| ヘッダー名 | 必須 | 説明 |
|-----------|------|------|
| `user_uuid` | ✅ | ユーザーID |

**リクエストBody:**

| フィールド名 | 必須 | 説明 |
|------------|------|------|
| `task_uuid` | ✅ | 取り消し対象のイベントID |

`do_today_event` で完了にしたイベントを未完了状態に戻します。

**レスポンス例 (200 OK):**
```json
{
  "success": true
}
```

**curlサンプル:**
```cmd
curl -s -X POST http://localhost:8888/rollback_today_event -H "user_uuid: 3c7a9a24-9e34-4f65-bc1e-9a6e6c7d7f12" -H "Content-Type: application/json" -d "{\"task_uuid\": \"fbcf83d0-13e6-419f-83eb-661ea656d7b1\"}"
```

---

## エラーレスポンス

| ステータスコード | 内容 |
|----------------|------|
| `400` | `user_uuid` ヘッダーが未指定 |
| `401` | `user_uuid` が無効 |
| `422` | リクエストBodyの必須フィールドが不足 |

**400 エラー例:**
```json
{
  "detail": "missing required header: user_uuid"
}
```

**401 エラー例:**
```json
{
  "detail": "unauthorized user_uuid"
}
```

**422 エラー例:**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "message"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

---

## サーバー起動方法

```bash
uvicorn demo:app --host 0.0.0.0 --port 8888 --reload
```
