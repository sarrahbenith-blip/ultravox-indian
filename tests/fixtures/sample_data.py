"""Sample data and fixtures for testing."""

import struct
import wave
from io import BytesIO

# Sample agent configurations for testing

SAMPLE_AGENT_HINDI = {
    "name": "Hindi Healthcare Assistant",
    "description": "Test agent for Hindi conversations",
    "language_config": {
        "primary_language": "hi-IN",
        "supported_languages": ["hi-IN", "en-IN"],
        "enable_code_mixing": True,
    },
    "tts_config": {
        "provider": "sarvam",
        "voice": "aditi",
        "language": "hi-IN",
        "speed": 1.0,
        "pitch": 1.0,
    },
    "stt_config": {
        "provider": "sarvam",
        "language": "hi-IN",
        "enable_punctuation": True,
        "streaming": True,
    },
    "model_config": {
        "model_path": "fixie-ai/ultravox-v0_2",
        "temperature": 0.7,
        "max_tokens": 150,
        "system_prompt": "You are a helpful healthcare assistant.",
    },
    "metadata": {
        "use_case": "healthcare",
        "owner": "user_123",
        "tags": ["healthcare", "hindi"],
    },
}

SAMPLE_AGENT_ENGLISH = {
    "name": "English Education Assistant",
    "description": "Test agent for English conversations",
    "language_config": {
        "primary_language": "en-IN",
        "supported_languages": ["en-IN"],
        "enable_code_mixing": False,
    },
    "tts_config": {
        "provider": "google",
        "voice": "en-IN-Wavenet-A",
        "language": "en-IN",
        "speed": 1.0,
        "pitch": 1.0,
    },
    "stt_config": {
        "provider": "google",
        "language": "en-IN",
        "enable_punctuation": True,
        "streaming": True,
    },
    "model_config": {
        "model_path": "fixie-ai/ultravox-v0_2",
        "temperature": 0.5,
        "max_tokens": 200,
        "system_prompt": "You are an educational assistant.",
    },
    "metadata": {
        "use_case": "education",
        "owner": "user_456",
        "tags": ["education", "english"],
    },
}

SAMPLE_AGENT_TAMIL = {
    "name": "Tamil E-commerce Assistant",
    "description": "Test agent for Tamil conversations",
    "language_config": {
        "primary_language": "ta-IN",
        "supported_languages": ["ta-IN", "en-IN"],
        "enable_code_mixing": True,
    },
    "tts_config": {
        "provider": "sarvam",
        "voice": "lakshmi",
        "language": "ta-IN",
        "speed": 1.0,
        "pitch": 1.0,
    },
    "stt_config": {
        "provider": "sarvam",
        "language": "ta-IN",
        "enable_punctuation": True,
        "streaming": True,
    },
    "model_config": {
        "model_path": "fixie-ai/ultravox-v0_2",
        "temperature": 0.6,
        "max_tokens": 150,
        "system_prompt": "You are an e-commerce support assistant.",
    },
    "metadata": {
        "use_case": "ecommerce",
        "owner": "user_789",
        "tags": ["ecommerce", "tamil"],
    },
}

SAMPLE_AGENT_TELUGU = {
    "name": "Telugu Support Assistant",
    "description": "Test agent for Telugu conversations",
    "language_config": {
        "primary_language": "te-IN",
        "supported_languages": ["te-IN"],
        "enable_code_mixing": False,
    },
    "tts_config": {
        "provider": "google",
        "voice": "te-IN-Wavenet-A",
        "language": "te-IN",
        "speed": 1.0,
        "pitch": 1.0,
    },
    "stt_config": {
        "provider": "google",
        "language": "te-IN",
        "enable_punctuation": True,
        "streaming": True,
    },
    "model_config": {
        "model_path": "fixie-ai/ultravox-v0_2",
        "temperature": 0.7,
        "max_tokens": 150,
        "system_prompt": "You are a support assistant.",
    },
    "metadata": {
        "use_case": "healthcare",
        "owner": "user_999",
        "tags": ["support", "telugu"],
    },
}

# Invalid agent configs for validation testing

