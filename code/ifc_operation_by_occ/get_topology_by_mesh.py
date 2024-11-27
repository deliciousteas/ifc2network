import itertools
import os
import time
import csv
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepExtrema import BRepExtrema_ShapeProximity
from OCC.Display.SimpleGui import init_display


"""

1.基于ifcopenshell创建创建OCC标准下的TopoDS_Shape(compound)类型，存储于字典，参考来源于github源码(已star)
2. 对TopoDS_Shape类型进行mesh处理，通过BRepMesh_IncrementalMesh函数，其中精度收到deflection参数控制
3. check_proximity函数利用BRepExtrema_ShapeProximity检测两个相加的shape情况，是否用相交的face数据组织类型

"""
def create_mesh(shape: TopoDS_Shape, deflection: float):
    """Create a mesh for the given shape"""
    mesher = BRepMesh_IncrementalMesh(shape, deflection)
    mesher.Perform()

def check_proximity(shape1: TopoDS_Shape, shape2: TopoDS_Shape, tolerance: float):
    """Check proximity between two shapes and return intersecting faces"""
    isect_test = BRepExtrema_ShapeProximity(shape1, shape2, tolerance)
    isect_test.Perform()

    # Get intersecting faces from Shape1
    overlaps1 = isect_test.OverlapSubShapes1()
    face_indices1 = overlaps1.Keys()
    shape_1_faces = []
    for ind in face_indices1:
        face = isect_test.GetSubShape1(ind)
        shape_1_faces.append(face)

    # Get intersecting faces from Shape2
    overlaps2 = isect_test.OverlapSubShapes2()
    face_indices2 = overlaps2.Keys()
    shape_2_faces = []
    for ind in face_indices2:
        face = isect_test.GetSubShape2(ind)
        shape_2_faces.append(face)

    return shape_1_faces, shape_2_faces

if __name__ == "__main__":
    try:
        import ifcopenshell
        import ifcopenshell.geom

        start_time = time.time()
        print("Loading ifc file ...", end="")
        ifc_filename = "D:/dzg/090thesis/091dataset/shuinuan.ifc"
        assert os.path.isfile(ifc_filename)
        ifc_file = ifcopenshell.open(ifc_filename)
        print("done.")

        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_PYTHON_OPENCASCADE, True)
        segment = ifc_file.by_type("IfcPipeSegment")
        fitting = ifc_file.by_type("IfcPipeFitting")
        products = fitting + segment

        # Create and store geometries for each shape
        geometry_dict = {}
        for product in products:
            shape_geometry = ifcopenshell.geom.create_shape(settings, inst=product).geometry
            geometry_dict[product.id()] = shape_geometry

        processed_combinations = 0
        total_combinations = len(products) * (len(products) - 1) // 2
        deflection = 1e-5
        tolerance = 0.001
        topology_list = []

        for i in range(len(products)):
            shape1 = products[i]
            geometry1 = geometry_dict[shape1.id()]
            create_mesh(geometry1, deflection)
            for j in range(i + 1, len(products)):
                shape2 = products[j]
                geometry2 = geometry_dict[shape2.id()]
                create_mesh(geometry2, deflection)

                shape_1_faces, shape_2_faces = check_proximity(geometry1, geometry2, tolerance)
                if shape_1_faces or shape_2_faces:
                    print(f"{shape1.id()} and {shape2.id()} have intersecting faces.")
                    topology_list.append([shape1.id(), shape2.id()])

                processed_combinations += 1
                if processed_combinations % 50 == 0:
                    print(f"Processed {processed_combinations}/{total_combinations} shape pairs.")

        end_time = time.time()
        print(f"Total execution time: {int(end_time - start_time)} seconds")

        if os.path.exists("D:/dzg/090thesis/092output/bnx_graph_mesh_all.csv"):
            os.remove("D:/dzg/090thesis/092output/bnx_graph_mesh_all.csv")
        with open("D:/dzg/090thesis/092output/bnx_graph_mesh_all.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID1", "ID2"])  # Write the header row
            for i in topology_list:
                writer.writerow([i[0], i[1]])  # Write each pair as a new row
        end_time1 = time.time()
        print(f"Total execution time: {int(end_time1 - start_time)} seconds")

    except ModuleNotFoundError:
        print("ifcopenshell package not found.")
        exit(0)