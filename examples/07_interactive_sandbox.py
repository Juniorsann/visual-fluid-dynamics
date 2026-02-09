"""
Example 7: Interactive Sandbox

Fully interactive mode - add fluids in real-time with keyboard controls
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.sph_solver import SPHSolver
from src.visualization.renderer import SPHRenderer
from src.fluids.presets import FluidPreset
import numpy as np


class InteractiveSandbox:
    """
    Interactive sandbox for SPH fluid simulation
    """
    
    def __init__(self):
        """Initialize sandbox"""
        print("=" * 60)
        print("SPH Interactive Sandbox")
        print("=" * 60)
        
        self.solver = SPHSolver(
            domain_size=(3.0, 3.0, 3.0),
            smoothing_length=0.05,
            time_step=0.0005
        )
        
        self.renderer = SPHRenderer(self.solver, window_size=(1920, 1080))
        
        # Setup controls
        self.setup_controls()
        
        # Simulation running flag
        self.running = True
        self.steps_per_frame = 10
    
    def setup_controls(self):
        """Setup keyboard controls"""
        
        # Add water
        def add_water():
            print("Adding water...")
            center = self.solver.domain_size / 2
            self.solver.add_fluid_box(
                position=center - [0.25, -1.5, 0.25],
                size=(0.5, 0.5, 0.5),
                n_particles=500,
                fluid_properties=FluidPreset.WATER
            )
            print(f"Total particles: {self.solver.n_active}")
        
        # Add oil
        def add_oil():
            print("Adding oil...")
            center = self.solver.domain_size / 2
            self.solver.add_fluid_box(
                position=center - [0.2, -1.5, 0.2],
                size=(0.4, 0.4, 0.4),
                n_particles=300,
                fluid_properties=FluidPreset.OIL_LIGHT
            )
            print(f"Total particles: {self.solver.n_active}")
        
        # Add honey
        def add_honey():
            print("Adding honey...")
            center = self.solver.domain_size / 2
            self.solver.add_fluid_box(
                position=center - [0.15, -1.5, 0.15],
                size=(0.3, 0.3, 0.3),
                n_particles=200,
                fluid_properties=FluidPreset.HONEY
            )
            print(f"Total particles: {self.solver.n_active}")
        
        # Reset simulation
        def reset():
            print("Resetting simulation...")
            self.solver = SPHSolver(
                domain_size=(3.0, 3.0, 3.0),
                smoothing_length=0.05,
                time_step=0.0005
            )
            self.renderer.solver = self.solver
            print("Simulation reset!")
        
        # Toggle pause
        def toggle_pause():
            self.running = not self.running
            status = "resumed" if self.running else "paused"
            print(f"Simulation {status}")
        
        # Add keyboard callbacks
        self.renderer.plotter.add_key_event('w', add_water)
        self.renderer.plotter.add_key_event('o', add_oil)
        self.renderer.plotter.add_key_event('h', add_honey)
        self.renderer.plotter.add_key_event('r', reset)
        self.renderer.plotter.add_key_event('space', toggle_pause)
        
        # Add control instructions
        self.renderer.add_text(
            "Controls:\n"
            "W - Add Water\n"
            "O - Add Oil\n"
            "H - Add Honey\n"
            "R - Reset\n"
            "SPACE - Pause/Resume\n"
            "Q - Quit",
            position='upper_left',
            font_size=12
        )
    
    def update_callback(self):
        """Update callback for timer"""
        if self.running and self.solver.n_active > 0:
            # Simulate several steps
            for _ in range(self.steps_per_frame):
                self.solver.step()
        
        # Update visualization
        if self.solver.n_active > 0:
            self.renderer.update_particles(color_by='default')
    
    def run(self):
        """Run interactive sandbox"""
        print("\n" + "=" * 60)
        print("Interactive Controls:")
        print("  W - Add Water")
        print("  O - Add Oil")
        print("  H - Add Honey")
        print("  R - Reset simulation")
        print("  SPACE - Pause/Resume")
        print("  Q - Quit")
        print("\nMouse Controls:")
        print("  Left click + drag - Rotate view")
        print("  Scroll wheel - Zoom")
        print("  Shift + Left click - Pan")
        print("=" * 60)
        print("\nStarting interactive mode...")
        print("Try pressing W to add some water!\n")
        
        # Add timer for continuous updates (60 FPS)
        self.renderer.plotter.add_timer_event(
            max_steps=None,
            duration=16,  # ~60 FPS
            callback=self.update_callback
        )
        
        # Show window
        self.renderer.plotter.show()
        
        print("\nSandbox closed!")


def main():
    """Run interactive sandbox"""
    sandbox = InteractiveSandbox()
    sandbox.run()


if __name__ == "__main__":
    main()
