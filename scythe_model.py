import numpy as np
from typing import List, Tuple

class ScytheModel:
    def __init__(self):
        # Base dimensions (in meters)
        self.handle_length = 1.8
        self.blade_length = 0.9
        self.blade_curve_radius = 0.6
        
        # Material properties
        self.materials = {
            'blade': {
                'color': (0.9, 0.8, 0.1),  # Golden
                'reflectivity': 0.8,
                'roughness': 0.2
            },
            'handle': {
                'color': (0.4, 0.2, 0.1),  # Wooden
                'reflectivity': 0.3,
                'roughness': 0.7
            },
            'energy_core': {
                'color': (0.1, 0.5, 1.0),  # Blue
                'intensity': 1.0,
                'glow_radius': 0.1
            }
        }
        
        # Ornamentation details
        self.engravings = {
            'blade': [
                {'type': 'rune', 'position': (0.1, 0.2)},
                {'type': 'rune', 'position': (0.3, 0.4)},
                {'type': 'rune', 'position': (0.5, 0.6)}
            ],
            'handle': [
                {'type': 'leather_wrap', 'start': 0.2, 'end': 0.8},
                {'type': 'metal_bands', 'positions': [0.1, 0.5, 0.9]}
            ]
        }
        
        # Energy core properties
        self.energy_core = {
            'path': self._generate_energy_path(),
            'pulse_rate': 2.0,  # pulses per second
            'intensity_variation': 0.2
        }

    def _generate_energy_path(self) -> List[Tuple[float, float, float]]:
        """Generate the path for the energy core through the blade"""
        points = []
        steps = 20
        for i in range(steps):
            t = i / (steps - 1)
            # Parametric curve for energy path
            x = t * self.blade_length
            y = self.blade_curve_radius * (1 - np.cos(t * np.pi))
            z = 0.02 * np.sin(t * 4 * np.pi)  # Slight wave effect
            points.append((x, y, z))
        return points

    def get_vertices(self) -> np.ndarray:
        """Generate the vertex positions for the scythe model"""
        # Handle vertices (simple cylinder)
        handle_vertices = self._generate_cylinder(
            radius=0.03,
            length=self.handle_length,
            segments=8
        )
        
        # Blade vertices (curved surface)
        blade_vertices = self._generate_blade_surface()
        
        return np.concatenate([handle_vertices, blade_vertices])

    def _generate_cylinder(self, radius: float, length: float, segments: int) -> np.ndarray:
        """Generate vertices for a cylinder"""
        vertices = []
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            vertices.extend([
                (x, y, 0),
                (x, y, length)
            ])
        return np.array(vertices)

    def _generate_blade_surface(self) -> np.ndarray:
        """Generate vertices for the curved blade surface"""
        vertices = []
        segments = 16
        for i in range(segments):
            t = i / (segments - 1)
            # Main curve of the blade
            x = t * self.blade_length
            y = self.blade_curve_radius * (1 - np.cos(t * np.pi))
            # Add thickness
            for z in [-0.02, 0.02]:
                vertices.append((x, y, z))
        return np.array(vertices)

    def get_energy_core_vertices(self) -> np.ndarray:
        """Get vertices for the energy core visualization"""
        return np.array(self.energy_core['path'])

    def update_energy_intensity(self, time: float) -> float:
        """Update the energy core intensity based on time"""
        pulse = np.sin(2 * np.pi * self.energy_core['pulse_rate'] * time)
        return (1.0 + self.energy_core['intensity_variation'] * pulse) 