from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import reels

app = FastAPI(title="Reel Reality Check API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reels.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
