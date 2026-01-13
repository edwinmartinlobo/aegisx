# Setup Notes - Import Issue Resolution

## Issue
The initial scaffold used absolute imports (`from ai_engine.api import ...`) which caused import errors when running the server.

## Resolution
All imports have been updated to use relative imports since the server runs from within the `ai-engine/` directory:

### Files Updated:
1. **ai-engine/main.py** - Changed to relative imports
2. **ai-engine/api/health.py** - Changed to relative imports
3. **ai-engine/api/planner.py** - Changed to relative imports
4. **ai-engine/core/planner_service.py** - Changed to relative imports
5. **ai-engine/db/database.py** - Changed to relative imports
6. **ai-engine/utils/logging_config.py** - Changed to relative imports
7. **ai-engine/core/config.py** - Updated default paths to be relative to ai-engine/

### Path Configuration
The default paths in `core/config.py` have been updated:
- `DATABASE_PATH`: `../data/aegisx.db` (relative to ai-engine/)
- `PROMPTS_DIR`: `../prompts` (relative to ai-engine/)

## How to Run

```bash
# From the AegisX root directory
make run

# Or manually
cd ai-engine
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Verification

All imports have been verified and the server should start successfully. You can test it:

```bash
# Check health
curl http://localhost:8000/health

# View interactive docs
open http://localhost:8000/docs
```

## Notes

- The Makefile already handles the directory change (`cd ai-engine`)
- All relative imports work correctly when running from `ai-engine/`
- The `.env.example` has been updated with correct relative paths
- Tests may need PYTHONPATH adjustments (see test configuration in conftest.py)
