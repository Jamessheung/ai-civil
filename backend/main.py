from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from .database import engine, Base
from .routes import clusters
from .services.heartbeat import HeartbeatService

# Initialize Scheduler
scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("System Starting... AI Civilization logic active.")
    
    # Start Heartbeat (Every 10 minutes seems long for demo, setting to 60s for verification)
    # IN PRODUCTION: Use independent worker process.
    hb = HeartbeatService()
    scheduler.add_job(hb.run_tick, 'interval', minutes=10, id='heartbeat_tick')
    scheduler.start()
    
    yield
    
    # Shutdown logic
    print("System Shutting down...")
    scheduler.shutdown()

app = FastAPI(title="AI Civilization News API", version="1.1.1", lifespan=lifespan)

# CORS Config
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
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
    return {"status": "active", "system": "AI Civilization News Observer", "version": "v1.1.1"}
