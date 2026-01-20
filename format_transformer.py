from typing import Dict, Any, List
from models import Finding, FindingsSubmission


class FormatTransformer:
    """Transform SecurePR response format to AgentArena format"""
    
    SEVERITY_MAPPING = {
        # Map SecurePR severity levels to AgentArena format
        "critical": "High",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "info": "Info",
        "informational": "Info",
    }
    
    @staticmethod
    def transform(task_id: str, securepr_response: Dict[str, Any], file_mapping: Dict[str, str]) -> FindingsSubmission:
        """
        Transform SecurePR findings to AgentArena format
        
        Args:
            task_id: AgentArena task ID
            securepr_response: Response from SecurePR API with 'vulnerabilities' array
            file_mapping: Mapping of uploaded filename to original path in repo
            
        Returns:
            Formatted findings for AgentArena submission
        """
        findings = []
        
        # Extract vulnerabilities from SecurePR response
        vulnerabilities = securepr_response.get("vulnerabilities", [])
        
        for vuln in vulnerabilities:
            # Map severity
            severity = vuln.get("severity", "info").lower()
            mapped_severity = FormatTransformer.SEVERITY_MAPPING.get(severity, "Info")
            
            # Get file path from mapping (if available)
            file_name = vuln.get("file_name", "unknown")
            file_paths = [file_mapping.get(file_name, file_name)]
            
            # Create title from type and CWE
            title = FormatTransformer._create_title(vuln)
            
            # Create AgentArena finding
            arena_finding = Finding(
                title=title,
                description=FormatTransformer._format_description(vuln),
                severity=mapped_severity,
                file_paths=file_paths
            )
            findings.append(arena_finding)
        
        return FindingsSubmission(task_id=task_id, findings=findings)
    
    @staticmethod
    def _create_title(vuln: Dict[str, Any]) -> str:
        """
        Create concise title from vulnerability data
        
        Args:
            vuln: Single vulnerability from SecurePR
            
        Returns:
            Clear, concise title
        """
        vuln_type = vuln.get("type", "Security Issue")
        cwe_id = vuln.get("cwe_id")
        
        if cwe_id:
            return f"{vuln_type} ({cwe_id})"
        return vuln_type
    
    @staticmethod
    def _format_description(vuln: Dict[str, Any]) -> str:
        """
        Format detailed description including exploitation details and recommendations
        
        Args:
            vuln: Single vulnerability from SecurePR
            
        Returns:
            Formatted description string
        """
        description_parts = []
        
        # Main description
        if desc := vuln.get("description"):
            description_parts.append(desc)
        
        # Add line information
        if line := vuln.get("line"):
            description_parts.append(f"\n**Location:** Line {line}")
        
        # Add confidence score
        if confidence := vuln.get("confidence"):
            description_parts.append(f"**Confidence:** {confidence}%")
        
        # Add CWE reference
        if cwe_id := vuln.get("cwe_id"):
            description_parts.append(f"**CWE:** {cwe_id}")
        
        # Add similar CVEs if available
        if similar_cves := vuln.get("similar_cves"):
            if similar_cves:
                cve_list = ", ".join(similar_cves[:5])  # Limit to first 5
                description_parts.append(f"**Related CVEs:** {cve_list}")
        
        # Add recommendation/fix
        if fix := vuln.get("fix"):
            description_parts.append(f"\n**Recommendation:**\n{fix}")
        
        return "\n".join(description_parts)
