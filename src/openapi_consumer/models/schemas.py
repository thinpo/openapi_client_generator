from pydantic import BaseModel
from typing import Optional, Dict, Any

class GenerateRequest(BaseModel):
    """
    Request model for client generation
    """
    specification: Dict[str, Any]
    package_name: Optional[str] = None
    
class ValidationResponse(BaseModel):
    """
    Response model for specification validation
    """
    is_valid: bool
    message: str 