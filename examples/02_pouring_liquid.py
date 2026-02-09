"""
Example 2: Pouring Liquid

Simulates liquid being poured from a height into a container
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.sph_solver import SPHSolver
from src.visualization.renderer import SPHRenderer
from src.fluids.presets import FluidPreset


def main():
    """Run pouring liquid simulation"""
    print("=" * 60)
    print("SPH Fluid Simulation - Pouring Liquid Example")
    print("=" * 60)
    
    # Create solver
    print("\nInitializing solver...")
    solver = SPHSolver(
        domain_size=(2.0, 3.0, 2.0),
        smoothing_length=0.05,
        time_step=0.0005,
        particle_mass=0.02,
        rest_density=FluidPreset.WATER['rest_density'],
        gas_constant=FluidPreset.WATER['gas_constant'],
        viscosity=FluidPreset.WATER['viscosity']
    )
    
    # Add water "stream" from top
    print("Adding water stream...")
    solver.add_fluid_box(
        position=(0.8, 2.0, 0.8),
        size=(0.4, 0.8, 0.4),
        n_particles=3000,
        fluid_properties=FluidPreset.WATER
    )
    
    print(f"Created {solver.n_active} particles")
    
    # Create renderer
    print("\nInitializing renderer...")
    renderer = SPHRenderer(solver, window_size=(1920, 1080))
    
    renderer.add_text(
        "Pouring Liquid Simulation\nPress 'q' to exit",
        position='upper_left',
        font_size=14
    )
    
    # Simulation callback
    def update_callback(solver, step):
        if step % 15 == 0:
            renderer.render_frame(color_by='velocity')
            
            if step % 200 == 0:
                info = solver.get_info()
                print(f"Step {step}: t={info['time']:.3f}s, "
                      f"max_vel={info['max_velocity']:.2f} m/s")
    
    # Run simulation
    print("\nRunning simulation...")
    print("Watch the water pour and splash!\n")
    
    solver.run(duration=6.0, callback=update_callback)
    renderer.show_interactive()
    
    print("\nSimulation complete!")


if __name__ == "__main__":
    main()
