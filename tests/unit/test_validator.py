"""Unit tests for agent configuration validator."""

import pytest

from ultravox.agent_manager.validator import (
    validate_agent_config,
    validate_language_code,
    validate_provider_name,
    validate_voice_id,
)
from tests.fixtures.sample_data import (
    INVALID_AGENT_BAD_LANGUAGE,
    INVALID_AGENT_BAD_PROVIDER,
    INVALID_AGENT_BAD_VOICE,
    INVALID_AGENT_NO_NAME,
    SAMPLE_AGENT_ENGLISH,
    SAMPLE_AGENT_HINDI,
    SAMPLE_AGENT_TAMIL,
    SAMPLE_AGENT_TELUGU,
)


class TestLanguageValidation:
    """Test language code validation."""

    def test_valid_languages(self):
        """Test valid language codes."""
        for lang in ["en-IN", "hi-IN", "ta-IN", "te-IN"]:
            is_valid, error = validate_language_code(lang)
            assert is_valid is True, f"Language {lang} should be valid"
            assert error is None

    def test_invalid_language(self):
        """Test invalid language code."""
        is_valid, error = validate_language_code("xx-XX")
        assert is_valid is False
        assert "not supported" in error


class TestProviderValidation:
    """Test provider name validation."""

    def test_valid_providers(self):
        """Test valid provider names."""
        for provider in ["sarvam", "google"]:
            is_valid, error = validate_provider_name(provider)
            assert is_valid is True
            assert error is None

    def test_invalid_provider(self):
        """Test invalid provider name."""
        is_valid, error = validate_provider_name("invalid")
        assert is_valid is False
        assert "not supported" in error


class TestVoiceValidation:
    """Test voice ID validation."""

    def test_valid_voices_sarvam(self):
        """Test valid Sarvam voices."""
        test_cases = [
            ("sarvam", "hi-IN", "aditi"),
            ("sarvam", "hi-IN", "arjun"),
            ("sarvam", "ta-IN", "lakshmi"),
            ("sarvam", "te-IN", "priya"),
        ]
        for provider, language, voice in test_cases:
            is_valid, error = validate_voice_id(provider, language, voice)
            assert is_valid is True, f"Voice {voice} should be valid for {language}"

    def test_valid_voices_google(self):
        """Test valid Google Cloud voices."""
        test_cases = [
            ("google", "hi-IN", "hi-IN-Wavenet-A"),
            ("google", "ta-IN", "ta-IN-Wavenet-B"),
            ("google", "en-IN", "en-IN-Wavenet-A"),
            ("google", "te-IN", "te-IN-Wavenet-A"),
        ]
        for provider, language, voice in test_cases:
            is_valid, error = validate_voice_id(provider, language, voice)
            assert is_valid is True, f"Voice {voice} should be valid"

    def test_invalid_voice(self):
        """Test invalid voice ID."""
        is_valid, error = validate_voice_id("sarvam", "hi-IN", "invalid_voice")
        assert is_valid is False
        assert "not available" in error

    def test_voice_language_mismatch(self):
        """Test voice not available for language."""
        is_valid, error = validate_voice_id("sarvam", "ta-IN", "arjun")
        assert is_valid is False
        assert "not available" in error


class TestAgentConfigValidation:
    """Test complete agent configuration validation."""

    def test_valid_agent_hindi(self):
        """Test valid Hindi agent configuration."""
        is_valid, error = validate_agent_config(SAMPLE_AGENT_HINDI)
        assert is_valid is True, f"Error: {error}"

    def test_valid_agent_english(self):
        """Test valid English agent configuration."""
        is_valid, error = validate_agent_config(SAMPLE_AGENT_ENGLISH)
        assert is_valid is True, f"Error: {error}"

    def test_valid_agent_tamil(self):
        """Test valid Tamil agent configuration."""
        is_valid, error = validate_agent_config(SAMPLE_AGENT_TAMIL)
        assert is_valid is True, f"Error: {error}"

    def test_valid_agent_telugu(self):
        """Test valid Telugu agent configuration."""
        is_valid, error = validate_agent_config(SAMPLE_AGENT_TELUGU)
        assert is_valid is True, f"Error: {error}"

    def test_invalid_no_name(self):
        """Test missing name field."""
        is_valid, error = validate_agent_config(INVALID_AGENT_NO_NAME)
        assert is_valid is False
        assert "name" in error.lower()

    def test_invalid_language(self):
        """Test invalid language code."""
        is_valid, error = validate_agent_config(INVALID_AGENT_BAD_LANGUAGE)
        assert is_valid is False

    def test_invalid_provider(self):
        """Test invalid provider."""
        is_valid, error = validate_agent_config(INVALID_AGENT_BAD_PROVIDER)
        assert is_valid is False

    def test_invalid_voice(self):
        """Test invalid voice ID."""
        is_valid, error = validate_agent_config(INVALID_AGENT_BAD_VOICE)
        assert is_valid is False

    def test_invalid_temperature(self):
        """Test invalid temperature range."""
        config = SAMPLE_AGENT_HINDI.copy()
        config["model_config"]["temperature"] = 5.0  # Out of range
        is_valid, error = validate_agent_config(config)
        assert is_valid is False
        assert "temperature" in error.lower()

    def test_invalid_max_tokens(self):
        """Test invalid max_tokens."""
        config = SAMPLE_AGENT_HINDI.copy()
        config["model_config"]["max_tokens"] = 10000  # Out of range
        is_valid, error = validate_agent_config(config)
        assert is_valid is False
        assert "max_tokens" in error.lower()


class TestAgentConfigEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_min_temperature(self):
        """Test minimum valid temperature."""
        config = SAMPLE_AGENT_HINDI.copy()
        config["model_config"]["temperature"] = 0.0
        is_valid, error = validate_agent_config(config)
        assert is_valid is True

    def test_max_temperature(self):
        """Test maximum valid temperature."""
        config = SAMPLE_AGENT_HINDI.copy()
        config["model_config"]["temperature"] = 2.0
        is_valid, error = validate_agent_config(config)
        assert is_valid is True

    def test_min_name_length(self):
        """Test minimum name length (3 chars)."""
        config = SAMPLE_AGENT_HINDI.copy()
        config["name"] = "AB"  # Too short
        is_valid, error = validate_agent_config(config)
        assert is_valid is False
        assert "name" in error.lower()

    def test_max_name_length(self):
        """Test maximum name length (100 chars)."""
        config = SAMPLE_AGENT_HINDI.copy()
        config["name"] = "A" * 101  # Too long
        is_valid, error = validate_agent_config(config)
        assert is_valid is False
        assert "name" in error.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
