"""
Usage event storage and retrieval.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class UsageStorage:
    """Store and retrieve usage events in JSON files."""

    def __init__(self, base_path: str = "./usage_data"):
        """
        Initialize storage with base directory.

        Args:
            base_path: Directory for usage data storage
        """
        self.base_path = Path(base_path)
        self.daily_path = self.base_path / "daily"
        self.monthly_path = self.base_path / "monthly"

        # Create directory structure
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.daily_path.mkdir(parents=True, exist_ok=True)
        self.monthly_path.mkdir(parents=True, exist_ok=True)

    def _get_daily_file_path(self, date: str) -> Path:
        """Get file path for daily usage (YYYY-MM-DD format)."""
        return self.daily_path / f"{date}.jsonl"

    def _get_monthly_file_path(self, month: str) -> Path:
        """Get file path for monthly aggregates (YYYY-MM format)."""
        return self.monthly_path / f"{month}.json"

    def record_event(self, usage_event: Dict[str, Any]) -> None:
        """
        Record single usage event.

        Args:
            usage_event: Usage event dict
        """
        # Get current date from event timestamp
        timestamp = usage_event.get("timestamp", datetime.utcnow().isoformat() + "Z")
        date_str = timestamp[:10]  # YYYY-MM-DD

        # Append to daily JSONL file
        daily_file = self._get_daily_file_path(date_str)
        with open(daily_file, "a") as f:
            f.write(json.dumps(usage_event) + "\n")

    def get_daily_usage(
        self,
        date: str,
        owner: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve usage events for a specific date.

        Args:
            date: Date string (YYYY-MM-DD)
            owner: Optional filter by owner

        Returns:
            List of usage events
        """
        daily_file = self._get_daily_file_path(date)

        if not daily_file.exists():
            return []

        events = []
        try:
            with open(daily_file, "r") as f:
                for line in f:
                    if not line.strip():
                        continue

                    event = json.loads(line)

                    # Apply filter
                    if owner and event.get("owner") != owner:
                        continue

                    events.append(event)
        except Exception:
            pass

        return events

    def get_usage_summary(
        self,
        start_date: str,
        end_date: str,
        owner: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get aggregated usage summary for date range.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            owner: Optional filter by owner

        Returns:
            Dict with aggregated usage data
        """
        from datetime import timedelta

        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        total_events = 0
        total_duration_seconds = 0.0
        total_cost_usd = 0.0
        by_provider = {}
        by_agent = {}

        # Iterate through each day in range
        current = start
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            events = self.get_daily_usage(date_str, owner)

            for event in events:
                total_events += 1
                total_duration_seconds += event.get("total_duration_seconds", 0.0)
                total_cost_usd += event.get("total_cost_usd", 0.0)

                # Aggregate by provider
                stt_provider = event.get("stt_usage", {}).get("provider")
                if stt_provider:
                    if stt_provider not in by_provider:
                        by_provider[stt_provider] = {
                            "stt_minutes": 0.0,
                            "tts_minutes": 0.0,
                            "cost_usd": 0.0,
                        }
                    by_provider[stt_provider]["stt_minutes"] += (
                        event.get("stt_usage", {}).get("audio_duration_seconds", 0.0) / 60
                    )
                    by_provider[stt_provider]["cost_usd"] += event.get("stt_usage", {}).get(
                        "cost_usd", 0.0
                    )

                tts_provider = event.get("tts_usage", {}).get("provider")
                if tts_provider:
                    if tts_provider not in by_provider:
                        by_provider[tts_provider] = {
                            "stt_minutes": 0.0,
                            "tts_minutes": 0.0,
                            "cost_usd": 0.0,
                        }
                    by_provider[tts_provider]["tts_minutes"] += (
                        event.get("tts_usage", {}).get("audio_duration_seconds", 0.0) / 60
                    )
                    by_provider[tts_provider]["cost_usd"] += event.get("tts_usage", {}).get(
                        "cost_usd", 0.0
                    )

                # Aggregate by agent
                agent_id = event.get("agent_id")
                if agent_id:
                    if agent_id not in by_agent:
                        by_agent[agent_id] = {
                            "conversations": 0,
                            "duration_minutes": 0.0,
                            "cost_usd": 0.0,
                        }
                    by_agent[agent_id]["conversations"] += 1
                    by_agent[agent_id]["duration_minutes"] += (
                        event.get("total_duration_seconds", 0.0) / 60
                    )
                    by_agent[agent_id]["cost_usd"] += event.get("total_cost_usd", 0.0)

            current += timedelta(days=1)

        # Format summary
        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date,
            },
            "summary": {
                "total_conversations": total_events,
                "total_duration_minutes": round(total_duration_seconds / 60, 2),
                "total_cost_usd": round(total_cost_usd, 4),
            },
            "by_provider": {
                provider: {
                    "stt_minutes": round(data["stt_minutes"], 2),
                    "tts_minutes": round(data["tts_minutes"], 2),
                    "cost_usd": round(data["cost_usd"], 4),
                }
                for provider, data in by_provider.items()
            },
            "by_agent": [
                {
                    "agent_id": agent_id,
                    "conversations": data["conversations"],
                    "duration_minutes": round(data["duration_minutes"], 2),
                    "cost_usd": round(data["cost_usd"], 4),
                }
                for agent_id, data in by_agent.items()
            ],
        }
