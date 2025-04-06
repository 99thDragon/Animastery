import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import time
import math

# Add these global variables at the top of the file
camera_distance = 5.0
camera_angle_x = 0.0
camera_angle_y = 30.0  # Start with a slight downward angle
camera_target = np.array([0.0, 1.0, 0.0])  # Look at point (center between characters)
camera_up = np.array([0.0, 1.0, 0.0])
camera_pan_x = 0.0
camera_pan_y = 0.0
is_mouse_down = False
is_right_mouse_down = False
last_mouse_x = 0
last_mouse_y = 0

class CharacterBone:
    def __init__(self, name, length, parent=None):
        self.name = name
        self.length = length
        self.parent = parent
        self.children = []
        self.rotation = np.array([0.0, 0.0, 0.0])  # Euler angles
        self.position = np.array([0.0, 0.0, 0.0])
        self.scale = np.array([1.0, 1.0, 1.0])
        self.effect_color = np.array([1.0, 1.0, 1.0])  # For special effects
        
        if parent:
            parent.children.append(self)

class CharacterRig:
    def __init__(self, character_type):
        self.bones = {}
        self.animations = {}
        self.current_animation = None
        self.animation_time = 0.0
        self.character_type = character_type
        self.effect_intensity = 0.0  # For dynamic effects
        self.combo_count = 0  # For combo animations
        
        self._create_skeleton()
        self._create_animations()

    def _create_skeleton(self):
        """Create character skeleton based on type"""
        # Root bone
        self.bones['root'] = CharacterBone('root', 0.0)
        
        # Spine chain
        self.bones['spine_1'] = CharacterBone('spine_1', 0.3, self.bones['root'])
        self.bones['spine_2'] = CharacterBone('spine_2', 0.3, self.bones['spine_1'])
        self.bones['neck'] = CharacterBone('neck', 0.2, self.bones['spine_2'])
        self.bones['head'] = CharacterBone('head', 0.2, self.bones['neck'])
        
        # Arms
        self.bones['l_shoulder'] = CharacterBone('l_shoulder', 0.2, self.bones['spine_2'])
        self.bones['l_upper_arm'] = CharacterBone('l_upper_arm', 0.3, self.bones['l_shoulder'])
        self.bones['l_elbow'] = CharacterBone('l_elbow', 0.2, self.bones['l_upper_arm'])
        self.bones['l_forearm'] = CharacterBone('l_forearm', 0.3, self.bones['l_elbow'])
        self.bones['l_hand'] = CharacterBone('l_hand', 0.2, self.bones['l_forearm'])
        
        self.bones['r_shoulder'] = CharacterBone('r_shoulder', 0.2, self.bones['spine_2'])
        self.bones['r_upper_arm'] = CharacterBone('r_upper_arm', 0.3, self.bones['r_shoulder'])
        self.bones['r_elbow'] = CharacterBone('r_elbow', 0.2, self.bones['r_upper_arm'])
        self.bones['r_forearm'] = CharacterBone('r_forearm', 0.3, self.bones['r_elbow'])
        self.bones['r_hand'] = CharacterBone('r_hand', 0.2, self.bones['r_forearm'])
        
        # Legs
        self.bones['l_hip'] = CharacterBone('l_hip', 0.3, self.bones['root'])
        self.bones['l_thigh'] = CharacterBone('l_thigh', 0.4, self.bones['l_hip'])
        self.bones['l_knee'] = CharacterBone('l_knee', 0.2, self.bones['l_thigh'])
        self.bones['l_calf'] = CharacterBone('l_calf', 0.4, self.bones['l_knee'])
        self.bones['l_foot'] = CharacterBone('l_foot', 0.2, self.bones['l_calf'])
        
        self.bones['r_hip'] = CharacterBone('r_hip', 0.3, self.bones['root'])
        self.bones['r_thigh'] = CharacterBone('r_thigh', 0.4, self.bones['r_hip'])
        self.bones['r_knee'] = CharacterBone('r_knee', 0.2, self.bones['r_thigh'])
        self.bones['r_calf'] = CharacterBone('r_calf', 0.4, self.bones['r_knee'])
        self.bones['r_foot'] = CharacterBone('r_foot', 0.2, self.bones['r_calf'])

    def _create_animations(self):
        """Create character-specific animations"""
        if self.character_type == "aaron":
            self._create_aaron_animations()
        elif self.character_type == "mani":
            self._create_mani_animations()

    def _create_aaron_animations(self):
        """Create Aaron's combat animations"""
        # Idle stance with breathing
        self.animations['idle'] = {
            'duration': 2.0,
            'keyframes': {
                0.0: {
                    'spine_1': np.array([0.0, 0.0, 0.0]),
                    'spine_2': np.array([0.0, 0.0, 0.0]),
                    'r_shoulder': np.array([30.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, 0.0, 0.0]),
                    'r_elbow': np.array([0.0, 30.0, 0.0]),
                    'r_forearm': np.array([0.0, 0.0, 0.0])
                },
                1.0: {
                    'spine_1': np.array([5.0, 0.0, 0.0]),
                    'spine_2': np.array([2.0, 0.0, 0.0]),
                    'r_shoulder': np.array([35.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, 0.0, 0.0]),
                    'r_elbow': np.array([0.0, 35.0, 0.0]),
                    'r_forearm': np.array([0.0, 0.0, 0.0])
                }
            }
        }
        
        # Scythe swing with follow-through
        self.animations['scythe_swing'] = {
            'duration': 1.2,
            'keyframes': {
                0.0: {
                    'spine_1': np.array([0.0, -30.0, 0.0]),
                    'spine_2': np.array([0.0, -15.0, 0.0]),
                    'r_shoulder': np.array([-45.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, -20.0, 0.0]),
                    'r_elbow': np.array([0.0, -90.0, 0.0]),
                    'r_forearm': np.array([0.0, 0.0, 0.0])
                },
                0.4: {
                    'spine_1': np.array([0.0, 30.0, 0.0]),
                    'spine_2': np.array([0.0, 15.0, 0.0]),
                    'r_shoulder': np.array([45.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, 20.0, 0.0]),
                    'r_elbow': np.array([0.0, 0.0, 0.0]),
                    'r_forearm': np.array([0.0, 0.0, 0.0])
                },
                0.8: {
                    'spine_1': np.array([0.0, 15.0, 0.0]),
                    'spine_2': np.array([0.0, 5.0, 0.0]),
                    'r_shoulder': np.array([60.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, 30.0, 0.0]),
                    'r_elbow': np.array([0.0, 45.0, 0.0]),
                    'r_forearm': np.array([0.0, 0.0, 0.0])
                }
            }
        }
        
        # Block stance with anticipation
        self.animations['block'] = {
            'duration': 0.8,
            'keyframes': {
                0.0: {
                    'spine_1': np.array([0.0, 0.0, 0.0]),
                    'spine_2': np.array([0.0, 0.0, 0.0]),
                    'r_shoulder': np.array([90.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, 0.0, 0.0]),
                    'r_elbow': np.array([0.0, 90.0, 0.0]),
                    'r_forearm': np.array([0.0, 0.0, 0.0])
                },
                0.4: {
                    'spine_1': np.array([0.0, 0.0, 0.0]),
                    'spine_2': np.array([0.0, 0.0, 0.0]),
                    'r_shoulder': np.array([120.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, 0.0, 0.0]),
                    'r_elbow': np.array([0.0, 120.0, 0.0]),
                    'r_forearm': np.array([0.0, 0.0, 0.0])
                }
            }
        }
        
        # New combo attack sequence
        self.animations['combo_attack'] = {
            'duration': 2.0,
            'keyframes': {
                0.0: {
                    'spine_1': np.array([0.0, -30.0, 0.0]),
                    'spine_2': np.array([0.0, -15.0, 0.0]),
                    'r_shoulder': np.array([-45.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, -20.0, 0.0]),
                    'r_elbow': np.array([0.0, -90.0, 0.0])
                },
                0.4: {
                    'spine_1': np.array([0.0, 30.0, 0.0]),
                    'spine_2': np.array([0.0, 15.0, 0.0]),
                    'r_shoulder': np.array([45.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, 20.0, 0.0]),
                    'r_elbow': np.array([0.0, 0.0, 0.0])
                },
                0.8: {
                    'spine_1': np.array([0.0, -20.0, 0.0]),
                    'spine_2': np.array([0.0, -10.0, 0.0]),
                    'r_shoulder': np.array([-30.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, -15.0, 0.0]),
                    'r_elbow': np.array([0.0, -60.0, 0.0])
                },
                1.2: {
                    'spine_1': np.array([0.0, 20.0, 0.0]),
                    'spine_2': np.array([0.0, 10.0, 0.0]),
                    'r_shoulder': np.array([30.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, 15.0, 0.0]),
                    'r_elbow': np.array([0.0, 0.0, 0.0])
                }
            }
        }
        
        # Special move: Scythe Spin
        self.animations['scythe_spin'] = {
            'duration': 1.5,
            'keyframes': {
                0.0: {
                    'spine_1': np.array([0.0, 0.0, 0.0]),
                    'spine_2': np.array([0.0, 0.0, 0.0]),
                    'r_shoulder': np.array([0.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, 0.0, 0.0]),
                    'r_elbow': np.array([0.0, 0.0, 0.0])
                },
                0.5: {
                    'spine_1': np.array([0.0, 180.0, 0.0]),
                    'spine_2': np.array([0.0, 90.0, 0.0]),
                    'r_shoulder': np.array([0.0, 360.0, 0.0]),
                    'r_upper_arm': np.array([0.0, 180.0, 0.0]),
                    'r_elbow': np.array([0.0, 360.0, 0.0])
                }
            }
        }

    def _create_mani_animations(self):
        """Create Mani's combat animations"""
        # Idle stance with glowing tattoos
        self.animations['idle'] = {
            'duration': 2.0,
            'keyframes': {
                0.0: {
                    'spine_1': np.array([0.0, 0.0, 0.0]),
                    'spine_2': np.array([0.0, 0.0, 0.0]),
                    'l_shoulder': np.array([20.0, 0.0, 0.0]),
                    'l_upper_arm': np.array([0.0, 0.0, 0.0]),
                    'r_shoulder': np.array([20.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, 0.0, 0.0])
                },
                1.0: {
                    'spine_1': np.array([5.0, 0.0, 0.0]),
                    'spine_2': np.array([2.0, 0.0, 0.0]),
                    'l_shoulder': np.array([25.0, 0.0, 0.0]),
                    'l_upper_arm': np.array([0.0, 0.0, 0.0]),
                    'r_shoulder': np.array([25.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, 0.0, 0.0])
                }
            }
        }
        
        # Energy blade attack with power buildup
        self.animations['blade_attack'] = {
            'duration': 1.0,
            'keyframes': {
                0.0: {
                    'spine_1': np.array([0.0, -45.0, 0.0]),
                    'spine_2': np.array([0.0, -20.0, 0.0]),
                    'r_shoulder': np.array([-90.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, -30.0, 0.0]),
                    'r_elbow': np.array([0.0, -45.0, 0.0]),
                    'r_forearm': np.array([0.0, 0.0, 0.0])
                },
                0.3: {
                    'spine_1': np.array([0.0, 45.0, 0.0]),
                    'spine_2': np.array([0.0, 20.0, 0.0]),
                    'r_shoulder': np.array([45.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, 30.0, 0.0]),
                    'r_elbow': np.array([0.0, 0.0, 0.0]),
                    'r_forearm': np.array([0.0, 0.0, 0.0])
                },
                0.6: {
                    'spine_1': np.array([0.0, 30.0, 0.0]),
                    'spine_2': np.array([0.0, 10.0, 0.0]),
                    'r_shoulder': np.array([60.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, 45.0, 0.0]),
                    'r_elbow': np.array([0.0, 30.0, 0.0]),
                    'r_forearm': np.array([0.0, 0.0, 0.0])
                }
            }
        }
        
        # Defensive stance with energy shield
        self.animations['defend'] = {
            'duration': 0.8,
            'keyframes': {
                0.0: {
                    'spine_1': np.array([0.0, 0.0, 0.0]),
                    'spine_2': np.array([0.0, 0.0, 0.0]),
                    'l_shoulder': np.array([45.0, 0.0, 0.0]),
                    'l_upper_arm': np.array([0.0, 0.0, 0.0]),
                    'r_shoulder': np.array([45.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, 0.0, 0.0]),
                    'l_elbow': np.array([0.0, 90.0, 0.0]),
                    'r_elbow': np.array([0.0, 90.0, 0.0])
                },
                0.4: {
                    'spine_1': np.array([0.0, 0.0, 0.0]),
                    'spine_2': np.array([0.0, 0.0, 0.0]),
                    'l_shoulder': np.array([60.0, 0.0, 0.0]),
                    'l_upper_arm': np.array([0.0, 0.0, 0.0]),
                    'r_shoulder': np.array([60.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, 0.0, 0.0]),
                    'l_elbow': np.array([0.0, 120.0, 0.0]),
                    'r_elbow': np.array([0.0, 120.0, 0.0])
                }
            }
        }
        
        # New combo attack sequence
        self.animations['combo_attack'] = {
            'duration': 2.0,
            'keyframes': {
                0.0: {
                    'spine_1': np.array([0.0, -45.0, 0.0]),
                    'spine_2': np.array([0.0, -20.0, 0.0]),
                    'r_shoulder': np.array([-90.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, -30.0, 0.0]),
                    'r_elbow': np.array([0.0, -45.0, 0.0])
                },
                0.4: {
                    'spine_1': np.array([0.0, 45.0, 0.0]),
                    'spine_2': np.array([0.0, 20.0, 0.0]),
                    'r_shoulder': np.array([45.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, 30.0, 0.0]),
                    'r_elbow': np.array([0.0, 0.0, 0.0])
                },
                0.8: {
                    'spine_1': np.array([0.0, -30.0, 0.0]),
                    'spine_2': np.array([0.0, -15.0, 0.0]),
                    'r_shoulder': np.array([-60.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, -20.0, 0.0]),
                    'r_elbow': np.array([0.0, -30.0, 0.0])
                },
                1.2: {
                    'spine_1': np.array([0.0, 30.0, 0.0]),
                    'spine_2': np.array([0.0, 15.0, 0.0]),
                    'r_shoulder': np.array([60.0, 0.0, 0.0]),
                    'r_upper_arm': np.array([0.0, 20.0, 0.0]),
                    'r_elbow': np.array([0.0, 0.0, 0.0])
                }
            }
        }
        
        # Special move: Energy Burst
        self.animations['energy_burst'] = {
            'duration': 1.2,
            'keyframes': {
                0.0: {
                    'spine_1': np.array([0.0, 0.0, 0.0]),
                    'spine_2': np.array([0.0, 0.0, 0.0]),
                    'l_shoulder': np.array([45.0, 0.0, 0.0]),
                    'r_shoulder': np.array([45.0, 0.0, 0.0]),
                    'l_elbow': np.array([0.0, 90.0, 0.0]),
                    'r_elbow': np.array([0.0, 90.0, 0.0])
                },
                0.6: {
                    'spine_1': np.array([0.0, 0.0, 0.0]),
                    'spine_2': np.array([0.0, 0.0, 0.0]),
                    'l_shoulder': np.array([90.0, 0.0, 0.0]),
                    'r_shoulder': np.array([90.0, 0.0, 0.0]),
                    'l_elbow': np.array([0.0, 180.0, 0.0]),
                    'r_elbow': np.array([0.0, 180.0, 0.0])
                }
            }
        }

    def play_animation(self, animation_name):
        """Start playing an animation"""
        if animation_name in self.animations:
            self.current_animation = animation_name
            self.animation_time = 0.0

    def update(self, delta_time):
        """Update animation state with effects"""
        if not self.current_animation:
            return
            
        animation = self.animations[self.current_animation]
        self.animation_time += delta_time
        
        # Update effect intensity based on animation
        if self.current_animation in ['scythe_swing', 'scythe_spin']:
            self.effect_intensity = math.sin(self.animation_time * 10) * 0.5 + 0.5
        elif self.current_animation in ['blade_attack', 'energy_burst']:
            self.effect_intensity = math.sin(self.animation_time * 8) * 0.5 + 0.5
        else:
            self.effect_intensity = 0.0
        
        # Loop or stop at end
        if self.animation_time > animation['duration']:
            if self.current_animation == 'idle':
                self.animation_time = 0.0
            else:
                self.play_animation('idle')
                return
        
        # Interpolate between keyframes
        self._update_bone_transforms()

    def _update_bone_transforms(self):
        """Update bone transforms based on current animation"""
        if not self.current_animation:
            return
            
        animation = self.animations[self.current_animation]
        keyframes = animation['keyframes']
        
        # Find surrounding keyframes
        times = sorted(keyframes.keys())
        next_idx = 0
        while next_idx < len(times) and times[next_idx] < self.animation_time:
            next_idx += 1
            
        if next_idx == 0:
            # Before first keyframe
            frame = keyframes[times[0]]
            self._apply_keyframe(frame)
        elif next_idx == len(times):
            # After last keyframe
            frame = keyframes[times[-1]]
            self._apply_keyframe(frame)
        else:
            # Interpolate between keyframes
            t1, t2 = times[next_idx-1], times[next_idx]
            f1, f2 = keyframes[t1], keyframes[t2]
            
            alpha = (self.animation_time - t1) / (t2 - t1)
            self._interpolate_keyframes(f1, f2, alpha)

    def _apply_keyframe(self, frame):
        """Apply a single keyframe to the skeleton"""
        for bone_name, rotation in frame.items():
            if bone_name in self.bones:
                self.bones[bone_name].rotation = rotation.copy()

    def _interpolate_keyframes(self, frame1, frame2, alpha):
        """Interpolate between two keyframes"""
        for bone_name in set(frame1.keys()) | set(frame2.keys()):
            if bone_name not in self.bones:
                continue
                
            r1 = frame1.get(bone_name, np.zeros(3))
            r2 = frame2.get(bone_name, np.zeros(3))
            
            rotation = r1 + alpha * (r2 - r1)
            self.bones[bone_name].rotation = rotation

    def draw(self):
        """Draw the character skeleton with effects"""
        glPushMatrix()
        
        # Set character color
        if self.character_type == "aaron":
            base_color = np.array([0.8, 0.2, 0.2])  # Red for Aaron
        else:
            base_color = np.array([0.2, 0.2, 0.8])  # Blue for Mani
        
        # Apply dynamic effect color
        effect_color = base_color + np.array([0.2, 0.2, 0.2]) * self.effect_intensity
        glColor3f(*effect_color)
        
        self._draw_bone_recursive(self.bones['root'])
        
        # Draw weapons and special effects
        if self.character_type == "aaron":
            if 'r_hand' in self.bones:
                self._draw_weapon(self.bones['r_hand'])
        elif self.character_type == "mani":
            if 'r_hand' in self.bones:
                self._draw_weapon(self.bones['r_hand'])
        
        self._draw_special_effects()
        
        glPopMatrix()

    def _draw_weapon(self, bone):
        """Draw character-specific weapons"""
        if self.character_type == "aaron":
            # Draw scythe
            glPushMatrix()
            glRotatef(90, 1, 0, 0)  # Rotate to horizontal
            glColor3f(0.8, 0.2, 0.2)  # Red scythe
            glutSolidCylinder(0.05, 1.0, 20, 20)  # Scythe handle
            glTranslatef(0, 0, 1.0)  # Move to blade position
            glRotatef(90, 0, 1, 0)  # Rotate blade
            glutSolidCone(0.3, 0.8, 20, 20)  # Scythe blade
            glPopMatrix()
        elif self.character_type == "mani":
            # Draw energy blade
            glPushMatrix()
            glColor3f(0.2, 0.2, 0.8)  # Blue energy blade
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            glBegin(GL_QUADS)
            glVertex3f(-0.1, 0, 0)
            glVertex3f(0.1, 0, 0)
            glVertex3f(0.1, 1.0, 0)
            glVertex3f(-0.1, 1.0, 0)
            glEnd()
            glDisable(GL_BLEND)
            glPopMatrix()

    def _draw_special_effects(self):
        """Draw character-specific special effects"""
        if self.character_type == "aaron":
            # Draw scythe trail
            if self.current_animation in ['scythe_swing', 'scythe_spin']:
                glPushMatrix()
                glDisable(GL_LIGHTING)
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE)
                glColor4f(0.8, 0.2, 0.2, 0.5 * self.effect_intensity)
                glBegin(GL_QUAD_STRIP)
                for i in range(10):
                    t = i / 9.0
                    glVertex3f(0, t, 0)
                    glVertex3f(0.2 * math.sin(t * math.pi), t, 0.2 * math.cos(t * math.pi))
                glEnd()
                glDisable(GL_BLEND)
                glEnable(GL_LIGHTING)
                glPopMatrix()
        elif self.character_type == "mani":
            # Draw energy burst
            if self.current_animation in ['energy_burst', 'combo_attack']:
                glPushMatrix()
                glDisable(GL_LIGHTING)
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE)
                glColor4f(0.2, 0.2, 0.8, 0.5 * self.effect_intensity)
                glutSolidSphere(0.5 * self.effect_intensity, 20, 20)
                glDisable(GL_BLEND)
                glEnable(GL_LIGHTING)
                glPopMatrix()

    def _draw_bone_recursive(self, bone):
        """Recursively draw bones with improved visuals"""
        glPushMatrix()
        
        # Apply bone transform
        glTranslatef(*bone.position)
        glRotatef(bone.rotation[0], 1, 0, 0)
        glRotatef(bone.rotation[1], 0, 1, 0)
        glRotatef(bone.rotation[2], 0, 0, 1)
        glScalef(*bone.scale)
        
        # Draw bone with improved visuals
        if bone.length > 0:
            self._draw_bone(bone.length)
        
        # Draw children
        for child in bone.children:
            glPushMatrix()
            glTranslatef(0, bone.length, 0)
            self._draw_bone_recursive(child)
            glPopMatrix()
        
        glPopMatrix()

    def _draw_bone(self, length):
        """Draw a single bone with improved visuals"""
        # Draw bone cylinder with improved detail
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        glutSolidCylinder(0.05, length, 20, 20)  # Increased detail
        glPopMatrix()
        
        # Draw joint sphere with improved detail
        glPushMatrix()
        glutSolidSphere(0.08, 20, 20)  # Increased detail
        glPopMatrix()

