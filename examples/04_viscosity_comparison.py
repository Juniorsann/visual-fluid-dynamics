"""
Example 4: Viscosity Comparison

Compare fluids with different viscosities side by side
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.sph_solver import SPHSolver
from src.visualization.renderer import SPHRenderer
from src.fluids.presets import FluidPreset


def main():
    """Run viscosity comparison simulation"""
    print("=" * 60)
    print("SPH Fluid Simulation - Viscosity Comparison")
    print("=" * 60)
    
    # Create solver
    print("\nInitializing solver...")
    solver = SPHSolver(
        domain_size=(4.0, 2.0, 1.5),
        smoothing_length=0.05,
        time_step=0.0005,
        particle_mass=0.02
    )
    
    # Add water (left, low viscosity)
    print("Adding water (low viscosity)...")
    solver.add_fluid_box(
        position=(0.2, 0.8, 0.3),
        size=(0.5, 0.8, 0.9),
        n_particles=2000,
        fluid_properties=FluidPreset.WATER
    )
    
    # Add oil (middle, medium viscosity)
    print("Adding oil (medium viscosity)...")
    solver.add_fluid_box(
        position=(1.5, 0.8, 0.3),
        size=(0.5, 0.8, 0.9),
        n_particles=2000,
        fluid_properties=FluidPreset.OIL_HEAVY
    )
    
    # Add honey (right, high viscosity)
    print("Adding honey (high viscosity)...")
    solver.add_fluid_box(
        position=(2.8, 0.8, 0.3),
        size=(0.5, 0.8, 0.9),
        n_particles=2000,
        fluid_properties=FluidPreset.HONEY
    )
    
    print(f"Created {solver.n_active} particles total")
    
    # Create renderer
    print("\nInitializing renderer...")
    renderer = SPHRenderer(solver, window_size=(1920, 1080))
    
    renderer.add_text(
        "Viscosity Comparison\n"
        "Left: Water (low) | Middle: Oil (medium) | Right: Honey (high)\n"
        "Press 'q' to exit",
        position='upper_left',
        font_size=12
    )
    
    # Simulation callback
    def update_callback(solver, step):
        if step % 20 == 0:
            renderer.render_frame(color_by='default')
            
            if step % 200 == 0:
                info = solver.get_info()
                print(f"Step {step}: t={info['time']:.3f}s")
    
    # Run simulation
    print("\nRunning simulation...")
    print("Notice how the different viscosities affect flow!\n")
    
    solver.run(duration=8.0, callback=update_callback)
    renderer.show_interactive()
    
    print("\nSimulation complete!")


if __name__ == "__main__":
    main()
