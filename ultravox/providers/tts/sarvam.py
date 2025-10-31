"""
Sarvam AI Text-to-Speech provider implementation.
"""

import io
import os
from typing import Any, Dict, List, Optional

import soundfile as sf

from ultravox.providers.base import (
    ProviderAPIError,
    ProviderConfigError,
    TTSProviderBase,
    UnsupportedLanguageError,
    validate_sarvam_config,
)

# Sarvam AI voice IDs per language
SARVAM_VOICES = {
    "en-IN": ["anushka", "meera"],
    "hi-IN": ["aditi", "arjun"],
    "ta-IN": ["lakshmi"],
    "te-IN": ["priya"],
}

SARVAM_VOICE_DETAILS = {
    "anushka": {"name": "Anushka", "gender": "female", "language": "en-IN"},
    "meera": {"name": "Meera", "gender": "female", "language": "en-IN"},
    "aditi": {"name": "Aditi", "gender": "female", "language": "hi-IN"},
    "arjun": {"name": "Arjun", "gender": "male", "language": "hi-IN"},
    "lakshmi": {"name": "Lakshmi", "gender": "female", "language": "ta-IN"},
    "priya": {"name": "Priya", "gender": "female", "language": "te-IN"},
}


class SarvamTTSProvider(TTSProviderBase):
    """Sarvam AI Text-to-Speech provider."""

    PROVIDER_NAME = "sarvam"
    SUPPORTED_LANGUAGES = ["en-IN", "hi-IN", "ta-IN", "te-IN"]
    DEFAULT_VOICE = {
        "en-IN": "anushka",
        "hi-IN": "aditi",
        "ta-IN": "lakshmi",
        "te-IN": "priya",
    }
    AVAILABLE_VOICES = SARVAM_VOICES

    def __init__(self, sample_rate: int = 16000):
        """
        Initialize Sarvam AI TTS provider.

        Args:
            sample_rate: Audio sample rate (default: 16000 Hz)

        Raises:
            ProviderConfigError: If configuration is invalid
        """
        super().__init__()
        self.sample_rate = sample_rate
        self.validate_config()

        try:
            from sarvamai import SarvamAI

            api_key = os.getenv("SARVAM_API_KEY")
            self.client = SarvamAI(api_subscription_key=api_key)
            self.model = "bulbul:v2"
        except ImportError:
            raise ProviderConfigError(
                "sarvam", "sarvamai library not installed. Install with: pip install sarvamai"
            )

    def validate_config(self) -> None:
        """Validate Sarvam AI configuration."""
        validate_sarvam_config()

    def synthesize(
        self, text: str, language: str, voice: Optional[str] = None, **kwargs
    ) -> bytes:
        """
        Convert text to speech using Sarvam AI.

        Args:
            text: Text to synthesize
            language: Language code (e.g., "hi-IN")
            voice: Voice ID (uses default if None)
            **kwargs: Additional parameters (speed, pitch)

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
        if voice not in SARVAM_VOICES.get(language, []):
            available = SARVAM_VOICES.get(language, [])
            raise ProviderAPIError(
                self.PROVIDER_NAME,
                f"Voice '{voice}' not available for language '{language}'. Available: {available}",
            )

        try:
            # Call Sarvam AI API
            audio_response = self.client.text_to_speech.convert(
                target_language_code=language,
                text=text,
                model=self.model,
                speaker=voice,
            )

            # Handle response - Sarvam returns bytes directly
            if isinstance(audio_response, bytes):
                audio_bytes = audio_response
            else:
                # If response has audio content attribute
                audio_bytes = audio_response.audio_content if hasattr(audio_response, 'audio_content') else audio_response

            return audio_bytes

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
        for voice_id in SARVAM_VOICES[language]:
            details = SARVAM_VOICE_DETAILS[voice_id]
            voices.append(
                {
                    "voice_id": voice_id,
                    "name": details["name"],
                    "gender": details["gender"],
                    "language": language,
                    "description": f"{details['name']} - {details['gender'].capitalize()} voice",
                }
            )
        return voices
