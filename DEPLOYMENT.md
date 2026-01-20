# Deployment Guide - SecurePR Arena

## Quick Deploy to Railway (Recommended)

### 1. Initialize Git Repository

```bash
cd /Users/jainilshah/codenstuff/securePR-arena

# Initialize git
git init
git add .
git commit -m "Initial commit: AgentArena integration service"

# Create GitHub repository (via GitHub CLI or web)
gh repo create securePR-arena --private --source=. --remote=origin --push
# OR manually create on GitHub.com and:
# git remote add origin https://github.com/YOUR_USERNAME/securePR-arena.git
# git push -u origin main
```

### 2. Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select `securePR-arena` repository
4. Railway will auto-detect Python and deploy

### 3. Configure Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```bash
AGENTARENA_API_KEY=your-agentarena-api-key
WEBHOOK_AUTH_TOKEN=your-generated-secret-token
SECUREPR_API_URL=https://secure-pr.vercel.app
SECUREPR_API_KEY=your-securepr-internal-api-key
```

**Generate webhook token:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Get Webhook URL

After deployment, Railway will give you a URL like:
```
https://securepr-arena-production.up.railway.app
```

Your webhook URL will be:
```
https://securepr-arena-production.up.railway.app/webhook
```

### 5. Register with AgentArena

Go to AgentArena registration and enter:
- **Agent Name:** `ja7sh`
- **Webhook URL:** `https://your-railway-url.up.railway.app/webhook`
- **Webhook Authorization Token:** (the token you generated)

---

## Alternative: Deploy to Render

### 1. Push to GitHub (same as above)

### 2. Deploy to Render

1. Go to [render.com](https://render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Configure:
   - **Name:** `securepr-arena`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Add Environment Variables

Same as Railway step 3.

---

## Testing Your Deployment

### Health Check
```bash
curl https://your-deployment-url.com/health
```

### Test Webhook
```bash
curl -X POST https://your-deployment-url.com/webhook \
  -H "Authorization: token YOUR_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "test123",
    "task_repository_url": "https://example.com/repo.zip",
    "task_details_url": "https://example.com/details",
    "post_findings_url": "https://example.com/findings"
  }'
```

Expected response:
```json
{"status": "accepted", "task_id": "test123"}
```

---

## Important: SecurePR API Authentication

**Before deploying**, ensure your SecurePR production API has authentication. The service needs a way to authenticate requests.

If your current API doesn't have authentication yet, you'll need to add an API key check to your SecurePR `/api/scan` endpoint.

---

## Monitoring Logs

**Railway:**
- Click on deployment → **"Deployments"** tab → View logs

**Render:**
- Dashboard → Your service → **"Logs"** tab

Watch for:
- `[task_id] Processing task: ...`
- `[task_id] Scan completed. Vulnerabilities: X`
- `[task_id] Submission successful`
