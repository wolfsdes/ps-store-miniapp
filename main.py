from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import Base, engine, SessionLocal
from .seed import seed_catalog
from .routers import games, subscriptions, settings, orders, sync
app=FastAPI(title="24XSTORE API",version="0.3.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
Base.metadata.create_all(bind=engine)
with SessionLocal() as db: seed_catalog(db)
app.include_router(games.router,prefix="/api"); app.include_router(subscriptions.router,prefix="/api"); app.include_router(settings.router,prefix="/api"); app.include_router(orders.router,prefix="/api"); app.include_router(sync.router,prefix="/api")
@app.get("/api/health")
def health(): return {"status":"ok","version":"0.3.0"}
FRONTEND_DIR=Path("/app/frontend_dist")
if FRONTEND_DIR.exists():
    assets=FRONTEND_DIR/"assets"
    if assets.exists(): app.mount("/assets",StaticFiles(directory=assets),name="assets")
    @app.get("/{full_path:path}")
    def frontend(full_path:str):
        target=FRONTEND_DIR/full_path
        return FileResponse(target if full_path and target.exists() and target.is_file() else FRONTEND_DIR/"index.html")
else:
    @app.get("/")
    def root(): return {"name":"24XSTORE API","status":"ok"}
