import struct
import codecs
import json
import zlib
from glob import glob
import os
import math
import numpy as np
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

class ModParser():
    def __init__(self, path=None, data=None):
        self.path = path
        if data is None:
            with open(path, "rb") as file_in:
                data = file_in.read()
        self.bs = Reader(data)

    def read(self):
        self.magic = self.bs.readUInt()
        self.version = self.bs.readUShort()
        if self.magic != 4476749 or self.version != 214:
            raise RuntimeError(str(self.path) + " is not a mhstories mod file (magic = " + str(self.magic) + ", version = " + str(self.version) + ")")

        bone_count = self.bs.readUShort()
        mesh_count = self.bs.readUShort()
        mat_count = self.bs.readUShort()
        vert_count = self.bs.readUInt()
        face_count = self.bs.readUInt()
        edge_count = self.bs.readUInt()
        vbuffer_size = self.bs.readUInt64()
        group_count = self.bs.readUInt64()
        bone_offset = self.bs.readUInt64()
        group_offset = self.bs.readUInt64()
        matname_offset = self.bs.readUInt64()

        mesh_offset = self.bs.readUInt64()
        vbuffer_offset = self.bs.readUInt64()
        fbuffer_offset = self.bs.readUInt64()
        _offset_4 = self.bs.readUInt64()

        bsphere_x = self.bs.readFloat()
        bsphere_y = self.bs.readFloat()
        bsphere_z = self.bs.readFloat()
        bsphere_r = self.bs.readFloat()
        bbox_minx = self.bs.readFloat()
        bbox_miny = self.bs.readFloat()
        bbox_minz = self.bs.readFloat()
        bbox_minw = self.bs.readFloat()
        bbox_maxx = self.bs.readFloat()
        bbox_maxy = self.bs.readFloat()
        bbox_maxz = self.bs.readFloat()
        bbox_maxw = self.bs.readFloat()

        mesh_position = np.array([bbox_minx, bbox_miny, bbox_minz])
        mesh_scaling = max([(bbox_maxx-bbox_minx), (bbox_maxy-bbox_miny), (bbox_maxz-bbox_minz)])

        materials = []
        for mat_i in range(mat_count):
            self.bs.seek(matname_offset + mat_i*128)
            material_name = self.bs.readString()
            materials.append(material_name)

        skeleton_infos = []
        self.bs.seek(bone_offset)
        armature_datas = []
        mesh_scale = None
        if bone_count != 0:
            for bone_i in range(bone_count):
                bone_info = {}
                bone_info["id"] = bone_i
                bone_info["function"] = self.bs.readUShort()
                bone_info["parent"] = self.bs.readUByte()
                bone_info["child"] = self.bs.readUByte()
                bone_info["float1"] = self.bs.readFloat()
                bone_info["length"] = self.bs.readFloat()
                # print(hex(self.bs.tell()), bone_info["function"], bone_i)
                bone_info["x"] = self.bs.readFloat()
                bone_info["y"] = self.bs.readFloat()
                bone_info["z"] = self.bs.readFloat()
                # print(bone_info["x"], bone_info["y"], bone_info["z"])
                armature_datas.append(bone_info)

            for bone_i in range(bone_count):
                # if bone_i == 42:
                    # print(hex(self.bs.tell()))
                matrix = []
                matrix.append([self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat()])
                matrix.append([self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat()])
                matrix.append([self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat()])
                matrix.append([self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat()])
                armature_datas[bone_i]["local_matrix"] = matrix
            for bone_i in range(bone_count):
                # if bone_i == 42:
                    # print(hex(self.bs.tell()))
                matrix = []
                matrix.append([self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat()])
                matrix.append([self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat()])
                matrix.append([self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat()])
                matrix.append([self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat(), self.bs.readFloat()])
                if mesh_scale is None:
                    mesh_scale = [matrix[0][0], matrix[1][1], matrix[2][2]]
                armature_datas[bone_i]["global_matrix"] = matrix
            remap_tmp = list(range(4096))
            for bone_i in range(4096):
                remapping = self.bs.readUByte()
                if remapping != 255:
                    remap_tmp[remapping] = bone_i
                    try:
                        armature_datas[remapping]["remap"] = bone_i
                    except:
                        pass
            for bone_i, bone_info in enumerate(armature_datas):
                if "remap" not in bone_info:
                    bone_info["remap"] = bone_i
            remap_np = np.array(remap_tmp, np.uint32)
        if mesh_scale is None:
            mesh_scale = [1.0, 1.0, 1.0]

        mesh_scaling = max(mesh_scale)

        mesh_infos = []

        cumsum = 0
        has_lod = False
        for mesh_i in range(mesh_count):

            self.bs.seek(mesh_offset+(mesh_i*0x38))
            mesh_info = {}
            mesh_info["shadow_flags"] = self.bs.readUShort()
            mesh_info["vert_count"] = self.bs.readUShort()
            mesh_info["group"] = self.bs.readUByte()
            mesh_info["mat_idx"] = int(self.bs.readUShort()/16)
            tmp_lod = self.bs.readUByte()
            if tmp_lod != 0xff:
                has_lod = True
            lod_dict = {
                0x01:0,
                0x02:1,
                0x0C:2,
                0x81:0,
                0x82:1,
                0x8c:2,
                0x7f:3,
                0xff:4
            }
            mesh_info["ori_lod"] = tmp_lod
            if tmp_lod in lod_dict.keys():
                mesh_info["lod"] = lod_dict[tmp_lod]
            else:
                mesh_info["lod"] = 0
            mesh_info["unk_short_1"] = self.bs.readUShort()

            mesh_info["blocksize"] = self.bs.readUByte()
            mesh_info["unk_byte_3"] = self.bs.readUByte() #44

            mesh_info["unk_short_2"] = self.bs.readUShort()
            mesh_info["unk_short_3"] = self.bs.readUShort()
            mesh_info["buffer_offset"] = self.bs.readUInt()
            mesh_info["encoding"] = self.bs.readUInt()

            mesh_info["face_sub"] = self.bs.readUInt()
            mesh_info["face_count"] = self.bs.readUInt()
            mesh_info["unk_int_1"] = self.bs.readUInt()
            mesh_info["unk_short_4"] = self.bs.readUShort()
            mesh_info["unk_short_45"] = self.bs.readUShort()


            mesh_info["unk_short_5"] = self.bs.readUShort()
            mesh_info["unk_short_6"] = self.bs.readUShort()
            mesh_info["unk_int_2"] = self.bs.readUInt()
            mesh_info["unk_int_3"] = self.bs.readUInt()
            mesh_info["unk_int_4"] = self.bs.readUInt()
            mesh_infos.append(mesh_info)
            cumsum += mesh_info["blocksize"]*mesh_info["vert_count"]

        mesh_datas = []
        for mesh_i, mesh_info in enumerate(mesh_infos[:]):

            mesh = {}

            mesh_offset = vbuffer_offset + mesh_info["buffer_offset"] + mesh_info["unk_int_1"]*mesh_info["blocksize"]
            mesh_poss = []
            mesh_faces = []
            mesh_norms = None
            mesh_uv1s = None
            mesh_uv2s = None
            mesh_weights_names = None
            mesh_weights_values = None
            mesh_colors = None
            mesh_colors2 = None
            self.bs.seek(mesh_offset)
            vert_bytes = self.bs.readBytes(mesh_info["blocksize"] * (mesh_info["vert_count"] + mesh_info["unk_short_2"]))
            poss_np = None
            norms_np = None
            uv1s_np = None
            uv2s_np = None
            weights_names_np = None
            weights_values_np = None
            colors_np = None
            colors2_np = None


            if mesh_info["encoding"] == 0xd8297027:
                vert_bytes_float32 = np.frombuffer(vert_bytes, dtype=np.float32).reshape([-1, int(mesh_info["blocksize"]/4)])
                vert_bytes_float16 = np.frombuffer(vert_bytes, dtype=np.float16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_int8 = np.frombuffer(vert_bytes, dtype=np.int8).reshape([-1, int(mesh_info["blocksize"])])
                poss_np = (vert_bytes_float32[:,0:3])
                norms_np = (vert_bytes_int8[:,12:15]/127.0)
                uv1s_np = (vert_bytes_float16[:,10:12])
            elif mesh_info["encoding"] == 0x77d87021:
                vert_bytes_float16 = np.frombuffer(vert_bytes, dtype=np.float16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_int16 = np.frombuffer(vert_bytes, dtype=np.int16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_uint8 = np.frombuffer(vert_bytes, dtype=np.uint8).reshape([-1, int(mesh_info["blocksize"])])
                vert_bytes_int8 = np.frombuffer(vert_bytes, dtype=np.int8).reshape([-1, int(mesh_info["blocksize"])])
                poss_np = ((vert_bytes_int16[:,0:3]/32768.0))*mesh_scaling + mesh_position
                wA = vert_bytes_int16[:,3]/32767
                norms_np = (vert_bytes_int8[:,8:11]/127.0)
                colors_np = (vert_bytes_int8[:,12:16])
                weights_names_np = remap_np[vert_bytes_uint8[:,16:20]]
                uv1s_np = (vert_bytes_float16[:,10:12])
                wB = vert_bytes_float16[:,12:14]
                wC = 1-(np.hstack([wA.reshape(-1, 1), wB]).sum(axis=1))
                weights_values_np = np.hstack([wA.reshape(-1, 1), wB, wC.reshape(-1, 1)])
            elif mesh_info["encoding"] == 0xd877801a:
                vert_bytes_float16 = np.frombuffer(vert_bytes, dtype=np.float16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_int16 = np.frombuffer(vert_bytes, dtype=np.int16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_uint8 = np.frombuffer(vert_bytes, dtype=np.uint8).reshape([-1, int(mesh_info["blocksize"])])
                vert_bytes_int8 = np.frombuffer(vert_bytes, dtype=np.int8).reshape([-1, int(mesh_info["blocksize"])])
                poss_np = ((vert_bytes_int16[:,0:3]/32768.0))*mesh_scaling + mesh_position
                weights_names_np = remap_np[vert_bytes_uint8[:,6:7]]
                norms_np = (vert_bytes_int8[:,8:11]/127.0)
                colors_np = (vert_bytes_int8[:,12:16])
                uv1s_np = (vert_bytes_float16[:,8:10])
                uv2s_np = (vert_bytes_float16[:,12:14])
                weights_values_np = np.ones(weights_names_np.shape, dtype=np.float32)
            elif mesh_info["encoding"] == 0xb392101e:
                vert_bytes_float16 = np.frombuffer(vert_bytes, dtype=np.float16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_int16 = np.frombuffer(vert_bytes, dtype=np.int16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_uint8 = np.frombuffer(vert_bytes, dtype=np.uint8).reshape([-1, int(mesh_info["blocksize"])])
                vert_bytes_int8 = np.frombuffer(vert_bytes, dtype=np.int8).reshape([-1, int(mesh_info["blocksize"])])
                poss_np = ((vert_bytes_int16[:,0:3]/32768.0))*mesh_scaling + mesh_position
                wA = vert_bytes_int16[:,3]/32767
                norms_np = (vert_bytes_int8[:,8:11]/127.0)
                colors_np = (vert_bytes_int8[:,12:16])
                weights_names_np = remap_np[vert_bytes_float16[:,8:10].astype(np.uint16)]
                uv1s_np = (vert_bytes_float16[:,10:12])
                uv2s_np = (vert_bytes_float16[:,12:14])
                wB = 1-wA
                weights_values_np = np.hstack([wA.reshape(-1, 1), wB.reshape(-1, 1)])
            elif mesh_info["encoding"] == 0xda55a020:
                vert_bytes_float16 = np.frombuffer(vert_bytes, dtype=np.float16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_int16 = np.frombuffer(vert_bytes, dtype=np.int16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_uint8 = np.frombuffer(vert_bytes, dtype=np.uint8).reshape([-1, int(mesh_info["blocksize"])])
                vert_bytes_int8 = np.frombuffer(vert_bytes, dtype=np.int8).reshape([-1, int(mesh_info["blocksize"])])
                poss_np = ((vert_bytes_int16[:,0:3]/32768.0))*mesh_scaling + mesh_position
                wA = vert_bytes_int16[:,3]/32767
                norms_np = (vert_bytes_int8[:,8:11]/127.0)
                colors_np = (vert_bytes_int8[:,12:16])
                weights_names_np = remap_np[vert_bytes_uint8[:,16:20]]
                uv1s_np = (vert_bytes_float16[:,10:12])
                wB = vert_bytes_float16[:,12:14]
                uv2s_np = (vert_bytes_float16[:,14:16])
                wC = 1-(np.hstack([wA.reshape(-1, 1), wB]).sum(axis=1))
                weights_values_np = np.hstack([wA.reshape(-1, 1), wB, wC.reshape(-1, 1)])
            elif mesh_info["encoding"] == 0x667b1018:
                vert_bytes_float16 = np.frombuffer(vert_bytes, dtype=np.float16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_int16 = np.frombuffer(vert_bytes, dtype=np.int16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_uint8 = np.frombuffer(vert_bytes, dtype=np.uint8).reshape([-1, int(mesh_info["blocksize"])])
                vert_bytes_int8 = np.frombuffer(vert_bytes, dtype=np.int8).reshape([-1, int(mesh_info["blocksize"])])
                poss_np = ((vert_bytes_int16[:,0:3]/32768.0))*mesh_scaling + mesh_position
                weights_names_np = remap_np[vert_bytes_uint8[:,6:7]]
                norms_np = (vert_bytes_int8[:,8:11]/127.0)
                colors_np = (vert_bytes_int8[:,12:16])
                uv1s_np = (vert_bytes_float16[:,8:10])
                uv2s_np = (vert_bytes_float16[:,10:12])
                weights_values_np = np.ones(weights_names_np.shape, dtype=np.float32)
            elif mesh_info["encoding"] == 0xcbcf7026:
                #print("GOT ONE 0xcbcf7026", mesh_i)
                vert_bytes_float16 = np.frombuffer(vert_bytes, dtype=np.float16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_int16 = np.frombuffer(vert_bytes, dtype=np.int16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_uint8 = np.frombuffer(vert_bytes, dtype=np.uint8).reshape([-1, int(mesh_info["blocksize"])])
                vert_bytes_int8 = np.frombuffer(vert_bytes, dtype=np.int8).reshape([-1, int(mesh_info["blocksize"])])
                poss_np = ((vert_bytes_int16[:,0:3]/32768.0))*mesh_scaling + mesh_position
                wA = vert_bytes_int16[:,3]/32767
                norms_np = (vert_bytes_int8[:,8:11]/127.0)
                wB = vert_bytes_uint8[:,12]/255.0
                wC = vert_bytes_uint8[:,13]/255.0
                wD = vert_bytes_uint8[:,14]/255.0
                wE = vert_bytes_uint8[:,15]/255.0
                weights_names_np = remap_np[vert_bytes_uint8[:,16:24]]
                uv1s_np = (vert_bytes_float16[:,12:14])
                wF = (vert_bytes_float16[:,14:16])
                wG = 1-(np.hstack([wA.reshape(-1, 1),
                                   wB.reshape(-1, 1),
                                   wC.reshape(-1, 1),
                                   wD.reshape(-1, 1),
                                   wE.reshape(-1, 1),
                                   wF]).sum(axis=1))
                weights_values_np = np.hstack([wA.reshape(-1, 1),
                                               wB.reshape(-1, 1),
                                               wC.reshape(-1, 1),
                                               wD.reshape(-1, 1),
                                               wE.reshape(-1, 1),
                                               wF,
                                               wG.reshape(-1, 1)])
            elif mesh_info["encoding"] == 0xa013501d:

                vert_bytes_float16 = np.frombuffer(vert_bytes, dtype=np.float16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_int16 = np.frombuffer(vert_bytes, dtype=np.int16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_uint8 = np.frombuffer(vert_bytes, dtype=np.uint8).reshape([-1, int(mesh_info["blocksize"])])
                vert_bytes_int8 = np.frombuffer(vert_bytes, dtype=np.int8).reshape([-1, int(mesh_info["blocksize"])])
                poss_np = ((vert_bytes_int16[:,0:3]/32768.0))*mesh_scaling + mesh_position
                wA = vert_bytes_int16[:,3]/32767
                norms_np = (vert_bytes_int8[:,8:11]/127.0)
                colors_np = (vert_bytes_int8[:,12:16])
                uv1s_np = (vert_bytes_float16[:,8:10])
                weights_names_np = remap_np[vert_bytes_float16[:,10:12].astype(np.uint16)]
                wB = 1-wA
                weights_values_np = np.hstack([wA.reshape(-1, 1), wB.reshape(-1, 1)])
            elif mesh_info["encoding"] == 0x64593022:
                vert_bytes_float16 = np.frombuffer(vert_bytes, dtype=np.float16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_int16 = np.frombuffer(vert_bytes, dtype=np.int16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_uint8 = np.frombuffer(vert_bytes, dtype=np.uint8).reshape([-1, int(mesh_info["blocksize"])])
                vert_bytes_int8 = np.frombuffer(vert_bytes, dtype=np.int8).reshape([-1, int(mesh_info["blocksize"])])
                poss_np = ((vert_bytes_int16[:,0:3]/32768.0))*mesh_scaling + mesh_position
                wA = vert_bytes_int16[:,3]/32767
                norms_np = (vert_bytes_int8[:,8:11]/127.0)
                colors_np = (vert_bytes_int8[:,12:16])
                weights_names_np = remap_np[vert_bytes_uint8[:,16:20]]
                uv1s_np = (vert_bytes_float16[:,10:12])
                wB = vert_bytes_float16[:,12:14]
                uv2s_np = (vert_bytes_float16[:,16:18])
                wC = 1-(np.hstack([wA.reshape(-1, 1), wB]).sum(axis=1))
                weights_values_np = np.hstack([wA.reshape(-1, 1), wB, wC.reshape(-1, 1)])
            elif mesh_info["encoding"] == 0x207d6036:
                vert_bytes_float32 = np.frombuffer(vert_bytes, dtype=np.float32).reshape([-1, int(mesh_info["blocksize"]/4)])
                vert_bytes_float16 = np.frombuffer(vert_bytes, dtype=np.float16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_uint8 = np.frombuffer(vert_bytes, dtype=np.uint8).reshape([-1, int(mesh_info["blocksize"])])
                vert_bytes_int8 = np.frombuffer(vert_bytes, dtype=np.int8).reshape([-1, int(mesh_info["blocksize"])])
                poss_np = (vert_bytes_float32[:,0:3])
                uv1s_np = (vert_bytes_float16[:,8:10])
                colors_np = (vert_bytes_int8[:,20:24])
            elif mesh_info["encoding"] == 0xa7d7d035:
                vert_bytes_float32 = np.frombuffer(vert_bytes, dtype=np.float32).reshape([-1, int(mesh_info["blocksize"]/4)])
                vert_bytes_float16 = np.frombuffer(vert_bytes, dtype=np.float16).reshape([-1, int(mesh_info["blocksize"]/2)])
                poss_np = (vert_bytes_float32[:,0:3])
                uv1s_np = (vert_bytes_float16[:,8:10])
            elif mesh_info["encoding"] == 0xcbf6c019:
                vert_bytes_float16 = np.frombuffer(vert_bytes, dtype=np.float16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_int16 = np.frombuffer(vert_bytes, dtype=np.int16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_uint8 = np.frombuffer(vert_bytes, dtype=np.uint8).reshape([-1, int(mesh_info["blocksize"])])
                vert_bytes_int8 = np.frombuffer(vert_bytes, dtype=np.int8).reshape([-1, int(mesh_info["blocksize"])])
                poss_np = ((vert_bytes_int16[:,0:3]/32768.0))*mesh_scaling + mesh_position
                weights_names_np = remap_np[vert_bytes_uint8[:,6:7]]
                norms_np = (vert_bytes_int8[:,8:11]/127.0)
                colors_np = (vert_bytes_int8[:,12:16])
                uv1s_np = (vert_bytes_float16[:,8:10])
                weights_values_np = np.ones(weights_names_np.shape, dtype=np.float32)
            elif mesh_info["encoding"] == 0x49b4f028:
                #print("GOT ONE 0x49b4f028", mesh_i)
                vert_bytes_float32 = np.frombuffer(vert_bytes, dtype=np.float32).reshape([-1, int(mesh_info["blocksize"]/4)])
                vert_bytes_float16 = np.frombuffer(vert_bytes, dtype=np.float16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_uint8 = np.frombuffer(vert_bytes, dtype=np.uint8).reshape([-1, int(mesh_info["blocksize"])])
                vert_bytes_int8 = np.frombuffer(vert_bytes, dtype=np.int8).reshape([-1, int(mesh_info["blocksize"])])
                poss_np = (vert_bytes_float32[:,0:3])
                norms_np = (vert_bytes_int8[:,12:15]/127.0)
                #tangent_np = (vert_bytes_int8[:,16:19]/127.0)
                uv1s_np = (vert_bytes_float16[:,10:12])
                colors_np = (vert_bytes_int8[:,24:28])
            elif mesh_info["encoding"] == 0xbb424023:
                vert_bytes_float16 = np.frombuffer(vert_bytes, dtype=np.float16).reshape([-1, 18])
                vert_bytes_int16 = np.frombuffer(vert_bytes, dtype=np.int16).reshape([-1, 18])
                vert_bytes_uint8 = np.frombuffer(vert_bytes, dtype=np.uint8).reshape([-1, 36])
                vert_bytes_int8 = np.frombuffer(vert_bytes, dtype=np.int8).reshape([-1, 36])
                poss_np = ((vert_bytes_int16[:,0:3]/32768.0))*mesh_scaling + mesh_position
                norms_np = (vert_bytes_int8[:,8:11]/127.0)
                uv1s_np = (vert_bytes_float16[:,12:14])
                weights_names_np = remap_np[vert_bytes_uint8[:,16:24]]
                colors_np = (vert_bytes_int8[:,32:36])
                wA = vert_bytes_int16[:,3]/32767
                wB = vert_bytes_uint8[:,12:16]/255
                wC = vert_bytes_float16[:,14:16]
                wD = 1-(np.hstack([wA.reshape(-1, 1), wB, wC]).sum(axis=1))
                weights_values_np = np.hstack([wA.reshape(-1, 1), wB, wC, wD.reshape(-1, 1)])
            elif mesh_info["encoding"] == 0x14d4001f:
                vert_bytes_float16 = np.frombuffer(vert_bytes, dtype=np.float16).reshape([-1, 14])
                vert_bytes_int16 = np.frombuffer(vert_bytes, dtype=np.int16).reshape([-1, 14])
                vert_bytes_uint8 = np.frombuffer(vert_bytes, dtype=np.uint8).reshape([-1, 28])
                vert_bytes_int8 = np.frombuffer(vert_bytes, dtype=np.int8).reshape([-1, 28])
                poss_np = ((vert_bytes_int16[:,0:3]/32768.0))*mesh_scaling + mesh_position
                norms_np = (vert_bytes_int8[:,8:11]/127.0)
                uv1s_np = (vert_bytes_float16[:,10:12])
                weights_names_np = remap_np[vert_bytes_uint8[:,16:20]]
                colors_np = (vert_bytes_int8[:,12:16])
                wA = vert_bytes_int16[:,3]/32767
                wB = vert_bytes_float16[:,12:14]
                wC = 1-(np.hstack([wA.reshape(-1, 1), wB]).sum(axis=1))
                weights_values_np = np.hstack([wA.reshape(-1, 1), wB, wC.reshape(-1, 1)])
            elif mesh_info["encoding"] == 0xc31f201b:
                vert_bytes_float16 = np.frombuffer(vert_bytes, dtype=np.float16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_int16 = np.frombuffer(vert_bytes, dtype=np.int16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_uint8 = np.frombuffer(vert_bytes, dtype=np.uint8).reshape([-1, int(mesh_info["blocksize"])])
                vert_bytes_int8 = np.frombuffer(vert_bytes, dtype=np.int8).reshape([-1, int(mesh_info["blocksize"])])
                poss_np = ((vert_bytes_int16[:,0:3]/32768.0))*mesh_scaling + mesh_position
                wA = vert_bytes_int16[:,3]/32767
                norms_np = (vert_bytes_int8[:,8:11]/127.0)
                colors_np = (vert_bytes_int8[:,12:16])
                uv1s_np = (vert_bytes_float16[:,8:10])
                weights_names_np = remap_np[vert_bytes_float16[:,10:12].astype(np.uint16)]
                wB = 1-(np.hstack([wA.reshape(-1, 1)]).sum(axis=1))
                weights_values_np = np.hstack([wA.reshape(-1, 1), wB.reshape(-1, 1)])
            elif mesh_info["encoding"] == 0xa8fab017:
                vert_bytes_float16 = np.frombuffer(vert_bytes, dtype=np.float16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_int16 = np.frombuffer(vert_bytes, dtype=np.int16).reshape([-1, int(mesh_info["blocksize"]/2)])
                vert_bytes_uint8 = np.frombuffer(vert_bytes, dtype=np.uint8).reshape([-1, int(mesh_info["blocksize"])])
                vert_bytes_int8 = np.frombuffer(vert_bytes, dtype=np.int8).reshape([-1, int(mesh_info["blocksize"])])
                poss_np = ((vert_bytes_int16[:,0:3]/32768.0))*mesh_scaling + mesh_position
                weights_names_np = remap_np[vert_bytes_uint8[:,6:7]]
                norms_np = (vert_bytes_int8[:,8:11]/127.0)
                colors_np = (vert_bytes_int8[:,12:16])
                uv1s_np = (vert_bytes_float16[:,8:10])
                weights_values_np = np.ones(weights_names_np.shape, dtype=np.float32)
            elif mesh_info["encoding"] in [0xa320c015, 0x0cb68014, 0xdb7da013, 0xb0983012]:
                continue
            else:
                logger.warning("ENCODING NOT SUPPORTED: " + str(hex(mesh_info["encoding"])))
                print("ENCODING NOT SUPPORTED: ", hex(mesh_info["encoding"]), self.path, mesh_i)
                continue


            self.bs.seek(fbuffer_offset + mesh_info["face_sub"]*2)
            face_bytes = self.bs.readBytes((mesh_info["face_count"]*2))
            faces_np = None
            face_bytes_uint16 = np.frombuffer(face_bytes, dtype=np.uint16)
            splitted_faces = np.split(face_bytes_uint16, np.where(face_bytes_uint16 == 65535)[0])
            tmps = [np.lib.stride_tricks.sliding_window_view(np.delete(subsplit, subsplit==65535),3) for subsplit in splitted_faces]
            tmps_2 = []
            for tmp in tmps:
                tmp_2 = tmp.copy()
                tmp_2[1::2,0:2] = tmp_2[1::2,1:-4:-1]
                tmps_2.append(tmp_2)
            faces_np = np.vstack(tmps_2)
            def nunique(a, axis):
                return (np.diff(np.sort(a,axis=axis),axis=axis)!=0).sum(axis=axis)+1

            faces_np = faces_np[nunique(faces_np, axis=1) == 3]

            ffaces = faces_np.flatten()
            uffaces = np.unique(ffaces)

            mesh_poss = poss_np[uffaces].tolist()
            if norms_np is not None:
                mesh_norms = norms_np[uffaces].tolist()

            if uv1s_np is not None:
                uv1s_np = uv1s_np[uffaces].copy()
                uv1s_np[:,1] = 1.0 - uv1s_np[:,1]
                mesh_uv1s = uv1s_np.tolist()

            if uv2s_np is not None:
                uv2s_np = uv2s_np[uffaces].copy()
                uv2s_np[:,1] = 1.0 - uv2s_np[:,1]
                mesh_uv2s = uv2s_np.tolist()

            if weights_names_np is not None and weights_values_np is not None:
                mesh_weights_names = weights_names_np[uffaces].tolist()
                mesh_weights_values = weights_values_np[uffaces].tolist()

            if colors_np is not None:
                mesh_colors = colors_np[uffaces].tolist()

            if colors2_np is not None:
                mesh_colors2 = colors2_np[uffaces].tolist()

            sorter = np.argsort(uffaces)
            sorted_faces = sorter[np.searchsorted(uffaces, ffaces, sorter=sorter)]
            mesh_faces = sorted_faces.reshape(-1,3).tolist()
            mesh["lod"] = mesh_info["lod"] if has_lod else 0
            mesh["id"] = mesh_i
            mesh["positions"] = mesh_poss[:]
            mesh["faces"] = mesh_faces
            mesh["normals"] = mesh_norms
            mesh["UVs"] = [mesh_uv1s, mesh_uv2s]
            mesh["weights_names"] = mesh_weights_names
            mesh["weights_values"] = mesh_weights_values
            mesh["colors"] = mesh_colors
            mesh["group"] = mesh_info["group"]
            mesh["scale"] = mesh_scale
            mesh["material"] = materials[mesh_info["mat_idx"]]
            mesh["material_name_hash"] = int("0b"+"1"*32, 2) - zlib.crc32(materials[mesh_info["mat_idx"]].encode())

            mesh_datas.append(mesh)

        return armature_datas, mesh_datas

if __name__ == "__main__":
    parser = ModParser(path="em096.mod")
    armature_datas, mesh_datas = parser.read()





