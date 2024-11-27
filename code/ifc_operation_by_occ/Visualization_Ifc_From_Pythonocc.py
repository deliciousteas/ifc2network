
import sys
import os
from OCC.Core.gp import gp_Vec
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.Graphic3d import Graphic3d_ClipPlane
from OCC.Display.SimpleGui import init_display

"""
基于pythonocc的IFC模型可视化

"""
try:
    import ifcopenshell
    import ifcopenshell.geom
except ModuleNotFoundError:
    print("ifcopenshell package not found.")
    sys.exit(0)

display, start_display, add_menu, add_function_to_menu = init_display()
settings = ifcopenshell.geom.settings()
settings.set(
    settings.USE_PYTHON_OPENCASCADE, True
)  # tells ifcopenshell to use pythonocc

print("Loading ifc file ...", end="")
ifc_filename = "D:\\dzg\\090thesis\\091dataset\\shuinuan.ifc"
assert os.path.isfile(ifc_filename)
ifc_file = ifcopenshell.open(ifc_filename)
print("done.")

# the clip plane

# clip plane number one, by default xOy
clip_plane_1 = Graphic3d_ClipPlane()

# set hatch on
clip_plane_1.SetCapping(True)
clip_plane_1.SetCappingHatch(True)

# off by default, user will have to enable it
clip_plane_1.SetOn(False)

# set clip plane color
aMat = clip_plane_1.CappingMaterial()
aColor = Quantity_Color(0.5, 0.6, 0.7, Quantity_TOC_RGB)
aMat.SetAmbientColor(aColor)
aMat.SetDiffuseColor(aColor)
clip_plane_1.SetCappingMaterial(aMat)

# and display each subshape
"""
设置可视化范围的构件类型和数量。
"""
fitting= ifc_file.by_type("IfcPipeFitting")[0:50]
segment=ifc_file.by_type("IfcPipeSegment")[0:50]
products = fitting+segment # traverse all IfcProducts
nb_of_products = len(products)

for i, product in enumerate(products):
    if (
        product.Representation is not None
    ):  # some IfcProducts don't have any 3d representation
        try:


            pdct_shape = ifcopenshell.geom.create_shape(settings, inst=product)# 返回一个Brep类型
            r, g, b, a = pdct_shape.styles[0]  # the shape color
            color = Quantity_Color(abs(r), abs(g), abs(b), Quantity_TOC_RGB)
            # speed up rendering, don't update rendering for each shape
            # only update all 50 shapes
            to_update = i % 50 == 0
            new_ais_shp = display.DisplayShape(
                pdct_shape.geometry,
                color=color,
                transparency=abs(1 - a),
                update=to_update,
            )[0]
            new_ais_shp.AddClipPlane(clip_plane_1)
        except RuntimeError:
            print("Failed to process shape geometry")

# topology boolean operations




def animate_translate_clip_plane(event=None):
    clip_plane_1.SetOn(True)
    plane_definition = clip_plane_1.ToPlane()  # it's a gp_Pln，将其转为gp_Pln，方便可视化
    h = 0.01 # along the Z-axis
    for _ in range(1000):
        plane_definition.Translate(gp_Vec(0.0, 0.0, h))
        clip_plane_1.SetEquation(plane_definition)
        display.Context.UpdateCurrentViewer()


if __name__ == "__main__":
    print("你好")
    add_menu("IFC clip plane")
    add_function_to_menu("IFC clip plane", animate_translate_clip_plane)
    display.FitAll()
    start_display()