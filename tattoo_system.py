import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import time

class TattooPattern:
    def __init__(self):
        # Base pattern definitions
        self.patterns = {
            'core': {
                'position': (0, 0, 0),  # Center of chest
                'size': 0.2,
                'intensity': 1.0,
                'connections': ['right_arm', 'left_arm', 'spine']
            },
            'right_arm': {
                'points': [
                    (0.2, 0, 0),    # Shoulder
                    (0.3, -0.1, 0), # Upper arm
                    (0.4, -0.2, 0), # Elbow
                    (0.5, -0.3, 0)  # Forearm
                ],
                'intensity': 0.8,
                'flow_speed': 1.2
            },
            'left_arm': {
                'points': [
                    (-0.2, 0, 0),    # Shoulder
                    (-0.3, -0.1, 0), # Upper arm
                    (-0.4, -0.2, 0), # Elbow
                    (-0.5, -0.3, 0)  # Forearm
                ],
                'intensity': 0.8,
                'flow_speed': 1.2
            },
            'spine': {
                'points': [
                    (0, 0.1, 0),   # Upper back
                    (0, 0, 0),     # Mid back
                    (0, -0.1, 0),  # Lower back
                ],
                'intensity': 1.0,
                'flow_speed': 0.8
            }
        }
        
        # Energy state
        self.energy_state = {
            'current_color': np.array([0.0, 1.0, 0.0]),  # Start with green
            'target_color': np.array([0.0, 1.0, 0.0]),
            'transition_speed': 2.0,
            'pulse_rate': 1.5,
            'flow_offset': 0.0
        }

    def update(self, delta_time):
        """Update tattoo animation state"""
        # Update color transition
        self._update_color_transition(delta_time)
        
        # Update energy flow
        self.energy_state['flow_offset'] += delta_time
        
        # Update pattern intensities
        self._update_pattern_intensities(delta_time)

    def _update_color_transition(self, delta_time):
        """Handle smooth color transitions"""
        diff = self.energy_state['target_color'] - self.energy_state['current_color']
        if np.any(np.abs(diff) > 0.01):
            self.energy_state['current_color'] += diff * self.energy_state['transition_speed'] * delta_time

    def _update_pattern_intensities(self, delta_time):
        """Update individual pattern intensities based on energy flow"""
        time_val = time.time()
        base_pulse = 0.5 + 0.5 * np.sin(time_val * self.energy_state['pulse_rate'])
        
        for pattern in self.patterns.values():
            if 'intensity' in pattern:
                flow_factor = np.sin(time_val * pattern.get('flow_speed', 1.0))
                pattern['intensity'] = 0.6 + 0.4 * (base_pulse + 0.5 * flow_factor)

class TattooVisualizer:
    def __init__(self):
        self.tattoo = TattooPattern()
        self.last_time = time.time()
        
        # Initialize GLUT
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(800, 600)
        glutCreateWindow(b"Tattoo Visualization")
        
        # Set up lighting
        self._setup_lighting()
        
        # Register callbacks
        glutDisplayFunc(self.display)
        glutIdleFunc(self.idle)
        glutReshapeFunc(self.reshape)
        glutKeyboardFunc(self.keyboard)
        glutSpecialFunc(self.special_keys)

    def _setup_lighting(self):
        """Set up OpenGL lighting"""
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glLightfv(GL_LIGHT0, GL_POSITION, (5.0, 5.0, 5.0, 1.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))

    def display(self):
        """Main display function"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Set up camera
        gluLookAt(0, 0, 2, 0, 0, 0, 0, 1, 0)
        
        # Draw tattoo patterns
        self._draw_patterns()
        
        glutSwapBuffers()

    def _draw_patterns(self):
        """Draw all tattoo patterns"""
        # Draw core pattern
        self._draw_core()
        
        # Draw connecting patterns
        for pattern_name, pattern in self.tattoo.patterns.items():
            if pattern_name != 'core':
                self._draw_pattern(pattern)

    def _draw_core(self):
        """Draw the core pattern"""
        core = self.tattoo.patterns['core']
        color = self.tattoo.energy_state['current_color'] * core['intensity']
        
        glPushMatrix()
        glTranslatef(*core['position'])
        
        glMaterialfv(GL_FRONT, GL_EMISSION, (*color, 1.0))
        
        glutSolidSphere(core['size'], 32, 32)
        
        glPopMatrix()

    def _draw_pattern(self, pattern):
        """Draw a single pattern"""
        if 'points' not in pattern:
            return
            
        color = self.tattoo.energy_state['current_color'] * pattern['intensity']
        
        glMaterialfv(GL_FRONT, GL_EMISSION, (*color, 1.0))
        
        glBegin(GL_LINE_STRIP)
        for point in pattern['points']:
            glVertex3fv(point)
        glEnd()

    def idle(self):
        """Idle function for animation"""
        current_time = time.time()
        delta_time = current_time - self.last_time
        
        # Update tattoo state
        self.tattoo.update(delta_time)
        
        self.last_time = current_time
        glutPostRedisplay()

    def reshape(self, width, height):
        """Handle window resize"""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width/height, 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)

    def keyboard(self, key, x, y):
        """Handle keyboard input"""
        if key == b'\x1b':  # ESC key
            sys.exit()
        elif key == b'r':  # Change to red
            self.tattoo.energy_state['target_color'] = np.array([1.0, 0.0, 0.0])
        elif key == b'g':  # Change to green
            self.tattoo.energy_state['target_color'] = np.array([0.0, 1.0, 0.0])

    def special_keys(self, key, x, y):
        """Handle special key inputs"""
        if key == GLUT_KEY_UP:
            self.tattoo.energy_state['pulse_rate'] *= 1.2
        elif key == GLUT_KEY_DOWN:
            self.tattoo.energy_state['pulse_rate'] *= 0.8

    def run(self):
        """Start the visualization"""
        glutMainLoop()

if __name__ == "__main__":
    visualizer = TattooVisualizer()
    visualizer.run() 