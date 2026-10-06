from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

from config import APP_NAME, APP_VERSION, HOST, PORT
from model import classifier
from schemas import HealthResponse, PredictionResponse

app = FastAPI(title=APP_NAME, version=APP_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    vision_model_available = await run_in_threadpool(classifier.is_model_available)
    return {"status": "ok", "vision_model_available": vision_model_available}


@app.post("/predict", response_model=PredictionResponse)
async def predict(image: UploadFile = File(...), language: str = Form(default="id")) -> PredictionResponse:
    if language not in {"id", "en"}:
        raise HTTPException(status_code=400, detail="Language must be 'id' or 'en'.")

    try:
        file_bytes = await image.read()
        result = await run_in_threadpool(
            classifier.validate_and_predict,
            image.filename or "image.jpg",
            file_bytes,
            language,
        )
        return PredictionResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ConnectionError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=f"Local vision model failed: {exc}") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
