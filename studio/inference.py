"""AI Provider Integration module using google-genai SDK.

Handles connection to Gemini models, enforces structured output schema,
and provides error handling for API timeouts and missing credentials.
"""

import os
from typing import Optional
from google import genai
from google.genai import types

from studio.models.treatment import TreatmentOutput


class InferenceError(Exception):
    """Custom exception raised during inference failures."""

    pass


class InferenceEngine:
    """Interface for invoking Gemini models with structured outputs."""

    DEFAULT_MODEL = "gemini-3.6-flash"

    @classmethod
    def generate_treatment(
        cls,
        prompt: str,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> TreatmentOutput:
        """Generate a structured film treatment using Gemini API.

        Args:
            prompt: The compiled hierarchical system prompt string.
            model_name: Optional model override. Defaults to GEMINI_MODEL env var or gemini-3.6-flash.
            api_key: Optional API key override. Defaults to GEMINI_API_KEY env var.

        Returns:
            TreatmentOutput: Structured Pydantic model instance.

        Raises:
            InferenceError: If API key is missing, network fails, or output schema fails validation.
        """
        resolved_api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not resolved_api_key:
            raise InferenceError(
                "Missing GEMINI_API_KEY environment variable.\n"
                "Please set GEMINI_API_KEY in your environment or .env file before running generation."
            )

        resolved_model = (
            model_name or os.environ.get("GEMINI_MODEL") or cls.DEFAULT_MODEL
        )

        try:
            client = genai.Client(api_key=resolved_api_key)
            response = client.models.generate_content(
                model=resolved_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=TreatmentOutput,
                ),
            )

            # Check if google-genai parsed the response automatically
            if hasattr(response, "parsed") and isinstance(response.parsed, TreatmentOutput):
                return response.parsed

            # Fallback to manual JSON validation if parsed is not populated
            if hasattr(response, "text") and response.text:
                return TreatmentOutput.model_validate_json(response.text)

            raise InferenceError("API returned an empty or invalid response payload.")

        except InferenceError:
            raise
        except Exception as err:
            raise InferenceError(f"Gemini API inference failed: {err}") from err
