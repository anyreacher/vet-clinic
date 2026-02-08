from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from .auth.db import init_db
from .auth.routes import router as auth_router

app = FastAPI(title="Vet clinic")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.on_event("startup")
async def on_startup():
  try:
    await init_db()
  except Exception as e:
    print(f"Error initializing database: {e}")
    raise e
        
