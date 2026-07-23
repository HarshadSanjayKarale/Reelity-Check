from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

_client: AsyncIOMotorClient | None = None


def get_db() -> AsyncIOMotorDatabase:
    global _client
    if _client is None:
        if not settings.mongo_uri:
            raise RuntimeError(
                "MONGO_URI is not set. Copy backend/.env.example to backend/.env "
                "and fill in your MongoDB Atlas connection string."
            )
        _client = AsyncIOMotorClient(settings.mongo_uri)
    return _client[settings.mongo_db_name]


async def ping() -> bool:
    db = get_db()
    await db.command("ping")
    return True
