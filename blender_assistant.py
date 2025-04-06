bl_info = {
    "name": "Animation Assistant",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Assistant",
    "description": "Provides step-by-step guidance for animation tasks",
    "category": "Animation",
}

import bpy
import time
from bpy.types import Panel, Operator
from bpy.props import StringProperty, BoolProperty

class BLENDER_PT_assistant_panel(Panel):
    bl_label = "Animation Assistant"
    bl_idname = "BLENDER_PT_assistant_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Assistant'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Current Task Display
        box = layout.box()
        box.label(text="Current Task:")
        box.label(text=scene.current_task, icon='INFO')
        
        # Step-by-Step Guide
        box = layout.box()
        box.label(text="Steps:")
        for i, step in enumerate(scene.task_steps):
            row = box.row()
            row.prop(step, "completed", text="")
            row.label(text=step.text)
        
        # Help Buttons
        box = layout.box()
        box.label(text="Need Help?")
        row = box.row()
        row.operator("assistant.show_hint", text="Show Hint")
        row.operator("assistant.next_step", text="Next Step")
        
        # Task Selection
        box = layout.box()
        box.label(text="Select Task:")
        row = box.row()
        row.operator("assistant.start_task", text="Setup Rig").task = "SETUP_RIG"
        row = box.row()
        row.operator("assistant.start_task", text="Create Animation").task = "CREATE_ANIMATION"

class BLENDER_OT_show_hint(Operator):
    bl_idname = "assistant.show_hint"
    bl_label = "Show Hint"
    bl_description = "Show a hint for the current step"
    
    def execute(self, context):
        current_step = context.scene.current_step
        if current_step < len(context.scene.task_steps):
            step = context.scene.task_steps[current_step]
            self.report({'INFO'}, f"Hint: {step.hint}")
        return {'FINISHED'}

class BLENDER_OT_next_step(Operator):
    bl_idname = "assistant.next_step"
    bl_label = "Next Step"
    bl_description = "Move to the next step"
    
    def execute(self, context):
        scene = context.scene
        if scene.current_step < len(scene.task_steps) - 1:
            scene.current_step += 1
            scene.current_task = scene.task_steps[scene.current_step].text
        return {'FINISHED'}

class BLENDER_OT_start_task(Operator):
    bl_idname = "assistant.start_task"
    bl_label = "Start Task"
    bl_description = "Start a new task"
    
    task: StringProperty()
    
    def execute(self, context):
        scene = context.scene
        scene.task_steps.clear()
        
        if self.task == "SETUP_RIG":
            scene.current_task = "Setting up character model and rig"
            steps = [
                ("Create base mesh", "Press Shift+A > Mesh > Cube for the body base", False),
                ("Shape the body", "Use Edit Mode (Tab) to shape the cube into a basic body", False),
                ("Add head", "Extrude (E) from the body to create the head", False),
                ("Add arms", "Extrude from the body to create arms", False),
                ("Add legs", "Extrude from the body to create legs", False),
                ("Create armature", "Press Shift+A > Armature > Single Bone", False),
                ("Add spine bones", "Extrude (E) from the root bone to create spine", False),
                ("Add arm bones", "Extrude from spine to create arms", False),
                ("Add leg bones", "Extrude from pelvis to create legs", False),
                ("Name bones", "Select each bone and rename in Properties panel", False),
                ("Parent mesh to armature", "Select mesh, then armature, press Ctrl+P > With Automatic Weights", False)
            ]
        elif self.task == "CREATE_ANIMATION":
            scene.current_task = "Creating combat animation"
            steps = [
                ("Select armature", "Click on the character's armature", False),
                ("Set keyframe", "Press I to insert keyframe", False),
                ("Move bones", "Select and rotate bones for the pose", False),
                ("Add keyframe", "Press I again to add keyframe", False),
                ("Preview animation", "Press Space to play animation", False),
                ("Adjust timing", "Use the timeline to adjust keyframe positions", False)
            ]
        
        for text, hint, completed in steps:
            step = scene.task_steps.add()
            step.text = text
            step.hint = hint
            step.completed = completed
        
        scene.current_step = 0
        return {'FINISHED'}

class TaskStep(bpy.types.PropertyGroup):
    text: StringProperty()
    hint: StringProperty()
    completed: BoolProperty(default=False)

def register():
    bpy.utils.register_class(TaskStep)
    bpy.utils.register_class(BLENDER_PT_assistant_panel)
    bpy.utils.register_class(BLENDER_OT_show_hint)
    bpy.utils.register_class(BLENDER_OT_next_step)
    bpy.utils.register_class(BLENDER_OT_start_task)
    
    bpy.types.Scene.current_task = StringProperty(default="No active task")
    bpy.types.Scene.current_step = bpy.props.IntProperty(default=0)
    bpy.types.Scene.task_steps = bpy.props.CollectionProperty(type=TaskStep)

def unregister():
    bpy.utils.unregister_class(TaskStep)
    bpy.utils.unregister_class(BLENDER_PT_assistant_panel)
    bpy.utils.unregister_class(BLENDER_OT_show_hint)
    bpy.utils.unregister_class(BLENDER_OT_next_step)
    bpy.utils.unregister_class(BLENDER_OT_start_task)
    
    del bpy.types.Scene.current_task
    del bpy.types.Scene.current_step
    del bpy.types.Scene.task_steps

if __name__ == "__main__":
    register() 