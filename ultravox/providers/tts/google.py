"""
Google Cloud Text-to-Speech provider implementation.
"""

import os
from typing import Any, Dict, List, Optional

from ultravox.providers.base import (
    ProviderAPIError,
    ProviderConfigError,
    TTSProviderBase,
    UnsupportedLanguageError,
    validate_google_config,
)

# Google Cloud voice IDs per language
GOOGLE_VOICES = {
    "en-IN": ["en-IN-Wavenet-A", "en-IN-Wavenet-B", "en-IN-Wavenet-C", "en-IN-Wavenet-D"],
    "hi-IN": ["hi-IN-Wavenet-A", "hi-IN-Wavenet-B", "hi-IN-Wavenet-C", "hi-IN-Wavenet-D"],
    "ta-IN": ["ta-IN-Wavenet-A", "ta-IN-Wavenet-B"],
    "te-IN": ["te-IN-Wavenet-A", "te-IN-Wavenet-B"],
}

GOOGLE_VOICE_DETAILS = {
    "en-IN-Wavenet-A": {"name": "English-IN A", "gender": "FEMALE", "language": "en-IN"},
    "en-IN-Wavenet-B": {"name": "English-IN B", "gender": "MALE", "language": "en-IN"},
    "en-IN-Wavenet-C": {"name": "English-IN C", "gender": "MALE", "language": "en-IN"},
    "en-IN-Wavenet-D": {"name": "English-IN D", "gender": "FEMALE", "language": "en-IN"},
    "hi-IN-Wavenet-A": {"name": "Hindi-IN A", "gender": "FEMALE", "language": "hi-IN"},
    "hi-IN-Wavenet-B": {"name": "Hindi-IN B", "gender": "MALE", "language": "hi-IN"},
    "hi-IN-Wavenet-C": {"name": "Hindi-IN C", "gender": "MALE", "language": "hi-IN"},
    "hi-IN-Wavenet-D": {"name": "Hindi-IN D", "gender": "FEMALE", "language": "hi-IN"},
    "ta-IN-Wavenet-A": {"name": "Tamil-IN A", "gender": "FEMALE", "language": "ta-IN"},
    "ta-IN-Wavenet-B": {"name": "Tamil-IN B", "gender": "MALE", "language": "ta-IN"},
    "te-IN-Wavenet-A": {"name": "Telugu-IN A", "gender": "FEMALE", "language": "te-IN"},
    "te-IN-Wavenet-B": {"name": "Telugu-IN B", "gender": "MALE", "language": "te-IN"},
}


class GoogleTTSProvider(TTSProviderBase):
    """Google Cloud Text-to-Speech provider."""

    PROVIDER_NAME = "google"
    SUPPORTED_LANGUAGES = ["en-IN", "hi-IN", "ta-IN", "te-IN"]
    DEFAULT_VOICE = {
        "en-IN": "en-IN-Wavenet-A",
        "hi-IN": "hi-IN-Wavenet-A",
        "ta-IN": "ta-IN-Wavenet-A",
        "te-IN": "te-IN-Wavenet-A",
    }
    AVAILABLE_VOICES = GOOGLE_VOICES

    def __init__(self, sample_rate: int = 16000):
        """
        Initialize Google Cloud TTS provider.

        Args:
            sample_rate: Audio sample rate (default: 16000 Hz)

        Raises:
            ProviderConfigError: If configuration is invalid
        """
        super().__init__()
        self.sample_rate = sample_rate
        self.validate_config()

        try:
            from google.cloud import texttospeech

            self.client = texttospeech.TextToSpeechClient()
            self.texttospeech = texttospeech
        except ImportError:
            raise ProviderConfigError(
                "google",
                "google-cloud-texttospeech library not installed. Install with: pip install google-cloud-texttospeech",
            )

    def validate_config(self) -> None:
        """Validate Google Cloud configuration."""
        validate_google_config()

    def synthesize(
        self, text: str, language: str, voice: Optional[str] = None, **kwargs
    ) -> bytes:
        """
        Convert text to speech using Google Cloud.

        Args:
            text: Text to synthesize
            language: Language code (e.g., "hi-IN")
            voice: Voice ID (uses default if None)
            **kwargs: Additional parameters

        Returns:
            WAV audio bytes (16kHz, 16-bit, mono PCM)

        Raises:
            ProviderAPIError: If API call fails
            UnsupportedLanguageError: If language not supported
        """
        if language not in self.SUPPORTED_LANGUAGES:
            raise UnsupportedLanguageError(
                self.PROVIDER_NAME, language, self.SUPPORTED_LANGUAGES
            )

        # Resolve voice
        if voice is None:
            voice = self.DEFAULT_VOICE[language]

        # Validate voice for language
        if voice not in GOOGLE_VOICES.get(language, []):
            available = GOOGLE_VOICES.get(language, [])
            raise ProviderAPIError(
                self.PROVIDER_NAME,
                f"Voice '{voice}' not available for language '{language}'. Available: {available}",
            )

        try:
            # Prepare request
            synthesis_input = self.texttospeech.SynthesisInput(text=text)
            voice_param = self.texttospeech.VoiceSelectionParams(
                language_code=language,
                name=voice,
            )
            audio_config = self.texttospeech.AudioConfig(
                audio_encoding=self.texttospeech.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.sample_rate,
            )

            # Call Google Cloud API
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice_param,
                audio_config=audio_config,
            )

            return response.audio_content

        except Exception as e:
            raise ProviderAPIError(
                self.PROVIDER_NAME,
                f"Failed to synthesize speech: {str(e)}",
                original_error=e,
            )

    def get_voices(self, language: str) -> List[Dict[str, Any]]:
        """
        Get available voices for a language.

        Args:
            language: Language code (e.g., "hi-IN")

        Returns:
            List of voice dicts with voice_id, name, gender, description

        Raises:
            UnsupportedLanguageError: If language not supported
        """
        if language not in self.SUPPORTED_LANGUAGES:
            raise UnsupportedLanguageError(
                self.PROVIDER_NAME, language, self.SUPPORTED_LANGUAGES
            )

        voices = []
        for voice_id in GOOGLE_VOICES[language]:
            details = GOOGLE_VOICE_DETAILS[voice_id]
            voices.append(
                {
                    "voice_id": voice_id,
                    "name": details["name"],
                    "gender": details["gender"].lower(),
                    "language": language,
                    "description": f"{details['name']} - {details['gender'].capitalize()} voice",
                }
            )
        return voices
