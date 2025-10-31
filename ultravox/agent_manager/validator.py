"""
Agent configuration validator.
"""

from typing import Optional, Tuple

SUPPORTED_LANGUAGES = ["en-IN", "hi-IN", "ta-IN", "te-IN"]
SUPPORTED_PROVIDERS = ["sarvam", "google"]
SUPPORTED_USE_CASES = ["healthcare", "education", "ecommerce"]

# Voice availability mapping
VOICES_BY_PROVIDER_LANGUAGE = {
    "sarvam": {
        "en-IN": ["anushka", "meera"],
        "hi-IN": ["aditi", "arjun"],
        "ta-IN": ["lakshmi"],
        "te-IN": ["priya"],
    },
    "google": {
        "en-IN": ["en-IN-Wavenet-A", "en-IN-Wavenet-B", "en-IN-Wavenet-C", "en-IN-Wavenet-D"],
        "hi-IN": ["hi-IN-Wavenet-A", "hi-IN-Wavenet-B", "hi-IN-Wavenet-C", "hi-IN-Wavenet-D"],
        "ta-IN": ["ta-IN-Wavenet-A", "ta-IN-Wavenet-B"],
        "te-IN": ["te-IN-Wavenet-A", "te-IN-Wavenet-B"],
    },
}


def validate_language_code(code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate language code.

    Args:
        code: Language code (e.g., "hi-IN")

    Returns:
        Tuple of (is_valid, error_message)
    """
    if code not in SUPPORTED_LANGUAGES:
        return False, f"Language '{code}' not supported. Supported: {', '.join(SUPPORTED_LANGUAGES)}"
    return True, None


def validate_provider_name(provider: str) -> Tuple[bool, Optional[str]]:
    """
    Validate provider name.

    Args:
        provider: Provider name (e.g., "sarvam", "google")

    Returns:
        Tuple of (is_valid, error_message)
    """
    if provider not in SUPPORTED_PROVIDERS:
        return False, f"Provider '{provider}' not supported. Supported: {', '.join(SUPPORTED_PROVIDERS)}"
    return True, None


def validate_voice_id(provider: str, language: str, voice: str) -> Tuple[bool, Optional[str]]:
    """
    Validate voice ID for provider and language.

    Args:
        provider: Provider name
        language: Language code
        voice: Voice ID

    Returns:
        Tuple of (is_valid, error_message)
    """
    if provider not in VOICES_BY_PROVIDER_LANGUAGE:
        return False, f"Provider '{provider}' not configured"

    if language not in VOICES_BY_PROVIDER_LANGUAGE[provider]:
        return False, f"Language '{language}' not supported by provider '{provider}'"

    available_voices = VOICES_BY_PROVIDER_LANGUAGE[provider][language]
    if voice not in available_voices:
        return False, f"Voice '{voice}' not available. Available: {', '.join(available_voices)}"

    return True, None


def validate_agent_config(config: dict) -> Tuple[bool, Optional[str]]:
    """
    Validate complete agent configuration.

    Args:
        config: Agent configuration dict

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate required fields
    if "name" not in config:
        return False, "Missing required field: name"

    if "language_config" not in config:
        return False, "Missing required field: language_config"

    if "tts_config" not in config:
        return False, "Missing required field: tts_config"

    if "stt_config" not in config:
        return False, "Missing required field: stt_config"

    if "model_config" not in config:
        return False, "Missing required field: model_config"

    # Validate name
    name = config.get("name", "")
    if not isinstance(name, str) or len(name) < 3 or len(name) > 100:
        return False, "Name must be a string between 3 and 100 characters"

    # Validate language_config
    lang_cfg = config.get("language_config", {})

    primary_lang = lang_cfg.get("primary_language")
    if not primary_lang:
        return False, "Missing primary_language in language_config"

    is_valid, error = validate_language_code(primary_lang)
    if not is_valid:
        return False, f"Invalid primary_language: {error}"

    # Validate supported languages
    supported_langs = lang_cfg.get("supported_languages", [])
    if not isinstance(supported_langs, list) or not supported_langs:
        return False, "supported_languages must be a non-empty list"

    for lang in supported_langs:
        is_valid, error = validate_language_code(lang)
        if not is_valid:
            return False, f"Invalid supported_languages: {error}"

    # Validate TTS config
    tts_cfg = config.get("tts_config", {})
    tts_provider = tts_cfg.get("provider")

    if not tts_provider:
        return False, "Missing provider in tts_config"

    is_valid, error = validate_provider_name(tts_provider)
    if not is_valid:
        return False, f"Invalid tts provider: {error}"

    tts_language = tts_cfg.get("language", primary_lang)
    is_valid, error = validate_language_code(tts_language)
    if not is_valid:
        return False, f"Invalid tts_config language: {error}"

    tts_voice = tts_cfg.get("voice")
    if not tts_voice:
        return False, "Missing voice in tts_config"

    is_valid, error = validate_voice_id(tts_provider, tts_language, tts_voice)
    if not is_valid:
        return False, f"Invalid tts_config voice: {error}"

    # Validate TTS speed and pitch
    speed = tts_cfg.get("speed", 1.0)
    if not isinstance(speed, (int, float)) or speed < 0.5 or speed > 2.0:
        return False, "TTS speed must be between 0.5 and 2.0"

    pitch = tts_cfg.get("pitch", 1.0)
    if not isinstance(pitch, (int, float)) or pitch < 0.5 or pitch > 2.0:
        return False, "TTS pitch must be between 0.5 and 2.0"

    # Validate STT config
    stt_cfg = config.get("stt_config", {})
    stt_provider = stt_cfg.get("provider")

    if not stt_provider:
        return False, "Missing provider in stt_config"

    is_valid, error = validate_provider_name(stt_provider)
    if not is_valid:
        return False, f"Invalid stt provider: {error}"

    stt_language = stt_cfg.get("language", primary_lang)
    is_valid, error = validate_language_code(stt_language)
    if not is_valid:
        return False, f"Invalid stt_config language: {error}"

    # Validate model config
    model_cfg = config.get("model_config", {})

    if "model_path" not in model_cfg:
        return False, "Missing model_path in model_config"

    temperature = model_cfg.get("temperature", 0.7)
    if not isinstance(temperature, (int, float)) or temperature < 0.0 or temperature > 2.0:
        return False, "Model temperature must be between 0.0 and 2.0"

    max_tokens = model_cfg.get("max_tokens", 150)
    if not isinstance(max_tokens, int) or max_tokens < 1 or max_tokens > 2048:
        return False, "Model max_tokens must be between 1 and 2048"

    return True, None