def init():
    """Initialize OpenGL settings"""
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_NORMALIZE)
    
    # Set up lighting
    glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 10.0, 10.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    
    # Set up material
    glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    glMaterialfv(GL_FRONT, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
    glMaterialfv(GL_FRONT, GL_SHININESS, [50.0])

def reshape(width, height):
    """Handle window resizing"""
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width/height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def mouse(button, state, x, y):
    """Handle mouse button events"""
    global is_mouse_down, is_right_mouse_down, last_mouse_x, last_mouse_y
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            is_mouse_down = True
            last_mouse_x = x
            last_mouse_y = y
        else:
            is_mouse_down = False
    elif button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            is_right_mouse_down = True
            last_mouse_x = x
            last_mouse_y = y
        else:
            is_right_mouse_down = False

def motion(x, y):
    """Handle mouse motion"""
    global camera_angle_x, camera_angle_y, camera_pan_x, camera_pan_y, last_mouse_x, last_mouse_y
    dx = x - last_mouse_x
    dy = y - last_mouse_y
    
    if is_mouse_down:  # Left mouse button - Orbit
        camera_angle_x += dx * 0.5
        camera_angle_y = max(-89.0, min(89.0, camera_angle_y + dy * 0.5))  # Clamp vertical rotation
    elif is_right_mouse_down:  # Right mouse button - Pan
        camera_pan_x += dx * 0.01
        camera_pan_y -= dy * 0.01
    
    last_mouse_x = x
    last_mouse_y = y
    glutPostRedisplay()

def special_keys(key, x, y):
    """Handle special keyboard keys"""
    global camera_distance, camera_angle_x, camera_angle_y, camera_pan_x, camera_pan_y
    if key == GLUT_KEY_UP:
        camera_distance = max(2.0, camera_distance - 0.5)  # Zoom in with min distance
    elif key == GLUT_KEY_DOWN:
        camera_distance = min(20.0, camera_distance + 0.5)  # Zoom out with max distance
    elif key == GLUT_KEY_LEFT:
        camera_angle_x -= 5.0  # Rotate left
    elif key == GLUT_KEY_RIGHT:
        camera_angle_x += 5.0  # Rotate right
    elif key == GLUT_KEY_HOME:  # Reset camera
        camera_distance = 5.0
        camera_angle_x = 0.0
        camera_angle_y = 30.0
        camera_pan_x = 0.0
        camera_pan_y = 0.0
    glutPostRedisplay()

def keyboard(key, x, y):
    """Handle keyboard input for animations and camera"""
    global camera_distance, camera_angle_x, camera_angle_y, camera_pan_x, camera_pan_y
    if key == b'1':
        aaron.play_animation("scythe_swing")
    elif key == b'2':
        aaron.play_animation("scythe_spin")
    elif key == b'3':
        aaron.play_animation("combo_attack")
    elif key == b'4':
        mani.play_animation("blade_attack")
    elif key == b'5':
        mani.play_animation("energy_burst")
    elif key == b'6':
        mani.play_animation("combo_attack")
    elif key == b'r':  # Reset camera
        camera_distance = 5.0
        camera_angle_x = 0.0
        camera_angle_y = 30.0
        camera_pan_x = 0.0
        camera_pan_y = 0.0
        glutPostRedisplay()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Calculate camera position based on spherical coordinates
    camera_x = camera_target[0] + camera_distance * math.cos(math.radians(camera_angle_y)) * math.sin(math.radians(camera_angle_x))
    camera_y = camera_target[1] + camera_distance * math.sin(math.radians(camera_angle_y))
    camera_z = camera_target[2] + camera_distance * math.cos(math.radians(camera_angle_y)) * math.cos(math.radians(camera_angle_x))
    
    # Set up the camera view
    gluLookAt(
        camera_x + camera_pan_x, camera_y + camera_pan_y, camera_z,  # Camera position
        camera_target[0] + camera_pan_x, camera_target[1] + camera_pan_y, camera_target[2],  # Look at point
        camera_up[0], camera_up[1], camera_up[2]  # Up vector
    )
    
    # Draw characters with better spacing
    glPushMatrix()
    glTranslatef(-2, 0, 0)  # Move Aaron further left
    aaron.draw()
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(2, 0, 0)   # Move Mani further right
    mani.draw()
    glPopMatrix()
    
    glutSwapBuffers()

def update():
    """Update animation state"""
    aaron.update(1/60)
    mani.update(1/60)
    glutPostRedisplay()

if __name__ == "__main__":
    # Test animation system
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Character Animation Test")
    
    init()
    
    aaron = CharacterRig("aaron")
    mani = CharacterRig("mani")
    
    aaron.play_animation("idle")
    mani.play_animation("idle")
    
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutIdleFunc(update)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutSpecialFunc(special_keys)
    glutMainLoop() 