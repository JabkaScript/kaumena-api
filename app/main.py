from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.audio import router as audio_router
from .core.config import load_models_config
from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model_config = load_models_config()
    yield
    # Clean up the ML models and release the resources
app = FastAPI(title="Kaumena API", version="0.1.0", lifespan=lifespan, debug=True)
app.include_router(audio_router, prefix="/v1/audio")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@app.get("/v1")
def root():
    return {"message": "Welcome to Kaumena API"}

