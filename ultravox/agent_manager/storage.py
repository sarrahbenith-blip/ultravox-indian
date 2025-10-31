"""
Agent configuration storage manager.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ultravox.agent_manager.validator import validate_agent_config


class AgentStorage:
    """Manage agent configuration storage in JSON files."""

    def __init__(self, base_path: str = "./agents"):
        """
        Initialize storage manager.

        Args:
            base_path: Directory for agent storage (default: ./agents)
        """
        self.base_path = Path(base_path)
        self.configs_path = self.base_path / "configs"
        self.index_path = self.base_path / "agents.json"

        # Create directory structure if not exists
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.configs_path.mkdir(parents=True, exist_ok=True)

        # Load or initialize index
        if not self.index_path.exists():
            self._save_index([])

    def _load_index(self) -> List[str]:
        """Load agent index from file."""
        if not self.index_path.exists():
            return []

        try:
            with open(self.index_path, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_index(self, agent_ids: List[str]) -> None:
        """Save agent index to file."""
        with open(self.index_path, "w") as f:
            json.dump(agent_ids, f, indent=2)

    def _generate_agent_id(self) -> str:
        """Generate unique agent ID."""
        return f"agent_{uuid.uuid4().hex[:8]}"

    def _get_agent_file_path(self, agent_id: str) -> Path:
        """Get file path for agent config."""
        return self.configs_path / f"{agent_id}.json"

    def create_agent(self, agent_data: Dict[str, Any]) -> str:
        """
        Create new agent configuration.

        Args:
            agent_data: Agent configuration dict (without agent_id)

        Returns:
            agent_id of created agent

        Raises:
            ValueError: If agent_data invalid
        """
        # Validate configuration
        is_valid, error = validate_agent_config(agent_data)
        if not is_valid:
            raise ValueError(f"Invalid agent configuration: {error}")

        # Generate ID and timestamps
        agent_id = self._generate_agent_id()
        now = datetime.utcnow().isoformat() + "Z"

        # Add metadata
        agent_config = {
            "agent_id": agent_id,
            **agent_data,
            "created_at": now,
            "updated_at": now,
            "status": "active",
        }

        # Save configuration
        agent_file = self._get_agent_file_path(agent_id)
        with open(agent_file, "w") as f:
            json.dump(agent_config, f, indent=2)

        # Update index
        index = self._load_index()
        index.append(agent_id)
        self._save_index(index)

        return agent_id

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve agent configuration by ID.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent config dict or None if not found
        """
        agent_file = self._get_agent_file_path(agent_id)

        if not agent_file.exists():
            return None

        try:
            with open(agent_file, "r") as f:
                return json.load(f)
        except Exception:
            return None

    def list_agents(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List all agents with optional filtering.

        Args:
            filters: Optional filters (status, use_case, owner, tags)

        Returns:
            List of agent configuration dicts
        """
        agents = []
        index = self._load_index()

        for agent_id in index:
            agent = self.get_agent(agent_id)
            if agent is None:
                continue

            # Apply filters
            if filters:
                skip = False

                if "status" in filters and agent.get("status") != filters["status"]:
                    skip = True

                if "use_case" in filters:
                    metadata = agent.get("metadata", {})
                    if metadata.get("use_case") != filters["use_case"]:
                        skip = True

                if "owner" in filters:
                    metadata = agent.get("metadata", {})
                    if metadata.get("owner") != filters["owner"]:
                        skip = True

                if "tags" in filters:
                    metadata = agent.get("metadata", {})
                    agent_tags = metadata.get("tags", [])
                    if filters["tags"] not in agent_tags:
                        skip = True

                if skip:
                    continue

            agents.append(agent)

        return agents

    def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update agent configuration.

        Args:
            agent_id: Agent identifier
            updates: Partial config to update (merged with existing)

        Returns:
            True if updated, False if agent not found

        Raises:
            ValueError: If updated config invalid
        """
        agent = self.get_agent(agent_id)
        if agent is None:
            return False

        # Merge updates
        updated_config = {**agent, **updates}

        # Don't update these fields
        updated_config["agent_id"] = agent_id
        updated_config["created_at"] = agent["created_at"]
        updated_config["updated_at"] = datetime.utcnow().isoformat() + "Z"

        # Validate merged config
        is_valid, error = validate_agent_config(updated_config)
        if not is_valid:
            raise ValueError(f"Invalid agent configuration after update: {error}")

        # Save updated config
        agent_file = self._get_agent_file_path(agent_id)
        with open(agent_file, "w") as f:
            json.dump(updated_config, f, indent=2)

        return True

    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete agent configuration.

        Args:
            agent_id: Agent identifier

        Returns:
            True if deleted, False if not found
        """
        agent_file = self._get_agent_file_path(agent_id)

        if not agent_file.exists():
            return False

        # Delete file
        agent_file.unlink()

        # Update index
        index = self._load_index()
        if agent_id in index:
            index.remove(agent_id)
            self._save_index(index)

        return True
