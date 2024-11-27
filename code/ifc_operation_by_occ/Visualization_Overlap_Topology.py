
from OCC.Core.gp import gp_Pnt
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepExtrema import BRepExtrema_ShapeProximity
from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()

# create two boxes that intersect
box1 = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), gp_Pnt(25, 25, 25)).Shape()
box2 = BRepPrimAPI_MakeBox(gp_Pnt(10, 10, 10), gp_Pnt(30, 30, 30)).Shape()

# Create meshes for the proximity algorithm
deflection = 1e-3
mesher1 = BRepMesh_IncrementalMesh(box1, deflection)
mesher2 = BRepMesh_IncrementalMesh(box2, deflection)
mesher1.Perform()
mesher2.Perform()

# Perform shape proximity check
tolerance = 0.1
isect_test = BRepExtrema_ShapeProximity(box1, box2, tolerance)
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




# display both boxes and intersecting faces, in RED
display.DisplayShape(box1, transparency=0.5)
display.DisplayShape(box2, transparency=0.5)
display.DisplayShape(shape_1_faces + shape_2_faces, color="RED")


display.FitAll()
start_display()