bl_info = {
    "name": "MH Stories 2 tool suite",
    "blender": (3, 6, 0),
    "version": (1, 3, 0),
    "category": "Import-Export",
}

import bpy
from bpy.types import Context, Menu, Panel, Operator
from bpy_extras.io_utils import ImportHelper, ExportHelper

import os
import platform
import numpy as np
import logging
logger = logging.getLogger("mhst2_import")
logger.propagate = False
import sys

from .ipr.ui import MHST2_IMPORT_PT_IprSettingPanel_1
from .ipr.ui import MHST2_IMPORT_PT_IprSettingPanel_2
from .ipr.ui import MHST2_ImportIpr

from .mod.ui import MHST2_IMPORT_PT_ModSettingPanel_1
from .mod.ui import MHST2_IMPORT_PT_ModSettingPanel_2
from .mod.ui import MHST2_ImportMod

from .tex.ui import MHST2_IMPORT_PT_TexSettingPanel_1
from .tex.ui import MHST2_IMPORT_PT_TexSettingPanel_2
from .tex.ui import MHST2_ImportTex

from .lmt.ui import MHST2_IMPORT_PT_LmtSettingPanel_1
from .lmt.ui import MHST2_ImportLmt

from .arc.arc_parser import bulk_extract_arc

class ColoredFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ANSI Coloring
        grey = "\x1b[38;20m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        bold_red = "\x1b[31;1m"
        _reset = "\x1b[0m"
        self.FORMATS = {
            logging.DEBUG: f"{grey}{self._fmt}{_reset}",
            logging.INFO: f"{grey}{self._fmt}{_reset}",
            logging.WARNING: f"{yellow}{self._fmt}{_reset}",
            logging.ERROR: f"{red}{self._fmt}{_reset}",
            logging.CRITICAL: f"{bold_red}{self._fmt}{_reset}"
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(levelname)s | %(message)s')
colored_formatter = formatter
is_windows = platform.system() == "Windows"
if not (is_windows and int(platform.release()) < 10):
    if is_windows:
        os.system("color")
    colored_formatter = ColoredFormatter('%(levelname)s | %(message)s')
handler.setFormatter(colored_formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)



class CustomAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    game_path: bpy.props.StringProperty(
        name="Unpacked game path",
        subtype='DIR_PATH',
    )

    installation_game_path: bpy.props.StringProperty(
        name="Installation game path",
        subtype='DIR_PATH',
    )
    
    logging_level: bpy.props.EnumProperty(
        name="Logging level",
        items = [('DEBUG','DEBUG','','',0), 
                 ('INFO','INFO','','',1),
                 ('WARNING','WARNING','','',2),
                 ('ERROR','ERROR','','',3)],
        default = 'INFO'
    )
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Path to where the game should be unpacked, or where it has been unpacked.")
        layout.prop(self, "game_path")
        layout.label(text="[Optionnal] Path to where the game is installed (the folder containing the .exe of the game), only necessary if you want to unpack the game.")
        layout.prop(self, "installation_game_path")
        layout.prop(self, "logging_level")
        row = layout.row()
        row.alert = True
        button = row.operator("mhst2_import.mhst2_extract_arc",
                         text="Unpack the game (check the system console for progress, might take around 10 minutes))",
                         icon="ERROR")


class MHST2_ArcExtract(bpy.types.Operator):
    bl_idname = "mhst2_import.mhst2_extract_arc"
    bl_label = "Bulk extract arc files"
    bl_options = {'REGISTER'}

    def execute(self, context):
        bulk_extract_arc(context)
        return {'FINISHED'}


class MHST2_import_menu(bpy.types.Menu):
    bl_label = "Monster Hunter Stories 2"
    bl_idname = "MHST2_MT_menu_import"

    def draw(self, context):
        self.layout.operator(MHST2_ImportMod.bl_idname, text="Model files (.mod)", icon="MESH_DATA")
        self.layout.operator(MHST2_ImportTex.bl_idname, text="Texture files (.tex)", icon="TEXTURE_DATA")
        self.layout.operator(MHST2_ImportLmt.bl_idname, text="Animation files (.lmt)", icon="ANIM_DATA")
        self.layout.operator(MHST2_ImportIpr.bl_idname, text="Map instance object files (.ipr)", icon="WORLD_DATA")

def MHST2_menu_func_import(self, context):
    self.layout.menu(MHST2_import_menu.bl_idname)

def register():
    bpy.utils.register_class(MHST2_ImportMod)
    bpy.utils.register_class(MHST2_ImportTex)
    bpy.utils.register_class(MHST2_ImportLmt)
    bpy.utils.register_class(MHST2_ImportIpr)
    bpy.utils.register_class(CustomAddonPreferences)
    bpy.utils.register_class(MHST2_IMPORT_PT_ModSettingPanel_1)
    bpy.utils.register_class(MHST2_IMPORT_PT_ModSettingPanel_2)
    bpy.utils.register_class(MHST2_IMPORT_PT_TexSettingPanel_1)
    bpy.utils.register_class(MHST2_IMPORT_PT_TexSettingPanel_2)
    bpy.utils.register_class(MHST2_IMPORT_PT_IprSettingPanel_1)
    bpy.utils.register_class(MHST2_IMPORT_PT_IprSettingPanel_2)
    bpy.utils.register_class(MHST2_IMPORT_PT_LmtSettingPanel_1)
    bpy.utils.register_class(MHST2_ArcExtract)
    bpy.utils.register_class(MHST2_import_menu)
    bpy.types.TOPBAR_MT_file_import.append(MHST2_menu_func_import)
    pass

def unregister():
    bpy.utils.unregister_class(MHST2_ImportMod)
    bpy.utils.unregister_class(MHST2_ImportTex)
    bpy.utils.unregister_class(MHST2_ImportLmt)
    bpy.utils.unregister_class(MHST2_ImportIpr)
    bpy.utils.unregister_class(CustomAddonPreferences)
    bpy.utils.unregister_class(MHST2_IMPORT_PT_ModSettingPanel_1)
    bpy.utils.unregister_class(MHST2_IMPORT_PT_ModSettingPanel_2)
    bpy.utils.unregister_class(MHST2_IMPORT_PT_TexSettingPanel_1)
    bpy.utils.unregister_class(MHST2_IMPORT_PT_TexSettingPanel_2)
    bpy.utils.unregister_class(MHST2_IMPORT_PT_IprSettingPanel_1)
    bpy.utils.unregister_class(MHST2_IMPORT_PT_IprSettingPanel_2)
    bpy.utils.unregister_class(MHST2_IMPORT_PT_LmtSettingPanel_1)
    bpy.utils.unregister_class(MHST2_ArcExtract)
    bpy.utils.unregister_class(MHST2_import_menu)
    bpy.types.TOPBAR_MT_file_import.remove(MHST2_menu_func_import)
    pass

