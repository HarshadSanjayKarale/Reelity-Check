from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import reels

app = FastAPI(title="Reel Reality Check API")

app.add_middleware(
    CORSMiddleware,
    # Vite auto-increments the port (5174, 5175, ...) if 5173 isn't free yet on
    # restart, which would otherwise intermittently break CORS in local dev.
    allow_origin_regex=r"http://localhost:\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reels.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
