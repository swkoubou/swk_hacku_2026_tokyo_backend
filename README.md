# 環境構築

## .env
以下の書式に従ってdocker-compose.yamlと同じディレクトリに配置してください
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxx
```

## 仕様
入力文章を多段階に分けて処理します
```
レベル1 janomeを用いた処理
レベル2 gpt-4.1-nanoと簡易プロンプトを用いた処理
レベル3 gpt-5-miniと通常プロンプトを用いた処理
```

## ライセンス

本プロジェクト本体のライセンスは未定です（決まり次第ここに記載してください）。

本プロジェクトでは以下のOSSを利用しています。各OSSの著作権およびライセンスは各開発者・団体に帰属します。

### バックエンドライブラリで利用している主なOSS

| コンポーネント / ライブラリ | 用途 | ライセンス |
| --- | --- | --- |
| FastAPI (`fastapi`) | Web API フレームワーク | MIT License |
| Pydantic (`pydantic`, `pydantic-core`) | リクエスト/レスポンススキーマのバリデーション | MIT License |
| Janome (`Janome`) | 日本語形態素解析エンジン | Apache License 2.0 |
| OpenAI Python SDK (`openai`) | OpenAI API クライアント | Apache License 2.0 |
| psycopg2-binary | PostgreSQL 用 Python ドライバ | GNU LGPL v3 以降（例外条項付き） |
| redis (`redis`) | Redis 用 Python クライアント | MIT License |
| Uvicorn (`uvicorn`) | ASGI サーバ | BSD 3-Clause License |

### コンテナイメージで利用している主なOSS

`docker-compose.yaml` で以下の公式コンテナイメージを利用しています。

| イメージ | 主なソフトウェア | ライセンス概要 |
| --- | --- | --- |
| `python:3.11-slim` | Python 本体 / Debian ベースイメージ | Python Software Foundation License および Debian 各パッケージの OSS ライセンス |
| `postgres:16` | PostgreSQL | PostgreSQL License（BSD 系ライセンス）および Docker 公式イメージの MIT License |
| `redis:7` | Redis | Redis Source Available License / SSPL など（Redis 本体）および Docker 公式イメージの BSD 3-Clause License |