"""
Example 6: Obstacle Flow

Water flows around obstacles in the domain
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.sph_solver import SPHSolver
from src.visualization.renderer import SPHRenderer
from src.fluids.presets import FluidPreset
import numpy as np


def main():
    """Run obstacle flow simulation"""
    print("=" * 60)
    print("SPH Fluid Simulation - Obstacle Flow")
    print("=" * 60)
    
    # Create solver
    print("\nInitializing solver...")
    solver = SPHSolver(
        domain_size=(3.0, 2.0, 1.5),
        smoothing_length=0.05,
        time_step=0.0005,
        particle_mass=0.02,
        rest_density=FluidPreset.WATER['rest_density'],
        gas_constant=FluidPreset.WATER['gas_constant'],
        viscosity=FluidPreset.WATER['viscosity']
    )
    
    # Add water block
    print("Adding water...")
    solver.add_fluid_box(
        position=(0.2, 0.5, 0.3),
        size=(0.8, 0.8, 0.9),
        n_particles=4000,
        fluid_properties=FluidPreset.WATER
    )
    
    print(f"Created {solver.n_active} particles")
    
    # Create renderer
    print("\nInitializing renderer...")
    renderer = SPHRenderer(solver, window_size=(1920, 1080))
    
    # Add obstacle visualization (simple box for now)
    try:
        import pyvista as pv
        obstacle_center = [1.5, 0.5, 0.75]
        obstacle_size = [0.3, 0.8, 0.3]
        
        bounds = [
            obstacle_center[0] - obstacle_size[0]/2,
            obstacle_center[0] + obstacle_size[0]/2,
            obstacle_center[1] - obstacle_size[1]/2,
            obstacle_center[1] + obstacle_size[1]/2,
            obstacle_center[2] - obstacle_size[2]/2,
            obstacle_center[2] + obstacle_size[2]/2
        ]
        
        obstacle = pv.Box(bounds=bounds)
        renderer.plotter.add_mesh(obstacle, color='red', opacity=0.7)
    except:
        pass
    
    renderer.add_text(
        "Obstacle Flow Simulation\nRed box = obstacle\nPress 'q' to exit",
        position='upper_left',
        font_size=14
    )
    
    # Simple obstacle collision (push particles away from obstacle)
    def apply_obstacle_collision(solver):
        """Simple obstacle collision - repel particles"""
        obstacle_center = np.array([1.5, 0.5, 0.75])
        obstacle_size = np.array([0.3, 0.8, 0.3])
        
        for i in range(solver.n_active):
            pos = solver.particles.positions[i]
            
            # Check if particle is inside obstacle
            diff = np.abs(pos - obstacle_center)
            
            if np.all(diff < obstacle_size / 2):
                # Push particle away
                direction = pos - obstacle_center
                if np.linalg.norm(direction) > 0.01:
                    direction = direction / np.linalg.norm(direction)
                else:
                    direction = np.array([1, 0, 0])
                
                # Move particle to surface
                for axis in range(3):
                    if abs(pos[axis] - obstacle_center[axis]) > obstacle_size[axis] / 2:
                        continue
                    
                    if pos[axis] > obstacle_center[axis]:
                        pos[axis] = obstacle_center[axis] + obstacle_size[axis] / 2 + 0.01
                    else:
                        pos[axis] = obstacle_center[axis] - obstacle_size[axis] / 2 - 0.01
                
                solver.particles.positions[i] = pos
                
                # Reflect velocity
                solver.particles.velocities[i] *= -0.5
    
    # Modify integrate to include obstacle collision
    original_integrate = solver.integrate
    
    def custom_integrate():
        original_integrate()
        apply_obstacle_collision(solver)
    
    solver.integrate = custom_integrate
    
    # Simulation callback
    def update_callback(solver, step):
        if step % 20 == 0:
            renderer.render_frame(color_by='velocity')
            
            if step % 200 == 0:
                info = solver.get_info()
                print(f"Step {step}: t={info['time']:.3f}s")
    
    # Run simulation
    print("\nRunning simulation...")
    print("Water flows around the obstacle!\n")
    
    solver.run(duration=8.0, callback=update_callback)
    renderer.show_interactive()
    
    print("\nSimulation complete!")


if __name__ == "__main__":
    main()
