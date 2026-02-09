"""
Predefined fluid properties and presets
"""


class FluidPreset:
    """
    Common fluid properties for various materials
    
    All values are in SI units unless otherwise specified
    """
    
    WATER = {
        'name': 'Water',
        'density': 1000.0,         # kg/m³
        'viscosity': 0.001,        # Pa·s (dynamic viscosity)
        'color': (0.2, 0.5, 1.0),  # RGB (blue)
        'gas_constant': 2000.0,    # Stiffness parameter
        'rest_density': 1000.0     # Rest density (kg/m³)
    }
    
    OIL_LIGHT = {
        'name': 'Light Oil',
        'density': 850.0,          # kg/m³
        'viscosity': 0.005,        # Pa·s (~5 cP)
        'color': (0.8, 0.6, 0.2),  # RGB (golden)
        'gas_constant': 1500.0,
        'rest_density': 850.0
    }
    
    OIL_MEDIUM = {
        'name': 'Medium Oil',
        'density': 900.0,
        'viscosity': 0.02,         # Pa·s (~20 cP)
        'color': (0.7, 0.5, 0.1),  # RGB (darker golden)
        'gas_constant': 1500.0,
        'rest_density': 900.0
    }
    
    OIL_HEAVY = {
        'name': 'Heavy Oil',
        'density': 950.0,
        'viscosity': 0.1,          # Pa·s (~100 cP)
        'color': (0.3, 0.2, 0.1),  # RGB (dark brown)
        'gas_constant': 1500.0,
        'rest_density': 950.0
    }
    
    HONEY = {
        'name': 'Honey',
        'density': 1420.0,
        'viscosity': 10.0,         # Pa·s (very viscous!)
        'color': (1.0, 0.7, 0.0),  # RGB (golden yellow)
        'gas_constant': 2500.0,
        'rest_density': 1420.0
    }
    
    GLYCERIN = {
        'name': 'Glycerin',
        'density': 1260.0,
        'viscosity': 1.5,          # Pa·s
        'color': (0.9, 0.9, 0.95), # RGB (clear/white)
        'gas_constant': 2200.0,
        'rest_density': 1260.0
    }
    
    MERCURY = {
        'name': 'Mercury',
        'density': 13534.0,        # kg/m³ (very dense!)
        'viscosity': 0.0015,       # Pa·s
        'color': (0.7, 0.7, 0.8),  # RGB (silver)
        'gas_constant': 5000.0,
        'rest_density': 13534.0
    }
    
    MILK = {
        'name': 'Milk',
        'density': 1030.0,
        'viscosity': 0.002,        # Pa·s
        'color': (1.0, 1.0, 0.95), # RGB (off-white)
        'gas_constant': 2000.0,
        'rest_density': 1030.0
    }
    
    BLOOD = {
        'name': 'Blood',
        'density': 1060.0,
        'viscosity': 0.004,        # Pa·s
        'color': (0.8, 0.1, 0.1),  # RGB (dark red)
        'gas_constant': 2100.0,
        'rest_density': 1060.0
    }
    
    @staticmethod
    def get_preset(name):
        """
        Get a fluid preset by name
        
        Args:
            name: Name of the preset (case-insensitive)
        
        Returns:
            Dictionary with fluid properties
        """
        name_upper = name.upper().replace(' ', '_')
        
        if hasattr(FluidPreset, name_upper):
            return getattr(FluidPreset, name_upper).copy()
        else:
            available = [attr for attr in dir(FluidPreset) 
                        if not attr.startswith('_') and attr.isupper()]
            raise ValueError(f"Unknown fluid preset: {name}. Available: {available}")
    
    @staticmethod
    def list_presets():
        """
        List all available fluid presets
        
        Returns:
            List of preset names
        """
        return [attr for attr in dir(FluidPreset) 
                if not attr.startswith('_') and attr.isupper() and attr != 'get_preset']
    
    @staticmethod
    def create_custom(name, density, viscosity, color, gas_constant=2000.0):
        """
        Create a custom fluid preset
        
        Args:
            name: Fluid name
            density: Density in kg/m³
            viscosity: Dynamic viscosity in Pa·s
            color: RGB tuple (0-1 range)
            gas_constant: Stiffness parameter
        
        Returns:
            Dictionary with fluid properties
        """
        return {
            'name': name,
            'density': density,
            'viscosity': viscosity,
            'color': color,
            'gas_constant': gas_constant,
            'rest_density': density
        }
