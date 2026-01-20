from typing import List, Optional
from pydantic import BaseModel


class QAPair(BaseModel):
    """Question-Answer pair from AgentArena task details"""
    question: str
    answer: str


class TaskResponse(BaseModel):
    """AgentArena task details response model"""
    id: str
    taskId: str
    projectRepo: Optional[str] = None
    title: str
    description: str
    bounty: Optional[str] = None
    status: str
    startTime: Optional[str] = None
    deadline: Optional[str] = None
    selectedBranch: Optional[str] = None
    selectedFiles: Optional[List[str]] = []
    selectedDocs: Optional[List[str]] = []
    additionalLinks: Optional[List[str]] = []
    additionalDocs: Optional[str] = None
    qaResponses: Optional[List[QAPair]] = []


class WebhookNotification(BaseModel):
    """Webhook payload from AgentArena"""
    task_id: str
    task_repository_url: str
    task_details_url: str
    post_findings_url: str


class Finding(BaseModel):
    """AgentArena finding format"""
    title: str
    description: str
    severity: str  # High|Medium|Low|Info
    file_paths: List[str]


class FindingsSubmission(BaseModel):
    """Final submission to AgentArena"""
    task_id: str
    findings: List[Finding]
