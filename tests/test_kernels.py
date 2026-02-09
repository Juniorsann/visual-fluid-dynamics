"""
Unit tests for SPH kernels
"""
import pytest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.kernel import SPHKernel, VectorizedKernels


class TestSPHKernels:
    """Test SPH kernel functions"""
    
    def test_poly6_at_zero(self):
        """Test Poly6 kernel at r=0"""
        kernel = SPHKernel()
        h = 0.1
        
        # At r=0, kernel should be maximum
        value_zero = kernel.poly6(0.0, h)
        
        # Should be positive
        assert value_zero > 0
        
        # At r=h/2, should be less than at zero
        value_half = kernel.poly6(np.array([h/2, 0, 0]), h)
        assert value_half < value_zero
    
    def test_poly6_beyond_h(self):
        """Test that Poly6 is zero beyond smoothing length"""
        kernel = SPHKernel()
        h = 0.1
        
        # Beyond h, should be zero
        value = kernel.poly6(np.array([h + 0.01, 0, 0]), h)
        assert value == 0.0
    
    def test_poly6_symmetry(self):
        """Test that Poly6 is symmetric"""
        kernel = SPHKernel()
        h = 0.1
        
        r1 = np.array([0.05, 0, 0])
        r2 = np.array([-0.05, 0, 0])
        
        value1 = kernel.poly6(r1, h)
        value2 = kernel.poly6(r2, h)
        
        assert np.isclose(value1, value2)
    
    def test_spiky_gradient_at_zero(self):
        """Test Spiky gradient at r=0"""
        kernel = SPHKernel()
        h = 0.1
        
        # At r=0, gradient should be zero (singularity handled)
        grad = kernel.spiky_gradient(np.zeros(3), h)
        assert np.allclose(grad, [0, 0, 0])
    
    def test_spiky_gradient_direction(self):
        """Test that Spiky gradient points away from center"""
        kernel = SPHKernel()
        h = 0.1
        
        r = np.array([0.05, 0, 0])
        grad = kernel.spiky_gradient(r, h)
        
        # Gradient should point in direction of r
        # (negative because of spiky kernel formulation)
        assert grad[0] < 0
        assert np.isclose(grad[1], 0)
        assert np.isclose(grad[2], 0)
    
    def test_spiky_gradient_beyond_h(self):
        """Test Spiky gradient is zero beyond h"""
        kernel = SPHKernel()
        h = 0.1
        
        r = np.array([h + 0.01, 0, 0])
        grad = kernel.spiky_gradient(r, h)
        
        assert np.allclose(grad, [0, 0, 0])
    
    def test_viscosity_laplacian_positive(self):
        """Test that viscosity Laplacian is positive within h"""
        kernel = SPHKernel()
        h = 0.1
        
        r = np.array([0.05, 0, 0])
        lap = kernel.viscosity_laplacian(r, h)
        
        # Should be positive within smoothing length
        assert lap > 0
    
    def test_viscosity_laplacian_beyond_h(self):
        """Test viscosity Laplacian is zero beyond h"""
        kernel = SPHKernel()
        h = 0.1
        
        r = np.array([h + 0.01, 0, 0])
        lap = kernel.viscosity_laplacian(r, h)
        
        assert lap == 0.0
    
    def test_vectorized_poly6(self):
        """Test vectorized Poly6 kernel"""
        vkernels = VectorizedKernels()
        h = 0.1
        
        # Multiple distance vectors
        r_vectors = np.array([
            [0.0, 0.0, 0.0],
            [0.05, 0.0, 0.0],
            [0.1, 0.0, 0.0],
            [0.15, 0.0, 0.0]
        ])
        
        values = vkernels.poly6_vectorized(r_vectors, h)
        
        # Check shape
        assert len(values) == 4
        
        # First should be maximum
        assert values[0] > values[1]
        
        # At h, should be zero
        assert values[2] == 0.0
        
        # Beyond h, should be zero
        assert values[3] == 0.0
    
    def test_vectorized_spiky_gradient(self):
        """Test vectorized Spiky gradient"""
        vkernels = VectorizedKernels()
        h = 0.1
        
        r_vectors = np.array([
            [0.05, 0.0, 0.0],
            [0.0, 0.05, 0.0],
            [0.15, 0.0, 0.0]
        ])
        
        gradients = vkernels.spiky_gradient_vectorized(r_vectors, h)
        
        # Check shape
        assert gradients.shape == (3, 3)
        
        # First gradient should point in x direction
        assert gradients[0, 0] < 0
        
        # Second gradient should point in y direction
        assert gradients[1, 1] < 0
        
        # Third (beyond h) should be zero
        assert np.allclose(gradients[2], [0, 0, 0])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
