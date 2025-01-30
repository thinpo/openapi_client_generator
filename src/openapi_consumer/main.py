from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import yaml
from openapi_spec_validator import validate_spec
import tempfile
import os
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Starting application...")

from .generator.client_generator import ClientGenerator
from .models.schemas import GenerateRequest, ValidationResponse

logger.debug("Imported all dependencies")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("FastAPI application starting up...")
    yield
    logger.debug("FastAPI application shutting down...")

app = FastAPI(
    title="OpenAPI Client Generator",
    description="A service to generate Python clients from OpenAPI specifications",
    version="1.0.0",
    lifespan=lifespan
)

@app.post("/generate", response_class=FileResponse)
async def generate_client(
    spec_file: UploadFile = File(...),
    package_name: Optional[str] = None
):
    """
    Generate a Python client from an OpenAPI specification file
    """
    logger.debug(f"Received generate request for package: {package_name}")
    try:
        # Read and parse the OpenAPI spec
        content = await spec_file.read()
        spec = yaml.safe_load(content)
        logger.debug("Successfully parsed OpenAPI spec")
        
        # Validate the spec
        validate_spec(spec)
        logger.debug("Successfully validated OpenAPI spec")
        
        # Generate the client
        generator = ClientGenerator(spec, package_name or "generated_client")
        logger.debug("Created ClientGenerator instance")
        
        # Create a temporary file to store the generated code
        with tempfile.NamedTemporaryFile(delete=False, suffix='.py') as tmp_file:
            generated_code = generator.generate()
            logger.debug("Generated client code")
            tmp_file.write(generated_code.encode())
            tmp_file.flush()
            logger.debug(f"Wrote generated code to: {tmp_file.name}")
            
            return FileResponse(
                tmp_file.name,
                media_type='application/python',
                filename='generated_client.py'
            )
            
    except Exception as e:
        logger.error(f"Error generating client: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/validate", response_model=ValidationResponse)
async def validate_spec(spec_file: UploadFile = File(...)):
    """
    Validate an OpenAPI specification file
    """
    logger.debug("Received validate request")
    try:
        content = await spec_file.read()
        spec = yaml.safe_load(content)
        validate_spec(spec)
        logger.debug("Successfully validated spec")
        return ValidationResponse(is_valid=True, message="Specification is valid")
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return ValidationResponse(is_valid=False, message=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 