import itertools
import os
from OCC.Core.Graphic3d import Graphic3d_ClipPlane
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.gp import gp_Vec
from OCC.Display.SimpleGui import init_display

import ifcopenshell.geom
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section


display, start_display, add_menu, add_function_to_menu = init_display()
settings = ifcopenshell.geom.settings()
settings.set(
    settings.USE_PYTHON_OPENCASCADE, True
)  # tells ifcopenshell to use pythonocc


#问题 没相交内容，也返回section内容

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


fitting= ifc_file.by_type("IfcPipeFitting")[0:50]
segment=ifc_file.by_type("IfcPipeSegment")[0:50]
products = fitting+segment
nb_of_products = len(products)
for i, product in enumerate(products):
    if (
        product.Representation is not None
    ):
        try:

            pdct_shape = ifcopenshell.geom.create_shape(settings, inst=product)# 返回一个Brep类型
            r, g, b, a = pdct_shape.styles[0]  # the shape color
            color = Quantity_Color(abs(r), abs(g), abs(b), Quantity_TOC_RGB)

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



def animate_translate_clip_plane(event=None):
    clip_plane_1.SetOn(True)
    plane_definition = clip_plane_1.ToPlane()  # it's a gp_Pln，将其转为gp_Pln，方便可视化
    h = 0.01 # along the Z-axis
    for _ in range(1000):
        plane_definition.Translate(gp_Vec(0.0, 0.0, h))
        clip_plane_1.SetEquation(plane_definition)
        display.Context.UpdateCurrentViewer()
def create_section(shape1, shape2):
    section_shape = BRepAlgoAPI_Section(shape1, shape2) # 初始化，返回一个None值
    section_shape.Build()
    if section_shape.IsDone():
        common_shape = section_shape.Shape()
        return not common_shape.IsNull()
    return False


Section_count = {}

for shape1, shape2 in itertools.combinations(products, 2):
    if shape1.Representation is not None and shape2.Representation is not None:
        shape1_id = shape1.id()
        shape2_id = shape2.id()

        # Initialize intersection count if not already present
        if shape1_id not in Section_count:
            Section_count[shape1_id] = 0
        if shape2_id not in Section_count:
            Section_count[shape2_id] = 0
        if Section_count[shape1_id] >= 5 or Section_count[shape2_id] >= 5:
            continue
        try:
            # Create shapes for each product
            shape1_geometry = ifcopenshell.geom.create_shape(settings, inst=shape1).geometry
            shape2_geometry = ifcopenshell.geom.create_shape(settings, inst=shape2).geometry

            section_result = create_section(shape1_geometry, shape2_geometry)


            # Optionally display the results in the viewer
            if section_result:
                print(f"{shape1.id()} intersection with {shape2.id()}")
                #display.DisplayShape(section_result, color=Quantity_Color(1, 0, 0, Quantity_TOC_RGB), transparency=0.5)

                # Update intersection count
                Section_count[shape1_id] += 1
                Section_count[shape2_id] += 1
        except RuntimeError:
            print(f"Failed to process shape geometry for products: {shape1}, {shape2}")

if __name__ == "__main__":
    print("你好")
    add_menu("IFC clip plane")
    add_function_to_menu("IFC clip plane", animate_translate_clip_plane)
    display.FitAll()
    start_display()