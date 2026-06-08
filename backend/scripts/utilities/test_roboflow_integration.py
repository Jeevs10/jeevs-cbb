#!/usr/bin/env python
"""Simple smoke test for Roboflow integration."""
import os
import sys

# Add backend to path
sys.path.insert(0, '/Users/sanjiv/jeevs-cbb/backend')

from app.services.roboflow_service import run_segmentation_workflow, WORKSPACE_NAME, WORKFLOW_ID
from app.core.config import settings

def test_config():
    """Test that configuration is loaded."""
    print("Testing configuration...")
    assert settings.roboflow_api_key, "ROBOFLOW_API_KEY not set"
    print(f"✓ API key loaded (length: {len(settings.roboflow_api_key)})")
    print(f"✓ Workspace: {WORKSPACE_NAME}")
    print(f"✓ Workflow: {WORKFLOW_ID}")

def test_import():
    """Test that the service can be imported."""
    print("\nTesting import...")
    from app.services.roboflow_service import (
        RoboflowError,
        RoboflowAuthenticationError,
        RoboflowRequestError,
        RoboflowTimeoutError
    )
    print("✓ All exceptions imported successfully")

def test_validation():
    """Test input validation."""
    print("\nTesting validation...")
    
    # Test HTTP URL rejection
    try:
        run_segmentation_workflow("http://example.com/test.jpg")
        assert False, "Should have rejected HTTP URL"
    except ValueError as e:
        assert "HTTPS" in str(e)
        print("✓ HTTP URLs correctly rejected")
    
    # Test missing API key
    original_key = settings.roboflow_api_key
    settings.roboflow_api_key = ""
    try:
        run_segmentation_workflow("https://example.com/test.jpg")
        assert False, "Should have raised auth error"
    except Exception as e:
        assert "Authentication" in str(type(e).__name__)
        print("✓ Missing API key correctly detected")
    finally:
        settings.roboflow_api_key = original_key

if __name__ == "__main__":
    print("=" * 60)
    print("Roboflow Integration Smoke Test")
    print("=" * 60)
    
    try:
        test_config()
        test_import()
        test_validation()
        
        print("\n" + "=" * 60)
        print("✓ All smoke tests passed!")
        print("=" * 60)
        print("\nNote: Actual API call test skipped (requires real image)")
        print("To test with a real image, use the API endpoint:")
        print("  POST /api/v1/segmentation")
        print("  { \"image_url\": \"https://example.com/image.jpg\" }")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
