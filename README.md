# AegisX AI Planning Engine

Production-ready FastAPI backend for intelligent task planning and management.

## Features

- **Weekly Planning**: Generate comprehensive weekly plans with prioritized tasks
- **Daily Planning**: Create focused daily task lists optimized for productivity
- **Strict Typing**: Pydantic models with comprehensive validation
- **Structured Logging**: Production-grade logging for observability
- **Error Handling**: Robust error handling with detailed logging
- **SQLite Database**: Persistent storage for plans and tasks
- **Health Monitoring**: Built-in health check endpoint
- **Clean Architecture**: Separation of concerns for maintainability

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Make (optional, for convenience commands)

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd AegisX
```

2. Set up the environment
```bash
make setup
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
mkdir -p data logs
```

3. Configure environment variables (optional)
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the server
```bash
make run
```

Or manually:
```bash
source venv/bin/activate
uvicorn ai_engine.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative API docs: `http://localhost:8000/redoc`

### Endpoints

#### Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-12T10:00:00Z",
  "version": "0.1.0",
  "database": "connected"
}
```

#### Create Weekly Plan
```bash
POST /plan/week
Content-Type: application/json

{
  "context": "I need to prepare for a product launch",
  "goals": [
    "Complete marketing materials",
    "Setup infrastructure",
    "Train support team"
  ],
  "constraints": [
    "Launch date is next Friday",
    "Budget is limited"
  ]
}
```

#### Create Daily Plan
```bash
POST /plan/today
Content-Type: application/json

{
  "context": "Need to finish sprint tasks",
  "goals": [
    "Complete code review",
    "Fix critical bugs",
    "Update documentation"
  ],
  "constraints": [
    "Team meeting at 2pm",
    "Code freeze at 5pm"
  ]
}
```

## Project Structure

```
AegisX/
├── ai_engine/              # Main application package
│   ├── api/                # API endpoints
│   │   ├── health.py       # Health check endpoint
│   │   └── planner.py      # Planning endpoints
│   ├── core/               # Business logic
│   │   ├── config.py       # Configuration
│   │   └── planner_service.py  # Planning service
│   ├── models/             # Data models
│   │   └── schemas.py      # Pydantic schemas
│   ├── db/                 # Database
│   │   └── database.py     # DB setup and queries
│   ├── utils/              # Utilities
│   │   ├── logging_config.py   # Logging setup
│   │   └── error_handler.py    # Error handling
│   └── main.py             # Application entry point
├── data/                   # SQLite database
├── prompts/                # AI prompt templates
├── docs/                   # Documentation
│   ├── PRD.md              # Product requirements
│   ├── architecture.md     # Architecture docs
│   ├── threat-model.md     # Security analysis
│   └── SLOs.md             # Service objectives
├── tests/                  # Test suite
├── venv/                   # Virtual environment (created by setup)
├── Makefile                # Build automation
├── pyproject.toml          # Package configuration
├── requirements.txt        # Dependencies (legacy)
└── README.md               # This file
```

## Development

### Running Tests
```bash
make test
```

Or manually:
```bash
source venv/bin/activate
pytest tests/ -v --cov=ai_engine --cov-report=term-missing
```

### Code Formatting
```bash
make format
```

Or manually:
```bash
source venv/bin/activate
black ai_engine/
ruff check --fix ai_engine/
```

### Linting
```bash
make lint
```

Or manually:
```bash
source venv/bin/activate
ruff check ai_engine/
black --check ai_engine/
```

### Cleaning Cache
```bash
make clean      # Clean cache files only
make clean-all  # Clean cache files and remove virtual environment
```

## Configuration

Configuration is managed through environment variables or `.env` file:

```bash
# Application
APP_NAME=AegisX AI Engine
DEBUG=false
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Database
DATABASE_PATH=data/aegisx.db

# CORS
ALLOWED_ORIGINS=["*"]

# Prompts
PROMPTS_DIR=prompts
```

## Testing

Run the test suite with coverage:
```bash
make test
```

Or manually:
```bash
source venv/bin/activate
pytest tests/ -v --cov=ai_engine --cov-report=term-missing
```

## Logging

The application uses structured logging. Logs include:
- Timestamp
- Log level
- Logger name
- Message
- Additional context (as key-value pairs)
- File location

Example log output:
```
timestamp=2026-01-12 10:00:00 | level=INFO | logger=ai_engine.api.planner | message=Weekly plan requested | goals_count=3 | has_constraints=true
```

## Error Handling

The API returns consistent error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation error)
- `500`: Internal Server Error
- `503`: Service Unavailable

## Production Deployment

### Security Checklist

- [ ] Enable HTTPS/TLS
- [ ] Set `DEBUG=false`
- [ ] Configure CORS properly (no wildcards)
- [ ] Implement authentication
- [ ] Add rate limiting
- [ ] Set secure file permissions (database: 600)
- [ ] Use environment variables for secrets
- [ ] Enable monitoring and alerting
- [ ] Regular security updates

### Recommended Setup

1. Use a reverse proxy (nginx, Caddy)
2. Run with a process manager (systemd, supervisor)
3. Set up log rotation
4. Configure automated backups
5. Implement health check monitoring
6. Use a proper database (PostgreSQL) for multi-instance deployments

### Docker Deployment (Future)
```bash
docker build -t aegisx .
docker run -p 8000:8000 -v ./data:/app/data aegisx
```

## Monitoring

Health check endpoint for monitoring:
```bash
curl http://localhost:8000/health
```

Integrate with:
- Prometheus (metrics)
- Grafana (dashboards)
- ELK Stack (log aggregation)
- Sentry (error tracking)

## Documentation

- [Product Requirements](docs/PRD.md)
- [Architecture](docs/architecture.md)
- [Threat Model](docs/threat-model.md)
- [SLOs](docs/SLOs.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run linting and formatting
6. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions:
- GitHub Issues: [Add issue tracker URL]
- Email: [Add support email]
- Documentation: [Add docs URL]

## Roadmap

### v0.2.0
- [ ] Authentication (API keys)
- [ ] Rate limiting
- [ ] Plan templates
- [ ] Task update endpoints

### v0.3.0
- [ ] PostgreSQL support
- [ ] Multi-user support
- [ ] Calendar integration
- [ ] Webhook notifications

### v1.0.0
- [ ] OAuth 2.0 authentication
- [ ] Real-time collaboration
- [ ] Advanced analytics
- [ ] Mobile API support
