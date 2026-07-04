import aiosqlite
from datetime import datetime, timezone

async def init_conversations_db(db_path: str):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                thread_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        await db.commit()


async def create_conversation(db_path: str, thread_id: str, title: str = "새 대화"):
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "INSERT INTO conversations (thread_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (thread_id, title, now, now),
        )
        await db.commit()
    return {"thread_id": thread_id, "title": title, "created_at": now, "updated_at": now}


async def list_conversations(db_path: str):
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM conversations ORDER BY updated_at DESC"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def update_conversation_title(db_path: str, thread_id: str, title: str):
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "UPDATE conversations SET title = ?, updated_at = ? WHERE thread_id = ?",
            (title, now, thread_id),
        )
        await db.commit()


async def touch_conversation(db_path: str, thread_id: str):
    """메시지 주고받을 때마다 updated_at만 갱신 (최근 대화가 목록 위로 올라오게)"""
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "UPDATE conversations SET updated_at = ? WHERE thread_id = ?",
            (now, thread_id),
        )
        await db.commit()