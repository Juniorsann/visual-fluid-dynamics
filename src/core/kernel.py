"""
SPH Kernel functions for density, pressure, and viscosity calculations
"""
import numpy as np


class SPHKernel:
    """
    SPH kernel functions (Poly6, Spiky, Viscosity)
    
    These kernels are used to interpolate properties between particles
    based on their distance.
    """
    
    @staticmethod
    def poly6(r, h):
        """
        Poly6 kernel (used for density calculation)
        
        W(r,h) = (315/(64πh⁹)) × (h² - r²)³  if r ≤ h
               = 0                           if r > h
        
        Args:
            r: distance vector or scalar distance
            h: smoothing length
        
        Returns:
            Kernel value
        """
        if isinstance(r, np.ndarray) and r.ndim > 0:
            r_norm = np.linalg.norm(r)
        else:
            r_norm = abs(r)
        
        if r_norm > h:
            return 0.0
        
        coef = 315.0 / (64.0 * np.pi * h**9)
        return coef * (h**2 - r_norm**2)**3
    
    @staticmethod
    def poly6_gradient(r, h):
        """
        Gradient of Poly6 kernel
        
        Args:
            r: distance vector [x, y, z]
            h: smoothing length
        
        Returns:
            Gradient vector
        """
        r_norm = np.linalg.norm(r)
        
        if r_norm > h or r_norm < 1e-6:
            return np.zeros(3, dtype=np.float32)
        
        coef = -945.0 / (32.0 * np.pi * h**9)
        return coef * (h**2 - r_norm**2)**2 * r
    
    @staticmethod
    def spiky_gradient(r, h):
        """
        Gradient of Spiky kernel (used for pressure force)
        
        ∇W(r,h) = -(45/(πh⁶)) × (h - r)² × r/|r|  if r ≤ h
                = 0                                if r > h
        
        This kernel has better gradient properties for pressure calculation
        
        Args:
            r: distance vector [x, y, z]
            h: smoothing length
        
        Returns:
            Gradient vector
        """
        r_norm = np.linalg.norm(r)
        
        if r_norm > h or r_norm < 1e-6:
            return np.zeros(3, dtype=np.float32)
        
        coef = -45.0 / (np.pi * h**6)
        return coef * (h - r_norm)**2 * r / r_norm
    
    @staticmethod
    def viscosity_laplacian(r, h):
        """
        Laplacian of viscosity kernel (used for viscosity force)
        
        ∇²W(r,h) = (45/(πh⁶)) × (h - r)  if r ≤ h
                 = 0                      if r > h
        
        Args:
            r: distance vector or scalar distance
            h: smoothing length
        
        Returns:
            Laplacian value
        """
        if isinstance(r, np.ndarray) and r.ndim > 0:
            r_norm = np.linalg.norm(r)
        else:
            r_norm = abs(r)
        
        if r_norm > h:
            return 0.0
        
        coef = 45.0 / (np.pi * h**6)
        return coef * (h - r_norm)


class VectorizedKernels:
    """
    Vectorized versions of kernels for processing multiple particles at once
    
    These provide better performance when computing kernel values for
    many particle pairs simultaneously.
    """
    
    @staticmethod
    def poly6_vectorized(r_vectors, h):
        """
        Vectorized Poly6 kernel calculation
        
        Args:
            r_vectors: (N, 3) array of distance vectors
            h: smoothing length
        
        Returns:
            (N,) array of kernel values
        """
        r_norms = np.linalg.norm(r_vectors, axis=1)
        
        coef = 315.0 / (64.0 * np.pi * h**9)
        
        # Compute kernel values
        values = np.zeros(len(r_norms), dtype=np.float32)
        mask = r_norms <= h
        
        values[mask] = coef * (h**2 - r_norms[mask]**2)**3
        
        return values
    
    @staticmethod
    def spiky_gradient_vectorized(r_vectors, h):
        """
        Vectorized Spiky gradient calculation
        
        Args:
            r_vectors: (N, 3) array of distance vectors
            h: smoothing length
        
        Returns:
            (N, 3) array of gradient vectors
        """
        r_norms = np.linalg.norm(r_vectors, axis=1, keepdims=True)
        
        coef = -45.0 / (np.pi * h**6)
        
        # Compute gradients
        gradients = np.zeros_like(r_vectors, dtype=np.float32)
        mask = (r_norms.squeeze() <= h) & (r_norms.squeeze() > 1e-6)
        
        if np.any(mask):
            gradients[mask] = coef * (h - r_norms[mask].squeeze())**2 * r_vectors[mask] / r_norms[mask]
        
        return gradients
    
    @staticmethod
    def viscosity_laplacian_vectorized(r_vectors, h):
        """
        Vectorized viscosity Laplacian calculation
        
        Args:
            r_vectors: (N, 3) array of distance vectors
            h: smoothing length
        
        Returns:
            (N,) array of Laplacian values
        """
        r_norms = np.linalg.norm(r_vectors, axis=1)
        
        coef = 45.0 / (np.pi * h**6)
        
        # Compute Laplacian values
        values = np.zeros(len(r_norms), dtype=np.float32)
        mask = r_norms <= h
        
        values[mask] = coef * (h - r_norms[mask])
        
        return values
