# Talent and Agent Orchestration Platform

## Overview

The Talent and Agent Orchestration Platform is a human-centered talent matching system that extends into people operations and agent governance. The platform helps organizations match talent to roles while preserving the human dimension of work.

## Repository Structure

```
talent-platform/
├── src/
│   ├── api/              # API endpoints and routes
│   ├── models/           # Data models and schemas
│   ├── services/         # Business logic services
│   ├── core/             # Core utilities and helpers
│   └── governance/       # Governance logic and controls
├── tests/               # Test files
├── docs/                # Documentation
├── migrations/          # Database migrations
├── scripts/             # Utility scripts
├── requirements.txt     # Python dependencies
├── pyproject.toml      # Project configuration
├── .env.example         # Environment variables example
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run migrations:
```bash
alembic upgrade head
```

4. Run the application:
```bash
uvicorn src.api.main:app --reload
```

## Documentation

- [Platform Proposal](../governance_services/TALENT_AND_AGENT_ORCHESTRATION_PLATFORM_PROPOSAL.md)
- [Data Model Specification](../governance_services/TALENT_PLATFORM_V1_DATA_MODEL_SPEC.md)
- [API Contract](../governance_services/TALENT_PLATFORM_V1_API_CONTRACT.md)
- [Scope-Gated Roadmap](../governance_services/TALENT_PLATFORM_V1_SCOPE_GATED_ROADMAP.md)
- [People Operations Governance Charter](../governance_services/PEOPLE_OPERATIONS_GOVERNANCE_CHARTER.md)
- [Agent Governance Charter](../governance_services/AGENT_GOVERNANCE_CHARTER_APPROVAL_ARTIFACT.md)
- [Agent Governance Data Model](../governance_services/AGENT_GOVERNANCE_DATA_MODEL_TEMPLATE.md)
- [Phase 3 Implementation Guide](../governance_services/PHASE_3_JOB_DESCRIPTION_GOVERNANCE_IMPLEMENTATION_GUIDE.md)
- [Project Backlog](../governance_services/PROJECT_BACKLOG.md)

## License

[Add your license here]
