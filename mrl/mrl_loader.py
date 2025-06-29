import bpy
from mathutils import Matrix, Vector

import numpy as np
import os
import logging
from glob import glob

from .mrl_parser import MrlParser
from .clc_parser import ClcParser
from ..tex.tex_loader import load_tex

logger = logging.getLogger("mhst2_import")

def string_reformat(s):
    if s[0] in ["t", "b", "f", "i"]:
        s = s[1:]
    elif beautified_texture_type.startswith("SS"):
        s = s[2:]
    return s.split("__")[0]

def create_img_node(game_path, nodes, filepath, position, use_loaded_tex=False, use_png_cache=False, overwrite_png_cache=False):
    node_img = nodes.new(type='ShaderNodeTexImage')
    node_img.location = Vector(position)

    if filepath is None:
        return node_img

    filepath = filepath.replace("\\", "/")
    new_filepath = os.path.join(game_path, filepath + ".tex")
    if not os.path.isfile(new_filepath):
        logger.warning("Could not load texture, file does not exists (path=" + new_filepath + ")")
        return node_img

    try:
        img = load_tex(new_filepath, use_loaded=use_loaded_tex, use_png_cache=use_png_cache, overwrite_png_cache=overwrite_png_cache)
    except Exception as e:
        if "Texture data format not supported" not in str(e):
            logger.warning("Could not load texture, exception during parsing (path=" + new_filepath + ", exception=" + str(e) + ")")
        img = None
    if img is not None:
        node_img.image = img
        node_img.extension = "REPEAT"

    return node_img

