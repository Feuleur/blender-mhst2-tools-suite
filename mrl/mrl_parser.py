import struct
import os
from glob import glob
import json
import logging
logger = logging.getLogger("mhst2_import")

class Reader():
    def __init__(self, data):
        self.offset = 0
        self.data = data

    def read(self, kind, size):
        result = struct.unpack(kind, self.data[self.offset:self.offset+size])[0]
        self.offset += size
        return result

    def seek(self, offset, start = None):
        if start is None:
            self.offset = offset
        else:
            self.offset += offset

    def readUInt(self):
        return self.read("I", 4)

    def readInt(self):
        return self.read("i", 4)

    def readUInt64(self):
        return self.read("Q", 8)

    def readHalf(self):
        return self.read("e", 2)

    def readFloat(self):
        return self.read("f", 4)

    def readShort(self):
        return self.read("h", 2)

    def readUShort(self):
        return self.read("H", 2)

    def readByte(self):
        return self.read("b", 1)

    def readBytes(self, size):
        return self.data[self.offset:self.offset + size]

    def readUByte(self):
        return self.read("B", 1)

    def readString(self):
        text = ""
        while True:
            char = self.readUByte()
            if char == 0:
                break
            else:
                text += chr(char)
        return text

    def readStringUTFAt(self, offset):
        previous_offset = self.tell()
        self.seek(offset)
        text = ""
        while True:
            char = self.readUShort()
            if char == 0:
                break
            else:
                text += chr(char)
        self.seek(previous_offset)
        return text

    def readStringUTF(self):
        text = ""
        while True:
            char = self.readUShort()
            if char == 0:
                break
            else:
                text += chr(char)
        return text

    def allign(self, size):
        self.offset = (int((self.offset)/size)*size)+size

    def tell(self):
        return self.offset

    def getSize(self):
        return len(self.data)

