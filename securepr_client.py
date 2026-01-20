import httpx
from pathlib import Path
from typing import Dict, Any, List, Tuple
from config import settings


class SecurePRClient:
    """Client for SecurePR production API"""
    
    def __init__(self):
        self.api_url = settings.securepr_api_url.rstrip('/')
    
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
        file_mapping = {}  # Maps filename to original repo path
        
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
        
        # Aggregate all vulnerabilities from all files
        all_vulnerabilities = []
        total_scan_time = 0
        
        # Scan each file individually (SecurePR API scans one file at a time)
        async with httpx.AsyncClient(timeout=300.0) as client:
            for full_path, relative_path in files_to_scan:
                filename = full_path.name
                file_mapping[filename] = relative_path
                
                # Read file content
                try:
                    code_content = full_path.read_text(encoding='utf-8')
                except Exception:
                    continue  # Skip files that can't be read
                
                # Prepare JSON payload as expected by SecurePR API
                payload = {
                    "diff": code_content,
                    "language": "solidity"
                }
                
                try:
                    response = await client.post(
                        f"{self.api_url}/api/scan",
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    
                    # Add file_name to each vulnerability
                    for vuln in result.get('vulnerabilities', []):
                        vuln['file_name'] = filename
                        all_vulnerabilities.append(vuln)
                    
                    total_scan_time += result.get('scan_time_ms', 0)
                    
                except Exception:
                    # If a file fails to scan, continue with others
                    continue
        
        # Aggregate results
        aggregated_result = {
            "vulnerabilities": all_vulnerabilities,
            "total_issues": len(all_vulnerabilities),
            "risk_level": self._calculate_risk_level(all_vulnerabilities),
            "scan_time_ms": total_scan_time
        }
        
        return aggregated_result, file_mapping
    
    def _calculate_risk_level(self, vulnerabilities: List[Dict]) -> str:
        """Calculate overall risk level from vulnerabilities"""
        if not vulnerabilities:
            return "low"
        
        severities = [v.get('severity', 'low').lower() for v in vulnerabilities]
        
        if 'critical' in severities:
            return "critical"
        elif 'high' in severities:
            return "high"
        elif 'medium' in severities:
            return "medium"
        else:
            return "low"
