"""
Example 3: Mixing Fluids

Demonstrates interaction between water and oil (different densities and viscosities)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.sph_solver import SPHSolver
from src.visualization.renderer import SPHRenderer
from src.fluids.presets import FluidPreset


def main():
    """Run fluid mixing simulation"""
    print("=" * 60)
    print("SPH Fluid Simulation - Mixing Fluids Example")
    print("=" * 60)
    
    # Create solver
    print("\nInitializing solver...")
    solver = SPHSolver(
        domain_size=(2.0, 2.0, 2.0),
        smoothing_length=0.05,
        time_step=0.0005,
        particle_mass=0.02
    )
    
    # Add water (bottom layer)
    print("Adding water particles...")
    solver.add_fluid_box(
        position=(0.5, 0.0, 0.5),
        size=(1.0, 0.5, 1.0),
        n_particles=3000,
        fluid_properties=FluidPreset.WATER
    )
    
    # Add oil (top layer)
    print("Adding oil particles...")
    solver.add_fluid_box(
        position=(0.5, 0.6, 0.5),
        size=(1.0, 0.5, 1.0),
        n_particles=2000,
        fluid_properties=FluidPreset.OIL_LIGHT
    )
    
    print(f"Created {solver.n_active} particles total")
    
    # Create renderer
    print("\nInitializing renderer...")
    renderer = SPHRenderer(solver, window_size=(1920, 1080))
    
    renderer.add_text(
        "Fluid Mixing: Water (blue) + Oil (golden)\nPress 'q' to exit",
        position='upper_left',
        font_size=14
    )
    
    # Simulation callback
    def update_callback(solver, step):
        if step % 20 == 0:  # Update every 20 steps
            renderer.render_frame(color_by='default')
            
            if step % 200 == 0:
                info = solver.get_info()
                print(f"Step {step}: t={info['time']:.3f}s, "
                      f"avg_density={info['avg_density']:.1f} kg/m³")
    
    # Run simulation
    print("\nRunning simulation...")
    print("Watch how water and oil interact due to different densities!")
    print("Press 'q' to exit\n")
    
    solver.run(duration=10.0, callback=update_callback)
    
    # Show interactive window
    renderer.show_interactive()
    
    print("\nSimulation complete!")


if __name__ == "__main__":
    main()
