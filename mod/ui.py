import bpy
from bpy.types import Panel
from bpy_extras.io_utils import ImportHelper, ExportHelper
import addon_utils

import os

import logging
logger = logging.getLogger("mhst2_import")

from .mod_loader import load_mod
from ..mrl.mrl_loader import load_mrl

def SetLoggingLevel(level):
    if level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    elif level == "INFO":
        logger.setLevel(logging.INFO)
    elif level == "WARNING":
        logger.setLevel(logging.WARNING)
    elif level == "ERROR":
        logger.setLevel(logging.ERROR)

class MHST2_IMPORT_PT_ModSettingPanel_1(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Import Settings"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "MHST2_IMPORT_OT_mhst2_mod"
    
    def draw(self, context):
        layout = self.layout
        sfile = context.space_data
        operator = sfile.active_operator
        
        layout.prop(operator, 'all_LOD')
        row = layout.row()
        row.enabled = not operator.all_LOD
        row.prop(operator, 'LOD')
        layout.prop(operator, 'fix_rotation')
        layout.prop(operator, 'fix_scale')
        layout.prop(operator, 'connect_bones')
        layout.prop(operator, 'import_material')
        row = layout.row()
        row.enabled = operator.import_material
        row.prop(operator, 'import_clc')
        row = layout.row()
        row.enabled = operator.import_material
        row.prop(operator, 'use_loaded_mat')
        row = layout.row()
        row.enabled = operator.import_material
        row.prop(operator, 'add_outline')


        

class MHST2_IMPORT_PT_ModSettingPanel_2(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Texture Settings"
    bl_parent_id = "MHST2_IMPORT_PT_ModSettingPanel_1"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "MHST2_IMPORT_OT_mhst2_mod"

    def draw(self, context):
        layout = self.layout
        
        sfile = context.space_data
        operator = sfile.active_operator
        layout.enabled = operator.import_material
        layout.prop(operator, 'use_png_cache')
        row = layout.row()
        row.enabled = operator.use_png_cache
        row.prop(operator, 'overwrite_png_cache')


class MHST2_ImportMod(bpy.types.Operator, ImportHelper):
    """Import from Mod file format (.mod)"""
    bl_idname = "mhst2_import.mhst2_mod"
    bl_label = 'Import MHST2 Mod'
    bl_options = {'UNDO'}
    filename_ext = ".mod"
    
    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    filter_glob: bpy.props.StringProperty(default="*.mod")
    all_LOD: bpy.props.BoolProperty(name="Import all LoD", description="Import all LoD", default=False)
    LOD: bpy.props.IntProperty(name="LoD", description="Import a specific Level of Detail (lower is more detailed)", default=0, min=0, max=10, step=1)
    fix_rotation: bpy.props.BoolProperty(name="Fix rotation", description="Rotate the mesh 90° to fit blender's frame of reference",  default=True)
    fix_scale: bpy.props.BoolProperty(name="Fix scale", description="Scale the mesh x0.1 to fit blender's frame of reference",  default=True)
    connect_bones: bpy.props.BoolProperty(name="Connect bones", description="Connect the bones to their children when available, WILL break animations",  default=False)
    import_material: bpy.props.BoolProperty(name="Import material", description="Import the material .mrl3 file",  default=True)
    import_clc: bpy.props.BoolProperty(name="Import extra colors", description="Import extra colors for monsters, located in a .clc file",  default=True)
    add_outline: bpy.props.BoolProperty(name="Add outline", description="Add an outline to the meshes",  default=True)
    use_loaded_mat: bpy.props.BoolProperty(name="Reuse loaded materials", description="Use already loaded materials when available, may cause glitches when two objects have similarly named materials", default=True)
    use_png_cache: bpy.props.BoolProperty(name="Use PNG cache", description="Save a copy of imported .tex in a .png file next to it (subsequent imports will be much faster)", default=True)
    overwrite_png_cache: bpy.props.BoolProperty(name="Overwrite PNG cache", description="Overwrite cached .png", default=False)
    
    def draw(self, context):
        pass

    def execute(self, context):
        #print("a")
        candidate_modules = [mod for mod in addon_utils.modules() if mod.bl_info["name"] == "MH Stories 2 tool suite"]
        if len(candidate_modules) > 1:
            logger.warning("Inconsistencies while loading the addon preferences: make sure you don't have multiple versions of the addon installed.")
        mod = candidate_modules[0]
        addon_prefs = context.preferences.addons[mod.__name__].preferences
        SetLoggingLevel(addon_prefs.logging_level)
        
        folder = (os.path.dirname(self.filepath))
        if len(self.files) == 0:
            filepaths = [str(self.filepath)]
        else:
            filepaths = [os.path.join(folder, x.name) for x in self.files]
        

        game_path = ""
        if self.import_material:
            if addon_prefs.game_path == "":
                self.report({"ERROR"}, "Import material was enabled, while the game path in not set in the addon preferences")
                return {"CANCELLED"}
            game_path = addon_prefs.game_path

        if self.import_material:
            logger.info("Linking node groups...")
            node_group_blend_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mrl", "new_materials_groups.blend")
            if not os.path.exists(node_group_blend_file):
                self.report({"ERROR"}, "Could not access node group .blend file")
                return {"CANCELLED"}
            logger.info("Importing nodes...")
            installed = [i.name for i in bpy.data.node_groups]
            por = []
            with bpy.data.libraries.load(node_group_blend_file, link = False) as (data_from, data_to):
                for i in data_from.node_groups:
                    if not i in installed:
                        por.append(i)
                data_to.node_groups = por
        
        if self.all_LOD:
            LOD = None
        else:
            LOD = self.LOD

        for filepath in filepaths:
            try:
                objs = load_mod(filepath, collection=None, LOD=LOD, fix_rotation=self.fix_rotation, fix_scale=self.fix_scale, connect_bones=self.connect_bones)
                if self.import_material:
                    mrl_filepath = ".".join(filepath.split(".")[:-1]) + ".mrl"
                    
                    try:
                        load_mrl(game_path, mrl_filepath, use_loaded_mat=self.use_loaded_mat, use_loaded_tex=True, use_png_cache=self.use_png_cache, overwrite_png_cache=self.overwrite_png_cache, import_clc=self.import_clc)
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        logger.warning("Unable to load material of path " + str(mrl_filepath) + ", reason = " + str(e))
                        self.report({"WARNING"}, "Unable to load material of path " + str(mrl_filepath) + ", reason = " + str(e))
                        continue
                        
                    if self.add_outline:
                        if context.scene.cycles.transparent_max_bounces == 8:
                            context.scene.cycles.transparent_max_bounces = 16
                        if "outline" in bpy.data.materials:
                            mat = bpy.data.materials["outline"]
                        else:
                            mat = bpy.data.materials.new(name="outline")
                            mat.use_nodes = True
                            mat.use_backface_culling = True
                            mat.blend_method = "HASHED"
                            if hasattr(mat, 'shadow_method'):
                                mat.shadow_method = "NONE"
                            nodes = mat.node_tree.nodes
                            links = mat.node_tree.links
                            node_BSDF = nodes["Principled BSDF"]
                            nodes.remove(node_BSDF)
                            outliner_node = nodes.new(type='ShaderNodeGroup')
                            outliner_node.location = [-500.0, 500.0]
                            outliner_node.node_tree = bpy.data.node_groups["outline_material"]
                            outliner_node.label = "outline_material"
                            node_output = nodes["Material Output"]
                            links.new(outliner_node.outputs["Shader"], node_output.inputs["Surface"])
                        for obj in objs:
                            if obj.type == "MESH":
                                if len(obj.material_slots) == 1:
                                    # Find the BM texture
                                    main_material = obj.material_slots[0].material
                                    main_nodes = main_material.node_tree.nodes
                                    img = None
                                    for main_node in main_nodes:
                                        if main_node.type == "TEX_IMAGE" and main_node.label == "AlbedoMap":
                                            img = main_node.image
                                            
                                    obj.data.materials.append(mat)
                                    mat_slot = obj.material_slots[1]
                                    mat_slot.link = 'OBJECT'
                                    mat_slot.material = mat
                                    
                                    
                                    outline_geonode = obj.modifiers.new("outline_geonode", 'NODES')
                                    outline_geonode.node_group = bpy.data.node_groups["outline_geonode"]
                                    outline_geonode["Input_2"] = 1.0
                                    # outline_geonode["Input_3"] = [1.0, 1.0, 1.0, 1.0]
                                    outline_geonode["Input_6"] = img
                                    outline_geonode["Input_5"] = mat
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.warning("Unable to load mod file of path " + str(filepath) + ", reason = " + str(e))
                self.report({"WARNING"}, "Unable to load mod file of path " + str(filepath) + ", reason = " + str(e))
                continue

        if self.import_material:
            for group in por:
                if group.users == 0:
                    bpy.data.node_groups.remove(group)

        return {"FINISHED"}


        
