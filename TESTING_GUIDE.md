# Testing Guide - Ultravox Indian Platform MVP

## Quick Start (5 minutes)

### Option 1: Run All Tests (Recommended First)

```bash
cd /workspace/cmhd1n92h004kr7im2isekfrs/ultravox-indian

# Run all tests
python -m pytest tests/unit/ -v

# Expected output: ✅ 56 passed in 0.16s
```

### Option 2: Run Specific Test Suite

```bash
# Test only validators
python -m pytest tests/unit/test_validator.py -v

# Test only storage
python -m pytest tests/unit/test_agent_storage.py -v

# Test only cost calculations
python -m pytest tests/unit/test_cost_calculator.py -v
```

---

## Manual Testing (Try It Yourself)

### Test 1: Create an Agent in Hindi

```python
# Create a new file: test_manual_1.py

from ultravox.agent_manager.storage import AgentStorage
from tests.fixtures.sample_data import SAMPLE_AGENT_HINDI
import json

# Create storage
storage = AgentStorage("./my_test_agents")

# Create agent
agent_id = storage.create_agent(SAMPLE_AGENT_HINDI)

print(f"✅ Agent created: {agent_id}")

# Retrieve and print
agent = storage.get_agent(agent_id)
print(f"\nAgent Details:")
print(f"  Name: {agent['name']}")
print(f"  Language: {agent['language_config']['primary_language']}")
print(f"  TTS Provider: {agent['tts_config']['provider']}")
print(f"  STT Provider: {agent['stt_config']['provider']}")
print(f"  Voice: {agent['tts_config']['voice']}")
print(f"  Status: {agent['status']}")
print(f"\nFull config:\n{json.dumps(agent, indent=2)}")
```

**Run it:**
```bash
python test_manual_1.py
```

**Expected output:**
```
✅ Agent created: agent_a1b2c3d4
Agent Details:
  Name: Hindi Healthcare Assistant
  Language: hi-IN
  TTS Provider: sarvam
  STT Provider: sarvam
  Voice: aditi
  Status: active
```

---

### Test 2: Create Agents in All 4 Languages

```python
# Create a new file: test_manual_2.py

from ultravox.agent_manager.storage import AgentStorage
from tests.fixtures.sample_data import (
    SAMPLE_AGENT_HINDI,
    SAMPLE_AGENT_ENGLISH,
    SAMPLE_AGENT_TAMIL,
    SAMPLE_AGENT_TELUGU,
)

storage = AgentStorage("./my_test_agents")

agents = [
    ("Hindi", SAMPLE_AGENT_HINDI),
    ("English", SAMPLE_AGENT_ENGLISH),
    ("Tamil", SAMPLE_AGENT_TAMIL),
    ("Telugu", SAMPLE_AGENT_TELUGU),
]

print("Creating agents in all 4 languages:\n")

for lang_name, agent_config in agents:
    agent_id = storage.create_agent(agent_config)
    agent = storage.get_agent(agent_id)
    print(f"✅ {lang_name:12} | ID: {agent_id} | Provider: {agent['tts_config']['provider']}")

print("\n\nListing all agents:")
all_agents = storage.list_agents()
print(f"Total agents: {len(all_agents)}")

for agent in all_agents:
    print(f"  • {agent['name']}")
```

**Run it:**
```bash
python test_manual_2.py
```

**Expected output:**
```
Creating agents in all 4 languages:

✅ Hindi        | ID: agent_abc123d4 | Provider: sarvam
✅ English      | ID: agent_def456g7 | Provider: google
✅ Tamil        | ID: agent_hij789k0 | Provider: sarvam
✅ Telugu       | ID: agent_lmn012o3 | Provider: google

Listing all agents:
Total agents: 4
  • Hindi Healthcare Assistant
  • English Education Assistant
  • Tamil E-commerce Assistant
  • Telugu Support Assistant
```

---

### Test 3: List and Filter Agents

```python
# Create a new file: test_manual_3.py

from ultravox.agent_manager.storage import AgentStorage
from tests.fixtures.sample_data import (
    SAMPLE_AGENT_HINDI,
    SAMPLE_AGENT_ENGLISH,
    SAMPLE_AGENT_TAMIL,
)

storage = AgentStorage("./my_test_agents")

# Create agents
storage.create_agent(SAMPLE_AGENT_HINDI)
storage.create_agent(SAMPLE_AGENT_ENGLISH)
storage.create_agent(SAMPLE_AGENT_TAMIL)

print("All agents:")
all_agents = storage.list_agents()
for agent in all_agents:
    print(f"  • {agent['name']} ({agent['language_config']['primary_language']})")

print("\n\nFilter by use_case='healthcare':")
healthcare = storage.list_agents({"use_case": "healthcare"})
for agent in healthcare:
    print(f"  • {agent['name']}")

print("\nFilter by use_case='education':")
education = storage.list_agents({"use_case": "education"})
for agent in education:
    print(f"  • {agent['name']}")
```

