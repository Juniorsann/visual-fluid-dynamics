"""
Spatial hash grid for efficient neighbor search in SPH simulation
"""
import numpy as np
from collections import defaultdict


class SpatialHashGrid:
    """
    Spatial hash grid for fast neighbor search
    
    Instead of O(N²) brute force search, this provides O(N) complexity
    by dividing space into cells and only checking nearby cells.
    
    Concept:
    - Divide space into uniform grid cells (size = smoothing length h)
    - Hash each particle into its cell
    - For neighbor search, only check the 27 adjacent cells (3x3x3 in 3D)
    """
    
    def __init__(self, cell_size):
        """
        Initialize spatial hash grid
        
        Args:
            cell_size: Size of each grid cell (typically = smoothing length h)
        """
        self.cell_size = cell_size
        self.grid = defaultdict(list)  # {(i,j,k): [particle_indices]}
    
    def hash_position(self, position):
        """
        Convert 3D position to grid cell coordinates
        
        Maps continuous position to discrete cell: (x, y, z) → (i, j, k)
        
        Args:
            position: [x, y, z] array
        
        Returns:
            Tuple (i, j, k) representing cell coordinates
        """
        i = int(np.floor(position[0] / self.cell_size))
        j = int(np.floor(position[1] / self.cell_size))
        k = int(np.floor(position[2] / self.cell_size))
        return (i, j, k)
    
    def build(self, positions):
        """
        Build/rebuild the grid from particle positions
        
        Should be called every timestep as particles move
        
        Args:
            positions: (N, 3) array of particle positions
        """
        self.grid.clear()
        
        for idx, pos in enumerate(positions):
            cell = self.hash_position(pos)
            self.grid[cell].append(idx)
    
    def get_neighbors(self, position, radius):
        """
        Get indices of particles within radius of a position
        
        Checks the cell containing position and all 26 adjacent cells
        
        Args:
            position: [x, y, z] search position
            radius: search radius (typically = smoothing length h)
        
        Returns:
            List of particle indices within radius
        """
        cell = self.hash_position(position)
        neighbors = []
        
        # Check current cell and all 26 adjacent cells (3x3x3 - 1)
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                for dk in [-1, 0, 1]:
                    neighbor_cell = (cell[0] + di, cell[1] + dj, cell[2] + dk)
                    
                    if neighbor_cell in self.grid:
                        neighbors.extend(self.grid[neighbor_cell])
        
        return neighbors
    
    def get_all_neighbors(self, positions, radius):
        """
        Get neighbors for all particles (vectorized approach)
        
        Args:
            positions: (N, 3) array of positions
            radius: search radius
        
        Returns:
            List of lists: neighbors[i] contains indices of neighbors of particle i
        """
        all_neighbors = []
        for pos in positions:
            all_neighbors.append(self.get_neighbors(pos, radius))
        return all_neighbors
    
    def get_neighbor_count(self, position, radius):
        """
        Get count of neighbors (faster than getting full list if only count is needed)
        
        Args:
            position: [x, y, z] search position
            radius: search radius
        
        Returns:
            Number of neighbors
        """
        return len(self.get_neighbors(position, radius))
    
    def get_cells_info(self):
        """
        Get information about the grid structure
        
        Returns:
            Dictionary with grid statistics
        """
        if not self.grid:
            return {
                'num_cells': 0,
                'num_particles': 0,
                'avg_particles_per_cell': 0,
                'max_particles_per_cell': 0
            }
        
        particles_per_cell = [len(particles) for particles in self.grid.values()]
        
        return {
            'num_cells': len(self.grid),
            'num_particles': sum(particles_per_cell),
            'avg_particles_per_cell': np.mean(particles_per_cell),
            'max_particles_per_cell': max(particles_per_cell)
        }
