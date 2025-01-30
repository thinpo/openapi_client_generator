from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import yaml
from openapi_spec_validator import validate_spec
import tempfile
import os

from .generator.client_generator import ClientGenerator
from .models.schemas import GenerateRequest, ValidationResponse

app = FastAPI(
    title="OpenAPI Client Generator",
    description="A service to generate Python clients from OpenAPI specifications",
    version="1.0.0"
)

@app.post("/generate", response_class=FileResponse)
async def generate_client(
    spec_file: UploadFile = File(...),
    package_name: Optional[str] = None
):
    """
    Generate a Python client from an OpenAPI specification file
    """
    try:
        # Read and parse the OpenAPI spec
        content = await spec_file.read()
        spec = yaml.safe_load(content)
        
        # Validate the spec
        validate_spec(spec)
        
        # Generate the client
        generator = ClientGenerator(spec, package_name or "generated_client")
        
        # Create a temporary file to store the generated code
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tmp_file:
            generated_code = generator.generate()
            tmp_file.write(generated_code.encode())
            tmp_file.flush()
            
            return FileResponse(
                tmp_file.name,
                media_type='application/python',
                filename='generated_client.py'
            )
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/validate", response_model=ValidationResponse)
async def validate_spec(spec_file: UploadFile = File(...)):
    """
    Validate an OpenAPI specification file
    """
    try:
        content = await spec_file.read()
        spec = yaml.safe_load(content)
        validate_spec(spec)
        return ValidationResponse(is_valid=True, message="Specification is valid")
    except Exception as e:
        return ValidationResponse(is_valid=False, message=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 