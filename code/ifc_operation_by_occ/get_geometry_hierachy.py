
import os

from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Solid, TopoDS_Compound
from OCC.Core.TopAbs import TopAbs_SOLID, TopAbs_FACE
from OCC.Core.TopoDS import topods

from OCC.Display.SimpleGui import init_display
from OCC.Core.TopAbs import TopAbs_VERTEX, TopAbs_EDGE, TopAbs_WIRE
display, start_display, add_menu, add_function_to_menu = init_display()

"""
获取IFC文件中构件在Brep中的几何组成层次关系。

"""
def get_shapes(compound: TopoDS_Compound):
    """Extract all shapes (solids, faces, vertices, edges, wires) from a TopoDS_Compound"""
    solids = []
    faces = []
    vertices = []
    edges = []
    wires = []

    # Extract solids
    explorer = TopExp_Explorer(compound, TopAbs_SOLID)
    while explorer.More():
        shape = explorer.Current()
        solid = topods.Solid(shape)
        if not solid.IsNull():
            solids.append(solid)
        explorer.Next()

    # Extract faces
    explorer = TopExp_Explorer(compound, TopAbs_FACE)
    while explorer.More():
        shape = explorer.Current()
        face = topods.Face(shape)
        if not face.IsNull():
            faces.append(face)
        explorer.Next()

    # Extract vertices
    explorer = TopExp_Explorer(compound, TopAbs_VERTEX)
    while explorer.More():
        shape = explorer.Current()
        vertex = topods.Vertex(shape)
        if not vertex.IsNull():
            vertices.append(vertex)
        explorer.Next()

    # Extract edges
    explorer = TopExp_Explorer(compound, TopAbs_EDGE)
    while explorer.More():
        shape = explorer.Current()
        edge = topods.Edge(shape)
        if not edge.IsNull():
            edges.append(edge)
        explorer.Next()

    # Extract wires
    explorer = TopExp_Explorer(compound, TopAbs_WIRE)
    while explorer.More():
        shape = explorer.Current()
        wire = topods.Wire(shape)
        if not wire.IsNull():
            wires.append(wire)
        explorer.Next()

    return solids, faces, vertices, edges, wires

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
        settings.set(
            settings.USE_PYTHON_OPENCASCADE, True
        )
        segment = ifc_file.by_type("IfcPipeSegment")[0:50]
        fitting = ifc_file.by_type("IfcPipeFitting")[0:50]
        products = fitting + segment
        for i, product in enumerate(products):
            if (
                    product.Representation is not None
            ):  # some IfcProducts don't have any 3d representation
                try:
                    pdct_shape = ifcopenshell.geom.create_shape(settings, inst=product)
                    pdct_shape= pdct_shape.geometry
                    print(type(pdct_shape))
                    solids, faces, vertices, edges, wires = get_shapes(pdct_shape)
                    print(solids)
                    print(faces)
                    print(vertices)
                    print(edges)
                    print(wires)


                except RuntimeError:
                    print("Failed to process shape geometry")



        display.FitAll()
        start_display()

    except ModuleNotFoundError:
        print("ifcopenshell package not found.")
        exit(0)

""""
结论发现，不是由solid组成，都是faces组成。对faces判断吧

"""