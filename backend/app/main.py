from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

load_dotenv()

from .auth.db import init_db, AsyncSessionLocal
from .auth.routes import router as auth_router
from .appointments.routes import router as appointments_router

app = FastAPI(title="Vet clinic")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(appointments_router)

# Serve frontend (register, login pages) from same origin so cookies work
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True))

@app.on_event("startup")
async def on_startup():
  try:
    await init_db()
    from app.appointments.crud import ensure_doctors_seed
    async with AsyncSessionLocal() as db:
      await ensure_doctors_seed(db)
  except Exception as e:
    print(f"Error initializing database: {e}")
    raise e
        
