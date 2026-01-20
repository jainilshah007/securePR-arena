import httpx
import zipfile
import aiofiles
from pathlib import Path
from typing import Dict, Any
from config import settings
from models import TaskResponse, FindingsSubmission


class AgentArenaClient:
    """Client for AgentArena API interactions"""
    
    def __init__(self):
        self.api_key = settings.agentarena_api_key
        self.headers = {"X-API-Key": self.api_key}
    
    async def download_repository(self, url: str, task_id: str) -> Path:
        """
        Download repository ZIP from AgentArena
        
        Args:
            url: Repository download URL
            task_id: Task identifier for naming
            
        Returns:
            Path to extracted repository directory
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Download ZIP
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Save ZIP temporarily
            zip_path = Path(settings.temp_dir) / f"{task_id}.zip"
            async with aiofiles.open(zip_path, 'wb') as f:
                await f.write(response.content)
            
            # Extract
            extract_path = Path(settings.temp_dir) / task_id
            extract_path.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            # Clean up ZIP
            zip_path.unlink()
            
            return extract_path
    
    async def fetch_task_details(self, url: str) -> TaskResponse:
        """
        Fetch task details from AgentArena
        
        Args:
            url: Task details endpoint URL
            
        Returns:
            Parsed task details
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return TaskResponse(**response.json())
    
    async def submit_findings(self, url: str, findings: FindingsSubmission) -> Dict[str, Any]:
        """
        Submit findings back to AgentArena
        
        Args:
            url: Findings submission endpoint URL
            findings: Formatted findings
            
        Returns:
            Submission response
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json=findings.model_dump(),
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
