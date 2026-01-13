# AegisX Quick Start Guide

## Installation

```bash
# Navigate to project
cd AegisX

# Install dependencies
make setup

# The setup command will:
# - Upgrade pip
# - Install all Python dependencies
# - Create data/ and logs/ directories
```

## Running the Server

```bash
# Start the server
make run

# Server will be available at:
# - API: http://localhost:8000
# - Interactive Docs: http://localhost:8000/docs
# - Alternative Docs: http://localhost:8000/redoc
```

## Testing the API

### Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-12T10:00:00Z",
  "version": "0.1.0",
  "database": "connected"
}
```

### Create a Weekly Plan
```bash
curl -X POST http://localhost:8000/plan/week \
  -H "Content-Type: application/json" \
  -d '{
    "context": "I need to launch a new product next month",
    "goals": [
      "Complete product documentation",
      "Setup marketing campaign",
      "Prepare sales materials"
    ],
    "constraints": [
      "Budget is $5000",
      "Launch date is March 1st"
    ]
  }'
```

### Create a Daily Plan
```bash
curl -X POST http://localhost:8000/plan/today \
  -H "Content-Type: application/json" \
  -d '{
    "context": "Busy day with multiple meetings",
    "goals": [
      "Review pull requests",
      "Update project documentation",
      "Prepare for demo"
    ],
    "constraints": [
      "Team meeting at 2pm",
      "Code freeze at 5pm"
    ]
  }'
```

## Project Structure

```
AegisX/
├── ai-engine/          # Run server from this directory
│   ├── main.py         # Application entry point
│   ├── api/            # API endpoints
│   ├── core/           # Business logic
│   ├── models/         # Pydantic models
│   ├── db/             # Database layer
│   └── utils/          # Utilities
├── data/               # SQLite database (created on first run)
├── prompts/            # AI prompt templates
├── docs/               # Documentation
└── tests/              # Test suite
```

## Common Commands

```bash
# Run the server
make run

# Run tests
make test

# Format code
make format

# Run linting
make lint

# Clean cache files
make clean

# View all commands
make help
```

## Troubleshooting

### Import Errors
If you see import errors, ensure you're running from the correct directory:
```bash
cd ai-engine
python3 -m uvicorn main:app --reload
```

### Database Issues
If the database isn't found, check that the `data/` directory exists:
```bash
mkdir -p data
```

### Port Already in Use
If port 8000 is busy, change the port:
```bash
cd ai-engine
python3 -m uvicorn main:app --reload --port 8080
```

## Development Workflow

1. **Make changes** to the code
2. **Format code**: `make format`
3. **Run tests**: `make test`
4. **Start server**: `make run`
5. **Test endpoints** using curl or http://localhost:8000/docs

## Environment Variables

Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

Edit `.env` to customize:
- `DEBUG=true` for development
- `LOG_LEVEL=DEBUG` for verbose logging
- `PORT=8080` to change the port

## Next Steps

- Read [README.md](README.md) for detailed information
- Check [docs/architecture.md](docs/architecture.md) for system design
- Review [docs/PRD.md](docs/PRD.md) for product requirements
- See [docs/threat-model.md](docs/threat-model.md) for security considerations
