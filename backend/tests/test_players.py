import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.player_service import PlayerService
from app.models.schemas import PlayerQueryParams

client = TestClient(app)

class TestPlayersEndpoint:
    """Test suite for players API endpoints."""

    def test_get_players_success(self):
        """Test successful retrieval of players."""
        response = client.get("/api/v1/players")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert "count" in data
        assert "filtered_count" in data
        assert "results" in data
        assert isinstance(data["results"], list)

    def test_get_players_with_pagination(self):
        """Test players endpoint with pagination."""
        response = client.get("/api/v1/players?limit=10&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["results"]) <= 10

    def test_get_players_with_search(self):
        """Test players endpoint with search parameter."""
        response = client.get("/api/v1/players?search=test")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert "results" in data

    def test_get_players_with_invalid_limit(self):
        """Test players endpoint with invalid limit parameter."""
        response = client.get("/api/v1/players?limit=0")
        
        assert response.status_code == 422  # Validation error

    def test_get_players_with_invalid_order(self):
        """Test players endpoint with invalid order parameter."""
        response = client.get("/api/v1/players?order=invalid")
        
        assert response.status_code == 422  # Validation error

    def test_get_player_by_id_success(self):
        """Test successful retrieval of a specific player."""
        # This test would need a real NCAA ID from your data
        response = client.get("/api/v1/players/123456")
        
        # Might return 404 if player doesn't exist, which is expected
        assert response.status_code in [200, 404]

    def test_get_player_by_id_not_found(self):
        """Test retrieval of non-existent player."""
        response = client.get("/api/v1/players/999999")
        
        assert response.status_code == 404
        data = response.json()
        
        assert "detail" in data

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data


class TestPlayerService:
    """Test suite for PlayerService."""

    def test_get_players_with_valid_params(self):
        """Test PlayerService.get_players with valid parameters."""
        params = PlayerQueryParams(
            limit=10,
            offset=0,
            sort="adj_rapm_margin",
            order="desc"
        )
        
        result = PlayerService.get_players(params)
        
        assert result.success is True
        assert isinstance(result.count, int)
        assert isinstance(result.filtered_count, int)
        assert isinstance(result.results, list)

    def test_get_players_with_search_filter(self):
        """Test PlayerService.get_players with search filter."""
        params = PlayerQueryParams(
            limit=10,
            offset=0,
            search="test"
        )
        
        result = PlayerService.get_players(params)
        
        assert result.success is True
        # Should return filtered results
        assert result.filtered_count <= result.count

    def test_get_players_with_year_filter(self):
        """Test PlayerService.get_players with year filter."""
        params = PlayerQueryParams(
            limit=10,
            offset=0,
            year=2025
        )
        
        result = PlayerService.get_players(params)
        
        assert result.success is True
        # Should return filtered results
        assert result.filtered_count <= result.count

    def test_get_player_by_invalid_id(self):
        """Test PlayerService.get_player_by_id with invalid ID."""
        with pytest.raises(ValueError, match="Player not found"):
            PlayerService.get_player_by_id("invalid_id")

    def test_validation_params(self):
        """Test parameter validation."""
        # Test invalid search length
        with pytest.raises(ValueError, match="Search term too long"):
            PlayerQueryParams(search="a" * 101)
        
        # Test invalid year
        with pytest.raises(ValueError, match="Year must be between 2000 and 2100"):
            PlayerQueryParams(year=1999)
