"""
Sarvam AI Speech-to-Text provider implementation.
"""

import base64
import io
import os
from typing import Any, AsyncIterator, Dict, Optional

from ultravox.providers.base import (
    ProviderAPIError,
    ProviderConfigError,
    STTProviderBase,
    UnsupportedLanguageError,
    validate_sarvam_config,
)


class SarvamSTTProvider(STTProviderBase):
    """Sarvam AI Speech-to-Text provider."""

    PROVIDER_NAME = "sarvam"
    SUPPORTED_LANGUAGES = ["en-IN", "hi-IN", "ta-IN", "te-IN"]

    def __init__(self):
        """
        Initialize Sarvam AI STT provider.

        Raises:
            ProviderConfigError: If configuration is invalid
        """
        super().__init__()
        self.validate_config()

        try:
            from sarvamai import SarvamAI, AsyncSarvamAI

            api_key = os.getenv("SARVAM_API_KEY")
            self.client = SarvamAI(api_subscription_key=api_key)
            self.async_client = AsyncSarvamAI(api_subscription_key=api_key)
            self.model = "saarika:v2.5"
        except ImportError:
            raise ProviderConfigError(
                "sarvam", "sarvamai library not installed. Install with: pip install sarvamai"
            )

    def validate_config(self) -> None:
        """Validate Sarvam AI configuration."""
        validate_sarvam_config()

    def _get_audio_duration_ms(self, audio_bytes: bytes, sample_rate: int = 16000) -> int:
        """
        Calculate audio duration from byte size.

        Args:
            audio_bytes: Raw audio bytes
            sample_rate: Sample rate in Hz

        Returns:
            Duration in milliseconds
        """
        # WAV format: 2 bytes per sample (16-bit), mono
        # Bytes per second = sample_rate * 2 (for 16-bit mono)
        bytes_per_second = sample_rate * 2
        duration_seconds = len(audio_bytes) / bytes_per_second
        return int(duration_seconds * 1000)

    def transcribe(self, audio_bytes: bytes, language: str, **kwargs) -> Dict[str, Any]:
        """
        Convert speech audio to text (batch mode).

        Args:
            audio_bytes: Audio data (WAV format, 16kHz, 16-bit, mono PCM)
            language: Language code (e.g., "hi-IN")
            **kwargs: Additional parameters

        Returns:
            Dict with:
                - text: Transcribed text
                - confidence: Confidence score
                - language_detected: Detected language
                - duration_ms: Audio duration in milliseconds

        Raises:
            ProviderAPIError: If API call fails
            UnsupportedLanguageError: If language not supported
        """
        if language not in self.SUPPORTED_LANGUAGES:
            raise UnsupportedLanguageError(
                self.PROVIDER_NAME, language, self.SUPPORTED_LANGUAGES
            )

        try:
            # Write audio to temporary in-memory file
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.wav"

            # Call Sarvam AI STT API
            response = self.client.speech_to_text.transcribe(
                file=audio_file,
                model=self.model,
                language_code=language,
            )

            # Extract text and confidence from response
            text = response.get("transcript", "") if isinstance(response, dict) else str(response)
            confidence = response.get("confidence", 0.0) if isinstance(response, dict) else 0.5

            # Calculate duration
            duration_ms = self._get_audio_duration_ms(audio_bytes)

            return {
                "text": text,
                "confidence": confidence,
                "language_detected": language,
                "duration_ms": duration_ms,
            }

        except Exception as e:
            raise ProviderAPIError(
                self.PROVIDER_NAME,
                f"Failed to transcribe audio: {str(e)}",
                original_error=e,
            )

    async def transcribe_streaming(
        self, audio_stream: AsyncIterator[bytes], language: str, **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream transcription results as audio arrives.

        Args:
            audio_stream: Async iterator of audio chunks
            language: Language code
            **kwargs: Additional parameters

        Yields:
            Partial transcription results with is_final flag

        Raises:
            ProviderAPIError: If streaming fails
        """
        if language not in self.SUPPORTED_LANGUAGES:
            raise UnsupportedLanguageError(
                self.PROVIDER_NAME, language, self.SUPPORTED_LANGUAGES
            )

        try:
            # Note: Sarvam's streaming API requires WebSocket connection
            # This is a basic implementation - production would use their streaming API directly

            # Collect all audio chunks
            audio_buffer = b""
            total_duration_ms = 0
            chunk_count = 0

            async for chunk in audio_stream:
                audio_buffer += chunk
                chunk_count += 1

                # Yield interim results every few chunks
                if chunk_count % 3 == 0:
                    # For interim results, we'd need to process partial audio
                    # For now, yield partial text
                    partial_duration_ms = self._get_audio_duration_ms(audio_buffer)
                    yield {
                        "text": "",  # Would contain partial transcript
                        "is_final": False,
                        "confidence": 0.0,
                        "duration_ms": partial_duration_ms,
                    }

            # Process complete audio
            if audio_buffer:
                result = self.transcribe(audio_buffer, language, **kwargs)
                result["is_final"] = True
                yield result

        except Exception as e:
            raise ProviderAPIError(
                self.PROVIDER_NAME,
                f"Failed to stream transcribe audio: {str(e)}",
                original_error=e,
            )
