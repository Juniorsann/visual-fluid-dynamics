# User Guide

## Getting Started

### Installation

```bash
pip install -r requirements.txt
```

### Your First Simulation

```python
from src.core.sph_solver import SPHSolver
from src.visualization.renderer import SPHRenderer
from src.fluids.presets import FluidPreset

# Create solver
solver = SPHSolver(
    domain_size=(2.0, 2.0, 2.0),
    smoothing_length=0.05
)

# Add fluid
solver.add_fluid_box(
    position=(0.5, 0.5, 0.5),
    size=(1.0, 1.0, 1.0),
    n_particles=5000,
    fluid_properties=FluidPreset.WATER
)

# Visualize
renderer = SPHRenderer(solver)

def callback(solver, step):
    if step % 10 == 0:
        renderer.render_frame()

solver.run(duration=5.0, callback=callback)
renderer.show_interactive()
```

## SPH Solver Parameters

### domain_size
Size of simulation box (meters). Example: `(2.0, 2.0, 2.0)`

### smoothing_length
Radius of influence for SPH kernels. Larger = smoother but less accurate.
Typical: 0.04-0.06 m

### particle_mass
Mass of each particle (kg). Affects density calculation.
Typical: 0.01-0.05 kg

### time_step
Integration time step (seconds). Smaller = more stable but slower.
Typical: 0.0005-0.002 s

### rest_density
Rest density of fluid (kg/m³). Water = 1000

### gas_constant
Pressure stiffness. Higher = less compressible but may need smaller time step.
Typical: 1500-3000

### viscosity
Dynamic viscosity (Pa·s). Water ≈ 0.001, Honey ≈ 10

## Adding Fluids

### Fluid Box
```python
solver.add_fluid_box(
    position=(x, y, z),      # Bottom corner
    size=(w, h, d),          # Dimensions
    n_particles=5000,        # Particle count
    fluid_properties=FluidPreset.WATER
)
```

### Custom Fluid
```python
my_fluid = {
    'density': 1200.0,
    'viscosity': 0.05,
    'color': (1.0, 0.5, 0.0),
    'gas_constant': 2000.0,
    'rest_density': 1200.0
}
```

## Visualization

### Color Modes

```python
renderer.render_frame(color_by='default')   # Use particle colors
renderer.render_frame(color_by='velocity')  # Color by speed
renderer.render_frame(color_by='pressure')  # Color by pressure
renderer.render_frame(color_by='density')   # Color by density
```

### Camera Control

```python
renderer.set_camera(
    position=[5, 5, 5],
    focal_point=[1, 1, 1],
    viewup=[0, 1, 0]
)
```

## Video Export

```python
from src.visualization.renderer import VideoExporter

exporter = VideoExporter(solver, filename='output.mp4', fps=30)
exporter.export(duration=10.0, color_by='velocity')
```

## Tips

1. Start with fewer particles (1000-2000) for testing
2. Increase smoothing_length if simulation is unstable
3. Decrease time_step if particles are "exploding"
4. Use spatial hash grid (automatically enabled) for performance

## Troubleshooting

**Particles explode**: Reduce time_step or increase viscosity

**Simulation too slow**: Reduce particle count or increase smoothing_length

**Fluids don't interact**: Check that particles overlap initially

**Render window doesn't open**: Install PyVista properly
