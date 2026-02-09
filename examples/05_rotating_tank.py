"""
Example 5: Rotating Tank

Water in a rotating reference frame - demonstrates external forces
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.sph_solver import SPHSolver
from src.visualization.renderer import SPHRenderer
from src.fluids.presets import FluidPreset
import numpy as np


def main():
    """Run rotating tank simulation"""
    print("=" * 60)
    print("SPH Fluid Simulation - Rotating Tank")
    print("=" * 60)
    
    # Create solver with reduced gravity (for dramatic effect)
    print("\nInitializing solver...")
    solver = SPHSolver(
        domain_size=(2.0, 2.0, 2.0),
        smoothing_length=0.05,
        time_step=0.0005,
        particle_mass=0.02,
        gravity=(0, -2.0, 0),  # Reduced gravity
        rest_density=FluidPreset.WATER['rest_density'],
        gas_constant=FluidPreset.WATER['gas_constant'],
        viscosity=FluidPreset.WATER['viscosity']
    )
    
    # Add water in center
    print("Adding water...")
    solver.add_fluid_box(
        position=(0.6, 0.0, 0.6),
        size=(0.8, 0.8, 0.8),
        n_particles=4000,
        fluid_properties=FluidPreset.WATER
    )
    
    print(f"Created {solver.n_active} particles")
    
    # Create renderer
    print("\nInitializing renderer...")
    renderer = SPHRenderer(solver, window_size=(1920, 1080))
    
    renderer.add_text(
        "Rotating Tank Simulation\nPress 'q' to exit",
        position='upper_left',
        font_size=14
    )
    
    # Add centrifugal force
    def add_centrifugal_force(solver, angular_velocity=2.0):
        """Add centrifugal force to simulate rotation"""
        center = solver.domain_size / 2
        omega = angular_velocity
        
        for i in range(solver.n_active):
            pos = solver.particles.positions[i]
            r_vec = pos - center
            r_vec[1] = 0  # Only horizontal distance
            
            # Centrifugal force: F = m * ω² * r
            if np.linalg.norm(r_vec) > 0.01:
                centrifugal = solver.particles.masses[i] * omega**2 * r_vec
                solver.particles.forces[i] += centrifugal
    
    # Custom step function
    original_compute_forces = solver.compute_forces
    
    def custom_compute_forces():
        original_compute_forces()
        add_centrifugal_force(solver, angular_velocity=1.5)
    
    solver.compute_forces = custom_compute_forces
    
    # Simulation callback
    def update_callback(solver, step):
        if step % 20 == 0:
            renderer.render_frame(color_by='pressure')
            
            if step % 200 == 0:
                info = solver.get_info()
                print(f"Step {step}: t={info['time']:.3f}s")
    
    # Run simulation
    print("\nRunning simulation...")
    print("Centrifugal force pushes water outward!\n")
    
    solver.run(duration=8.0, callback=update_callback)
    renderer.show_interactive()
    
    print("\nSimulation complete!")


if __name__ == "__main__":
    main()
