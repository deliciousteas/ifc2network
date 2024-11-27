import itertools
import os
import time
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Pnt
import csv

"""通过读取IFC文件，基于包围盒构建IFC网络的函数
1. 包围盒拓扑判断：关键在于构建包围盒后的比较，这里主要使用OCC的Bnd_Box类，其distance很好计算了两个包围盒之间的距离
2. 内存优化：通过字典设置局部变量，减少临时变量占用

:param ifc_file: ifc文件路径
:param  products :ifc文件中的products'instances
:param tolerance: 两个包围盒之间的容差(十分重要）
"""
def compute_bounding_box(shape: TopoDS_Shape) -> Bnd_Box:
    """Compute the bounding box for a given shape"""
    bbox = Bnd_Box()
    brepbndlib_Add(shape, bbox)
    return bbox

def bounding_boxes_within_tolerance(bbox1: Bnd_Box, bbox2: Bnd_Box, tolerance: float) -> bool:
    """Check if two bounding boxes are within a specified tolerance"""
    """Distance 函数计算两个三维边界框之间的最小欧几里得距离。它通过比较两个边界框在X、Y、Z三个坐标轴上的投影区间，确定它们是否在每个轴上重叠。如果重叠，则该轴上的距离为0；如果不重叠，则计算两个区间的最小平方距离。最终，函数将三个轴上的距离平方和开方，得到两个边界框之间的总最小距离。这种方法有效地考虑了边界框的整体空间位置，适用于碰撞检测和空间分析等场景。"""
    """具体查看源码"""
    return bbox1.Distance(bbox2) <= tolerance

if __name__ == "__main__":
    try:
        import ifcopenshell
        import ifcopenshell.geom

        start_time = time.time()
        print("Loading ifc file ...", end="")
        ifc_filename = "D:\\dzg\\090thesis\\091dataset\\shuinuan.ifc"
        assert os.path.isfile(ifc_filename)
        ifc_file = ifcopenshell.open(ifc_filename)
        print("done.")

        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_PYTHON_OPENCASCADE, True)
        #可以自行filter文件中的构件类型
        segment = ifc_file.by_type("IfcPipeSegment")
        fitting = ifc_file.by_type("IfcPipeFitting")
        products = fitting + segment


        bbox_dict = {}#为包围盒创建一个字典存储变量，减少内存占用
        for product in products:
            shape_geometry = ifcopenshell.geom.create_shape(settings, inst=product).geometry
            bbox_dict[product.id()] = compute_bounding_box(shape_geometry)

        processed_combinations = 0
        total_combinations = len(list(itertools.combinations(products, 2)))
        tolerance = 0.01
        topology_list = []

        for shape1, shape2 in itertools.combinations(products, 2):
            bbox1 = bbox_dict[shape1.id()]
            bbox2 = bbox_dict[shape2.id()]

            if bounding_boxes_within_tolerance(bbox1, bbox2, tolerance):
                print(f"{shape1.id()} and {shape2.id()} are within tolerance.")
                topology_list.append([shape1.id(), shape2.id()])

            processed_combinations += 1
            if processed_combinations % 50 == 0:
                print(f"Processed {processed_combinations}/{total_combinations} shape pairs.")

        end_time = time.time()
        print(f"Total execution time: {int(end_time - start_time)} seconds")

        if os.path.exists("D:/dzg/090thesis/092output/bnx_graph.csv"):
            os.remove("D:/dzg/090thesis/092output/bnx_graph.csv")
        with open("D:/dzg/090thesis/092output/bnx_graph.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID1", "ID2"])  # Write the header row
            for i in topology_list:
                writer.writerow([i[0], i[1]])  # Write each pair as a new row
        end_time1 = time.time()
        print(f"Total execution time: {int(end_time1 - start_time)} seconds")

    except ModuleNotFoundError:
        print("ifcopenshell package not found.")
        exit(0)