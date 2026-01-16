from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import clusters

app = FastAPI(title="AI Civilization News API", version="1.1.1")

# CORS Config
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clusters.router, prefix="/api", tags=["clusters"])

@app.get("/")
def read_root():
    return {"status": "active", "system": "AI Civilization News Observer (Cloud Mode)", "version": "v1.1.1"}
