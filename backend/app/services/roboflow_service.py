"""Roboflow service for running segmentation workflows."""
import os
import base64
import time
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import httpx

from inference_sdk import InferenceHTTPClient
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Workflow configuration
WORKSPACE_NAME = "sanjivs-workspace-qelhy"
WORKFLOW_ID = "general-segmentation-api-3"
API_URL = "https://serverless.roboflow.com"

# Retry configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1.0
REQUEST_TIMEOUT = 30.0  # seconds


class RoboflowError(Exception):
    """Base exception for Roboflow-related errors."""
    pass


class RoboflowAuthenticationError(RoboflowError):
    """Raised when API key is invalid or missing."""
    pass


class RoboflowRequestError(RoboflowError):
    """Raised when workflow request fails."""
    pass


class RoboflowTimeoutError(RoboflowError):
    """Raised when workflow request times out."""
    pass


def run_segmentation_workflow(
    image_input: Union[str, Path],
    classes: Optional[Union[str, List[str]]] = None,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run the General Segmentation API 3 workflow on an image.
    
    Args:
        image_input: URL of the image (must be https) or local file path
        classes: Optional list of classes to filter (or comma-separated string)
        output_dir: Optional directory to save image outputs (base64 decoded)
    
    Returns:
        Dict containing workflow results. Image-shaped outputs are saved to disk
        and replaced with file paths in the response.
    
    Raises:
        RoboflowAuthenticationError: If API key is missing or invalid
        RoboflowRequestError: If the workflow request fails
        RoboflowTimeoutError: If the request times out
        RoboflowError: For other Roboflow-related errors
    """
    if not settings.roboflow_api_key:
        raise RoboflowAuthenticationError(
            "ROBOFLOW_API_KEY not configured. Set it in your environment or .env file."
        )
    
    # Determine if input is a data URL, local file, or remote URL
    image_str = str(image_input) if isinstance(image_input, str) else str(image_input)
    
    # Initialize variables for logging
    is_local_file = False
    image_path = None
    
    # Check for data URL (base64 encoded image with prefix)
    if image_str.startswith("data:image/"):
        # Extract base64 data from data URL
        # Format: data:image/<type>;base64,<data>
        if ";base64," in image_str:
            image_value = image_str.split(";base64,", 1)[1]
            logger.info("Using base64 image data from data URL")
        else:
            raise ValueError("Invalid data URL format. Expected: data:image/<type>;base64,<data>")
    else:
        # Check if it's a local file path
        image_path = Path(image_input) if isinstance(image_input, str) else image_input
        is_local_file = image_path.exists()
        
        if is_local_file:
            # Read local file and encode as base64
            if not image_path.is_file():
                raise ValueError(f"Local path is not a file: {image_path}")
            
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
            
            image_value = image_data
            logger.info(f"Using local image file: {image_path}")
        else:
            # Use URL
            if not image_str.startswith("https://"):
                raise ValueError("Image URL must use HTTPS (http:// is rejected by Roboflow)")
            image_value = image_str
            logger.info(f"Using remote image URL: {image_input}")
    
    # Prepare parameters - workflow requires classes parameter as string
    # Always provide a value, never None
    if classes is not None:
        # Convert list to comma-separated string if needed
        if isinstance(classes, list):
            classes_str = ",".join(classes)
        else:
            classes_str = classes
    else:
        # Default to empty string
        classes_str = ""
    parameters = {"classes": classes_str}
    
    # Prepare image input
    images_input = {"image": image_value}
    
    # Retry logic with exponential backoff
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(
                f"Running segmentation workflow (attempt {attempt + 1}/{MAX_RETRIES}) "
                f"on image: {image_path if is_local_file else image_input}"
            )
            
            client = InferenceHTTPClient(
                api_url=API_URL,
                api_key=settings.roboflow_api_key
            )
            
            result = client.run_workflow(
                workspace_name=WORKSPACE_NAME,
                workflow_id=WORKFLOW_ID,
                images=images_input,
                parameters=parameters
            )
            
            # Result is a list with one entry per input image
            if not result or len(result) == 0:
                raise RoboflowRequestError("Workflow returned empty result")
            
            # Extract the single result (we only sent one image)
            workflow_result = result[0]
            
            # Handle image outputs (base64 blobs) - decode and save to disk
            if output_dir:
                workflow_result = _handle_image_outputs(
                    workflow_result, 
                    output_dir, 
                    image_url
                )
            else:
                # If no output dir, strip image outputs to avoid large payloads
                workflow_result = _strip_image_outputs(workflow_result)
            
            logger.info("Segmentation workflow completed successfully")
            return workflow_result
            
        except httpx.TimeoutException as e:
            last_error = RoboflowTimeoutError(f"Request timed out: {e}")
            logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise RoboflowAuthenticationError(
                    "Invalid Roboflow API key. Check your ROBOFLOW_API_KEY setting."
                )
            last_error = RoboflowRequestError(f"HTTP error {e.response.status_code}: {e}")
            logger.warning(f"HTTP error on attempt {attempt + 1}: {e}")
            
        except Exception as e:
            last_error = RoboflowError(f"Unexpected error: {e}")
            logger.warning(f"Error on attempt {attempt + 1}: {e}")
        
        # Exponential backoff before retry
        if attempt < MAX_RETRIES - 1:
            delay = INITIAL_RETRY_DELAY * (2 ** attempt)
            logger.info(f"Retrying in {delay} seconds...")
            time.sleep(delay)
    
    # All retries exhausted
    raise last_error or RoboflowError("Workflow failed after maximum retries")


def _handle_image_outputs(
    result: Dict[str, Any], 
    output_dir: str, 
    source_url: str
) -> Dict[str, Any]:
    """
    Decode base64 image outputs and save to disk.
    
    Args:
        result: Workflow result dict
        output_dir: Directory to save images
        source_url: Original image URL (for naming)
    
    Returns:
        Result dict with image outputs replaced by file paths
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate a safe filename from the source URL
    filename = _url_to_filename(source_url)
    
    processed_result = {}
    
    for key, value in result.items():
        # Check if this is an image-shaped output (base64 blob)
        if isinstance(value, dict) and value.get("type") == "base64":
            # Decode and save
            base64_data = value.get("value", "")
            if base64_data:
                image_filename = f"{filename}_{key}.png"
                image_path = output_path / image_filename
                
                try:
                    image_bytes = base64.b64decode(base64_data)
                    image_path.write_bytes(image_bytes)
                    processed_result[key] = str(image_path)
                    logger.info(f"Saved image output to {image_path}")
                except Exception as e:
                    logger.error(f"Failed to decode/save image output {key}: {e}")
                    processed_result[key] = None
            else:
                processed_result[key] = None
        else:
            # Keep non-image outputs as-is
            processed_result[key] = value
    
    return processed_result


def _strip_image_outputs(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove image-shaped outputs from result to keep payload small.
    
    Args:
        result: Workflow result dict
    
    Returns:
        Result dict with image outputs removed
    """
    processed_result = {}
    
    for key, value in result.items():
        if isinstance(value, dict) and value.get("type") == "base64":
            # Skip image outputs
            logger.debug(f"Stripped image output: {key}")
        else:
            processed_result[key] = value
    
    return processed_result


def _url_to_filename(url_or_path: str) -> str:
    """
    Convert a URL or file path to a safe filename.
    
    Args:
        url_or_path: Image URL or file path
    
    Returns:
        Safe filename string
    """
    # Extract the last part of the URL path or file path
    path = url_or_path.split("/")[-1]
    # Remove query parameters and extensions
    name = path.split("?")[0].split(".")[0]
    # Remove any non-alphanumeric characters
    safe_name = "".join(c for c in name if c.isalnum() or c in "_-")
    return safe_name or "image"
