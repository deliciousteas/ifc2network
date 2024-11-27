import itertools
import os

from OCC.Core.TopoDS import TopoDS_Compound, TopoDS_Solid, TopoDS_Shape, topods
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_SOLID, TopAbs_FACE
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepExtrema import BRepExtrema_ShapeProximity
from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()

"""
将IFC构件转为Mesh模型，然后计算不同mesh之间是否存在相交情况。
todo：每次判断重复创建几何实体，内存消耗大。

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

        print("Loading ifc file ...", end="")
        ifc_filename = "D:\\dzg\\090thesis\\091dataset\\shuinuan.ifc"
        assert os.path.isfile(ifc_filename)
        ifc_file = ifcopenshell.open(ifc_filename)
        print("done.")

        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_PYTHON_OPENCASCADE, True)
        segment = ifc_file.by_type("IfcPipeSegment")[0:30]
        fitting = ifc_file.by_type("IfcPipeFitting")[0:30]
        products = fitting + segment

        overlaplist = []
        total_combinations = len(list(itertools.combinations(products, 2)))
        processed_combinations = 0
        deflection = 1e-4
        tolerance = 0.001

        for shape1, shape2 in itertools.combinations(products, 2):
            if shape1.Representation is not None and shape2.Representation is not None:
                shape1_geometry = ifcopenshell.geom.create_shape(settings, inst=shape1).geometry
                shape2_geometry = ifcopenshell.geom.create_shape(settings, inst=shape2).geometry

                # Create meshes for the shapes
                create_mesh(shape1_geometry, deflection)
                create_mesh(shape2_geometry, deflection)

                # Check proximity
                shape_1_faces, shape_2_faces = check_proximity(shape1_geometry, shape2_geometry, tolerance)
                if shape_1_faces or shape_2_faces:
                    print(f"{shape1.id()} and {shape2.id()} have intersecting faces.")
                    overlaplist.append([shape1.id(), shape2.id()])
                    display.DisplayShape(shape1_geometry, transparency=0.5)
                    display.DisplayShape(shape2_geometry, transparency=0.5)
                    display.DisplayShape(shape_1_faces + shape_2_faces, color="RED")

                processed_combinations += 1
                if processed_combinations % 10 == 0:
                    print(f"Processed {processed_combinations}/{total_combinations} shape pairs.")

        display.FitAll()
        start_display()
        print(overlaplist)

    except ModuleNotFoundError:
        print("ifcopenshell package not found.")
        exit(0)