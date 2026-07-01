# API Documentation

## Overview

This document describes the API endpoints for the Talent and Agent Orchestration Platform.

## Endpoints

### Role Definition

- `POST /v1/roles` - Create a new role definition
- `GET /v1/roles/{role_id}` - Get a role definition
- `PUT /v1/roles/{role_id}` - Update a role definition (full replacement)
- `DELETE /v1/roles/{role_id}` - Delete a role definition

### Personal Profile

- `POST /v1/profiles` - Create a new personal profile
- `GET /v1/profiles/{profile_id}` - Get a personal profile
- `PUT /v1/profiles/{profile_id}` - Update a personal profile (full replacement)
- `DELETE /v1/profiles/{profile_id}` - Delete a personal profile

### Matching

- `POST /v1/match` - Calculate match between profile and role
- `GET /v1/match/{match_id}` - Get match result

### Job Description Governance

- `POST /v1/job-descriptions` - Create a new job description
- `GET /v1/job-descriptions/{job_id}` - Get a job description
- `PUT /v1/job-descriptions/{job_id}` - Update a job description (full replacement)
- `POST /v1/job-descriptions/{job_id}/submit` - Submit job description for review
- `POST /v1/job-descriptions/{job_id}/approve` - Approve job description (NVEDO only)
- `POST /v1/job-descriptions/{job_id}/reject` - Reject job description (NVEDO only)

## Authentication

All endpoints require Bearer token authentication.

```
Authorization: Bearer <token>
```

## Rate Limiting

1000 requests per hour per user.

## Versioning

The API is versioned at `/v1`. Breaking changes will increment the version number.
