#!/bin/bash

# Test script for webhook endpoint
# Usage: ./test_webhook.sh

WEBHOOK_URL="http://localhost:8001/webhook"
WEBHOOK_TOKEN="your-webhook-secret"  # Replace with your actual token

curl -X POST "$WEBHOOK_URL" \
  -H "Authorization: token $WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "test_task_123",
    "task_repository_url": "https://backend.agentarena.com/api/task-repository/test_task_123",
    "task_details_url": "https://backend.agentarena.com/api/task-details/test_task_123",
    "post_findings_url": "https://arbiter.agentarena.com/process_findings"
  }'

echo -e "\n\nWebhook test completed. Check server logs for processing status."
