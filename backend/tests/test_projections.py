"""
Tests for the projection service and API.
"""

import pytest
from app.services.projection_service import ProjectionService, get_projection_service


class TestProjectionService:
    """Test cases for ProjectionService."""
    
    def test_service_initialization(self):
        """Test that the service initializes correctly."""
        service = get_projection_service()
        assert service is not None
        assert service._clusters_df is not None
        assert service._bpm_change_df is not None
        assert service._cluster_descriptions is not None
    
    def test_get_player_cluster(self):
        """Test getting cluster information for a player."""
        service = get_projection_service()
        
        # Test with a known player (using first player in clusters dataset)
        first_player = service._clusters_df.iloc[0]
        ncaa_id = str(first_player['AthleteSourceId'])
        
        cluster_info = service.get_player_cluster(ncaa_id)
        
        assert cluster_info is not None
        assert 'cluster_id' in cluster_info
        assert 'cluster_description' in cluster_info
        assert 'player_features' in cluster_info
    
    def test_get_cluster_historical_data(self):
        """Test getting historical data for a cluster."""
        service = get_projection_service()
        
        # Test with cluster 4 (should have data)
        historical_data = service.get_cluster_historical_data(4)
        
        assert len(historical_data) > 0
        assert 'bpm_change' in historical_data.columns
        assert 'player_key' in historical_data.columns
    
    def test_calculate_similarity(self):
        """Test similarity calculation between players."""
        service = get_projection_service()
        
        target_features = {
            'Usage_from': 20.0,
            'BPM_from': 5.0,
            'Height': 77.0,
            'off_rtg_from': 110.0,
            'def_rtg_from': 100.0,
            'eFG_from': 0.5,
            'TS_per_from': 0.55,
        }
        
        # Test with identical features (should be 1.0)
        identical_features = target_features.copy()
        similarity = service.calculate_similarity(target_features, identical_features)
        assert similarity == 1.0
        
        # Test with different features (should be less than 1.0)
        different_features = {
            'Usage_from': 10.0,
            'BPM_from': -2.0,
            'Height': 70.0,
            'off_rtg_from': 95.0,
            'def_rtg_from': 110.0,
            'eFG_from': 0.4,
            'TS_per_from': 0.45,
        }
        similarity = service.calculate_similarity(target_features, different_features)
        assert 0.0 <= similarity < 1.0
    
    def test_calculate_projection(self):
        """Test full projection calculation."""
        service = get_projection_service()
        
        # Use a known player from the dataset
        first_player = service._clusters_df.iloc[0]
        ncaa_id = str(first_player['AthleteSourceId'])
        
        result = service.calculate_projection(
            ncaa_id=ncaa_id,
            current_year=2026,
            years_ahead=1,
            min_samples=5
        )
        
        # Check that result has expected structure
        assert 'player_id' in result
        assert 'current_year' in result
        assert 'cluster_id' in result
        assert 'historical_samples' in result
        assert 'projections' in result
        assert 'methodology' in result
        
        # If no error, check projection details
        if 'error' not in result:
            assert len(result['projections']) > 0
            projection = result['projections'][0]
            assert 'year' in projection
            assert 'projected_bpm' in projection or 'error' in projection


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
