from fastapi import (
    FastAPI,
    HTTPException,
)  # FastAPIフレームワークの基本機能とエラー処理用のクラス
from fastapi.middleware.cors import CORSMiddleware  # CORSを有効にするためのミドルウェア
from fastapi.responses import HTMLResponse  # HTMLを返すためのレスポンスクラス
from pydantic import BaseModel  # データのバリデーション（検証）を行うための基本クラス
from typing import Optional  # 省略可能な項目を定義するために使用
import sqlite3  # SQLiteデータベースを使用するためのライブラリ
import uvicorn # ASGIサーバーを起動するためのライブラリ

# FastAPIアプリケーションのインスタンスを作成
app = FastAPI()


# corsを無効化（開発時のみ）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# データベースの初期設定を行う関数
def init_questions_db():
    with sqlite3.connect("questions.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                options TEXT NOT NULL,
                correct INTEGER NOT NULL
            )
        """)


# アプリケーション起動時にデータベースを初期化
init_questions_db()


# リクエストボディのデータ構造を定義するクラス
class Todo(BaseModel):
    title: str  # TODOのタイトル（必須）
    completed: Optional[bool] = False  # 完了状態（省略可能、デフォルトは未完了）


# レスポンスのデータ構造を定義するクラス（TodoクラスにIDを追加）
class TodoResponse(Todo):
    id: int  # TODOのID


# クライアント用のHTMLを返すエンドポイント
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("client.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/questions")
def add_question(question: dict):
    options_str = "|".join(question["options"])
    with sqlite3.connect("questions.db") as conn:
        cursor = conn.execute(
            "INSERT INTO questions (category, content, options, correct) VALUES (?, ?, ?, ?)",
            (question["category"], question["content"], options_str, question["correct"])
        )
        return {"id": cursor.lastrowid, "message": "Question added successfully"}

@app.get("/questions")
def get_questions():
    with sqlite3.connect("questions.db") as conn:
        rows = conn.execute("SELECT * FROM questions").fetchall()
        return [
            {
                "id": row[0],
                "category": row[1],
                "content": row[2],
                "options": row[3].split("|"),
                "correct": row[4]
            } for row in rows
        ]


if __name__ == "__main__":
    # FastAPIアプリケーションを非同期モードで起動
    uvicorn.run(app, host="0.0.0.0", port=8000)
