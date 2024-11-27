import multiprocessing
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
import ifcopenshell.util.element
import ifcopenshell.api.geometry
import os

from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Common
from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_WIRE
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Display.SimpleGui import init_display
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Core.gp import gp_Pnt

"""
1. 提取点线面信息
"""


def extracte_whole_info(ifc_path,txt_path):

    if (os.path.exists(ifc_path)):
        ifcdata_list = []
        ifc_data = ifcopenshell.open(ifc_path)
        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_WORLD_COORDS, True)
        iterator = ifcopenshell.geom.iterator(settings, ifc_data, multiprocessing.cpu_count())
        if iterator.initialize():
            while True:
                shape = iterator.get()
                shape_id = shape.id
                shape_type = shape.type
                faces = ifcopenshell.util.shape.get_faces(shape.geometry)
                verts = ifcopenshell.util.shape.get_vertices(shape.geometry)
                verts=verts.tolist()
                ifcdata_list.append(f"{shape_id};{shape_type};{verts};{faces}")

                if not iterator.next():
                    break
        # 保存到txt路径中去
        if (os.path.exists(txt_path)):
            print(f"{txt_path}文件存在，删除重新创建了。")
            os.remove(txt_path)


        with open(txt_path, 'a') as file:
            for i in ifcdata_list:
                #line = str(i)
                file.write(i)
                file.write("\n")
        print(f"txt文件保存在 {txt_path}")

    else:
        print("ifc文件不存在，路径不对。")


"""
2. 用OCC提取点面信息，构成mesh判断是否相交

2.1 提取txt文件中的信息
2.2 create mesh for the shapes
2.3 对mesh进行相交判断，tolerance可以设置不那么精确，只需要初步判断是否相交就看也
2.3.1 用mesh的BRepExtrema_ShapeProximity判断
2.3.2 用BRepAlgoAPI_Common得到的结果，判断构成是否有occ中face的结构，有则代表相交
"""

def create_face(verts_list, face_list):
    polygon = BRepBuilderAPI_MakePolygon()
    for index in face_list:
        vertex = verts_list[index]
        polygon.Add(gp_Pnt(vertex[0], vertex[1], vertex[2]))
    polygon.Close()
    return BRepBuilderAPI_MakeFace(polygon.Wire()).Face()
def create_mesh(verts, faces):
    mesh = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(mesh)
    for face_indices in faces:
        face = create_face(verts, face_indices)
        builder.Add(mesh, face)
    return mesh

def check_intersections(txt_path, output_path):
    instance_list = []
    if os.path.exists(txt_path):
        with open(txt_path, 'r') as file:
            for line in file:
                items = line.split(";")
                shape_id = items[0]
                verts = eval(items[2])
                faces = eval(items[3])
                instance_list.append((shape_id, verts, faces))

    intersections = {}#待优化，如果中心点距离相差太原就不用配对计算了，可以提前得到一个更小的组合相差，中心距离相差10米

    checked_pairs = 0

    for i, (id1, verts1, faces1) in enumerate(instance_list):
        mesh1 = create_mesh(verts1, faces1)
        for j in range(i + 1, len(instance_list)):
            id2, verts2, faces2 = instance_list[j]
            mesh2 = create_mesh(verts2, faces2)
            common = BRepAlgoAPI_Common(mesh1, mesh2)
            common_shape = common.Shape()
            if not common_shape.IsNull():
                has_face_or_wire = False
                explorer = TopExp_Explorer(common_shape, TopAbs_FACE)
                if explorer.More():
                    has_face_or_wire = True
                else:
                    explorer = TopExp_Explorer(common_shape, TopAbs_WIRE)
                    if explorer.More():
                        has_face_or_wire = True

                if has_face_or_wire:
                    if id1 not in intersections:
                        intersections[id1] = []
                    intersections[id1].append(id2)
        checked_pairs += 1
        print(f"Checked {checked_pairs}/{len(instance_list)} pairs")

    with open(output_path, 'w') as file:
        for key, value in intersections.items():
            file.write(f"{key}: {value}\n")
def visualize_mesh(txt_path):
    instance_list = []
    if os.path.exists(txt_path):
        with open(txt_path, 'r') as file:
            for line in file:
                items = line.split(";")
                verts = eval(items[2])
                faces = eval(items[3])
                instance_list.append((verts, faces))

    display, start_display, add_menu, add_function_to_menu = init_display()

    for verts, faces in instance_list:
        mesh = TopoDS_Compound()
        builder = BRep_Builder()
        builder.MakeCompound(mesh)
        for face_indices in faces:
            face = create_face(verts, face_indices)
            builder.Add(mesh, face)
        display.DisplayShape(mesh, update=True)

    start_display()

if __name__ == "__main__":


    # ifcpath = "D:\\dzg\\090thesis\\091dataset\\shuinuan.ifc"
    #
    # outputpath = "D:/dzg/090thesis/092output/shuiguan_info.txt"
    # extracte_whole_info(ifcpath,outputpath)

    txt_path=("D:/dzg/090thesis/092output/shuiguan_info_500.txt")
    output_path = 'D:/dzg/090thesis/092output/intersections.txt'
    #create_mesh(txt_path)
   #visualize_mesh(txt_path)
    check_intersections(txt_path, output_path)