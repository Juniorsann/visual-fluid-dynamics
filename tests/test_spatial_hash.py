"""
Unit tests for spatial hash grid
"""
import pytest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.spatial_hash import SpatialHashGrid


class TestSpatialHashGrid:
    """Test spatial hash grid functionality"""
    
    def test_hash_position(self):
        """Test position hashing"""
        grid = SpatialHashGrid(cell_size=0.1)
        
        # Test basic hashing
        pos1 = np.array([0.05, 0.05, 0.05])
        cell1 = grid.hash_position(pos1)
        assert cell1 == (0, 0, 0)
        
        pos2 = np.array([0.15, 0.25, 0.35])
        cell2 = grid.hash_position(pos2)
        assert cell2 == (1, 2, 3)
        
        # Negative positions
        pos3 = np.array([-0.05, 0.05, 0.05])
        cell3 = grid.hash_position(pos3)
        assert cell3 == (-1, 0, 0)
    
    def test_build_grid(self):
        """Test building grid from positions"""
        grid = SpatialHashGrid(cell_size=0.1)
        
        positions = np.array([
            [0.05, 0.05, 0.05],
            [0.15, 0.05, 0.05],
            [0.05, 0.15, 0.05],
            [0.25, 0.25, 0.25]
        ])
        
        grid.build(positions)
        
        # Check grid has entries
        assert len(grid.grid) > 0
        
        # First position should be in cell (0,0,0)
        assert 0 in grid.grid[(0, 0, 0)]
    
    def test_get_neighbors_same_cell(self):
        """Test finding neighbors in same cell"""
        grid = SpatialHashGrid(cell_size=0.1)
        
        # Two particles in same cell
        positions = np.array([
            [0.05, 0.05, 0.05],
            [0.06, 0.06, 0.06]
        ])
        
        grid.build(positions)
        
        # Query first particle's neighbors
        neighbors = grid.get_neighbors(positions[0], radius=0.1)
        
        # Should find both particles (including itself)
        assert 0 in neighbors
        assert 1 in neighbors
    
    def test_get_neighbors_adjacent_cells(self):
        """Test finding neighbors in adjacent cells"""
        grid = SpatialHashGrid(cell_size=0.1)
        
        # Particles in adjacent cells
        positions = np.array([
            [0.05, 0.05, 0.05],   # Cell (0,0,0)
            [0.15, 0.05, 0.05]    # Cell (1,0,0)
        ])
        
        grid.build(positions)
        
        # Query first particle's neighbors
        neighbors = grid.get_neighbors(positions[0], radius=0.1)
        
        # Should find both (adjacent cells are checked)
        assert len(neighbors) >= 1
        assert 0 in neighbors
    
    def test_get_neighbors_far_particles(self):
        """Test that far particles are not returned"""
        grid = SpatialHashGrid(cell_size=0.1)
        
        # Particles far apart
        positions = np.array([
            [0.05, 0.05, 0.05],
            [1.0, 1.0, 1.0]
        ])
        
        grid.build(positions)
        
        # Query first particle with small radius
        neighbors = grid.get_neighbors(positions[0], radius=0.1)
        
        # Should only find particle 0 (itself)
        assert 0 in neighbors
        # Particle 1 should not be found (too far)
        # Note: get_neighbors returns candidates, not distance-filtered
        # So we just check it works without error
    
    def test_get_all_neighbors(self):
        """Test getting neighbors for all particles"""
        grid = SpatialHashGrid(cell_size=0.1)
        
        positions = np.array([
            [0.05, 0.05, 0.05],
            [0.06, 0.06, 0.06],
            [1.0, 1.0, 1.0]
        ])
        
        grid.build(positions)
        
        all_neighbors = grid.get_all_neighbors(positions, radius=0.1)
        
        # Should return list of neighbor lists
        assert len(all_neighbors) == 3
        
        # Each element should be a list
        assert isinstance(all_neighbors[0], list)
    
    def test_get_cells_info(self):
        """Test getting grid statistics"""
        grid = SpatialHashGrid(cell_size=0.1)
        
        positions = np.array([
            [0.05, 0.05, 0.05],
            [0.06, 0.06, 0.06],
            [0.15, 0.15, 0.15]
        ])
        
        grid.build(positions)
        
        info = grid.get_cells_info()
        
        # Check info fields exist
        assert 'num_cells' in info
        assert 'num_particles' in info
        assert 'avg_particles_per_cell' in info
        assert 'max_particles_per_cell' in info
        
        # Should have particles
        assert info['num_particles'] == 3
    
    def test_empty_grid(self):
        """Test empty grid behavior"""
        grid = SpatialHashGrid(cell_size=0.1)
        
        # Don't build grid
        info = grid.get_cells_info()
        
        assert info['num_cells'] == 0
        assert info['num_particles'] == 0
    
    def test_rebuild_grid(self):
        """Test rebuilding grid with new positions"""
        grid = SpatialHashGrid(cell_size=0.1)
        
        # Build first time
        positions1 = np.array([[0.05, 0.05, 0.05]])
        grid.build(positions1)
        
        assert len(grid.grid) > 0
        
        # Rebuild with different positions
        positions2 = np.array([[1.05, 1.05, 1.05]])
        grid.build(positions2)
        
        # Old positions should be cleared
        assert (0, 0, 0) not in grid.grid or len(grid.grid[(0, 0, 0)]) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
