#!/usr/bin/env python
"""
Validation script for SPH fluid simulator

Tests all core functionality without requiring PyVista visualization.
Run this to verify the simulator is working correctly.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.sph_solver import SPHSolver
from src.core.kernel import SPHKernel, VectorizedKernels
from src.core.spatial_hash import SpatialHashGrid
from src.fluids.presets import FluidPreset
import numpy as np


def print_header(text):
    """Print section header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def test_kernels():
    """Test SPH kernel functions"""
    print_header("Testing SPH Kernels")
    
    kernel = SPHKernel()
    h = 0.1
    
    # Poly6
    val = kernel.poly6(np.array([0.05, 0, 0]), h)
    assert val > 0, "Poly6 should be positive within h"
    print(f"✓ Poly6 kernel: {val:.2f}")
    
    # Spiky gradient
    grad = kernel.spiky_gradient(np.array([0.05, 0, 0]), h)
    assert grad[0] < 0, "Spiky gradient should point inward"
    print(f"✓ Spiky gradient magnitude: {np.linalg.norm(grad):.2f}")
    
    # Viscosity laplacian
    lap = kernel.viscosity_laplacian(np.array([0.05, 0, 0]), h)
    assert lap > 0, "Viscosity laplacian should be positive"
    print(f"✓ Viscosity laplacian: {lap:.2f}")
    
    # Vectorized
    vkernels = VectorizedKernels()
    r_vectors = np.array([[0.0, 0.0, 0.0], [0.05, 0.0, 0.0], [0.15, 0.0, 0.0]])
    vals = vkernels.poly6_vectorized(r_vectors, h)
    assert len(vals) == 3, "Vectorized should return array"
    print(f"✓ Vectorized kernels working")


def test_spatial_hash():
    """Test spatial hash grid"""
    print_header("Testing Spatial Hash Grid")
    
    grid = SpatialHashGrid(cell_size=0.1)
    
    positions = np.array([
        [0.05, 0.05, 0.05],
        [0.06, 0.06, 0.06],
        [1.0, 1.0, 1.0]
    ])
    
    grid.build(positions)
    neighbors = grid.get_neighbors(positions[0], radius=0.1)
    
    assert len(neighbors) >= 1, "Should find at least self"
    print(f"✓ Found {len(neighbors)} neighbors for particle 0")
    
    info = grid.get_cells_info()
    print(f"✓ Grid has {info['num_cells']} cells")
    print(f"✓ Average particles/cell: {info['avg_particles_per_cell']:.1f}")


def test_fluid_presets():
    """Test fluid presets"""
    print_header("Testing Fluid Presets")
    
    presets = FluidPreset.list_presets()
    print(f"✓ Found {len(presets)} fluid presets")
    
    for name in ['WATER', 'OIL_LIGHT', 'HONEY']:
        fluid = getattr(FluidPreset, name)
        print(f"  - {fluid['name']:15} ρ={fluid['density']:7.1f} kg/m³  μ={fluid['viscosity']:7.4f} Pa·s")
    
    water = FluidPreset.get_preset('water')
    assert water['name'] == 'Water', "get_preset should work"
    print(f"✓ get_preset() working")


def test_sph_solver():
    """Test complete SPH solver"""
    print_header("Testing SPH Solver")
    
    # Initialize solver
    solver = SPHSolver(
        domain_size=(1.0, 1.0, 1.0),
        smoothing_length=0.1,
        time_step=0.001
    )
    print(f"✓ Solver initialized")
    
    # Add particles
    solver.add_fluid_box(
        position=(0.3, 0.3, 0.3),
        size=(0.4, 0.4, 0.4),
        n_particles=100,
        fluid_properties=FluidPreset.WATER
    )
    print(f"✓ Added {solver.n_active} particles")
    
    # Test density calculation
    solver.compute_density_pressure()
    avg_density = np.mean(solver.particles.densities[:solver.n_active])
    print(f"✓ Average density: {avg_density:.1f} kg/m³")
    
    # Test force calculation
    solver.compute_forces()
    avg_force = np.mean(np.linalg.norm(solver.particles.forces[:solver.n_active], axis=1))
    print(f"✓ Average force magnitude: {avg_force:.3f} N")
    
    # Test time integration
    initial_pos = solver.particles.positions[0].copy()
    solver.step()
    final_pos = solver.particles.positions[0]
    distance_moved = np.linalg.norm(final_pos - initial_pos)
    print(f"✓ Particle moved {distance_moved:.6f} m in one step")
    
    # Test multiple steps
    for i in range(99):
        solver.step()
    print(f"✓ Completed 100 steps, time = {solver.time:.3f} s")
    
    # Test boundary conditions
    positions = solver.particles.positions[:solver.n_active]
    in_bounds = np.all((positions >= 0) & (positions <= solver.domain_size))
    assert in_bounds, "All particles should be within domain"
    print(f"✓ All particles within domain bounds")
    
    # Get simulation info
    info = solver.get_info()
    print(f"✓ Step {info['step']}: avg_vel={info['avg_velocity']:.3f} m/s")


def test_multi_fluid():
    """Test multiple fluids"""
    print_header("Testing Multiple Fluids")
    
    solver = SPHSolver(domain_size=(2.0, 2.0, 2.0))
    
    # Add water
    solver.add_fluid_box(
        position=(0.5, 0.0, 0.5),
        size=(1.0, 0.5, 1.0),
        n_particles=200,
        fluid_properties=FluidPreset.WATER
    )
    water_count = solver.n_active
    print(f"✓ Added {water_count} water particles")
    
    # Add oil
    solver.add_fluid_box(
        position=(0.5, 0.6, 0.5),
        size=(1.0, 0.5, 1.0),
        n_particles=200,
        fluid_properties=FluidPreset.OIL_LIGHT
    )
    oil_count = solver.n_active - water_count
    print(f"✓ Added {oil_count} oil particles")
    
    # Run simulation
    for i in range(50):
        solver.step()
    
    print(f"✓ Simulated {solver.step_count} steps with mixed fluids")


def run_all_tests():
    """Run all validation tests"""
    print("\n" + "=" * 60)
    print("  SPH FLUID SIMULATOR - VALIDATION SUITE")
    print("=" * 60)
    
    try:
        test_kernels()
        test_spatial_hash()
        test_fluid_presets()
        test_sph_solver()
        test_multi_fluid()
        
        print("\n" + "=" * 60)
        print("  ✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe SPH fluid simulator is working correctly.")
        print("\nNext steps:")
        print("  1. Install PyVista for visualization: pip install pyvista")
        print("  2. Run examples: python examples/01_basic_dam_break.py")
        print("  3. Try interactive sandbox: python examples/07_interactive_sandbox.py")
        print("\n")
        
        return True
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
