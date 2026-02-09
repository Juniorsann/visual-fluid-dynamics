# SPH Theory and Equations

## Introduction to Smoothed Particle Hydrodynamics

Smoothed Particle Hydrodynamics (SPH) is a computational method used for simulating fluid flows. Unlike grid-based methods (like Finite Difference or Finite Element), SPH is a **Lagrangian meshless method** where the fluid is represented by discrete particles.

## Core Concepts

### 1. Particle Representation

Each particle carries:
- Position **r**
- Velocity **v**
- Mass **m**
- Density **ρ**
- Pressure **P**
- Other properties (temperature, color, etc.)

### 2. Kernel Functions

Properties are interpolated using **kernel functions** W(r, h):

```
f(r) = Σⱼ mⱼ/ρⱼ f(rⱼ) W(r - rⱼ, h)
```

Where:
- **f** is any property
- **h** is the smoothing length (radius of influence)
- **W** is a smooth, decreasing function

### 3. Kernel Types

#### Poly6 Kernel (for density)
```
W(r, h) = (315/(64πh⁹)) × (h² - r²)³  if r ≤ h
        = 0                           if r > h
```

#### Spiky Kernel Gradient (for pressure)
```
∇W(r, h) = -(45/(πh⁶)) × (h - r)² × r/|r|  if r ≤ h
         = 0                                if r > h
```

#### Viscosity Kernel Laplacian
```
∇²W(r, h) = (45/(πh⁶)) × (h - r)  if r ≤ h
          = 0                      if r > h
```

## SPH Equations

### 1. Density Calculation

```
ρᵢ = Σⱼ mⱼ W(rᵢ - rⱼ, h)
```

This computes the density at particle i by summing contributions from all neighbors j.

### 2. Pressure

Using the equation of state:

```
P = k(ρ - ρ₀)
```

Where:
- **k** is the gas constant (stiffness)
- **ρ₀** is the rest density

### 3. Pressure Force

```
Fᵢᵖʳᵉˢˢᵘʳᵉ = -Σⱼ mⱼ (Pᵢ + Pⱼ)/(2ρⱼ) ∇W(rᵢ - rⱼ, h)
```

This symmetrized formulation ensures momentum conservation.

### 4. Viscosity Force

```
Fᵢᵛⁱˢᶜᵒˢⁱᵗʸ = μ Σⱼ mⱼ (vⱼ - vᵢ)/ρⱼ ∇²W(rᵢ - rⱼ, h)
```

Where **μ** is the dynamic viscosity coefficient.

### 5. External Forces

```
Fᵢᵉˣᵗᵉʳⁿᵃˡ = mᵢ g
```

Typically gravity, but can include other forces.

### 6. Time Integration

Semi-implicit Euler (simplified Velocity Verlet):

```
vᵢ(t+Δt) = vᵢ(t) + (Fᵢ(t)/mᵢ) × Δt
xᵢ(t+Δt) = xᵢ(t) + vᵢ(t+Δt) × Δt
```

## Boundary Conditions

### Wall Collision

When a particle hits a wall:
1. Position clamped to domain
2. Velocity reflected with damping

```python
if pos[i] < 0:
    pos[i] = 0
    vel[i] = abs(vel[i]) * damping
```

## Spatial Optimization

### Spatial Hash Grid

To avoid O(N²) neighbor search, we use a **spatial hash grid**:

1. Divide space into cells of size h
2. Hash particles into cells: `(i, j, k) = floor(pos / h)`
3. For neighbors, only check 27 adjacent cells (3×3×3)

This reduces complexity to **O(N)**.

## Stability Considerations

### Time Step

The CFL condition requires:

```
Δt ≤ 0.25 × h / vₘₐₓ
```

Smaller time steps = more stable but slower.

### Smoothing Length

Typical values:
- **h = 2-3 × particle spacing**
- Too small: noisy, unstable
- Too large: over-smoothed, slow

## Parameters

Typical values for water:
- Density: ρ₀ = 1000 kg/m³
- Viscosity: μ = 0.001 Pa·s
- Gas constant: k = 2000
- Smoothing length: h = 0.05 m
- Time step: Δt = 0.0005 s
- Particle mass: m = 0.02 kg

## References

1. Müller, M., Charypar, D., & Gross, M. (2003). "Particle-based fluid simulation for interactive applications." SCA 2003.

2. Monaghan, J. J. (2005). "Smoothed particle hydrodynamics." Reports on Progress in Physics.

3. Becker, M., & Teschner, M. (2007). "Weakly compressible SPH for free surface flows." SCA 2007.
