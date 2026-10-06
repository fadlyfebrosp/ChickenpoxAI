from typing import Literal

from pydantic import BaseModel


class PredictionResponse(BaseModel):
    prediction: Literal["Healthy Skin", "Chickenpox"]
    visual_observation: str
    model: str
    status: Literal["estimate"]


class HealthResponse(BaseModel):
    status: str = "ok"
    vision_model_available: bool
