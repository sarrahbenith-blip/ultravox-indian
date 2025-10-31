#!/usr/bin/env python3
"""Quick test to verify everything works (no API keys needed)."""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

print("""
╔════════════════════════════════════════════════════════════════╗
║          Ultravox Indian Platform - Quick Test                ║
║                                                                ║
║  No API keys needed - this tests the core logic only          ║
╚════════════════════════════════════════════════════════════════╝
""")

# Test 1: Create agents
print("\n[TEST 1] Creating agents in all 4 languages...")
print("-" * 60)

try:
    from ultravox.agent_manager.storage import AgentStorage
    from tests.fixtures.sample_data import (
        SAMPLE_AGENT_HINDI,
        SAMPLE_AGENT_ENGLISH,
        SAMPLE_AGENT_TAMIL,
        SAMPLE_AGENT_TELUGU,
    )

    storage = AgentStorage("./test_agents_quicktest")

    agents_data = [
        ("Hindi", SAMPLE_AGENT_HINDI),
        ("English", SAMPLE_AGENT_ENGLISH),
        ("Tamil", SAMPLE_AGENT_TAMIL),
        ("Telugu", SAMPLE_AGENT_TELUGU),
    ]

    agent_ids = []
    for lang_name, agent_config in agents_data:
        agent_id = storage.create_agent(agent_config)
        agent_ids.append(agent_id)
        print(f"  ✅ {lang_name:12} | ID: {agent_id}")

    print(f"\n  ✅ Created {len(agent_ids)} agents successfully")

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 2: List agents
print("\n[TEST 2] Listing and filtering agents...")
print("-" * 60)

try:
    all_agents = storage.list_agents()
    print(f"  ✅ Total agents: {len(all_agents)}")

    healthcare = storage.list_agents({"use_case": "healthcare"})
    print(f"  ✅ Healthcare agents: {len(healthcare)}")

    education = storage.list_agents({"use_case": "education"})
    print(f"  ✅ Education agents: {len(education)}")

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 3: Cost calculations
print("\n[TEST 3] Calculating costs...")
print("-" * 60)

try:
    from ultravox.cost_tracking.calculator import (
        calculate_stt_cost,
        calculate_tts_cost,
        calculate_model_cost,
        calculate_total_cost,
        calculate_customer_cost,
    )

    # 1-minute conversation (3 turns)
    stt_cost = calculate_stt_cost("sarvam", 60)
    tts_cost = calculate_tts_cost("sarvam", audio_duration_seconds=45)
    model_cost = calculate_model_cost() * 3

    total_cost = calculate_total_cost(stt_cost, model_cost, tts_cost)
    print(f"  ✅ 1-min conversation cost: ${total_cost:.6f}")

    basic_billing = calculate_customer_cost(1.0, tier="basic")
    print(f"  ✅ Basic tier (1 min): ${basic_billing['cost_usd']:.2f}")

    premium_billing = calculate_customer_cost(1.0, tier="premium")
    print(f"  ✅ Premium tier (1 min): ${premium_billing['cost_usd']:.2f}")

    margin = ((basic_billing['cost_usd'] - total_cost) / total_cost) * 100
    print(f"  ✅ Profit margin: {margin:.0f}%")

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 4: Validation
print("\n[TEST 4] Validation system...")
print("-" * 60)

try:
    from ultravox.agent_manager.validator import (
        validate_language_code,
        validate_agent_config,
    )

    # Valid language
    is_valid, _ = validate_language_code("hi-IN")
    assert is_valid, "Hindi should be valid"
    print(f"  ✅ Valid language (hi-IN) accepted")

    # Invalid language
    is_valid, _ = validate_language_code("xx-XX")
    assert not is_valid, "xx-XX should be invalid"
    print(f"  ✅ Invalid language (xx-XX) rejected")

    # Valid agent config
    is_valid, _ = validate_agent_config(SAMPLE_AGENT_HINDI)
    assert is_valid, "Hindi agent should be valid"
    print(f"  ✅ Valid agent config accepted")

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 5: Update operations
print("\n[TEST 5] Update operations...")
print("-" * 60)

try:
    test_agent_id = agent_ids[0]
    original = storage.get_agent(test_agent_id)

    # Update agent
    success = storage.update_agent(test_agent_id, {"name": "Updated Test Agent"})
    assert success, "Update should succeed"
    print(f"  ✅ Updated agent name")

    updated = storage.get_agent(test_agent_id)
    assert updated["name"] == "Updated Test Agent"
    print(f"  ✅ Verified update persisted")

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Test 6: Delete operations
print("\n[TEST 6] Delete operations...")
print("-" * 60)

try:
    test_agent_id = agent_ids[-1]

    # Delete agent
    success = storage.delete_agent(test_agent_id)
    assert success, "Delete should succeed"
    print(f"  ✅ Deleted agent")

    # Verify deletion
    deleted_agent = storage.get_agent(test_agent_id)
    assert deleted_agent is None, "Agent should not exist after deletion"
    print(f"  ✅ Verified deletion")

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("""
What was tested:
  ✅ Agent creation (4 languages)
  ✅ Agent retrieval and listing
  ✅ Cost calculations
  ✅ Validation system
  ✅ Update operations
  ✅ Delete operations

Next steps:
  1. Run: python -m pytest tests/unit/ -v
     (This runs 56 comprehensive tests)

  2. Try manual tests:
     - python test_manual_1.py  (create agent)
     - python test_manual_5.py  (cost calculations)

  3. Read: TESTING_GUIDE.md for more examples

No API keys are needed - everything works locally!
""")
