bl_info = {
    "name": "Smart Collection Nesting",
    "author": "RimuruDev",
    "version": (1, 9),
    "blender": (4, 0, 0),
    "location": "View3D > Object > Context Menu + Option+M",
    "description": "Automatically nests new collection inside active one",
    "category": "Object",
}

import bpy

addon_keymaps = []

class OBJECT_OT_smart_collection(bpy.types.Operator):
    bl_idname = "object.smart_new_collection"
    bl_label = "Smart New Collection"
    bl_options = {'REGISTER', 'UNDO'}

    name: bpy.props.StringProperty(name="Collection Name", default="New Collection")

    def execute(self, context):
        active = context.active_object
        if not active or not active.users_collection:
            self.report({'WARNING'}, "No object or not inside a collection")
            return {'CANCELLED'}

        parent = active.users_collection[0]
        newcol = bpy.data.collections.new(self.name)
        parent.children.link(newcol)

        for obj in context.selected_objects:
            for col in obj.users_collection:
                col.objects.unlink(obj)
            newcol.objects.link(obj)

        self.report({'INFO'}, f"Collection '{self.name}' created in '{parent.name}'")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

def menu_func(self, context):
    self.layout.operator(OBJECT_OT_smart_collection.bl_idname, icon='GROUP')

def register():
    bpy.utils.register_class(OBJECT_OT_smart_collection)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    if hasattr(bpy.types, "VIEW3D_MT_object_move_to_collection"):
        bpy.types.VIEW3D_MT_object_move_to_collection.append(menu_func)

    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.get('Object Mode') or kc.keymaps.new(name='Object Mode', space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            OBJECT_OT_smart_collection.bl_idname,
            'M', 'PRESS',
            alt=True, shift=False, ctrl=False
        )
        addon_keymaps.append((km, kmi))

        km2 = kc.keymaps.get('Outliner') or kc.keymaps.new(name='Outliner', space_type='OUTLINER')
        kmi2 = km2.keymap_items.new(
            OBJECT_OT_smart_collection.bl_idname,
            'M', 'PRESS',
            alt=True, shift=False, ctrl=False
        )
        addon_keymaps.append((km2, kmi2))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.types.VIEW3D_MT_object.remove(menu_func)
    if hasattr(bpy.types, "VIEW3D_MT_object_move_to_collection"):
        bpy.types.VIEW3D_MT_object_move_to_collection.remove(menu_func)
    bpy.utils.unregister_class(OBJECT_OT_smart_collection)

if __name__ == "__main__":
    register()