class MrlParser():
    def __init__(self, path=None, data=None):
        self.path = path
        if data is None:
            with open(path, "rb") as file_in:
                data = file_in.read()
        self.bs = Reader(data)
        self.debug_data = {}
        local_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(local_path, "resources_dict.json"), "r") as json_in:
            self.resources_dict = json.load(json_in)
        #with open(os.path.join(local_path, "property_dict.json"), "r") as json_in:
            #self.property_dict = json.load(json_in)
        #with open(os.path.join(local_path, "shader_dict.json"), "r") as json_in:
            #self.shader_dict = json.load(json_in)


    def read(self):
        self.magic = self.bs.readUInt()
        if self.magic != 5001805:
            raise RuntimeError(str(self.path) + " is not a mdf2 file (magic = " + str(self.magic) + ")")
        version = self.bs.readUInt()
        mat_count = self.bs.readUInt()
        tex_count = self.bs.readUInt()
        _ = self.bs.readUInt()
        _ = self.bs.readUInt()
        tex_offset = self.bs.readUInt64()
        mat_offset = self.bs.readUInt64()

        texture_paths = []
        tex_size_dict = {
            0x00000000:58, #0
            0x451e3333:94, #1159607091
            0x59993333:152, #1503212339
            0xc53e7fff:94, #3309207551
            0xcccc9999:94, #3435960729
            0x241f5deb:24+128, #606035435
            0x60850864:94,
            0xe6cfbabe:94,
        }

        self.bs.seek(tex_offset)
        tex_i = 0
        while tex_i < tex_count:

        #for tex_i in range(tex_count):
            tex_origin = self.bs.tell()
            tex_hash = self.bs.readUInt()
            #print(hex(tex_hash))
            if tex_hash in tex_size_dict.keys():
                if tex_hash == 606035435:
                    self.bs.readUInt()
                    self.bs.readUInt64()
                    self.bs.readUInt64()
                    #self.bs.seek(tex_offset + (256+16)*tex_i)
                    texture_paths.append(self.bs.readString())
                    tex_i += 1
                elif tex_hash == 0:
                    pass
                else:
                    texture_paths.append(None)
                    tex_i += 1
                self.bs.seek(tex_origin+tex_size_dict[tex_hash])
            else:
                texture_paths.append(None)
                tex_i += 1
                #print("UNKNOWN TEXTURE", hex(tex_hash))
                self.bs.seek(tex_origin+94)
            #self.bs.seek(tex_offset + (256+16)*tex_i)
            #self.bs.seek(tex_offset + (0x130)*tex_i)

        #print(texture_paths)
        self.bs.seek(mat_offset)
        #mat_offset
        mat_infos = []
        for mat_i in range(mat_count):
            mat_info = {}
            mat_info["shader_hash"] = self.bs.readUInt()
            #print(mat_info["shader_hash"])
            mat_info["unk1"] = self.bs.readUInt()
            mat_info["matname_hash"] = self.bs.readUInt()
            mat_info["mat_size"] = self.bs.readUInt()

            mat_info["unk2"] = self.bs.readUInt()
            mat_info["unk3"] = self.bs.readUInt()
            mat_info["unk4"] = self.bs.readUInt()
            mat_info["data_size"] = self.bs.readUByte()
            mat_info["unk5"] = self.bs.readUByte()
            mat_info["alpha_coef"] = self.bs.readUByte()
            mat_info["unk6"] = self.bs.readUByte()

            mat_info["unk7"] = self.bs.readUInt()
            mat_info["unk8"] = self.bs.readUInt()
            mat_info["unk9"] = self.bs.readUInt()
            mat_info["unk10"] = self.bs.readUInt()

            mat_info["unk11"] = self.bs.readUInt()
            mat_info["unk12"] = self.bs.readUInt()
            mat_info["data_offset"] = self.bs.readUInt64()

            mat_info["unk13"] = self.bs.readUInt64()
            mat_infos.append(mat_info)
        #print(mat_infos)
        all_materials = {}
        for mat_i, mat_info in enumerate(mat_infos):
            current_material = {}
            current_material["shader_hash"] = mat_info["shader_hash"]
            current_material["textures"] = {}
            current_material["properties"] = {}
            current_material["matname_hash"] = mat_info["matname_hash"]
            self.bs.seek(mat_info["data_offset"])
            property_infos = []
            #print(mat_info["data_size"])
            for data_i in range(mat_info["data_size"]):
                ressource_type = self.bs.readUByte()
                _ = self.bs.readUByte()
                _ = self.bs.readUByte()
                _ = self.bs.readUByte()

                _ = self.bs.readUInt()
                ressource_id = self.bs.readUInt()
                _ = self.bs.readUInt()
                ressource_hash = self.bs.readUInt()
                _ = self.bs.readUInt()

                if ressource_type & 0xF == 3:
                    if hex(ressource_hash) in self.resources_dict.keys():
                        #print(self.resources_dict[hex(ressource_hash)], mat_i, data_i, ressource_id)
                        #print(texture_paths)
                        current_material["textures"][self.resources_dict[hex(ressource_hash)]] = texture_paths[ressource_id-1]
                if ressource_type & 0xF == 0:
                    if hex(ressource_hash) in self.resources_dict.keys():
                        current_material["properties"][self.resources_dict[hex(ressource_hash)]] = None
                    else:
                        print("UNKNOWN PROPERTY")
            #current_material["property_block_hashes"] = property_infos
            #property_block_names = [self.property_dict[str(x)]["name"] for x in property_infos]
            #current_material["property_block_names"] = property_block_names.copy()
            #property_block_names.remove("CBMaterialCommon__disclosure")
            ##current_material["shader_name"] = property_block_names[0]
            #for property_name in current_material["properties"]:
            #print(mat_info["matname_hash"])
            #if mat_info["shader_hash"] == 1050971523:

                #properties = []
                #for x in range(40):
                    #properties.append([self.bs.readFloat() for _ in range(4)].copy())
                    ##print(properties[-1])
                #current_material["raw_properties"] = properties.copy()
            #print("\n\n\n")
            #for property_info in property_infos:
                #if "fields" in self.property_dict[str(property_info)].keys():
                    #for field_name, field_type_raw in self.property_dict[str(property_info)]["fields"].items():
                        ##print(field_name)
                        #if field_type_raw.find("[") != -1:
                            #field_type = field_type_raw[:field_type_raw.find("[")]
                            #array_size = int(field_type_raw[field_type_raw.find("[")+1:field_type_raw.find("]")])
                        #else:
                            #field_type = field_type_raw
                            #array_size = 1
                        #content = []
                        #for field_i in range(array_size):
                            #if field_type == "float":
                                #content.append(self.bs.readFloat())
                            #elif field_type == "uint":
                                #content.append(self.bs.readUInt())
                            #elif field_type == "int":
                                #content.append(self.bs.readInt())
                            #elif field_type == "ubyte":
                                #content.append(self.bs.readUByte())
                            #elif field_type == "byte":
                                #content.append(self.bs.readByte())
                            #elif field_type == "bbool":
                                #content.append(bool(self.bs.readUInt() >> 30))
                            #else:
                                #print("ERROR ERROR", field_type)
                                #content.append(self.bs.readFloat())
                        #current_material["properties"][field_name] = content
            all_materials[mat_info["matname_hash"]] = current_material
            #print(current_material)
        return all_materials

if __name__ == "__main__":
    from glob import glob
    mrl_files = glob("./*.mrl", recursive=True)

    all_properties = []
    for mrl_file in mrl_files:
        #print(mrl_file)
        parser = MrlParser(path=mrl_file)
        material_datas = parser.read()
        for material_data in material_datas.values():
            if "raw_properties" in material_data.keys():
                all_properties.append(material_data["raw_properties"])
        #import json
        #print(json.dumps(material_data, indent=4))
    #import numpy as np
    #for i in range(len(all_properties)):
        #print(len(all_properties[i]))
    #print()
    #print(np.mean(np.array(all_properties), axis=0))
    #print(np.std(np.array(all_properties), axis=0))
