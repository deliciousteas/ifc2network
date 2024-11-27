import itertools
import os
import time
from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Compound
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Pnt

display, start_display, add_menu, add_function_to_menu = init_display()

displayed_shapes = set()

def compute_bounding_box(shape: TopoDS_Shape) -> Bnd_Box:
    """Compute the bounding box for a given shape"""
    bbox = Bnd_Box()
    brepbndlib_Add(shape, bbox)
    return bbox

def bounding_boxes_within_tolerance(bbox1: Bnd_Box, bbox2: Bnd_Box, tolerance: float) -> bool:
    """Check if two bounding boxes are within a specified tolerance"""
    return bbox1.Distance(bbox2) <= tolerance

def create_box_from_bounding_box(bbox: Bnd_Box) -> TopoDS_Shape:
    """Create a box shape from a bounding box"""
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    p1 = gp_Pnt(xmin, ymin, zmin)
    p2 = gp_Pnt(xmax, ymax, zmax)
    box = BRepPrimAPI_MakeBox(p1, p2).Shape()
    return box

def display_shape_once(shape, transparency=0.5, color=None):
    """Display shape only if it hasn't been displayed before"""
    shape_id = hash(shape)
    if shape_id not in displayed_shapes:
        displayed_shapes.add(shape_id)
        if color:
            display.DisplayShape(shape, color=color)
        else:
            display.DisplayShape(shape, transparency=transparency)

def process_pair(pair, settings, tolerance):
    shape1, shape2 = pair
    if shape1.Representation is not None and shape2.Representation is not None:
        shape1_geometry = ifcopenshell.geom.create_shape(settings, inst=shape1).geometry
        shape2_geometry = ifcopenshell.geom.create_shape(settings, inst=shape2).geometry

        bbox1 = compute_bounding_box(shape1_geometry)
        bbox2 = compute_bounding_box(shape2_geometry)

        if bounding_boxes_within_tolerance(bbox1, bbox2, tolerance):
            return (shape1.id(), shape2.id(), shape1_geometry, shape2_geometry, bbox1, bbox2)
    return None

if __name__ == "__main__":
    try:
        import ifcopenshell
        import ifcopenshell.geom
        import tempfile

        os.chdir("D:\\dzg\\090thesis")
        custom_temp_dir = "D:\\dzg\\090thesis\\tmp"
        os.makedirs(custom_temp_dir, exist_ok=True)

        print("Loading ifc file ...", end="")
        ifc_filename = "D:\\dzg\\090thesis\\091dataset\\shuinuan.ifc"
        assert os.path.isfile(ifc_filename)
        ifc_file = ifcopenshell.open(ifc_filename)
        print("done.")

        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_PYTHON_OPENCASCADE, True)
        segment = ifc_file.by_type("IfcPipeSegment")
        fitting = ifc_file.by_type("IfcPipeFitting")
        products = fitting + segment

        overlaplist = []
        processed_combinations = 0
        #这里排列组合有优化空间，默认对所有进行组合，但其实根据bbox可以指导如果两者的中心点距离超过10米，就不用计算了，可以得到一个更小的组合
        total_combinations = len(list(itertools.combinations(products, 2)))
        tolerance = 0.001

        start_time = time.time()

        #逻辑有问题，如果distance<tolerance，就认为是相交的
        for pair in itertools.combinations(products, 2):
            result = process_pair(pair, settings, tolerance)
            if result:
                shape1_id, shape2_id, shape1_geometry, shape2_geometry, bbox1, bbox2 = result
                print(f"{shape1_id} and {shape2_id} are within tolerance.")
                overlaplist.append([shape1_id, shape2_id])

                processed_combinations += 1
                if processed_combinations % 50 == 0:
                    print(f"Processed {processed_combinations}/{total_combinations} shape pairs.")

        end_time = time.time()
        print(f"Total execution time: {int(end_time - start_time)} seconds")

        display.FitAll()
        start_display()


        if os.path.exists("D:/dzg/090thesis/092output/bnx_graph.txt"):
            os.remove("D:/dzg/090thesis/092output/bnx_graph.txt")
        with open("D:/dzg/090thesis/092output/bnx_graph.txt", "w") as f:
            for i in overlaplist:
                f.write(str(i[0]) + ' ' + str(i[1]) + '\n')
        end_time1 = time.time()
        print(f"Total execution time: {int(end_time1 - start_time)} seconds")

    except ModuleNotFoundError:
        print("ifcopenshell package not found.")
        exit(0)