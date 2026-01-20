import httpx
from pathlib import Path
from typing import Dict, Any, List, Tuple
from config import settings


class SecurePRClient:
    """Client for SecurePR production API"""
    
    def __init__(self):
        self.api_url = settings.securepr_api_url.rstrip('/')
        self.api_key = settings.securepr_api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    async def scan_repository(
        self, 
        repo_path: Path, 
        selected_files: List[str] = None
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Send repository to SecurePR API for scanning
        
        Args:
            repo_path: Path to extracted repository
            selected_files: Optional list of specific files to scan
            
        Returns:
            Tuple of (scan_results, file_mapping)
            - scan_results: SecurePR API response
            - file_mapping: Dict mapping uploaded filename to original path in repo
        """
        # Collect files to scan
        files_to_scan = []
        file_mapping = {}  # Maps uploaded filename to original repo path
        
        if selected_files:
            # Scan only selected files
            for file_path in selected_files:
                full_path = repo_path / file_path
                if full_path.exists() and full_path.is_file():
                    files_to_scan.append((full_path, file_path))
        else:
            # Scan all Solidity files
            for full_path in repo_path.rglob("*.sol"):
                # Get relative path from repo root
                relative_path = full_path.relative_to(repo_path)
                files_to_scan.append((full_path, str(relative_path)))
        
        if not files_to_scan:
            return {"vulnerabilities": [], "total_issues": 0, "error": "No Solidity files found"}, {}
        
        # Prepare multipart file upload and build mapping
        files = []
        for full_path, relative_path in files_to_scan:
            filename = full_path.name
            file_mapping[filename] = relative_path
            
            with open(full_path, 'rb') as f:
                files.append(
                    ('files', (filename, f.read(), 'text/plain'))
                )
        
        # Call SecurePR API
        async with httpx.AsyncClient(timeout=300.0) as client:  # 5 min timeout for scanning
            response = await client.post(
                f"{self.api_url}/api/scan",
                files=files,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json(), file_mapping
