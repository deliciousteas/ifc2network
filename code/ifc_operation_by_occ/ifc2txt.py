import os.path

import ifcopenshell
import multiprocessing
import ifcopenshell.geom
import ifcopenshell.util.shape
import json
""""
读取ifc构件信息，保存为txt文件、json格式，需要手动修改。

parameter:
    ifc_path: str, ifc文件路径
    saved_path: str, 保存路径
"""

class Ifc_entity_instance_MetaData:
    def __init__(self, GlobalId: str, id: int, shape_type: str, name:str,verts_list: list[float], lines_list: list[int],
                 faces_list: list[int],
                 center_coor: list[float]) -> object:
        self.GlobalId = GlobalId
        self.shape_type = shape_type
        self.name = name
        self.verts_list = verts_list
        self.faces_list = faces_list
        self.center_coor = center_coor
        self.id = id
        self.lines_list = lines_list
    def __str__(self):
        return f"GlobalId:{self.GlobalId},id:{self.id},shape_type:{self.shape_type},verts_list:{self.verts_list},lines_list:{self.lines_list},faces_list:{self.faces_list},center_coor:{self.center_coor}"

def extract_info(ifc_path,saved_path):
    ifc_info_list = []
    ifc_data = ifcopenshell.open(ifc_path)
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    iterator = ifcopenshell.geom.iterator(settings, ifc_data, multiprocessing.cpu_count())
    x=0
    if iterator.initialize():
        while True:
            shape = iterator.get()
            shape_name = shape.name
            shape_guid = shape.guid
            shape_id = shape.id
            shape_type = shape.type
            faces = ifcopenshell.util.shape.get_faces(shape.geometry)
            lines = ifcopenshell.util.shape.get_edges(shape.geometry)
            verts = ifcopenshell.util.shape.get_vertices(shape.geometry)
            verts = verts.tolist()
            center_coor = ifcopenshell.util.shape.get_shape_bbox_centroid(shape, shape.geometry).tolist()

            ifc_info_list.append(
                Ifc_entity_instance_MetaData(shape_guid, shape_id, shape_type, shape_name, verts, lines, faces,
                                             center_coor))
            print(f"读取第{x+1}个实例")
            x+=1
            if not iterator.next():
                break
        print(f"ifc文件信息提取完毕，共有{len(ifc_info_list)}个实例。")
    else:
        print("ifc文件不存在，路径不对。")

    if os.path.exists(saved_path):
        os.remove(saved_path)
    with open(saved_path, "w") as f:
        json.dump([instance.__dict__ for instance in ifc_info_list], f, ensure_ascii=False, indent=4)

    print(f"ifc文件信息保存完毕，保存路径为{saved_path}.")


if __name__ == '__main__':
    ifc_path= "D:\\dzg\\090thesis\\091dataset\\shuinuan.ifc"
    saved_path="D:\\dzg\\090thesis\\091dataset\\test.json"
    extract_info(ifc_path,saved_path)