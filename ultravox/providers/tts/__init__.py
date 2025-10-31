"""Text-to-Speech provider implementations."""

from ultravox.providers.tts.factory import create_tts_provider
from ultravox.providers.tts.sarvam import SarvamTTSProvider

__all__ = ["create_tts_provider", "SarvamTTSProvider"]
