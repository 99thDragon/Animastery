import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import time
from scythe_model import ScytheModel
from tattoo_system import TattooPattern

class CombatEffect:
    def __init__(self):
        self.effects = []
        self.particles = []
        
    def add_collision(self, position, energy1, energy2):
        """Add a collision effect at the given position"""
        self.effects.append({
            'type': 'collision',
            'position': np.array(position),
            'energy1': energy1,  # Blue scythe energy
            'energy2': energy2,  # Green tattoo energy
            'lifetime': 1.0,
            'scale': 1.0,
            'particles': self._generate_particles(position)
        })
        
    def add_shockwave(self, position, radius, color):
        """Add a shockwave effect"""
        self.effects.append({
            'type': 'shockwave',
            'position': np.array(position),
            'radius': radius,
            'color': color,
            'lifetime': 0.5,
            'current_radius': 0.0
        })

    def _generate_particles(self, position, count=20):
        """Generate particles for collision effects"""
        particles = []
        for _ in range(count):
            angle = np.random.uniform(0, 2 * np.pi)
            speed = np.random.uniform(0.5, 2.0)
            direction = np.array([
                np.cos(angle),
                np.sin(angle),
                np.random.uniform(-0.5, 0.5)
            ])
            particles.append({
                'position': np.array(position),
                'velocity': direction * speed,
                'lifetime': np.random.uniform(0.5, 1.5),
                'size': np.random.uniform(0.02, 0.08)
            })
        return particles

    def update(self, delta_time):
        """Update all active effects"""
        # Update existing effects
        for effect in self.effects[:]:
            effect['lifetime'] -= delta_time
            if effect['lifetime'] <= 0:
                self.effects.remove(effect)
                continue
                
            if effect['type'] == 'shockwave':
                max_radius = effect['radius']
                progress = 1 - (effect['lifetime'] / 0.5)
                effect['current_radius'] = max_radius * progress
                
        # Update particles
        for particle in self.particles[:]:
            particle['lifetime'] -= delta_time
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
                continue
            
            # Update position
            particle['position'] += particle['velocity'] * delta_time
            # Add gravity effect
            particle['velocity'][1] -= 9.8 * delta_time

class CombatSystem:
    def __init__(self):
        self.scythe = ScytheModel()
        self.tattoo = TattooPattern()
        self.effects = CombatEffect()
        self.last_time = time.time()
        
        # Combat state
        self.collision_points = []
        self.environment_damage = []
        
        # Initialize GLUT
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(1024, 768)
        glutCreateWindow(b"Combat Visualization")
        
        self._setup_lighting()
        self._setup_callbacks()

    def _setup_lighting(self):
        """Set up OpenGL lighting"""
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Main light
        glLightfv(GL_LIGHT0, GL_POSITION, (5.0, 5.0, 5.0, 1.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))

    def _setup_callbacks(self):
        """Set up GLUT callbacks"""
        glutDisplayFunc(self.display)
        glutIdleFunc(self.idle)
        glutReshapeFunc(self.reshape)
        glutKeyboardFunc(self.keyboard)
        glutSpecialFunc(self.special_keys)

    def simulate_combat(self):
        """Simulate a combat interaction"""
        # Generate collision point
        collision_point = (
            np.random.uniform(-0.5, 0.5),
            np.random.uniform(-0.5, 0.5),
            np.random.uniform(-0.5, 0.5)
        )
        
        # Add collision effect
        self.effects.add_collision(
            collision_point,
            self.scythe.materials['energy_core']['color'],
            self.tattoo.energy_state['current_color']
        )
        
        # Add shockwave
        self.effects.add_shockwave(
            collision_point,
            1.0,
            np.array([0.5, 0.5, 1.0])  # Blended color
        )
        
        # Update environment damage
        self.environment_damage.append({
            'position': collision_point,
            'radius': np.random.uniform(0.2, 0.5)
        })

    def display(self):
        """Main display function"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Set up camera
        gluLookAt(3, 3, 3, 0, 0, 0, 0, 1, 0)
        
        # Draw scythe
        self._draw_scythe()
        
        # Draw tattoo patterns
        self._draw_tattoos()
        
        # Draw effects
        self._draw_effects()
        
        # Draw environment damage
        self._draw_environment_damage()
        
        glutSwapBuffers()

    def _draw_scythe(self):
        """Draw the scythe model"""
        glPushMatrix()
        # Draw scythe implementation
        glPopMatrix()

    def _draw_tattoos(self):
        """Draw the tattoo patterns"""
        glPushMatrix()
        # Draw tattoo implementation
        glPopMatrix()

    def _draw_effects(self):
        """Draw all combat effects"""
        for effect in self.effects.effects:
            if effect['type'] == 'collision':
                self._draw_collision_effect(effect)
            elif effect['type'] == 'shockwave':
                self._draw_shockwave_effect(effect)

    def _draw_collision_effect(self, effect):
        """Draw a collision effect"""
        glPushMatrix()
        glTranslatef(*effect['position'])
        
        # Draw energy burst
        glMaterialfv(GL_FRONT, GL_EMISSION, (*effect['energy1'], effect['lifetime']))
        glutSolidSphere(0.1 * effect['scale'], 16, 16)
        
        # Draw particles
        for particle in effect['particles']:
            glPushMatrix()
            glTranslatef(*particle['position'])
            glMaterialfv(GL_FRONT, GL_EMISSION, (*effect['energy2'], particle['lifetime']))
            glutSolidSphere(particle['size'], 8, 8)
            glPopMatrix()
            
        glPopMatrix()

    def _draw_shockwave_effect(self, effect):
        """Draw a shockwave effect"""
        glPushMatrix()
        glTranslatef(*effect['position'])
        
        # Draw expanding ring
        glMaterialfv(GL_FRONT, GL_EMISSION, (*effect['color'], effect['lifetime'] * 2))
        
        glBegin(GL_LINE_STRIP)
        segments = 32
        for i in range(segments + 1):
            angle = 2 * np.pi * i / segments
            x = effect['current_radius'] * np.cos(angle)
            y = effect['current_radius'] * np.sin(angle)
            glVertex3f(x, y, 0)
        glEnd()
        
        glPopMatrix()

    def _draw_environment_damage(self):
        """Draw environmental damage effects"""
        for damage in self.environment_damage:
            glPushMatrix()
            glTranslatef(*damage['position'])
            
            # Draw damage crater
            glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.2, 0.2, 0.2, 1.0))
            glutSolidSphere(damage['radius'], 16, 16)
            
            glPopMatrix()

    def idle(self):
        """Idle function for animation"""
        current_time = time.time()
        delta_time = current_time - self.last_time
        
        # Update effects
        self.effects.update(delta_time)
        
        # Simulate combat periodically
        if np.random.random() < 0.02:  # 2% chance each frame
            self.simulate_combat()
        
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
        elif key == b' ':  # Spacebar
            self.simulate_combat()

    def special_keys(self, key, x, y):
        """Handle special key inputs"""
        pass

    def run(self):
        """Start the combat visualization"""
        glutMainLoop()

if __name__ == "__main__":
    combat = CombatSystem()
    combat.run() 