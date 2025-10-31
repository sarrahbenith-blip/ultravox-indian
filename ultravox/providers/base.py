"""
Base classes and exceptions for provider abstraction layer.
"""

import abc
import os
from typing import Any, AsyncIterator, Dict, List, Optional


# ============================================================================
# Custom Exceptions
# ============================================================================


class ProviderAPIError(Exception):
    """Raised when provider API call fails."""

    def __init__(self, provider: str, message: str, original_error: Optional[Exception] = None):
        self.provider = provider
        self.original_error = original_error
        super().__init__(f"[{provider}] {message}")


class UnsupportedLanguageError(Exception):
    """Raised when requested language is not supported by provider."""

    def __init__(self, provider: str, language: str, supported_languages: List[str]):
        self.provider = provider
        self.language = language
        self.supported_languages = supported_languages
        msg = f"[{provider}] Language '{language}' not supported. Supported: {', '.join(supported_languages)}"
        super().__init__(msg)


class ProviderConfigError(Exception):
    """Raised when provider configuration is invalid."""

    def __init__(self, provider: str, message: str):
        self.provider = provider
        super().__init__(f"[{provider}] Config error: {message}")


# ============================================================================
# Base Classes
# ============================================================================


class TTSProviderBase(abc.ABC):
    """Abstract base class for Text-to-Speech providers."""

    PROVIDER_NAME: str  # e.g., "sarvam", "google"
    SUPPORTED_LANGUAGES: List[str]  # e.g., ["en-IN", "hi-IN", "ta-IN", "te-IN"]
    DEFAULT_VOICE: Dict[str, str]  # language -> default voice mapping
    AVAILABLE_VOICES: Dict[str, List[str]]  # language -> voice list mapping

    def __init__(self):
        """Initialize TTS provider."""
        if not hasattr(self, "PROVIDER_NAME"):
            raise NotImplementedError("PROVIDER_NAME must be defined in subclasses")
        if not hasattr(self, "SUPPORTED_LANGUAGES"):
            raise NotImplementedError("SUPPORTED_LANGUAGES must be defined in subclasses")
        if not hasattr(self, "DEFAULT_VOICE"):
            raise NotImplementedError("DEFAULT_VOICE must be defined in subclasses")
        if not hasattr(self, "AVAILABLE_VOICES"):
            raise NotImplementedError("AVAILABLE_VOICES must be defined in subclasses")

    @abc.abstractmethod
    def synthesize(
        self, text: str, language: str, voice: Optional[str] = None, **kwargs
    ) -> bytes:
        """
        Convert text to speech audio.

        Args:
            text: Text to synthesize
            language: Language code (e.g., "en-IN", "hi-IN")
            voice: Voice ID (uses default if None)
            **kwargs: Provider-specific parameters

        Returns:
            WAV audio bytes (16kHz, 16-bit, mono PCM)

        Raises:
            ProviderAPIError: If API call fails
            UnsupportedLanguageError: If language not supported
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_voices(self, language: str) -> List[Dict[str, Any]]:
        """
        Get available voices for a language.

        Args:
            language: Language code

        Returns:
            List of voice dicts with: voice_id, name, gender, description

        Raises:
            UnsupportedLanguageError: If language not supported
        """
        raise NotImplementedError

    def validate_config(self) -> None:
        """
        Validate provider configuration (API keys, credentials, etc.).

        Raises:
            ProviderConfigError: If configuration is invalid
        """
        pass


class STTProviderBase(abc.ABC):
    """Abstract base class for Speech-to-Text providers."""

    PROVIDER_NAME: str
    SUPPORTED_LANGUAGES: List[str]

    def __init__(self):
        """Initialize STT provider."""
        if not hasattr(self, "PROVIDER_NAME"):
            raise NotImplementedError("PROVIDER_NAME must be defined in subclasses")
        if not hasattr(self, "SUPPORTED_LANGUAGES"):
            raise NotImplementedError("SUPPORTED_LANGUAGES must be defined in subclasses")

    @abc.abstractmethod
    def transcribe(self, audio_bytes: bytes, language: str, **kwargs) -> Dict[str, Any]:
        """
        Convert speech audio to text (batch mode).

        Args:
            audio_bytes: Audio data (WAV format, 16kHz, 16-bit, mono PCM)
            language: Language code (e.g., "en-IN", "hi-IN")
            **kwargs: Provider-specific parameters

        Returns:
            Dict with:
                - text: Transcribed text
                - confidence: Confidence score (0.0 to 1.0)
                - language_detected: Detected language code (if different from requested)
                - duration_ms: Audio duration in milliseconds

        Raises:
            ProviderAPIError: If API call fails
            UnsupportedLanguageError: If language not supported
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def transcribe_streaming(
        self, audio_stream: AsyncIterator[bytes], language: str, **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream transcription results as audio arrives.

        Args:
            audio_stream: Async iterator of audio chunks
            language: Language code
            **kwargs: Provider-specific parameters

        Yields:
            Partial transcription results with:
                - text: Transcribed text (partial or final)
                - is_final: Boolean indicating if this is the final result
                - confidence: Confidence score

        Raises:
            ProviderAPIError: If streaming fails
        """
        raise NotImplementedError

    def validate_config(self) -> None:
        """
        Validate provider configuration (API keys, credentials, etc.).

        Raises:
            ProviderConfigError: If configuration is invalid
        """
        pass


# ============================================================================
# Validation Helpers
# ============================================================================


def validate_sarvam_config() -> None:
    """Validate Sarvam AI configuration."""
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        raise ProviderConfigError(
            "sarvam", "SARVAM_API_KEY environment variable not set"
        )


def validate_google_config() -> None:
    """Validate Google Cloud configuration."""
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        raise ProviderConfigError(
            "google",
            "GOOGLE_APPLICATION_CREDENTIALS environment variable not set",
        )
    if not os.path.exists(creds_path):
        raise ProviderConfigError(
            "google", f"Google Cloud credentials file not found: {creds_path}"
        )
