# Examples Gallery

This document showcases all available examples with usage instructions.

## 1. Dam Break

**File**: `examples/01_basic_dam_break.py`

**Description**: Classic SPH validation case. Water contained in a box is suddenly released and falls, demonstrating gravity and collision dynamics.

**Run**:
```bash
python examples/01_basic_dam_break.py
```

**Key Features**:
- 5,000 particles
- Velocity-based coloring
- Demonstrates boundary conditions
- Validation case from SPH literature

**Expected Behavior**: Water block collapses and spreads across the domain floor.

---

## 2. Pouring Liquid

**File**: `examples/02_pouring_liquid.py`

**Description**: Simulates liquid being poured from a height, creating splashes and waves.

**Run**:
```bash
python examples/02_pouring_liquid.py
```

**Key Features**:
- Taller domain (3m height)
- Stream of water falling
- Splash effects
- Velocity visualization

**Expected Behavior**: Water falls from top and splashes at bottom.

---

## 3. Mixing Fluids

**File**: `examples/03_mixing_fluids.py`

**Description**: Demonstrates interaction between two fluids with different properties (water and oil).

**Run**:
```bash
python examples/03_mixing_fluids.py
```

**Key Features**:
- Two fluid types (water + oil)
- Different densities
- Different colors
- 5,000 total particles

**Expected Behavior**: Oil (lighter) rises above water (denser) due to buoyancy.

---

## 4. Viscosity Comparison

**File**: `examples/04_viscosity_comparison.py`

**Description**: Side-by-side comparison of three fluids with different viscosities.

**Run**:
```bash
python examples/04_viscosity_comparison.py
```

**Key Features**:
- Three fluid columns (water, oil, honey)
- Same initial height
- Viscosity: 0.001, 0.1, 10.0 Pa·s
- 6,000 total particles

**Expected Behavior**: 
- Water flows quickly
- Oil flows moderately
- Honey flows very slowly

---

## 5. Rotating Tank

**File**: `examples/05_rotating_tank.py`

**Description**: Demonstrates external forces by applying centrifugal force to simulate a rotating reference frame.

**Run**:
```bash
python examples/05_rotating_tank.py
```

**Key Features**:
- Custom force addition
- Centrifugal force
- Reduced gravity for effect
- Pressure visualization

**Expected Behavior**: Water pushed outward by centrifugal force, creating a vortex-like pattern.

**Physics**: Shows how to add custom forces to the SPH framework.

---

## 6. Obstacle Flow

**File**: `examples/06_obstacle_flow.py`

**Description**: Water flows around a static obstacle, demonstrating collision detection.

**Run**:
```bash
python examples/06_obstacle_flow.py
```

**Key Features**:
- Static obstacle (red box)
- Collision handling
- Flow visualization
- 4,000 particles

**Expected Behavior**: Water flows around the obstacle, demonstrating basic obstacle collision.

---

## 7. Interactive Sandbox 🎮

**File**: `examples/07_interactive_sandbox.py`

**Description**: **Most interactive!** Add fluids in real-time with keyboard controls. Great for experimentation!

**Run**:
```bash
python examples/07_interactive_sandbox.py
```

**Controls**:
- `W` - Add water (blue, 500 particles)
- `O` - Add oil (golden, 300 particles)
- `H` - Add honey (yellow, very viscous, 200 particles)
- `R` - Reset simulation completely
- `SPACE` - Pause/Resume simulation
- `Q` - Quit

**Mouse Controls**:
- Left click + drag - Rotate view
- Scroll wheel - Zoom in/out
- Shift + Left click + drag - Pan view

**Key Features**:
- Real-time particle addition
- Multiple fluid types
- Pause/resume capability
- 3×3×3 meter domain

**Expected Behavior**: 
- Start with empty domain
- Add fluids dynamically
- Watch them interact in real-time

**Tips**:
- Add water first to fill the bottom
- Add oil on top to see separation
- Add honey to see slow viscous flow
- Experiment with different combinations!

---

## Running Tips

### All Examples

1. **Interactive Mode**: All examples open an interactive 3D window
2. **Rotation**: Left-click and drag to rotate view
3. **Zoom**: Use scroll wheel
4. **Exit**: Press `Q` to quit

### Performance

- Examples use 2,000-6,000 particles for good performance
- Reduce `n_particles` in code if too slow
- Increase for better visual quality (but slower)

### Customization

All examples can be easily modified:

```python
# Change particle count
n_particles=10000  # More particles

# Change domain size
domain_size=(5.0, 3.0, 2.0)  # Larger domain

# Change fluid type
fluid_properties=FluidPreset.HONEY  # Use honey instead

# Change visualization
color_by='pressure'  # Color by pressure instead of velocity
```

## Video Export

Any example can export video:

```python
# At the end of any example, before show_interactive():

from src.visualization.renderer import VideoExporter

exporter = VideoExporter(
    solver,
    filename='my_simulation.mp4',
    fps=30,
    quality=9
)

# Reset solver and run with export
solver.time = 0.0
solver.step_count = 0

exporter.export(
    duration=5.0,
    color_by='velocity',
    show_progress=True
)
```

## Creating Your Own Example

Template:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.sph_solver import SPHSolver
from src.visualization.renderer import SPHRenderer
from src.fluids.presets import FluidPreset

def main():
    # Create solver
    solver = SPHSolver(
        domain_size=(2.0, 2.0, 2.0),
        smoothing_length=0.05,
        time_step=0.001
    )
    
    # Add your fluid
    solver.add_fluid_box(
        position=(0.5, 0.5, 0.5),
        size=(1.0, 1.0, 1.0),
        n_particles=3000,
        fluid_properties=FluidPreset.WATER
    )
    
    # Create renderer
    renderer = SPHRenderer(solver)
    
    # Simulation callback
    def callback(solver, step):
        if step % 10 == 0:
            renderer.render_frame(color_by='velocity')
    
    # Run
    solver.run(duration=5.0, callback=callback)
    renderer.show_interactive()

if __name__ == "__main__":
    main()
```

## Troubleshooting

**Window doesn't open**: Check PyVista installation
```bash
pip install --upgrade pyvista
```

**Simulation crashes**: Reduce `n_particles` or increase `time_step`

**Too slow**: Reduce `n_particles` or increase rendering interval (`step % 20`)

**Particles explode**: Decrease `time_step` or increase `viscosity`
