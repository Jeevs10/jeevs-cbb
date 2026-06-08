import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)


class TestSegmentationEndpoint:
    """Test suite for segmentation API endpoints."""

    def test_segmentation_health_check(self):
        """Test segmentation health check endpoint."""
        response = client.get("/api/v1/segmentation/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
        assert "workflow" in data
        assert "workspace" in data

    @patch('app.services.roboflow_service.run_segmentation_workflow')
    def test_segmentation_success(self, mock_run_workflow):
        """Test successful segmentation request."""
        # Mock the workflow response
        mock_result = {
            "segmentation_mask": {"type": "base64", "value": "fake_base64_data"},
            "detections": [{"class": "person", "confidence": 0.95}]
        }
        mock_run_workflow.return_value = mock_result
        
        response = client.post(
            "/api/v1/segmentation",
            json={
                "image_url": "https://example.com/test-image.jpg",
                "classes": "person,car",
                "save_outputs": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "result" in data
        assert data["result"] == mock_result

    @patch('app.services.roboflow_service.run_segmentation_workflow')
    def test_segmentation_without_classes(self, mock_run_workflow):
        """Test segmentation request without classes filter."""
        mock_result = {"detections": []}
        mock_run_workflow.return_value = mock_result
        
        response = client.post(
            "/api/v1/segmentation",
            json={
                "image_url": "https://example.com/test-image.jpg"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "result" in data

    @patch('app.services.roboflow_service.run_segmentation_workflow')
    def test_segmentation_with_output_dir(self, mock_run_workflow):
        """Test segmentation request with output directory."""
        mock_result = {
            "annotated_image": "/tmp/output/image_annotated.png",
            "detections": []
        }
        mock_run_workflow.return_value = mock_result
        
        response = client.post(
            "/api/v1/segmentation",
            json={
                "image_url": "https://example.com/test-image.jpg",
                "save_outputs": True,
                "output_dir": "/tmp/test_output"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "result" in data

    @patch('app.services.roboflow_service.run_segmentation_workflow')
    def test_segmentation_authentication_error(self, mock_run_workflow):
        """Test segmentation with authentication error."""
        from app.services.roboflow_service import RoboflowAuthenticationError
        mock_run_workflow.side_effect = RoboflowAuthenticationError("Invalid API key")
        
        response = client.post(
            "/api/v1/segmentation",
            json={
                "image_url": "https://example.com/test-image.jpg"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        
        assert "detail" in data

    @patch('app.services.roboflow_service.run_segmentation_workflow')
    def test_segmentation_timeout_error(self, mock_run_workflow):
        """Test segmentation with timeout error."""
        from app.services.roboflow_service import RoboflowTimeoutError
        mock_run_workflow.side_effect = RoboflowTimeoutError("Request timed out")
        
        response = client.post(
            "/api/v1/segmentation",
            json={
                "image_url": "https://example.com/test-image.jpg"
            }
        )
        
        assert response.status_code == 504
        data = response.json()
        
        assert "detail" in data

    @patch('app.services.roboflow_service.run_segmentation_workflow')
    def test_segmentation_request_error(self, mock_run_workflow):
        """Test segmentation with request error."""
        from app.services.roboflow_service import RoboflowRequestError
        mock_run_workflow.side_effect = RoboflowRequestError("Invalid image URL")
        
        response = client.post(
            "/api/v1/segmentation",
            json={
                "image_url": "https://example.com/test-image.jpg"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        
        assert "detail" in data

    def test_segmentation_invalid_url(self):
        """Test segmentation with invalid URL."""
        response = client.post(
            "/api/v1/segmentation",
            json={
                "image_url": "not-a-valid-url"
            }
        )
        
        assert response.status_code == 422  # Validation error

    def test_segmentation_http_url_rejected(self):
        """Test that http:// URLs are rejected."""
        with patch('app.services.roboflow_service.run_segmentation_workflow') as mock_run:
            from app.services.roboflow_service import RoboflowError
            mock_run.side_effect = ValueError("Image URL must use HTTPS")
            
            response = client.post(
                "/api/v1/segmentation",
                json={
                    "image_url": "http://example.com/test-image.jpg"
                }
            )
            
            assert response.status_code == 400


class TestRoboflowService:
    """Test suite for Roboflow service layer."""

    @patch('app.services.roboflow_service.InferenceHTTPClient')
    def test_run_segmentation_workflow_success(self, mock_client_class):
        """Test successful workflow execution."""
        from app.services.roboflow_service import run_segmentation_workflow
        from app.core.config import settings
        
        # Set a fake API key for testing
        settings.roboflow_api_key = "test_api_key"
        
        # Mock the client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.run_workflow.return_value = [
            {"detections": [{"class": "person", "confidence": 0.9}]}
        ]
        
        result = run_segmentation_workflow(
            image_url="https://example.com/test.jpg"
        )
        
        assert "detections" in result
        mock_client.run_workflow.assert_called_once()

    @patch('app.services.roboflow_service.InferenceHTTPClient')
    def test_run_segmentation_workflow_no_api_key(self, mock_client_class):
        """Test workflow execution with missing API key."""
        from app.services.roboflow_service import (
            run_segmentation_workflow,
            RoboflowAuthenticationError
        )
        from app.core.config import settings
        
        settings.roboflow_api_key = ""
        
        with pytest.raises(RoboflowAuthenticationError):
            run_segmentation_workflow(
                image_url="https://example.com/test.jpg"
            )

    @patch('app.services.roboflow_service.InferenceHTTPClient')
    def test_run_segmentation_workflow_http_url_rejected(self, mock_client_class):
        """Test that http:// URLs are rejected."""
        from app.services.roboflow_service import run_segmentation_workflow
        from app.core.config import settings
        
        settings.roboflow_api_key = "test_api_key"
        
        with pytest.raises(ValueError, match="must use HTTPS"):
            run_segmentation_workflow(
                image_url="http://example.com/test.jpg"
            )
