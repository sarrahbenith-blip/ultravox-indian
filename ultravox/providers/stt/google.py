"""
Google Cloud Speech-to-Text provider implementation.
"""

import os
from typing import Any, AsyncIterator, Dict, Optional

from ultravox.providers.base import (
    ProviderAPIError,
    ProviderConfigError,
    STTProviderBase,
    UnsupportedLanguageError,
    validate_google_config,
)


class GoogleSTTProvider(STTProviderBase):
    """Google Cloud Speech-to-Text provider."""

    PROVIDER_NAME = "google"
    SUPPORTED_LANGUAGES = ["en-IN", "hi-IN", "ta-IN", "te-IN"]

    def __init__(self):
        """
        Initialize Google Cloud STT provider.

        Raises:
            ProviderConfigError: If configuration is invalid
        """
        super().__init__()
        self.validate_config()

        try:
            from google.cloud import speech

            self.client = speech.SpeechClient()
            self.speech = speech
        except ImportError:
            raise ProviderConfigError(
                "google",
                "google-cloud-speech library not installed. Install with: pip install google-cloud-speech",
            )

    def validate_config(self) -> None:
        """Validate Google Cloud configuration."""
        validate_google_config()

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
            # Prepare audio
            audio = self.speech.RecognitionAudio(content=audio_bytes)

            # Prepare config
            config = self.speech.RecognitionConfig(
                encoding=self.speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language,
                enable_automatic_punctuation=True,
            )

            # Call Google Cloud API
            response = self.client.recognize(config=config, audio=audio)

            # Extract results
            text = ""
            confidence = 0.0

            if response.results:
                result = response.results[0]
                if result.alternatives:
                    alternative = result.alternatives[0]
                    text = alternative.transcript
                    confidence = alternative.confidence

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
            # Collect all audio chunks
            audio_buffer = b""
            chunk_count = 0

            async for chunk in audio_stream:
                audio_buffer += chunk
                chunk_count += 1

                # Yield interim results every few chunks
                if chunk_count % 3 == 0:
                    partial_duration_ms = self._get_audio_duration_ms(audio_buffer)
                    yield {
                        "text": "",
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
