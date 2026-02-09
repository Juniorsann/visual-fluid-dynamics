"""
Example 1: Basic Dam Break

Classic SPH validation case.
Water contained in a box is released and falls.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.sph_solver import SPHSolver
from src.visualization.renderer import SPHRenderer, VideoExporter
from src.fluids.presets import FluidPreset


def main():
    """Run dam break simulation"""
    print("=" * 60)
    print("SPH Fluid Simulation - Dam Break Example")
    print("=" * 60)
    
    # Create solver
    print("\nInitializing solver...")
    solver = SPHSolver(
        domain_size=(3.0, 2.0, 1.0),  # 3m x 2m x 1m
        smoothing_length=0.05,
        time_step=0.0005,
        particle_mass=0.02,
        rest_density=FluidPreset.WATER['rest_density'],
        gas_constant=FluidPreset.WATER['gas_constant'],
        viscosity=FluidPreset.WATER['viscosity']
    )
    
    # Add water block (left side - dam)
    print("Adding fluid particles...")
    solver.add_fluid_box(
        position=(0.2, 0.0, 0.1),
        size=(0.6, 1.0, 0.8),
        n_particles=5000,
        fluid_properties=FluidPreset.WATER
    )
    
    print(f"Created {solver.n_active} particles")
    
    # Create renderer
    print("\nInitializing renderer...")
    renderer = SPHRenderer(solver, window_size=(1920, 1080))
    
    # Add info text
    renderer.add_text(
        "Dam Break Simulation\nPress 'q' to exit",
        position='upper_left',
        font_size=14
    )
    
    # Simulation callback
    def update_callback(solver, step):
        if step % 10 == 0:  # Update every 10 steps
            renderer.render_frame(color_by='velocity')
            
            # Print progress
            if step % 100 == 0:
                info = solver.get_info()
                print(f"Step {step}: t={info['time']:.3f}s, "
                      f"avg_vel={info['avg_velocity']:.3f} m/s")
    
    # Run simulation
    print("\nRunning simulation...")
    print("Rotate view: Left click + drag")
    print("Zoom: Scroll wheel")
    print("Pan: Shift + Left click + drag")
    print("Press 'q' to exit\n")
    
    # Run for 5 seconds
    solver.run(duration=5.0, callback=update_callback)
    
    # Show interactive window
    renderer.show_interactive()
    
    print("\nSimulation complete!")


if __name__ == "__main__":
    main()
