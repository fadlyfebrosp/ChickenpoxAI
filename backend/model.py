from __future__ import annotations

import base64
import json
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config import ALLOWED_CLASSES, OLLAMA_MODEL, OLLAMA_URL
from preprocessing import validate_image_bytes


class OllamaVisionAnalyzer:
    def __init__(self, base_url: str = OLLAMA_URL, model_name: str = OLLAMA_MODEL) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    def _request_json(self, endpoint: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.base_url}{endpoint}",
            data=data,
            headers={"Content-Type": "application/json"} if data is not None else {},
            method="GET" if data is None else "POST",
        )
        try:
            with urlopen(request, timeout=180) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Ollama returned HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise ConnectionError(
                "Ollama is unavailable. Start the Ollama application and ensure its local API is running."
            ) from exc

    def is_model_available(self) -> bool:
        try:
            response = self._request_json("/api/tags")
        except (ConnectionError, RuntimeError):
            return False
        model_names = {item.get("name") for item in response.get("models", [])}
        return self.model_name in model_names or f"{self.model_name}:latest" in model_names

    def analyze_image(self, file_name: str, file_bytes: bytes, language: str = "id") -> Dict[str, str]:
        if not self.is_model_available():
            raise ConnectionError(
                f"Local model '{self.model_name}' is unavailable. Start Ollama and run 'ollama pull {self.model_name}'."
            )

        image = validate_image_bytes(file_bytes, file_name)
        from io import BytesIO

        image_buffer = BytesIO()
        image.save(image_buffer, format="JPEG", quality=90)
        image_base64 = base64.b64encode(image_buffer.getvalue()).decode("ascii")

        if language == "en":
            prompt = (
                "Research demo, not medical diagnosis. Look at the skin image and choose the closest dataset label: "
                "Healthy Skin or Chickenpox. Give your best visual guess. "
                "Briefly describe only visible features in English. Do not infer itch, pain, or other unseen symptoms. "
                "Visual appearance alone cannot confirm disease."
            )
        else:
            prompt = (
                "Research demo, not medical diagnosis. Look at the skin image and choose the closest dataset label: "
                "Healthy Skin or Chickenpox. Give your best visual guess. "
                "Briefly describe only visible features in Bahasa Indonesia. Do not infer itch, pain, or other unseen symptoms. "
                "Visual appearance alone cannot confirm disease."
            )

        response_schema = {
            "type": "object",
            "properties": {
                "prediction": {"type": "string", "enum": ALLOWED_CLASSES},
                "visual_observation": {"type": "string"},
            },
            "required": ["prediction", "visual_observation"],
        }
        response = self._request_json(
            "/api/chat",
            {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": f"{prompt} Respond only with the required JSON.",
                        "images": [image_base64],
                    }
                ],
                "format": response_schema,
                "stream": False,
                "options": {"temperature": 0, "num_predict": 150},
            },
        )

        content = response.get("message", {}).get("content")
        if not isinstance(content, str):
            raise RuntimeError("Ollama returned an empty image analysis.")
        try:
            result = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Ollama returned an invalid structured analysis.") from exc

        prediction = result.get("prediction")
        visual_observation = result.get("visual_observation")
        if (
            prediction not in ALLOWED_CLASSES
            or not isinstance(visual_observation, str)
            or not visual_observation.strip()
        ):
            raise RuntimeError("Ollama returned an analysis outside the supported response format.")

        return {
            "prediction": prediction,
            "visual_observation": visual_observation.strip(),
            "model": self.model_name,
            "status": "estimate",
        }

    def validate_and_predict(self, file_name: str, file_bytes: bytes, language: str = "id") -> Dict[str, Any]:
        return self.analyze_image(file_name, file_bytes, language)


classifier = OllamaVisionAnalyzer()
