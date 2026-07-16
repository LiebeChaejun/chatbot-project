import aiosqlite
from datetime import datetime, timezone


async def init_conversations_db(db_path: str):
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                thread_id TEXT PRIMARY KEY,
                owner_id TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        await db.commit()


async def create_conversation(db_path: str, thread_id: str, owner_id: str, title: str = "새 대화"):
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "INSERT INTO conversations (thread_id, owner_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (thread_id, owner_id, title, now, now),
        )
        await db.commit()
    return {"thread_id": thread_id, "owner_id": owner_id, "title": title, "created_at": now, "updated_at": now}


async def list_conversations(db_path: str, owner_id: str):
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM conversations WHERE owner_id = ? ORDER BY updated_at DESC",
            (owner_id,),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def is_owner(db_path: str, thread_id: str, owner_id: str) -> bool:
    """이 thread_id가 실제로 이 owner_id 소유인지 확인"""
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(
            "SELECT 1 FROM conversations WHERE thread_id = ? AND owner_id = ?",
            (thread_id, owner_id),
        )
        row = await cursor.fetchone()
        return row is not None


async def update_conversation_title(db_path: str, thread_id: str, title: str):
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "UPDATE conversations SET title = ?, updated_at = ? WHERE thread_id = ?",
            (title, now, thread_id),
        )
        await db.commit()


async def touch_conversation(db_path: str, thread_id: str):
    now = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "UPDATE conversations SET updated_at = ? WHERE thread_id = ?",
            (now, thread_id),
        )
        await db.commit()