**Run it:**
```bash
python test_manual_3.py
```

---

### Test 4: Update Agent Configuration

```python
# Create a new file: test_manual_4.py

from ultravox.agent_manager.storage import AgentStorage
from tests.fixtures.sample_data import SAMPLE_AGENT_HINDI

storage = AgentStorage("./my_test_agents")

# Create agent
agent_id = storage.create_agent(SAMPLE_AGENT_HINDI)
print(f"Created agent: {agent_id}\n")

# Get original config
original = storage.get_agent(agent_id)
print(f"Original name: {original['name']}")
print(f"Original voice: {original['tts_config']['voice']}")

# Update agent name
success = storage.update_agent(agent_id, {
    "name": "Updated Hindi Agent"
})
print(f"\n✅ Update successful: {success}")

# Get updated config
updated = storage.get_agent(agent_id)
print(f"\nUpdated name: {updated['name']}")
print(f"Same voice: {updated['tts_config']['voice']}")
print(f"Timestamps changed: {original['updated_at'] != updated['updated_at']}")
```

**Run it:**
```bash
python test_manual_4.py
```

---

### Test 5: Cost Calculations

```python
# Create a new file: test_manual_5.py

from ultravox.cost_tracking.calculator import (
    calculate_stt_cost,
    calculate_tts_cost,
    calculate_model_cost,
    calculate_total_cost,
    calculate_customer_cost,
    get_profit_margin,
)

print("COST CALCULATION EXAMPLES")
print("=" * 60)

# Typical 1-minute conversation: 3 turns, 20 sec each
print("\n1. STT COSTS (60 seconds)")
print("-" * 60)
sarvam_stt = calculate_stt_cost("sarvam", 60.0)
google_stt = calculate_stt_cost("google", 60.0)
print(f"Sarvam AI:    ${sarvam_stt:.6f}")
print(f"Google Cloud: ${google_stt:.6f}")

print("\n2. TTS COSTS")
print("-" * 60)
sarvam_tts = calculate_tts_cost("sarvam", audio_duration_seconds=60.0)
google_tts = calculate_tts_cost("google", text_length=1000)
print(f"Sarvam AI (60s):      ${sarvam_tts:.6f}")
print(f"Google Cloud (1000c): ${google_tts:.6f}")

print("\n3. MODEL COST")
print("-" * 60)
model_cost = calculate_model_cost()
print(f"Per inference: ${model_cost:.6f}")

print("\n4. TOTAL COST FOR 1-MIN CONVERSATION (3 turns)")
print("-" * 60)
typical_stt = calculate_stt_cost("sarvam", 60)  # 3 turns × 20s
typical_model = calculate_model_cost() * 3       # 3 inferences
typical_tts = calculate_tts_cost("sarvam", audio_duration_seconds=45)  # 3 turns × 15s
total = calculate_total_cost(typical_stt, typical_model, typical_tts)
print(f"STT Cost:   ${typical_stt:.6f}")
print(f"Model Cost: ${typical_model:.6f}")
print(f"TTS Cost:   ${typical_tts:.6f}")
print(f"TOTAL:      ${total:.6f}")

print("\n5. CUSTOMER BILLING")
print("-" * 60)
basic = calculate_customer_cost(1.0, tier="basic")
premium = calculate_customer_cost(1.0, tier="premium")
print(f"Basic Tier (1 min):   ${basic['cost_usd']:.2f} (₹{basic['cost_inr']:.2f})")
print(f"Premium Tier (1 min): ${premium['cost_usd']:.2f} (₹{premium['cost_inr']:.2f})")

print("\n6. PROFIT MARGIN")
print("-" * 60)
margin = get_profit_margin(total, basic['cost_usd'])
print(f"Provider cost:  ${total:.6f}")
print(f"Customer price: ${basic['cost_usd']:.2f}")
print(f"Profit margin:  {margin:.0f}%")
```

**Run it:**
```bash
python test_manual_5.py
```

