"""
Particle system implementation for SPH fluid simulation
"""
import numpy as np
from dataclasses import dataclass


@dataclass
class Particle:
    """
    Represents a single SPH fluid particle
    """
    position: np.ndarray      # [x, y, z]
    velocity: np.ndarray      # [vx, vy, vz]
    force: np.ndarray         # [fx, fy, fz]
    mass: float
    density: float
    pressure: float
    viscosity: float          # Dynamic viscosity
    color: tuple              # RGB for visualization
    
    # Additional properties
    temperature: float = 20.0
    active: bool = True
    
    def __post_init__(self):
        self.position = np.array(self.position, dtype=np.float32)
        self.velocity = np.array(self.velocity, dtype=np.float32)
        self.force = np.zeros(3, dtype=np.float32)


class ParticleSystem:
    """
    Manages a collection of particles using compact arrays for better performance
    """
    def __init__(self, max_particles: int = 100000):
        self.max_particles = max_particles
        self.n_particles = 0
        
        # Compact arrays (better performance and memory locality)
        self.positions = np.zeros((max_particles, 3), dtype=np.float32)
        self.velocities = np.zeros((max_particles, 3), dtype=np.float32)
        self.forces = np.zeros((max_particles, 3), dtype=np.float32)
        self.masses = np.zeros(max_particles, dtype=np.float32)
        self.densities = np.zeros(max_particles, dtype=np.float32)
        self.pressures = np.zeros(max_particles, dtype=np.float32)
        self.colors = np.zeros((max_particles, 3), dtype=np.float32)
        self.viscosities = np.ones(max_particles, dtype=np.float32) * 0.001
        
    def add_particle(self, position, velocity, mass, color, viscosity=0.001):
        """
        Add a particle to the system
        
        Args:
            position: [x, y, z] position
            velocity: [vx, vy, vz] velocity
            mass: particle mass
            color: [r, g, b] color (0-1 range)
            viscosity: dynamic viscosity
        
        Returns:
            Index of the added particle
        """
        if self.n_particles >= self.max_particles:
            raise RuntimeError("Maximum number of particles reached")
        
        idx = self.n_particles
        self.positions[idx] = position
        self.velocities[idx] = velocity
        self.masses[idx] = mass
        self.colors[idx] = color
        self.viscosities[idx] = viscosity
        self.densities[idx] = 0.0
        self.pressures[idx] = 0.0
        self.forces[idx] = [0, 0, 0]
        
        self.n_particles += 1
        return idx
    
    def remove_particle(self, index):
        """
        Remove a particle from the system
        
        Args:
            index: Index of particle to remove
        """
        if index >= self.n_particles:
            return
        
        # Swap with last particle and reduce count
        last_idx = self.n_particles - 1
        if index != last_idx:
            self.positions[index] = self.positions[last_idx]
            self.velocities[index] = self.velocities[last_idx]
            self.forces[index] = self.forces[last_idx]
            self.masses[index] = self.masses[last_idx]
            self.densities[index] = self.densities[last_idx]
            self.pressures[index] = self.pressures[last_idx]
            self.colors[index] = self.colors[last_idx]
            self.viscosities[index] = self.viscosities[last_idx]
        
        self.n_particles -= 1
    
    def get_positions(self):
        """
        Get all active particle positions
        
        Returns:
            (N, 3) array of positions
        """
        return self.positions[:self.n_particles]
    
    def get_velocities(self):
        """
        Get all active particle velocities
        
        Returns:
            (N, 3) array of velocities
        """
        return self.velocities[:self.n_particles]
    
    def get_colors_by_property(self, property_name='default', cmap='viridis'):
        """
        Color particles by a property (velocity, pressure, density, etc.)
        
        Args:
            property_name: 'default', 'velocity', 'pressure', 'density'
            cmap: matplotlib colormap name
        
        Returns:
            (N, 3) array of RGB colors
        """
        if property_name == 'default':
            return self.colors[:self.n_particles]
        
        # Get property values
        if property_name == 'velocity':
            values = np.linalg.norm(self.velocities[:self.n_particles], axis=1)
        elif property_name == 'pressure':
            values = self.pressures[:self.n_particles]
        elif property_name == 'density':
            values = self.densities[:self.n_particles]
        else:
            return self.colors[:self.n_particles]
        
        # Normalize to [0, 1]
        if values.max() > values.min():
            normalized = (values - values.min()) / (values.max() - values.min())
        else:
            normalized = np.zeros_like(values)
        
        # Map to colormap
        import matplotlib.cm as cm
        colormap = cm.get_cmap(cmap)
        colors = colormap(normalized)[:, :3]  # Get RGB, drop alpha
        
        return colors.astype(np.float32)