INVALID_AGENT_NO_NAME = {
    "language_config": {
        "primary_language": "hi-IN",
        "supported_languages": ["hi-IN", "en-IN"],
    },
    "tts_config": {"provider": "sarvam", "voice": "aditi", "language": "hi-IN"},
    "stt_config": {"provider": "sarvam", "language": "hi-IN"},
    "model_config": {"model_path": "fixie-ai/ultravox-v0_2", "temperature": 0.7, "max_tokens": 150},
}

INVALID_AGENT_BAD_LANGUAGE = {
    "name": "Bad Language Agent",
    "language_config": {
        "primary_language": "xx-XX",
        "supported_languages": ["xx-XX"],
    },
    "tts_config": {"provider": "sarvam", "voice": "aditi", "language": "xx-XX"},
    "stt_config": {"provider": "sarvam", "language": "xx-XX"},
    "model_config": {"model_path": "fixie-ai/ultravox-v0_2", "temperature": 0.7, "max_tokens": 150},
}

INVALID_AGENT_BAD_PROVIDER = {
    "name": "Bad Provider Agent",
    "language_config": {
        "primary_language": "hi-IN",
        "supported_languages": ["hi-IN"],
    },
    "tts_config": {"provider": "invalid_provider", "voice": "aditi", "language": "hi-IN"},
    "stt_config": {"provider": "sarvam", "language": "hi-IN"},
    "model_config": {"model_path": "fixie-ai/ultravox-v0_2", "temperature": 0.7, "max_tokens": 150},
}

INVALID_AGENT_BAD_VOICE = {
    "name": "Bad Voice Agent",
    "language_config": {
        "primary_language": "hi-IN",
        "supported_languages": ["hi-IN"],
    },
    "tts_config": {"provider": "sarvam", "voice": "invalid_voice", "language": "hi-IN"},
    "stt_config": {"provider": "sarvam", "language": "hi-IN"},
    "model_config": {"model_path": "fixie-ai/ultravox-v0_2", "temperature": 0.7, "max_tokens": 150},
}


def create_sample_wav_audio(duration_seconds: float = 2.0, sample_rate: int = 16000) -> bytes:
    """
    Create a sample WAV audio file for testing.

    Args:
        duration_seconds: Duration of audio in seconds
        sample_rate: Sample rate in Hz (default 16000)

    Returns:
        WAV audio bytes (16-bit, mono PCM)
    """
    num_samples = int(duration_seconds * sample_rate)

    # Create simple sine wave
    frequency = 440  # 440 Hz (A note)
    samples = []
    for i in range(num_samples):
        sample = int(32767 * 0.5 * sin_sample(2 * 3.14159 * frequency * i / sample_rate))
        samples.append(sample)

    # Create WAV file in memory
    wav_buffer = BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        # Pack samples as 16-bit signed integers
        for sample in samples:
            wav_file.writeframes(struct.pack("<h", sample))

    return wav_buffer.getvalue()


def sin_sample(x: float) -> float:
    """Simple sine wave approximation."""
    # Normalize to [-1, 1]
    x = x % (2 * 3.14159)
    if x < 3.14159:
        return x / 3.14159
    else:
        return 2 - (x / 3.14159)


# Usage tracking sample events

SAMPLE_USAGE_EVENT = {
    "event_id": "evt_test1234",
    "timestamp": "2025-01-15T10:30:05.800Z",
    "agent_id": "agent_a1b2c3d4",
    "session_id": "sess_12345",
    "owner": "user_123",
    "api_endpoint": "/api/v1/agents/agent_a1b2c3d4/chat",
    "stt_usage": {
        "provider": "sarvam",
        "audio_duration_seconds": 2.1,
        "language": "hi-IN",
        "transcript_length": 45,
        "cost_usd": 0.00042,
    },
    "model_usage": {
        "model_path": "fixie-ai/ultravox-v0_2",
        "input_tokens": 25,
        "output_tokens": 45,
        "total_tokens": 70,
        "inference_time_seconds": 0.3,
        "cost_usd": 0.001,
    },
    "tts_usage": {
        "provider": "sarvam",
        "text_length": 85,
        "audio_duration_seconds": 3.2,
        "language": "hi-IN",
        "voice": "aditi",
        "cost_usd": 0.00064,
    },
    "total_duration_seconds": 5.6,
    "total_cost_usd": 0.00206,
}
