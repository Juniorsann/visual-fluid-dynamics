"""
Visual Fluid Dynamics - 3D Interactive Fluid Simulator using SPH

This package provides a complete implementation of Smoothed Particle Hydrodynamics (SPH)
for simulating fluid dynamics in 3D with real-time visualization.
"""

__version__ = "0.1.0"
__author__ = "Juniorsann"

from .core.sph_solver import SPHSolver
from .fluids.presets import FluidPreset
from .visualization.renderer import SPHRenderer

__all__ = [
    "SPHSolver",
    "FluidPreset",
    "SPHRenderer",
]
