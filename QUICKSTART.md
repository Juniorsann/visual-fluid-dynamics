# Quick Start Guide

Welcome to the Visual Fluid Dynamics SPH Simulator! This guide will get you running in minutes.

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Juniorsann/visual-fluid-dynamics.git
cd visual-fluid-dynamics
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

**Required packages:**
- numpy (numerical computing)
- scipy (scientific computing)
- pyvista (3D visualization) *
- matplotlib (plotting/colormaps)
- imageio + imageio-ffmpeg (video export)
- pyyaml (configuration files)
- tqdm (progress bars)

\* PyVista requires a display. For headless servers, use off-screen rendering.

### 3. Verify Installation
```bash
python validate.py
```

You should see:
```
✓ ALL TESTS PASSED!
```

## Your First Simulation

### Option 1: Dam Break (Classic Example)

```bash
python examples/01_basic_dam_break.py
```

This will:
1. Create a 3D domain (3m × 2m × 1m)
2. Add 5,000 water particles in a "dam"
3. Simulate the dam breaking and water falling
4. Open an interactive 3D window

**Controls:**
- Rotate: Left-click + drag
- Zoom: Scroll wheel
- Pan: Shift + left-click + drag
- Quit: Press 'Q'

### Option 2: Interactive Sandbox (Most Fun!)

```bash
python examples/07_interactive_sandbox.py
```

**Keyboard controls:**
- `W` - Add water
- `O` - Add oil
- `H` - Add honey
- `R` - Reset
- `SPACE` - Pause/Resume
- `Q` - Quit

Try adding water, then oil on top to see density separation!

## Simple Python Example

Create a file `my_simulation.py`:

```python
from src.core.sph_solver import SPHSolver
from src.visualization.renderer import SPHRenderer
from src.fluids.presets import FluidPreset

# Create solver
solver = SPHSolver(
    domain_size=(2.0, 2.0, 2.0),  # 2m cube
    smoothing_length=0.05,         # 5cm influence radius
    time_step=0.001                # 1ms time step
)

# Add water
solver.add_fluid_box(
    position=(0.5, 0.5, 0.5),
    size=(1.0, 1.0, 1.0),
    n_particles=3000,
    fluid_properties=FluidPreset.WATER
)

# Visualize
renderer = SPHRenderer(solver)

def callback(solver, step):
    if step % 10 == 0:  # Update every 10 steps
        renderer.render_frame(color_by='velocity')

# Run for 5 seconds
solver.run(duration=5.0, callback=callback)
renderer.show_interactive()
```

Run it:
```bash
python my_simulation.py
```

## Exploring Examples

All examples are in `examples/`:

1. **01_basic_dam_break.py** - Dam break validation
2. **02_pouring_liquid.py** - Pouring from height
3. **03_mixing_fluids.py** - Water + oil mixing
4. **04_viscosity_comparison.py** - Compare fluids
5. **05_rotating_tank.py** - Rotating reference frame
6. **06_obstacle_flow.py** - Flow around obstacles
7. **07_interactive_sandbox.py** - Interactive mode

Try them all:
```bash
python examples/01_basic_dam_break.py
python examples/03_mixing_fluids.py
python examples/07_interactive_sandbox.py
```

## Available Fluids

Access via `FluidPreset`:

```python
from src.fluids.presets import FluidPreset

# Use preset
solver.add_fluid_box(..., fluid_properties=FluidPreset.WATER)
solver.add_fluid_box(..., fluid_properties=FluidPreset.HONEY)
solver.add_fluid_box(..., fluid_properties=FluidPreset.OIL_LIGHT)

# List all presets
print(FluidPreset.list_presets())
# ['WATER', 'OIL_LIGHT', 'OIL_MEDIUM', 'OIL_HEAVY', 
#  'HONEY', 'GLYCERIN', 'MERCURY', 'MILK', 'BLOOD']
```

## Export Video

Add to any example:

```python
from src.visualization.renderer import VideoExporter

# Create exporter
exporter = VideoExporter(
    solver,
    filename='my_video.mp4',
    fps=30,
    quality=9
)

# Export
exporter.export(
    duration=10.0,
    color_by='velocity',
    show_progress=True
)
```

Output: `my_video.mp4` (60 FPS, high quality)

## Customization

### Change Particle Count
```python
n_particles=10000  # More particles = better quality, slower
```

### Change Domain Size
```python
domain_size=(5.0, 3.0, 2.0)  # Larger domain
```

### Change Time Step
```python
time_step=0.0005  # Smaller = more stable, slower
```

### Color by Property
```python
renderer.render_frame(color_by='velocity')  # Speed
renderer.render_frame(color_by='pressure')  # Pressure
renderer.render_frame(color_by='density')   # Density
renderer.render_frame(color_by='default')   # Particle color
```

## Troubleshooting

### "PyVista not available"
Install PyVista:
```bash
pip install pyvista
```

### Window doesn't open
- Check if you have a display
- For servers, use `off_screen=True`:
```python
renderer = SPHRenderer(solver, off_screen=True)
```

### Simulation is slow
- Reduce `n_particles` (try 1000-2000)
- Increase `time_step` (try 0.002)
- Increase rendering interval:
```python
if step % 20 == 0:  # Render every 20 steps
    renderer.render_frame()
```

### Particles "explode"
- Decrease `time_step` (try 0.0005)
- Increase `viscosity`
- Decrease `gas_constant`

### Simulation looks wrong
- Check domain size vs particle positions
- Verify fluid properties are realistic
- Ensure enough particles for density

## Next Steps

1. **Read the docs**: See `docs/` for detailed guides
2. **Run tests**: `pytest tests/` (requires pytest)
3. **Experiment**: Modify examples
4. **Create**: Build your own scenarios
5. **Learn**: Study the SPH theory in `docs/theory.md`

## Getting Help

- **Documentation**: `docs/`
- **Examples**: `examples/`
- **Tests**: `tests/`
- **Code**: `src/`

## Performance Tips

- Start with 1,000-2,000 particles
- Use `h = 0.05` (good balance)
- Use `dt = 0.001` (stable)
- Render every 10-20 steps
- Check `docs/performance.md` for more

## Have Fun!

The interactive sandbox (`examples/07_interactive_sandbox.py`) is the best way to explore. Start there!

```bash
python examples/07_interactive_sandbox.py
```

Press 'W' to add water and watch the physics in action! 🌊
