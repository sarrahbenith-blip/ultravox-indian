"""
Usage tracking and recording for cost calculation.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from ultravox.cost_tracking.calculator import calculate_total_cost


class UsageTracker:
    """Track API usage for cost calculation and billing."""

    def __init__(self):
        """Initialize usage tracker."""
        self.current_event: Optional[Dict[str, Any]] = None

    def start_event(
        self,
        agent_id: str,
        session_id: str,
        owner: str,
        api_endpoint: str,
    ) -> None:
        """
        Start tracking a new usage event.

        Args:
            agent_id: Agent identifier
            session_id: Conversation session ID
            owner: User/account ID
            api_endpoint: API endpoint called
        """
        self.current_event = {
            "event_id": f"evt_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent_id": agent_id,
            "session_id": session_id,
            "owner": owner,
            "api_endpoint": api_endpoint,
            "stt_usage": {},
            "model_usage": {},
            "tts_usage": {},
        }

    def record_stt_usage(
        self,
        provider: str,
        audio_duration_seconds: float,
        language: str,
        transcript_length: int = 0,
        cost_usd: float = 0.0,
    ) -> None:
        """
        Record STT provider usage.

        Args:
            provider: Provider name
            audio_duration_seconds: Audio duration in seconds
            language: Language code
            transcript_length: Length of transcript
            cost_usd: Cost in USD
        """
        if self.current_event is None:
            return

        self.current_event["stt_usage"] = {
            "provider": provider,
            "audio_duration_seconds": round(audio_duration_seconds, 2),
            "language": language,
            "transcript_length": transcript_length,
            "cost_usd": round(cost_usd, 6),
        }

    def record_model_usage(
        self,
        model_path: str,
        input_tokens: int,
        output_tokens: int,
        inference_time_seconds: float,
        cost_usd: float = 0.0,
    ) -> None:
        """
        Record model inference usage.

        Args:
            model_path: Model path/name
            input_tokens: Input token count
            output_tokens: Output token count
            inference_time_seconds: Inference time in seconds
            cost_usd: Cost in USD
        """
        if self.current_event is None:
            return

        self.current_event["model_usage"] = {
            "model_path": model_path,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "inference_time_seconds": round(inference_time_seconds, 3),
            "cost_usd": round(cost_usd, 6),
        }

    def record_tts_usage(
        self,
        provider: str,
        text_length: int,
        audio_duration_seconds: float,
        language: str,
        voice: str,
        cost_usd: float = 0.0,
    ) -> None:
        """
        Record TTS provider usage.

        Args:
            provider: Provider name
            text_length: Text length in characters
            audio_duration_seconds: Generated audio duration in seconds
            language: Language code
            voice: Voice ID
            cost_usd: Cost in USD
        """
        if self.current_event is None:
            return

        self.current_event["tts_usage"] = {
            "provider": provider,
            "text_length": text_length,
            "audio_duration_seconds": round(audio_duration_seconds, 2),
            "language": language,
            "voice": voice,
            "cost_usd": round(cost_usd, 6),
        }

    def finalize_event(self) -> Dict[str, Any]:
        """
        Finalize current usage event and calculate totals.

        Returns:
            Finalized event dict with total costs calculated
        """
        if self.current_event is None:
            raise RuntimeError("No event in progress")

        # Calculate total costs
        stt_cost = self.current_event.get("stt_usage", {}).get("cost_usd", 0.0)
        model_cost = self.current_event.get("model_usage", {}).get("cost_usd", 0.0)
        tts_cost = self.current_event.get("tts_usage", {}).get("cost_usd", 0.0)

        total_cost = calculate_total_cost(stt_cost, model_cost, tts_cost)

        # Calculate duration
        stt_duration = self.current_event.get("stt_usage", {}).get("audio_duration_seconds", 0.0)
        model_duration = self.current_event.get("model_usage", {}).get("inference_time_seconds", 0.0)
        tts_duration = self.current_event.get("tts_usage", {}).get("audio_duration_seconds", 0.0)
        total_duration = stt_duration + model_duration + tts_duration

        # Add totals
        self.current_event["total_duration_seconds"] = round(total_duration, 2)
        self.current_event["total_cost_usd"] = round(total_cost, 6)

        return self.current_event

    def get_event(self) -> Optional[Dict[str, Any]]:
        """Get current event dict."""
        return self.current_event