**Expected output:**
```
COST CALCULATION EXAMPLES
============================================================

1. STT COSTS (60 seconds)
------------------------------------------------------------
Sarvam AI:    $0.003600
Google Cloud: $0.024000

2. TTS COSTS
------------------------------------------------------------
Sarvam AI (60s):      $0.006000
Google Cloud (1000c): $0.004000

3. MODEL COST
------------------------------------------------------------
Per inference: $0.001000

4. TOTAL COST FOR 1-MIN CONVERSATION (3 turns)
------------------------------------------------------------
STT Cost:   $0.003600
Model Cost: $0.003000
TTS Cost:   $0.004500
TOTAL:      $0.011100

5. CUSTOMER BILLING
------------------------------------------------------------
Basic Tier (1 min):   $0.03 (₹2.50)
Premium Tier (1 min): $0.05 (₹4.00)

6. PROFIT MARGIN
------------------------------------------------------------
Provider cost:  $0.011100
Customer price: $0.03
Profit margin:  170%
```

---

### Test 6: Validation Tests

```python
# Create a new file: test_manual_6.py

from ultravox.agent_manager.validator import (
    validate_language_code,
    validate_provider_name,
    validate_voice_id,
    validate_agent_config,
)

print("VALIDATION TESTS")
print("=" * 60)

print("\n1. LANGUAGE VALIDATION")
print("-" * 60)
languages = ["en-IN", "hi-IN", "ta-IN", "te-IN", "xx-XX"]
for lang in languages:
    is_valid, error = validate_language_code(lang)
    status = "✅" if is_valid else "❌"
    print(f"{status} {lang}: {error or 'Valid'}")

print("\n2. PROVIDER VALIDATION")
print("-" * 60)
providers = ["sarvam", "google", "openai", "invalid"]
for provider in providers:
    is_valid, error = validate_provider_name(provider)
    status = "✅" if is_valid else "❌"
    print(f"{status} {provider}: {error or 'Valid'}")

print("\n3. VOICE VALIDATION")
print("-" * 60)
voices = [
    ("sarvam", "hi-IN", "aditi"),
    ("sarvam", "hi-IN", "invalid"),
    ("google", "hi-IN", "hi-IN-Wavenet-A"),
    ("google", "ta-IN", "invalid"),
]
for provider, language, voice in voices:
    is_valid, error = validate_voice_id(provider, language, voice)
    status = "✅" if is_valid else "❌"
    print(f"{status} {provider}/{language}/{voice}: {error or 'Valid'}")

print("\n4. FULL AGENT CONFIG VALIDATION")
print("-" * 60)
from tests.fixtures.sample_data import (
    SAMPLE_AGENT_HINDI,
    INVALID_AGENT_BAD_LANGUAGE,
)

is_valid, error = validate_agent_config(SAMPLE_AGENT_HINDI)
print(f"Valid Hindi agent:      {'✅ Valid' if is_valid else f'❌ {error}'}")

is_valid, error = validate_agent_config(INVALID_AGENT_BAD_LANGUAGE)
print(f"Invalid language agent: {'✅ Valid' if is_valid else f'❌ {error}'}")
```

**Run it:**
```bash
python test_manual_6.py
```

---

## File System After Testing

After running the tests, you'll see:

```
ultravox-indian/
├── my_test_agents/          (Created by manual tests)
│   ├── agents.json          (Agent index)
│   └── configs/
│       ├── agent_abc123d4.json
│       ├── agent_def456g7.json
│       └── ...
├── tests/
└── [all source files]
```

You can inspect the created agents:

```bash
# View agents index
cat my_test_agents/agents.json

# View a specific agent config
cat my_test_agents/configs/agent_abc123d4.json
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'ultravox'"

**Solution:**
```bash
cd /workspace/cmhd1n92h004kr7im2isekfrs/ultravox-indian
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python test_manual_1.py
```

### Issue: "pytest not found"

**Solution:**
```bash
pip install pytest
python -m pytest tests/unit/ -v
```

### Issue: Permissions denied on my_test_agents

**Solution:**
```bash
rm -rf my_test_agents
python test_manual_1.py  # Will recreate
```

---

## Summary

| Test | Command | Time | What It Tests |
|------|---------|------|---------------|
| **All Tests** | `pytest tests/unit/ -v` | 0.16s | Everything (56 tests) |
| **Manual 1** | `python test_manual_1.py` | <1s | Create one agent |
| **Manual 2** | `python test_manual_2.py` | <1s | Create 4 agents |
| **Manual 3** | `python test_manual_3.py` | <1s | List & filter agents |
| **Manual 4** | `python test_manual_4.py` | <1s | Update agent config |
| **Manual 5** | `python test_manual_5.py` | <1s | Cost calculations |
| **Manual 6** | `python test_manual_6.py` | <1s | Validation logic |

**Next:** Once you verify everything works locally, we'll build the FastAPI server and conversation API!
