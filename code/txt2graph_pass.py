import ifcopenshell
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Section
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCC.Core.TopoDS import TopoDS_Compound, TopoDS_Iterator
from OCC.Core.gp import gp_Pnt
import json
import os
"""
拓扑关系判断
:parameter
    verts: list[list[float]], 顶点坐标
    faces: list[list[int]], 三角形面的顶点索引
"""

def instance2triangular(verts,faces):
    compound = TopoDS_Compound()
    compound_builder = BRep_Builder()
    compound_builder.MakeCompound(compound)

    for i in range(len(faces)):
        p1 = gp_Pnt(verts[faces[i][0]][0], verts[faces[i][0]][1], verts[faces[i][0]][2])
        p2 = gp_Pnt(verts[faces[i][1]][0], verts[faces[i][1]][1], verts[faces[i][1]][2])
        p3 = gp_Pnt(verts[faces[i][2]][0], verts[faces[i][2]][1], verts[faces[i][2]][2])

        # 创建三角形
        polygon_maker = BRepBuilderAPI_MakePolygon()
        polygon_maker.Add(p1)
        polygon_maker.Add(p2)
        polygon_maker.Add(p3)
        polygon_maker.Add(p1)
        triangle = polygon_maker.Shape()
        compound_builder.Add(compound, triangle)
    return compound


def is_shape_empty(shape):
    it = TopoDS_Iterator(shape)
    return not it.More()


def overlap_detection(instance1,instance2):
    compound1 = instance2triangular(instance1.verts_list, instance1.faces_list)
    compound2 = instance2triangular(instance2.verts_list, instance2.faces_list)
    common_operation = BRepAlgoAPI_Common(instance1, instance2)
    common_operation.Build()

    if common_operation.IsDone():
        common_shape = common_operation.Shape()
        if is_shape_empty(common_shape):
            return False
        else:
            print("common operation success")
            return True

    else:
        print("common operation failed")
        return False

def touch_detection(instance1,instance2):
    compound1 = instance2triangular(instance1.verts_list, instance1.faces_list)
    compound2 = instance2triangular(instance2.verts_list, instance2.faces_list)

    Section_operation = BRepAlgoAPI_Section(instance1, instance2)
    Section_operation.Build()

    if Section_operation.IsDone():
        common_shape = Section_operation.Shape()  # true,则返回交集形状
        if is_shape_empty(common_shape):
            return False
        else:
            return True

    else:
        print("common operation failed")
        return False

def topology_detection(json_file_path,intersection_file_path):
    # 读取json文件中的信息
    with open(json_file_path, "r") as f:
        data = json.load(f)

    # 将json文件中的点面坐标，三角化
    topology_map = {}

    for instance in data:
        key=instance["id"]
        Compound_shape=instance2triangular(instance["verts_list"],instance["faces_list"])
        topology_map[key]=Compound_shape

    #开始检测拓扑关系,必须得用AABB包围盒，很慢
    topology_map_intersection_basedonOCC = {}
    topology_map_tangent_basedonOCC = {}
    for h in range(len(topology_map)):
        key = list(topology_map.keys())[h]
        value1 = topology_map[key]
        #print(key, value1)

        for i in range(h+1,len(topology_map)):
            key2 = list(topology_map.keys())[i]
            value2 = topology_map[key2]
            #print(key2, value2)



            #检测相交
            common_operation = BRepAlgoAPI_Common(value1, value2)
            common_operation.Build()
            if common_operation.IsDone():
                common_shape = common_operation.Shape()
                if is_shape_empty(common_shape):
                    pass
                else:
                    topology_map_intersection_basedonOCC[key]=key2
                    print(f"{key2}和{key}相交")



            else:
                print("common operation failed")
            del value2
        del value1
        print(f"这是第{h+1}/{len(topology_map)},测试相交")
    #输出topology_map_intersection_basedonOCC
    #将topology_map_intersection_basedonOCC字典写入文件中，保存

    if os.path.exists(intersection_file_path):
        os.remove(intersection_file_path)
    with open(intersection_file_path, "a") as file:
        for key, value in topology_map_intersection_basedonOCC.items():
            if value:  # 如果value不为空
                file.write(f'{key}: {value}\n')






if __name__ == '__main__':

    json_file_path = "D:\\dzg\\090thesis\\091dataset\\test.json"
    intersection_file_path="D:\\dzg\\090thesis\\091dataset\\test_output.txt"
    topology_detection(json_file_path,intersection_file_path)


    ##拓扑关系用OCC是会判断错误。11016、275、6449、11120是消防火栓，不存在相交
    #重新选择一种拓扑判断方法,pythonocc会判断错误且很慢