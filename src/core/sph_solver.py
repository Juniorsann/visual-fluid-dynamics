"""
Main SPH solver implementation
"""
import numpy as np
from .particle import ParticleSystem
from .kernel import SPHKernel, VectorizedKernels
from .spatial_hash import SpatialHashGrid


class SPHSolver:
    """
    Smoothed Particle Hydrodynamics (SPH) solver for fluid simulation
    
    Implements the core SPH algorithm:
    1. Compute density and pressure
    2. Compute forces (pressure, viscosity, external)
    3. Integrate motion using time stepping
    4. Apply boundary conditions
    """
    
    def __init__(self,
                 domain_size=(2.0, 2.0, 2.0),
                 smoothing_length=0.05,
                 particle_mass=0.02,
                 rest_density=1000.0,
                 gas_constant=2000.0,
                 viscosity=0.001,
                 gravity=(0, -9.81, 0),
                 time_step=0.001,
                 max_particles=100000):
        """
        Initialize SPH solver
        
        Args:
            domain_size: (width, height, depth) of simulation domain in meters
            smoothing_length: SPH smoothing radius (h parameter)
            particle_mass: Mass of each particle in kg
            rest_density: Rest density of fluid in kg/m³
            gas_constant: Gas constant for pressure calculation (stiffness)
            viscosity: Dynamic viscosity in Pa·s
            gravity: Gravity vector (x, y, z) in m/s²
            time_step: Time step for integration in seconds
            max_particles: Maximum number of particles
        """
        self.domain_size = np.array(domain_size, dtype=np.float32)
        self.h = smoothing_length
        self.particle_mass = particle_mass
        self.rest_density = rest_density
        self.gas_constant = gas_constant
        self.viscosity = viscosity
        self.gravity = np.array(gravity, dtype=np.float32)
        self.dt = time_step
        
        # Particle system
        self.particles = ParticleSystem(max_particles)
        self.n_active = 0
        
        # Spatial hash grid for neighbor search optimization
        self.spatial_grid = SpatialHashGrid(cell_size=self.h)
        
        # Kernels
        self.kernel = SPHKernel()
        self.vectorized_kernels = VectorizedKernels()
        
        # Simulation state
        self.time = 0.0
        self.step_count = 0
    
    def add_fluid_box(self, position, size, n_particles, fluid_properties):
        """
        Add a box of fluid particles
        
        Args:
            position: (x, y, z) bottom corner of box
            size: (width, height, depth) of box
            n_particles: Number of particles to create
            fluid_properties: Dictionary with 'density', 'viscosity', 'color', etc.
        """
        # Calculate particle spacing for uniform distribution
        volume = size[0] * size[1] * size[2]
        spacing = (volume / n_particles) ** (1/3)
        
        nx = max(1, int(size[0] / spacing))
        ny = max(1, int(size[1] / spacing))
        nz = max(1, int(size[2] / spacing))
        
        # Add particles in a grid
        count = 0
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    if count >= n_particles:
                        break
                    
                    # Add small random offset to avoid perfect grid
                    offset = np.random.uniform(-0.1, 0.1, 3) * spacing
                    pos = (np.array(position) + 
                          np.array([i * spacing, j * spacing, k * spacing]) +
                          offset)
                    
                    # Ensure particle is within bounds
                    pos = np.clip(pos, 0, self.domain_size)
                    
                    # Add particle
                    self.particles.add_particle(
                        position=pos,
                        velocity=[0, 0, 0],
                        mass=self.particle_mass,
                        color=fluid_properties.get('color', (0.2, 0.5, 1.0)),
                        viscosity=fluid_properties.get('viscosity', self.viscosity)
                    )
                    
                    self.n_active += 1
                    count += 1
    
    def compute_density_pressure(self):
        """
        Compute density and pressure for all particles using SPH interpolation
        
        Density: ρᵢ = Σⱼ mⱼ W(rᵢ - rⱼ, h)
        Pressure: P = k(ρ - ρ₀)
        """
        # Rebuild spatial grid
        self.spatial_grid.build(self.particles.positions[:self.n_active])
        
        # Compute density for each particle
        for i in range(self.n_active):
            pos_i = self.particles.positions[i]
            
            # Find neighbors
            neighbors = self.spatial_grid.get_neighbors(pos_i, self.h)
            
            # Compute density using Poly6 kernel
            density = 0.0
            for j in neighbors:
                pos_j = self.particles.positions[j]
                r = pos_i - pos_j
                
                W = self.kernel.poly6(r, self.h)
                density += self.particles.masses[j] * W
            
            # Ensure minimum density
            density = max(density, self.rest_density * 0.01)
            self.particles.densities[i] = density
            
            # Compute pressure using equation of state
            # P = k(ρ - ρ₀)
            self.particles.pressures[i] = self.gas_constant * (density - self.rest_density)
    
    def compute_forces(self):
        """
        Compute all forces acting on particles
        
        Forces include:
        - Pressure force (prevents compression)
        - Viscosity force (internal friction)
        - Gravity (external force)
        """
        # Reset forces
        self.particles.forces[:self.n_active] = 0.0
        
        # Compute forces for each particle
        for i in range(self.n_active):
            pos_i = self.particles.positions[i]
            vel_i = self.particles.velocities[i]
            
            neighbors = self.spatial_grid.get_neighbors(pos_i, self.h)
            
            f_pressure = np.zeros(3, dtype=np.float32)
            f_viscosity = np.zeros(3, dtype=np.float32)
            
            for j in neighbors:
                if i == j:
                    continue
                
                pos_j = self.particles.positions[j]
                vel_j = self.particles.velocities[j]
                r = pos_i - pos_j
                
                # Pressure force
                # F^pressure = -Σⱼ mⱼ (Pᵢ + Pⱼ)/(2ρⱼ) ∇W
                grad_W = self.kernel.spiky_gradient(r, self.h)
                
                if self.particles.densities[j] > 0:
                    P_avg = (self.particles.pressures[i] + self.particles.pressures[j]) / 2.0
                    f_pressure += (-self.particles.masses[j] * P_avg / 
                                  self.particles.densities[j] * grad_W)
                
                # Viscosity force
                # F^viscosity = μ Σⱼ mⱼ (vⱼ - vᵢ)/ρⱼ ∇²W
                lap_W = self.kernel.viscosity_laplacian(r, self.h)
                
                if self.particles.densities[j] > 0:
                    visc = self.particles.viscosities[i]
                    f_viscosity += (visc * self.particles.masses[j] * 
                                   (vel_j - vel_i) / self.particles.densities[j] * lap_W)
            
            # Gravity force
            f_gravity = self.particles.masses[i] * self.gravity
            
            # Total force
            self.particles.forces[i] = f_pressure + f_viscosity + f_gravity
    
    def integrate(self):
        """
        Integrate equations of motion using semi-implicit Euler method
        
        This is a simplified version of Velocity Verlet
        """
        for i in range(self.n_active):
            # Compute acceleration
            if self.particles.masses[i] > 0:
                acceleration = self.particles.forces[i] / self.particles.masses[i]
            else:
                acceleration = np.zeros(3, dtype=np.float32)
            
            # Update velocity (semi-implicit)
            self.particles.velocities[i] += acceleration * self.dt
            
            # Update position
            self.particles.positions[i] += self.particles.velocities[i] * self.dt
            
            # Apply boundary conditions
            self.apply_boundary_conditions(i)
    
    def apply_boundary_conditions(self, particle_idx):
        """
        Apply boundary conditions (particles bounce off domain walls)
        
        Args:
            particle_idx: Index of particle to apply boundaries to
        """
        pos = self.particles.positions[particle_idx]
        vel = self.particles.velocities[particle_idx]
        
        damping = 0.5  # Coefficient of restitution (energy loss on collision)
        epsilon = 0.001  # Small offset to prevent particles from sticking to walls
        
        # Check each axis
        for axis in range(3):
            # Lower boundary
            if pos[axis] < 0:
                pos[axis] = epsilon
                vel[axis] = abs(vel[axis]) * damping  # Bounce back
            
            # Upper boundary
            elif pos[axis] > self.domain_size[axis]:
                pos[axis] = self.domain_size[axis] - epsilon
                vel[axis] = -abs(vel[axis]) * damping  # Bounce back
        
        self.particles.positions[particle_idx] = pos
        self.particles.velocities[particle_idx] = vel
    
    def step(self):
        """
        Advance simulation by one time step
        
        SPH algorithm:
        1. Compute density and pressure
        2. Compute forces
        3. Integrate motion
        """
        if self.n_active == 0:
            return
        
        self.compute_density_pressure()
        self.compute_forces()
        self.integrate()
        
        self.time += self.dt
        self.step_count += 1
    
    def run(self, duration, callback=None):
        """
        Run simulation for a specified duration
        
        Args:
            duration: Simulation time in seconds
            callback: Optional function called after each step: callback(solver, step)
        """
        n_steps = int(duration / self.dt)
        
        for step in range(n_steps):
            self.step()
            
            if callback is not None:
                callback(self, step)
    
    def get_info(self):
        """
        Get information about current simulation state
        
        Returns:
            Dictionary with simulation statistics
        """
        if self.n_active == 0:
            return {
                'time': self.time,
                'step': self.step_count,
                'particles': 0,
                'avg_density': 0,
                'avg_pressure': 0,
                'avg_velocity': 0
            }
        
        velocities = self.particles.velocities[:self.n_active]
        speeds = np.linalg.norm(velocities, axis=1)
        
        return {
            'time': self.time,
            'step': self.step_count,
            'particles': self.n_active,
            'avg_density': np.mean(self.particles.densities[:self.n_active]),
            'avg_pressure': np.mean(self.particles.pressures[:self.n_active]),
            'avg_velocity': np.mean(speeds),
            'max_velocity': np.max(speeds) if len(speeds) > 0 else 0,
            'grid_info': self.spatial_grid.get_cells_info()
        }
