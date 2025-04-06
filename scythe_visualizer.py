from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
from scythe_model import ScytheModel
import time

class ScytheVisualizer:
    def __init__(self):
        self.scythe = ScytheModel()
        self.rotation = 0
        self.last_time = time.time()
        
        # Initialize GLUT
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(800, 600)
        glutCreateWindow(b"Scythe Visualization")
        
        # Set up lighting
        self._setup_lighting()
        
        # Register callbacks
        glutDisplayFunc(self.display)
        glutIdleFunc(self.idle)
        glutReshapeFunc(self.reshape)
        glutKeyboardFunc(self.keyboard)

    def _setup_lighting(self):
        """Set up OpenGL lighting"""
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_COLOR_MATERIAL)
        
        # Set up light properties
        glLightfv(GL_LIGHT0, GL_POSITION, (5.0, 5.0, 5.0, 1.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))

    def display(self):
        """Main display function"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Set up camera
        gluLookAt(3, 3, 3, 0, 0, 0, 0, 1, 0)
        
        # Rotate the scene
        glRotatef(self.rotation, 0, 1, 0)
        
        # Draw the scythe
        self._draw_scythe()
        
        glutSwapBuffers()

    def _draw_scythe(self):
        """Draw the scythe model"""
        # Get current time for energy pulse
        current_time = time.time()
        energy_intensity = self.scythe.update_energy_intensity(current_time)
        
        # Draw handle
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.scythe.materials['handle']['color'])
        glMaterialf(GL_FRONT, GL_SHININESS, self.scythe.materials['handle']['reflectivity'] * 128)
        self._draw_handle()
        glPopMatrix()
        
        # Draw blade
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.scythe.materials['blade']['color'])
        glMaterialf(GL_FRONT, GL_SHININESS, self.scythe.materials['blade']['reflectivity'] * 128)
        self._draw_blade()
        glPopMatrix()
        
        # Draw energy core
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_EMISSION, 
                    (np.array(self.scythe.materials['energy_core']['color']) * energy_intensity).tolist())
        self._draw_energy_core()
        glPopMatrix()

    def _draw_handle(self):
        """Draw the scythe handle"""
        vertices = self.scythe.get_vertices()[:16]  # Handle vertices
        glBegin(GL_QUAD_STRIP)
        for i in range(0, len(vertices), 2):
            glVertex3fv(vertices[i])
            glVertex3fv(vertices[i+1])
        glEnd()

    def _draw_blade(self):
        """Draw the scythe blade"""
        vertices = self.scythe.get_vertices()[16:]  # Blade vertices
        glBegin(GL_QUAD_STRIP)
        for i in range(0, len(vertices), 2):
            glVertex3fv(vertices[i])
            glVertex3fv(vertices[i+1])
        glEnd()

    def _draw_energy_core(self):
        """Draw the energy core"""
        vertices = self.scythe.get_energy_core_vertices()
        glBegin(GL_LINE_STRIP)
        for vertex in vertices:
            glVertex3fv(vertex)
        glEnd()

    def idle(self):
        """Idle function for animation"""
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.rotation += 30.0 * delta_time
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

    def run(self):
        """Start the visualization"""
        glutMainLoop()

if __name__ == "__main__":
    visualizer = ScytheVisualizer()
    visualizer.run() 