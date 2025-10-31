# Download & Test Locally

## Option A: Direct Download (Easiest)

### 1. Get the Files

The complete working code is in:
```
/workspace/cmhd1n92h004kr7im2isekfrs/ultravox-indian/
```

**Download these folders to your computer:**
```
ultravox/
  ├── providers/       (TTS/STT implementations)
  ├── agent_manager/   (Agent CRUD operations)
  ├── cost_tracking/   (Cost calculations)
  └── __init__.py

tests/
  ├── fixtures/
  │   └── sample_data.py
  └── unit/
      ├── test_validator.py
      ├── test_agent_storage.py
      └── test_cost_calculator.py
```

### 2. Install Python

Make sure you have Python 3.8+:
```bash
python --version
# Should output: Python 3.X.X
```

### 3. Install Dependencies

```bash
# Required packages
pip install pytest

# Optional (for API server in next phase)
pip install fastapi uvicorn websockets
```

### 4. Run Tests

```bash
# Go to your project directory
cd /path/to/your/downloaded/ultravox-indian

# Run all 56 tests
python -m pytest tests/unit/ -v

# Expected output: ✅ 56 passed
```

### 5. Run Quick Test

```bash
python quick_test.py
```

Expected output:
```
✅ Created 4 agents successfully
✅ Total agents: 4
✅ 1-min conversation cost: $0.011100
✅ Basic tier (1 min): $0.03
✅ Premium tier (1 min): $0.05
✅ Profit margin: 170%
✅ ALL TESTS PASSED!
```

---

## Option B: Git Clone (If You Have Git)

```bash
# Clone the repository
git clone <URL-from-github>
cd ultravox-indian

# Install dependencies
pip install pytest

# Run tests
python -m pytest tests/unit/ -v

# Run quick test
python quick_test.py
```

---

## Option C: Cloud Environment (Recommended for Testing)

If you want to test immediately without downloading:

### Use an Online Python Playground:
- **Replit.com** - Free online IDE
- **Colab.research.google.com** - Free Jupyter notebooks
- **Glitch.com** - Free Node/Python hosting

**Steps:**
1. Go to Replit.com
2. Create new Python project
3. Upload the `ultravox/` and `tests/` folders
4. Open terminal and run:
   ```bash
   pip install pytest
   python quick_test.py
   ```

---

## File Structure After Download

```
your-project/
├── ultravox/
│   ├── providers/
│   │   ├── base.py
│   │   ├── tts/
│   │   │   ├── sarvam.py
│   │   │   ├── google.py
│   │   │   └── factory.py
│   │   └── stt/
│   │       ├── sarvam.py
│   │       ├── google.py
│   │       └── factory.py
│   ├── agent_manager/
│   │   ├── storage.py
│   │   ├── validator.py
│   │   └── __init__.py
│   ├── cost_tracking/
│   │   ├── calculator.py
│   │   ├── tracker.py
│   │   ├── storage.py
│   │   └── __init__.py
│   └── __init__.py
├── tests/
│   ├── fixtures/
│   │   ├── sample_data.py
│   │   └── __init__.py
│   └── unit/
│       ├── test_validator.py
│       ├── test_agent_storage.py
│       ├── test_cost_calculator.py
│       └── __init__.py
├── quick_test.py
├── TESTING_GUIDE.md
└── [other ultravox files]
```

---

## Manual Testing Examples

### Example 1: Create an Agent

Create file `test_it.py`:

```python
from ultravox.agent_manager.storage import AgentStorage
from tests.fixtures.sample_data import SAMPLE_AGENT_HINDI

storage = AgentStorage("./my_agents")
agent_id = storage.create_agent(SAMPLE_AGENT_HINDI)

agent = storage.get_agent(agent_id)
print(f"Created: {agent['name']}")
print(f"Language: {agent['language_config']['primary_language']}")
print(f"Provider: {agent['tts_config']['provider']}")
```

Run:
```bash
python test_it.py
```

Output:
```
Created: Hindi Healthcare Assistant
Language: hi-IN
Provider: sarvam
```

### Example 2: Calculate Costs

Create file `test_costs.py`:

```python
from ultravox.cost_tracking.calculator import calculate_customer_cost

result = calculate_customer_cost(5.0, tier="basic")  # 5 minutes
print(f"5 minutes basic tier: ${result['cost_usd']:.2f}")

result = calculate_customer_cost(5.0, tier="premium")
print(f"5 minutes premium tier: ${result['cost_usd']:.2f}")
```

Run:
```bash
python test_costs.py
```

Output:
```
5 minutes basic tier: $0.15
5 minutes premium tier: $0.24
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'ultravox'"

**Solution:**
```bash
# Make sure you're in the right directory
ls -la ultravox/

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Try again
python quick_test.py
```

### Issue: "pytest not found"

**Solution:**
```bash
pip install pytest
python -m pytest tests/unit/ -v
```

### Issue: Permission denied

**Solution:**
```bash
chmod +x quick_test.py
python quick_test.py
```

---

## What Each Test Suite Tests

| Test File | What It Tests | Run Command |
|-----------|---------------|-------------|
| `test_validator.py` | Language, provider, voice validation (22 tests) | `pytest tests/unit/test_validator.py -v` |
| `test_agent_storage.py` | Agent CRUD operations (13 tests) | `pytest tests/unit/test_agent_storage.py -v` |
| `test_cost_calculator.py` | Cost calculations (21 tests) | `pytest tests/unit/test_cost_calculator.py -v` |
| `quick_test.py` | End-to-end functionality (6 tests) | `python quick_test.py` |

---

## What Will YOU Test?

When you run these tests locally, you're verifying:

✅ **4 Languages Work**
- English (en-IN)
- Hindi (hi-IN)
- Tamil (ta-IN)
- Telugu (te-IN)

✅ **Agent Management Works**
- Create agents
- Store configurations
- Retrieve by ID
- List with filters
- Update configs
- Delete agents

✅ **Cost Tracking Works**
- STT pricing (Sarvam: $0.00006/sec, Google: $0.0004/sec)
- TTS pricing (Sarvam: $0.0001/sec, Google: $0.000004/char)
- Model inference ($0.001/request)
- Customer billing tiers ($0.03/min basic, $0.048/min premium)
- Profit margin calculations (170%+ typical)

✅ **Validation Works**
- Language codes
- Provider names
- Voice IDs
- Agent configurations
- Edge cases (min/max boundaries)

---

## Next Steps

Once you've verified everything works locally:

1. **Review the code** - Check the implementations in `ultravox/`
2. **Read the test files** - Understand what's being tested
3. **Try the examples** - Run manual tests from TESTING_GUIDE.md
4. **Wait for Phase 2** - FastAPI server & conversation API coming next

---

## Questions?

All source files have docstrings:

```bash
# View docstrings
python -c "from ultravox.agent_manager.storage import AgentStorage; help(AgentStorage.create_agent)"
```

---

## Total Test Results Expected

After running everything:

```
validators............ 22 passed ✅
storage............... 13 passed ✅
cost_calculator....... 21 passed ✅
quick_test............ 6 passed ✅
─────────────────────────────────
TOTAL................ 56 passed ✅

No API keys needed - everything works locally!
```
