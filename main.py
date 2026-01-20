import shutil
from fastapi import FastAPI, Header, HTTPException, BackgroundTasks
from pathlib import Path
import logging
from models import WebhookNotification
from config import settings
from agentarena_client import AgentArenaClient
from securepr_client import SecurePRClient
from format_transformer import FormatTransformer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SecurePR Arena Bridge",
    description="AgentArena integration for SecurePR",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "SecurePR Arena Bridge",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/webhook")
async def receive_webhook(
    notification: WebhookNotification,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None)
):
    """
    Receive task notifications from AgentArena
    
    Headers:
        Authorization: token <WEBHOOK_AUTH_TOKEN>
    
    Body:
        WebhookNotification with task details
    """
    # Verify webhook authentication
    expected_auth = f"token {settings.webhook_auth_token}"
    if authorization != expected_auth:
        logger.warning("Unauthorized webhook attempt")
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    logger.info(f"Received task notification: {notification.task_id}")
    
    # Process in background to avoid blocking webhook response
    background_tasks.add_task(process_task, notification)
    
    return {"status": "accepted", "task_id": notification.task_id}


async def process_task(notification: WebhookNotification):
    """
    Main task processing pipeline:
    1. Download repository from AgentArena
    2. Fetch task details
    3. Scan with SecurePR API
    4. Transform results
    5. Submit to AgentArena
    """
    task_id = notification.task_id
    logger.info(f"Processing task: {task_id}")
    
    arena_client = AgentArenaClient()
    securepr_client = SecurePRClient()
    
    try:
        # Step 1: Download repository
        logger.info(f"[{task_id}] Downloading repository...")
        repo_path = await arena_client.download_repository(
            notification.task_repository_url,
            task_id
        )
        logger.info(f"[{task_id}] Repository downloaded to {repo_path}")
        
        # Step 2: Fetch task details
        logger.info(f"[{task_id}] Fetching task details...")
        task_details = await arena_client.fetch_task_details(
            notification.task_details_url
        )
        logger.info(f"[{task_id}] Task: {task_details.title}")
        
        # Step 3: Scan with SecurePR
        logger.info(f"[{task_id}] Scanning with SecurePR API...")
        scan_results, file_mapping = await securepr_client.scan_repository(
            repo_path,
            selected_files=task_details.selectedFiles
        )
        logger.info(f"[{task_id}] Scan completed. Vulnerabilities: {len(scan_results.get('vulnerabilities', []))}")
        
        # Step 4: Transform results
        logger.info(f"[{task_id}] Transforming results to AgentArena format...")
        arena_findings = FormatTransformer.transform(task_id, scan_results, file_mapping)
        
        # Step 5: Submit to AgentArena
        logger.info(f"[{task_id}] Submitting findings to AgentArena...")
        submission_result = await arena_client.submit_findings(
            notification.post_findings_url,
            arena_findings
        )
        logger.info(f"[{task_id}] Submission successful: {submission_result}")
        
    except Exception as e:
        logger.error(f"[{task_id}] Error processing task: {str(e)}", exc_info=True)
        # TODO: Optionally notify AgentArena of failure
        raise
    
    finally:
        # Cleanup: Remove temporary files
        try:
            repo_path = Path(settings.temp_dir) / task_id
            if repo_path.exists():
                shutil.rmtree(repo_path)
                logger.info(f"[{task_id}] Cleaned up temporary files")
        except Exception as e:
            logger.warning(f"[{task_id}] Failed to cleanup: {str(e)}")


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "securepr_api": settings.securepr_api_url,
        "temp_dir": settings.temp_dir,
        "temp_dir_exists": Path(settings.temp_dir).exists()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
