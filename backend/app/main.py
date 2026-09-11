from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import Base, engine, SessionLocal
from .seed import seed_games
from .routers import games, settings, orders

app = FastAPI(title="PS Store Turkey Mini App API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_games(db)

app.include_router(games.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(orders.router, prefix="/api")

@app.get("/api/health")
def health():
    return {"status": "ok"}

FRONTEND_DIR = Path("/app/frontend_dist")

if FRONTEND_DIR.exists():
    assets_dir = FRONTEND_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    def frontend(full_path: str):
        target = FRONTEND_DIR / full_path
        if full_path and target.exists() and target.is_file():
            return FileResponse(target)
        return FileResponse(FRONTEND_DIR / "index.html")
else:
    @app.get("/")
    def root():
        return {"name": "PS Store Turkey Mini App API", "status": "ok"}
