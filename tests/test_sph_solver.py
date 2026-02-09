"""
Unit tests for SPH solver
"""
import pytest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.sph_solver import SPHSolver
from src.fluids.presets import FluidPreset


class TestSPHSolver:
    """Test SPH solver functionality"""
    
    def test_solver_initialization(self):
        """Test that solver initializes correctly"""
        solver = SPHSolver(
            domain_size=(2.0, 2.0, 2.0),
            smoothing_length=0.05,
            time_step=0.001
        )
        
        assert solver.n_active == 0
        assert np.allclose(solver.domain_size, [2.0, 2.0, 2.0])
        assert solver.h == 0.05
        assert solver.dt == 0.001
    
    def test_add_fluid_box(self):
        """Test adding fluid particles"""
        solver = SPHSolver(domain_size=(2.0, 2.0, 2.0))
        
        initial_count = solver.n_active
        
        solver.add_fluid_box(
            position=(0.5, 0.5, 0.5),
            size=(0.5, 0.5, 0.5),
            n_particles=100,
            fluid_properties=FluidPreset.WATER
        )
        
        # Check particles were added
        assert solver.n_active > initial_count
        assert solver.n_active <= 100  # May be slightly less due to spacing
    
    def test_density_calculation(self):
        """Test density computation"""
        solver = SPHSolver(
            domain_size=(1.0, 1.0, 1.0),
            smoothing_length=0.1,
            rest_density=1000.0
        )
        
        # Add some particles
        solver.add_fluid_box(
            position=(0.2, 0.2, 0.2),
            size=(0.3, 0.3, 0.3),
            n_particles=50,
            fluid_properties=FluidPreset.WATER
        )
        
        # Compute density
        solver.compute_density_pressure()
        
        # Check that densities are positive
        for i in range(solver.n_active):
            assert solver.particles.densities[i] > 0
            # Density should be around rest density
            assert solver.particles.densities[i] > 0.01 * solver.rest_density
    
    def test_forces_computation(self):
        """Test force calculation"""
        solver = SPHSolver(domain_size=(1.0, 1.0, 1.0))
        
        solver.add_fluid_box(
            position=(0.3, 0.5, 0.3),
            size=(0.4, 0.3, 0.4),
            n_particles=30,
            fluid_properties=FluidPreset.WATER
        )
        
        # Compute forces
        solver.compute_density_pressure()
        solver.compute_forces()
        
        # Check forces exist
        for i in range(solver.n_active):
            force = solver.particles.forces[i]
            # Force should include at least gravity
            assert not np.allclose(force, [0, 0, 0])
    
    def test_integration_step(self):
        """Test time integration"""
        solver = SPHSolver(domain_size=(2.0, 2.0, 2.0), time_step=0.001)
        
        solver.add_fluid_box(
            position=(1.0, 1.5, 1.0),
            size=(0.3, 0.3, 0.3),
            n_particles=20,
            fluid_properties=FluidPreset.WATER
        )
        
        # Record initial positions
        initial_positions = solver.particles.positions[:solver.n_active].copy()
        
        # Take one step
        solver.step()
        
        # Positions should have changed
        final_positions = solver.particles.positions[:solver.n_active]
        assert not np.allclose(initial_positions, final_positions)
    
    def test_boundary_conditions(self):
        """Test that particles stay within domain"""
        solver = SPHSolver(domain_size=(1.0, 1.0, 1.0))
        
        solver.add_fluid_box(
            position=(0.3, 0.3, 0.3),
            size=(0.4, 0.4, 0.4),
            n_particles=50,
            fluid_properties=FluidPreset.WATER
        )
        
        # Run simulation
        for _ in range(100):
            solver.step()
        
        # Check all particles are within domain
        positions = solver.particles.positions[:solver.n_active]
        
        for i in range(solver.n_active):
            pos = positions[i]
            assert 0 <= pos[0] <= solver.domain_size[0]
            assert 0 <= pos[1] <= solver.domain_size[1]
            assert 0 <= pos[2] <= solver.domain_size[2]
    
    def test_simulation_run(self):
        """Test running simulation for duration"""
        solver = SPHSolver(domain_size=(1.0, 1.0, 1.0), time_step=0.001)
        
        solver.add_fluid_box(
            position=(0.3, 0.3, 0.3),
            size=(0.3, 0.3, 0.3),
            n_particles=20,
            fluid_properties=FluidPreset.WATER
        )
        
        step_count = 0
        
        def callback(solver, step):
            nonlocal step_count
            step_count = step
        
        # Run for 0.1 seconds
        solver.run(duration=0.1, callback=callback)
        
        # Should have taken 100 steps (0.1s / 0.001s)
        assert solver.step_count == 100
        assert step_count == 99  # Zero-indexed
    
    def test_get_info(self):
        """Test simulation info retrieval"""
        solver = SPHSolver(domain_size=(1.0, 1.0, 1.0))
        
        solver.add_fluid_box(
            position=(0.3, 0.3, 0.3),
            size=(0.3, 0.3, 0.3),
            n_particles=30,
            fluid_properties=FluidPreset.WATER
        )
        
        info = solver.get_info()
        
        assert info['particles'] == solver.n_active
        assert 'time' in info
        assert 'step' in info
        assert 'avg_density' in info
        assert 'avg_pressure' in info


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
