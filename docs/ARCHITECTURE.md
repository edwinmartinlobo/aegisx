# AegisX Architecture

## Overview

AegisX is architected as a **security intelligence engine** - a focused, API-driven system that sits between security scanners and engineering teams. This document describes the system's components, data flows, and architectural decisions.

---

## System Definition

**Type:** Intelligence Engine (not platform, not agent, not monolith)

**Characteristics:**
- API-first design
- Event-driven processing
- Stateful intelligence layer
- Horizontally scalable
- Multi-tenant capable

---

## Core Architecture Layers

```
External Scanners → Ingestion Layer → Processing Layer → Storage Layer → API Layer → Consumers
```

See full diagram in docs/VISION.md

---

## Core Components

### 1. API Gateway
- FastAPI + Uvicorn
- Authentication (API keys, mTLS)
- Rate limiting
- Request validation

### 2. Scanner Adapter Layer
- Normalizes scanner-specific formats
- SARIF, CycloneDX, custom JSON support
- Pluggable adapter pattern

### 3. Deduplication Engine
- Fingerprint-based deduplication
- Finding lifecycle tracking
- Reduces noise by 40-60%

### 4. Context Enrichment Service
- Git metadata enrichment
- Service registry integration
- Historical pattern analysis

### 5. Risk Scoring Engine
- AI-driven risk calculation
- Exploitability + Impact + Urgency + Cost
- Hybrid LLM + rule-based approach

### 6. Prioritization & Routing
- Priority queue management
- Team assignment via CODEOWNERS
- Alert routing (Slack, PagerDuty, Jira)

---

## Data Models

### Finding
```python
class Finding(BaseModel):
    id: UUID
    source: str
    title: str
    severity: Severity
    risk_score: float
    status: FindingStatus
    service_id: UUID
    file_path: str
    # ... (see full model in codebase)
```

### Service
```python
class Service(BaseModel):
    id: UUID
    name: str
    tier: ServiceTier
    data_classification: DataClassification
    ownership: Ownership
```

---

## Technology Stack

**Core:** FastAPI, Pydantic, SQLAlchemy  
**Storage:** PostgreSQL, Redis, S3  
**Processing:** Celery, RabbitMQ  
**AI/ML:** OpenAI/Anthropic API, scikit-learn  
**Observability:** Prometheus, Grafana, OpenTelemetry, ELK  
**Infrastructure:** Docker, Kubernetes, Terraform

---

## Scalability

**Horizontal Scaling:**
- Stateless API instances
- Independent Celery workers
- PostgreSQL read replicas

**Performance Targets:**
- 100K findings/day per org
- <50ms API response time (p95)
- 1M+ findings stored

---

## Architectural Principles

1. API-First
2. Event-Driven
3. Idempotent
4. Fail-Safe
5. Observable
6. Secure-by-Default
7. Multi-Tenant
8. Evolvable
