import bpy

# Basic blender addon info
bl_info = {
    "name": "Test GPT",
    "author": "GPT",
    "version": (1, 0),
    "blender": (3, 5, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Add a new object",
}

# Define the operator class
class CURB_OT_create(bpy.types.Operator):
    """Create a curb from an edge"""
    bl_idname = "curb.create"
    bl_label = "Create Curb"
    bl_options = {'REGISTER', 'UNDO'}

    # Define some properties for the operator
    height: bpy.props.FloatProperty(name="Height", default=0.1, precision=2)
    width: bpy.props.FloatProperty(name="Width", default=0.2, precision=2)
    bevel: bpy.props.FloatProperty(name="Bevel", default=0.05, precision=2)

    def execute(self, context):
        # Get the selected edge
        obj = context.active_object
        mesh = obj.data
        edge = None
        for e in mesh.edges:
            if e.select:
                edge = e
                break
        if edge is None:
            # No edge selected, handle this case
            self.report({'ERROR'}, "No edge selected")
            return {'CANCELLED'}

        # Get the vertices of the edge
        v1 = mesh.vertices[edge.vertices[0]]
        v2 = mesh.vertices[edge.vertices[1]]

        # Calculate some vectors for the curb
        edge_vec = v2.co - v1.co
        normal_vec = edge_vec.cross(obj.matrix_world @ obj.data.polygons[0].normal).normalized()
        height_vec = normal_vec * self.height
        width_vec = normal_vec * self.width
        bevel_vec = normal_vec * self.bevel

        # Create a new mesh for the curb
        curb_mesh = bpy.data.meshes.new("Curb")
        curb_obj = bpy.data.objects.new("Curb", curb_mesh)
        context.collection.objects.link(curb_obj)

        # Add vertices for the curb
        curb_verts = [
            v1.co,
            v1.co + height_vec,
            v1.co + height_vec + bevel_vec,
            v1.co + height_vec + width_vec,
            v2.co,
            v2.co + height_vec,
            v2.co + height_vec + bevel_vec,
            v2.co + height_vec + width_vec,
        ]
        curb_mesh.from_pydata(curb_verts, [], [])

        # Add faces for the curb
        bpy.ops.object.select_all(action='DESELECT')
        curb_obj.select_set(True)
        context.view_layer.objects.active = curb_obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.edge_face_add()
        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}

# Define the menu class
class CURB_MT_menu(bpy.types.Menu):
    """Menu for creating curbs"""
    bl_idname = "CURB_MT_menu"
    bl_label = "Curb Menu"

    def draw(self, context):
        layout = self.layout

        # Add an operator to the menu
        layout.operator(CURB_OT_create.bl_idname)

# Register and unregister functions
def register():
    # Register the classes
    bpy.utils.register_class(CURB_OT_create)
    bpy.utils.register_class(CURB_MT_menu)

    # Add the menu to the mesh add menu
    bpy.types.VIEW3D_MT_mesh_add.append(CURB_MT_menu.draw)

def unregister():
    # Remove the menu from the mesh add menu
    bpy.types.VIEW3D_MT_mesh_add.remove(CURB_MT_menu.draw)

    # Unregister the classes
    bpy.utils.unregister_class(CURB_MT_menu)
    bpy.utils.unregister_class(CURB_OT_create)

# Run register function when Blender starts
if __name__ == "__main__":
    register()