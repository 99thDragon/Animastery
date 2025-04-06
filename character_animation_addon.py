bl_info = {
    "name": "Character Combat Animation",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Combat Animation",
    "description": "Create and manage combat animations for Aaron and Mani",
    "category": "Animation",
}

import bpy
import math
from mathutils import Vector, Euler

class COMBAT_PT_animation_panel(bpy.types.Panel):
    bl_label = "Combat Animation"
    bl_idname = "COMBAT_PT_animation_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Combat Animation'

    def draw(self, context):
        layout = self.layout
        
        # Character selection
        row = layout.row()
        row.prop(context.scene, "combat_character", text="Character")
        
        # Animation buttons
        box = layout.box()
        box.label(text="Combat Moves")
        
        if context.scene.combat_character == 'AARON':
            col = box.column(align=True)
            col.operator("combat.create_animation", text="Idle Stance").animation_type = 'AARON_IDLE'
            col.operator("combat.create_animation", text="Scythe Swing").animation_type = 'AARON_SWING'
            col.operator("combat.create_animation", text="Scythe Spin").animation_type = 'AARON_SPIN'
            col.operator("combat.create_animation", text="Block").animation_type = 'AARON_BLOCK'
            col.operator("combat.create_animation", text="Combo Attack").animation_type = 'AARON_COMBO'
        else:
            col = box.column(align=True)
            col.operator("combat.create_animation", text="Idle Stance").animation_type = 'MANI_IDLE'
            col.operator("combat.create_animation", text="Energy Blade").animation_type = 'MANI_BLADE'
            col.operator("combat.create_animation", text="Energy Burst").animation_type = 'MANI_BURST'
            col.operator("combat.create_animation", text="Defense").animation_type = 'MANI_DEFENSE'
            col.operator("combat.create_animation", text="Combo Attack").animation_type = 'MANI_COMBO'

class COMBAT_OT_create_animation(bpy.types.Operator):
    bl_idname = "combat.create_animation"
    bl_label = "Create Combat Animation"
    bl_options = {'REGISTER', 'UNDO'}
    
    animation_type: bpy.props.StringProperty()
    
    def execute(self, context):
        # Get the active armature
        armature = context.active_object
        if not armature or armature.type != 'ARMATURE':
            self.report({'ERROR'}, "Please select an armature")
            return {'CANCELLED'}
        
        # Create animation based on type
        if self.animation_type == 'AARON_IDLE':
            self.create_aaron_idle(armature)
        elif self.animation_type == 'AARON_SWING':
            self.create_aaron_swing(armature)
        elif self.animation_type == 'AARON_SPIN':
            self.create_aaron_spin(armature)
        elif self.animation_type == 'MANI_IDLE':
            self.create_mani_idle(armature)
        elif self.animation_type == 'MANI_BLADE':
            self.create_mani_blade(armature)
        elif self.animation_type == 'MANI_BURST':
            self.create_mani_burst(armature)
        
        return {'FINISHED'}
    
    def create_aaron_idle(self, armature):
        # Set up idle animation for Aaron
        self.create_keyframes(armature, {
            'spine': [(0, (0,0,0)), (24, (5,0,0))],
            'right_shoulder': [(0, (30,0,0)), (24, (35,0,0))],
            'right_arm': [(0, (0,30,0)), (24, (0,35,0))]
        }, "Aaron_Idle", 48)
    
    def create_aaron_swing(self, armature):
        # Set up scythe swing animation
        self.create_keyframes(armature, {
            'spine': [(0, (0,-30,0)), (12, (0,30,0)), (24, (0,15,0))],
            'right_shoulder': [(0, (-45,0,0)), (12, (45,0,0)), (24, (60,0,0))],
            'right_arm': [(0, (0,-90,0)), (12, (0,0,0)), (24, (0,45,0))]
        }, "Aaron_Swing", 36)
    
    def create_aaron_spin(self, armature):
        # Set up scythe spin animation
        self.create_keyframes(armature, {
            'spine': [(0, (0,0,0)), (24, (0,360,0))],
            'right_shoulder': [(0, (0,0,0)), (24, (0,360,0))],
            'right_arm': [(0, (0,0,0)), (24, (0,360,0))]
        }, "Aaron_Spin", 48)
    
    def create_mani_idle(self, armature):
        # Set up idle animation for Mani
        self.create_keyframes(armature, {
            'spine': [(0, (0,0,0)), (24, (5,0,0))],
            'left_shoulder': [(0, (20,0,0)), (24, (25,0,0))],
            'right_shoulder': [(0, (20,0,0)), (24, (25,0,0))]
        }, "Mani_Idle", 48)
    
    def create_mani_blade(self, armature):
        # Set up energy blade animation
        self.create_keyframes(armature, {
            'spine': [(0, (0,-45,0)), (12, (0,45,0)), (24, (0,30,0))],
            'right_shoulder': [(0, (-90,0,0)), (12, (45,0,0)), (24, (60,0,0))],
            'right_arm': [(0, (0,-45,0)), (12, (0,0,0)), (24, (0,30,0))]
        }, "Mani_Blade", 36)
    
    def create_mani_burst(self, armature):
        # Set up energy burst animation
        self.create_keyframes(armature, {
            'spine': [(0, (0,0,0)), (24, (0,0,0))],
            'left_shoulder': [(0, (45,0,0)), (24, (90,0,0))],
            'right_shoulder': [(0, (45,0,0)), (24, (90,0,0))],
            'left_arm': [(0, (0,90,0)), (24, (0,180,0))],
            'right_arm': [(0, (0,90,0)), (24, (0,180,0))]
        }, "Mani_Burst", 48)
    
    def create_keyframes(self, armature, bone_keyframes, action_name, frame_end):
        # Create new action if it doesn't exist
        action = bpy.data.actions.new(name=action_name)
        if not armature.animation_data:
            armature.animation_data_create()
        armature.animation_data.action = action
        
        # Set keyframes for each bone
        for bone_name, keyframes in bone_keyframes.items():
            if bone_name in armature.pose.bones:
                bone = armature.pose.bones[bone_name]
                for frame, rotation in keyframes:
                    bone.rotation_euler = Euler(map(math.radians, rotation))
                    bone.keyframe_insert(data_path="rotation_euler", frame=frame)
        
        # Set end frame
        bpy.context.scene.frame_end = frame_end

def register():
    bpy.utils.register_class(COMBAT_PT_animation_panel)
    bpy.utils.register_class(COMBAT_OT_create_animation)
    bpy.types.Scene.combat_character = bpy.props.EnumProperty(
        items=[
            ('AARON', "Aaron", "Aaron's combat animations"),
            ('MANI', "Mani", "Mani's combat animations")
        ],
        default='AARON'
    )

def unregister():
    bpy.utils.unregister_class(COMBAT_PT_animation_panel)
    bpy.utils.unregister_class(COMBAT_OT_create_animation)
    del bpy.types.Scene.combat_character

if __name__ == "__main__":
    register() 