def load_mrl(game_path, filepath, mod_mat_hashes={}, use_loaded_mat=False, use_loaded_tex=False, use_png_cache=False, overwrite_png_cache=False, mat_prefix="", beautify=True, import_clc=False):
    parser = MrlParser(path=filepath)
    mat_dict = parser.read()
    returned_mats = []
    
    extra_color = None
    if import_clc:
        try:
            clc_files = glob(os.path.join(os.path.dirname(filepath), ".", "*.clc"), recursive=True)
            if len(clc_files) == 0:
                clc_files = glob(os.path.join(os.path.dirname(filepath), ".", "**", "*.clc"), recursive=True)
            if len(clc_files) == 0:
                clc_files = glob(os.path.join(os.path.dirname(filepath), "..", "**", "*.clc"), recursive=True)
            if len(clc_files) > 0:
                # print(clc_files)
                clc_file = sorted(clc_files, key=len)[0]
                clc_parser = ClcParser(clc_file)
                extra_color = clc_parser.read()["color"] + [1.0]
                # print(extra_color)
        except:
            pass

    existing_mat_hashes = {}
    for material in bpy.data.materials:
        if "original_name" in material.keys() and "name_hash" in material.keys():
            existing_mat_hashes[int(material["name_hash"])] = material["original_name"]
    
    for mat_hashed_name, mat_values in mat_dict.items():


        if mat_hashed_name in existing_mat_hashes.keys():
            mat_name = existing_mat_hashes[mat_hashed_name]
        else:
            #print("AAAAAAAAAAAA")
            continue

        mat_name = mat_prefix + mat_name
        if len(mat_name) > 55:
            #FUCK blender
            mat_name = "HASHED_" + str(abs(int(hash(mat_name)))).zfill(20)
        
        if use_loaded_mat:
            if mat_name in bpy.data.materials and bpy.data.materials[mat_name].use_nodes:
                returned_mats.append(bpy.data.materials[mat_name])
                continue
        if mat_name not in bpy.data.materials or bpy.data.materials[mat_name].use_nodes == True:
            mat = bpy.data.materials.new(name=mat_name)
        else:
            mat = bpy.data.materials[mat_name]
        
        if mat.use_nodes == False:
            mat.use_nodes = True
        
        mat["shader_hash"] = str(mat_values["shader_hash"])

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        general_frame_x = -1650.0
        general_frame_y = 500.0
        property_frame_x = -1400.0
        property_frame_y = 500.0
        texture_frame_x = -1000.0
        texture_frame_y = 500.0
        general_frame = nodes.new(type='NodeFrame')
        general_frame.label = "General"
        property_frame = nodes.new(type='NodeFrame')
        property_frame.label = "Properties"
        texture_frame = nodes.new(type='NodeFrame')
        texture_frame.label = "Texture paths for export are in the custom properties"
        texture_frame.label_size = 12

        node_BSDF = nodes["Principled BSDF"]
        nodes.remove(node_BSDF)
        st2_shader_node = nodes.new(type='ShaderNodeGroup')
        st2_shader_node.location = Vector((-500.0, 500.0))
        st2_shader_node.node_tree = bpy.data.node_groups["STShader"]
        st2_shader_node.label = "ST2Shader"
        #node_UVMap1 = nodes.new(type='ShaderNodeUVMap')
        #node_UVMap1.location = Vector((general_frame_x, general_frame_y-0.0))
        #node_UVMap1.uv_map = "UV1"
        #node_UVMap1.parent = general_frame
        #node_UVMap2 = nodes.new(type='ShaderNodeUVMap')
        #node_UVMap2.location = Vector((general_frame_x, general_frame_y-100.0))
        #node_UVMap2.uv_map = "UV2"
        #node_UVMap2.parent = general_frame
        #node_UVMap3 = nodes.new(type='ShaderNodeUVMap')
        #node_UVMap3.location = Vector((general_frame_x, general_frame_y-200.0))
        #node_UVMap3.uv_map = "UV3"
        #node_UVMap3.parent = general_frame
        #node_UVMap4 = nodes.new(type='ShaderNodeUVMap')
        #node_UVMap4.location = Vector((general_frame_x, general_frame_y-300.0))
        #node_UVMap4.uv_map = "UV4"
        #node_UVMap4.parent = general_frame
        node_VertexColor = nodes.new(type='ShaderNodeVertexColor')
        node_VertexColor.location = Vector((general_frame_x, general_frame_y-400.0))
        node_VertexColor.layer_name = "Attribute"
        node_VertexColor.parent = general_frame
        #node_geometry = nodes.new(type='ShaderNodeNewGeometry')
        #node_geometry.location = Vector((general_frame_x, general_frame_y-500.0))
        #node_geometry.parent = general_frame
        #node_object_info = nodes.new(type='ShaderNodeObjectInfo')
        #node_object_info.location = Vector((general_frame_x, general_frame_y-700.0))
        #node_object_info.parent = general_frame
        node_output = nodes["Material Output"]
        links.new(st2_shader_node.outputs["Shader"], node_output.inputs["Surface"])
        #links.new(st2_shader_node.outputs["Displacement"], node_output.inputs["Displacement"])

        texture_node_dict = {}
        for texture_i, texture_type in enumerate(mat_values["textures"].keys()):
            try:
                texture_path = mat_values["textures"][texture_type]
                node_position = (texture_frame_x, texture_frame_y)
                texture_frame_y -= 300.0
                node_img = create_img_node(game_path, nodes, texture_path, node_position, use_loaded_tex=use_loaded_tex, use_png_cache=use_png_cache, overwrite_png_cache=overwrite_png_cache)
                texture_node_dict[texture_type] = node_img
                node_img.parent = texture_frame

                image_node_name = string_reformat(texture_type)
                #if beautify:
                node_img.label = image_node_name
                #else:
                    #node_img.label = texture_type

                mat[texture_type] = texture_path
            except Exception as e:
                logger.warning("Exception while connecting textures (path=" + filepath + ", exception=" + str(e) + ")")


        if "tAlbedoBlendMapR" in texture_node_dict.keys():
            separate_node = nodes.new('ShaderNodeSeparateColor')
            links.new(node_VertexColor.outputs["Color"], separate_node.inputs[0])

            mix_node_bm_1 = nodes.new('ShaderNodeMix')
            mix_node_bm_1.data_type = "RGBA"
            links.new(separate_node.outputs["Red"], mix_node_bm_1.inputs["Factor"])
            links.new(texture_node_dict["tAlbedoMap"].outputs["Color"], mix_node_bm_1.inputs[6])
            links.new(texture_node_dict["tAlbedoBlendMapR"].outputs["Color"], mix_node_bm_1.inputs[7])

            mix_node_bm_2 = nodes.new('ShaderNodeMix')
            mix_node_bm_2.data_type = "RGBA"
            links.new(separate_node.outputs["Green"], mix_node_bm_2.inputs["Factor"])
            links.new(mix_node_bm_1.outputs[2], mix_node_bm_2.inputs[6])
            links.new(texture_node_dict["tAlbedoBlendMapG"].outputs["Color"], mix_node_bm_2.inputs[7])
            links.new(mix_node_bm_2.outputs[2], st2_shader_node.inputs["BM"])

            mix_node_nm_1 = nodes.new('ShaderNodeMix')
            mix_node_nm_1.data_type = "RGBA"
            links.new(separate_node.outputs["Red"], mix_node_nm_1.inputs["Factor"])
            links.new(texture_node_dict["tNormalMap"].outputs["Color"], mix_node_nm_1.inputs[6])
            links.new(texture_node_dict["tNormalBlendMapR"].outputs["Color"], mix_node_nm_1.inputs[7])

            mix_node_nm_2 = nodes.new('ShaderNodeMix')
            mix_node_nm_2.data_type = "RGBA"
            links.new(separate_node.outputs["Green"], mix_node_nm_2.inputs["Factor"])
            links.new(mix_node_nm_1.outputs[2], mix_node_nm_2.inputs[6])
            links.new(texture_node_dict["tNormalBlendMapG"].outputs["Color"], mix_node_nm_2.inputs[7])
            links.new(mix_node_nm_2.outputs[2], st2_shader_node.inputs["NM"])
        else:
            if "tAlbedoMap" in texture_node_dict.keys():
                links.new(texture_node_dict["tAlbedoMap"].outputs["Color"], st2_shader_node.inputs["BM"])
                #if mat_values["shader_hash"] != 1605430244:
                links.new(texture_node_dict["tAlbedoMap"].outputs["Alpha"], st2_shader_node.inputs["BM_A"])

            if "tAlbedoMaskMap" in texture_node_dict.keys():
                links.new(texture_node_dict["tAlbedoMaskMap"].outputs["Color"], st2_shader_node.inputs["CMM"])

            if "tEmissionMap" in texture_node_dict.keys():
                links.new(texture_node_dict["tEmissionMap"].outputs["Color"], st2_shader_node.inputs["EM"])
                #links.new(texture_node_dict["tEmissionMap"].outputs["Alpha"], st2_shader_node.inputs["BM_A"])

            if "tNormalMap" in texture_node_dict.keys():
                links.new(texture_node_dict["tNormalMap"].outputs["Color"], st2_shader_node.inputs["NM"])

        if extra_color is not None:
            st2_shader_node.inputs["Color 2"].default_value = extra_color

        mat.blend_method = "HASHED"
        if hasattr(mat, 'shadow_method'):
            mat.shadow_method = "HASHED"
        
        returned_mats.append(mat)
    return returned_mats
