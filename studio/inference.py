"""AI Provider Integration module using google-genai SDK.

Handles connection to Gemini models, enforces structured output schema,
and provides error handling for API timeouts and missing credentials.
"""

import os
import time
from typing import Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

from studio.models.treatment import TreatmentOutput

load_dotenv()


class InferenceError(Exception):
    """Custom exception raised during inference failures."""

    pass


class InferenceEngine:
    """Interface for invoking Gemini models with structured outputs."""

    DEFAULT_MODEL = "gemini-3.6-flash"
    MAX_RETRIES = 3

    @classmethod
    def revise_treatment(
        cls,
        current_treatment: TreatmentOutput,
        notes: str,
        original_prompt: Optional[str] = None,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> TreatmentOutput:
        """Revise an existing film treatment based on user notes and original prompt context."""
        from studio.utils.prompt_builder import PromptBuilder

        revised_prompt = PromptBuilder.compile_revision_prompt(
            current_treatment=current_treatment,
            notes=notes,
            original_prompt=original_prompt,
        )
        return cls.generate_treatment(
            prompt=revised_prompt,
            model_name=model_name,
            api_key=api_key,
        )

    @classmethod
    def generate_screenplay(
        cls,
        prompt: str,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> str:
        """Generate a raw Fountain screenplay string using Gemini API.

        Args:
            prompt: The compiled screenplay prompt string.
            model_name: Optional model override.
            api_key: Optional API key override.

        Returns:
            str: Clean Fountain screenplay text.

        Raises:
            InferenceError: If API key is missing or network fails.
        """
        from studio.utils.screenplay_store import clean_fountain_text

        resolved_api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not resolved_api_key:
            raise InferenceError(
                "Missing GEMINI_API_KEY environment variable.\n"
                "Please set GEMINI_API_KEY in your environment or .env file before running screenplay generation."
            )

        resolved_model = (
            model_name or os.environ.get("GEMINI_MODEL") or cls.DEFAULT_MODEL
        )

        last_exception = None
        for attempt in range(1, cls.MAX_RETRIES + 1):
            try:
                client = genai.Client(api_key=resolved_api_key)
                response = client.models.generate_content(
                    model=resolved_model,
                    contents=prompt,
                )

                if hasattr(response, "text") and response.text:
                    return clean_fountain_text(response.text)

                raise InferenceError("API returned an empty response payload.")

            except InferenceError:
                raise
            except Exception as err:
                last_exception = err
                err_str = str(err).lower()
                is_transient = any(
                    code in err_str
                    for code in [
                        "500",
                        "502",
                        "503",
                        "504",
                        "overloaded",
                        "unavailable",
                        "resourceexhausted",
                        "internal server error",
                        "transient",
                        "rate limit",
                    ]
                )
                if is_transient and attempt < cls.MAX_RETRIES:
                    backoff = 2 ** (attempt - 1)
                    time.sleep(backoff)
                    continue
                else:
                    raise InferenceError(f"Gemini API screenplay generation failed: {err}") from err

        raise InferenceError(f"Gemini API screenplay generation failed after {cls.MAX_RETRIES} attempts: {last_exception}")

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

        last_exception = None
        for attempt in range(1, cls.MAX_RETRIES + 1):
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
                last_exception = err
                err_str = str(err).lower()
                is_transient = any(
                    code in err_str
                    for code in [
                        "500",
                        "502",
                        "503",
                        "504",
                        "overloaded",
                        "unavailable",
                        "resourceexhausted",
                        "internal server error",
                        "transient",
                        "rate limit",
                    ]
                )
                if is_transient and attempt < cls.MAX_RETRIES:
                    backoff = 2 ** (attempt - 1)
                    time.sleep(backoff)
                    continue
                else:
                    raise InferenceError(f"Gemini API inference failed: {err}") from err

        raise InferenceError(f"Gemini API inference failed after {cls.MAX_RETRIES} attempts: {last_exception}")

