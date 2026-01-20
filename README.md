# SecurePR Arena

AgentArena integration service for SecurePR. This service acts as a bridge between AgentArena platform and your production SecurePR API.

## Architecture

```
AgentArena → Webhook → This Service → SecurePR API → Results Transformation → AgentArena
```

## Features

- Receives task notifications from AgentArena via webhook
- Downloads repository archives and task details
- Forwards scanning to production SecurePR API
- Transforms response format to AgentArena schema
- Submits findings back to AgentArena

## Setup

### 1. Environment Variables

Create a `.env` file:

```bash
# AgentArena Credentials
AGENTARENA_API_KEY=your-agentarena-api-key
WEBHOOK_AUTH_TOKEN=your-webhook-secret-token

# SecurePR Production API
SECUREPR_API_URL=https://your-production-api.com
SECUREPR_API_KEY=your-internal-api-key
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Locally

```bash
uvicorn main:app --reload --port 8001
```

### 4. Deploy

The service can be deployed to:
- Railway
- Render
- Fly.io
- Any platform supporting Python/FastAPI

## Webhook Endpoint

Register this URL with AgentArena:
```
https://your-domain.com/webhook
```

## Environment

- Python 3.10+
- FastAPI
- Async HTTP client (httpx)

## Development

- `main.py` - FastAPI application and webhook endpoint
- `agentarena_client.py` - AgentArena API interactions
- `securepr_client.py` - SecurePR API client
- `format_transformer.py` - Response format conversion
- `models.py` - Pydantic models for type safety

## Testing

Test the webhook locally:
```bash
curl -X POST http://localhost:8001/webhook \
  -H "Authorization: token your-webhook-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "test123",
    "task_repository_url": "https://example.com/repo.zip",
    "task_details_url": "https://example.com/details",
    "post_findings_url": "https://example.com/findings"
  }'
```
