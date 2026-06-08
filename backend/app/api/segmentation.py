from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, HttpUrl

from app.services.roboflow_service import (
    run_segmentation_workflow,
    RoboflowError,
    RoboflowAuthenticationError,
    RoboflowRequestError,
    RoboflowTimeoutError,
    WORKSPACE_NAME,
    WORKFLOW_ID
)
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


class SegmentationRequest(BaseModel):
    """Request model for segmentation workflow."""
    image_url: Optional[HttpUrl] = None
    image_path: Optional[str] = None
    image_data: Optional[str] = None  # Base64 encoded image data
    classes: Optional[str] = None
    save_outputs: bool = False
    output_dir: Optional[str] = None


class SegmentationResponse(BaseModel):
    """Response model for segmentation workflow."""
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/segmentation", response_model=SegmentationResponse)
def segment_image(request: SegmentationRequest):
    """
    Run the General Segmentation API 3 workflow on an image.
    
    Args:
        request: SegmentationRequest containing image_url or image_path and optional parameters
    
    Returns:
        SegmentationResponse with workflow results or error message
    
    Raises:
        HTTPException: If the workflow fails
    """
    try:
        # Validate that either image_url, image_path, or image_data is provided
        if not request.image_url and not request.image_path and not request.image_data:
            raise HTTPException(
                status_code=400,
                detail="Either image_url, image_path, or image_data must be provided"
            )
        
        # Determine image input
        if request.image_data:
            # Base64 encoded image data
            image_input = f"data:image/jpeg;base64,{request.image_data}"
            logger.info("Segmentation request for base64 image data")
        else:
            image_input = str(request.image_url) if request.image_url else request.image_path
            logger.info(f"Segmentation request for image: {image_input}")
        
        result = run_segmentation_workflow(
            image_input=image_input,
            classes=request.classes,
            output_dir=request.output_dir if request.save_outputs else None
        )
        
        return SegmentationResponse(success=True, result=result)
        
    except RoboflowAuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail=str(e))
        
    except RoboflowTimeoutError as e:
        logger.error(f"Timeout error: {e}")
        raise HTTPException(status_code=504, detail=str(e))
        
    except RoboflowRequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except RoboflowError as e:
        logger.error(f"Roboflow error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/segmentation/health")
def segmentation_health():
    """Health check for the segmentation endpoint."""
    return {
        "status": "healthy",
        "workflow": WORKFLOW_ID,
        "workspace": WORKSPACE_NAME
    }
