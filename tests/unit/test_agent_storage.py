"""Unit tests for agent storage."""

import tempfile
from pathlib import Path

import pytest

from ultravox.agent_manager.storage import AgentStorage
from tests.fixtures.sample_data import (
    SAMPLE_AGENT_ENGLISH,
    SAMPLE_AGENT_HINDI,
    SAMPLE_AGENT_TAMIL,
)


class TestAgentStorage:
    """Test agent storage CRUD operations."""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = AgentStorage(base_path=tmpdir)
            yield storage

    def test_create_agent(self, temp_storage):
        """Test creating a new agent."""
        agent_id = temp_storage.create_agent(SAMPLE_AGENT_HINDI)

        assert agent_id is not None
        assert agent_id.startswith("agent_")
        assert len(agent_id) == 14  # "agent_" + 8 chars

    def test_get_agent(self, temp_storage):
        """Test retrieving agent by ID."""
        agent_id = temp_storage.create_agent(SAMPLE_AGENT_HINDI)
        agent = temp_storage.get_agent(agent_id)

        assert agent is not None
        assert agent["agent_id"] == agent_id
        assert agent["name"] == SAMPLE_AGENT_HINDI["name"]
        assert agent["status"] == "active"
        assert "created_at" in agent
        assert "updated_at" in agent

    def test_get_nonexistent_agent(self, temp_storage):
        """Test retrieving nonexistent agent."""
        agent = temp_storage.get_agent("agent_nonexistent")
        assert agent is None

    def test_list_agents(self, temp_storage):
        """Test listing all agents."""
        id1 = temp_storage.create_agent(SAMPLE_AGENT_HINDI)
        id2 = temp_storage.create_agent(SAMPLE_AGENT_ENGLISH)
        id3 = temp_storage.create_agent(SAMPLE_AGENT_TAMIL)

        agents = temp_storage.list_agents()
        assert len(agents) == 3
        agent_ids = [a["agent_id"] for a in agents]
        assert id1 in agent_ids
        assert id2 in agent_ids
        assert id3 in agent_ids

    def test_list_agents_with_status_filter(self, temp_storage):
        """Test listing agents filtered by status."""
        id1 = temp_storage.create_agent(SAMPLE_AGENT_HINDI)

        # Update agent to inactive
        agent = temp_storage.get_agent(id1)
        agent["status"] = "inactive"
        temp_storage.update_agent(id1, {"status": "inactive"})

        # Filter by active status
        active_agents = temp_storage.list_agents({"status": "active"})
        assert len(active_agents) == 0

        # Filter by inactive status
        inactive_agents = temp_storage.list_agents({"status": "inactive"})
        assert len(inactive_agents) == 1
        assert inactive_agents[0]["agent_id"] == id1

    def test_list_agents_with_use_case_filter(self, temp_storage):
        """Test listing agents filtered by use case."""
        id1 = temp_storage.create_agent(SAMPLE_AGENT_HINDI)  # healthcare
        id2 = temp_storage.create_agent(SAMPLE_AGENT_ENGLISH)  # education

        healthcare_agents = temp_storage.list_agents({"use_case": "healthcare"})
        assert len(healthcare_agents) == 1
        assert healthcare_agents[0]["agent_id"] == id1

        education_agents = temp_storage.list_agents({"use_case": "education"})
        assert len(education_agents) == 1
        assert education_agents[0]["agent_id"] == id2

    def test_update_agent(self, temp_storage):
        """Test updating agent configuration."""
        agent_id = temp_storage.create_agent(SAMPLE_AGENT_HINDI)
        original_agent = temp_storage.get_agent(agent_id)
        original_created_at = original_agent["created_at"]

        # Update agent
        success = temp_storage.update_agent(agent_id, {"name": "Updated Name"})
        assert success is True

        # Verify update
        updated_agent = temp_storage.get_agent(agent_id)
        assert updated_agent["name"] == "Updated Name"
        assert updated_agent["created_at"] == original_created_at  # Should not change
        assert updated_agent["updated_at"] > original_agent["updated_at"]  # Should be newer

    def test_update_nonexistent_agent(self, temp_storage):
        """Test updating nonexistent agent."""
        success = temp_storage.update_agent("agent_nonexistent", {"name": "Updated"})
        assert success is False

    def test_delete_agent(self, temp_storage):
        """Test deleting agent."""
        agent_id = temp_storage.create_agent(SAMPLE_AGENT_HINDI)

        # Verify agent exists
        agent = temp_storage.get_agent(agent_id)
        assert agent is not None

        # Delete agent
        success = temp_storage.delete_agent(agent_id)
        assert success is True

        # Verify agent is deleted
        agent = temp_storage.get_agent(agent_id)
        assert agent is None

    def test_delete_nonexistent_agent(self, temp_storage):
        """Test deleting nonexistent agent."""
        success = temp_storage.delete_agent("agent_nonexistent")
        assert success is False

    def test_agent_id_uniqueness(self, temp_storage):
        """Test that agent IDs are unique."""
        id1 = temp_storage.create_agent(SAMPLE_AGENT_HINDI)
        id2 = temp_storage.create_agent(SAMPLE_AGENT_ENGLISH)

        assert id1 != id2

    def test_invalid_config_on_create(self, temp_storage):
        """Test that invalid config raises error on create."""
        invalid_config = {"name": "Invalid"}  # Missing required fields

        with pytest.raises(ValueError):
            temp_storage.create_agent(invalid_config)

    def test_invalid_config_on_update(self, temp_storage):
        """Test that invalid config raises error on update."""
        agent_id = temp_storage.create_agent(SAMPLE_AGENT_HINDI)

        invalid_update = {"model_config": {"temperature": 5.0}}  # Out of range

        with pytest.raises(ValueError):
            temp_storage.update_agent(agent_id, invalid_update)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
