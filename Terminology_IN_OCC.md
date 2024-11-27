# terminology
Clip Plane：剪切面，定义在相机所见的场景范围。  
hatch：填充，an opening of restrictied size allowing for passage from one area to another.it refers to the technique of filling an area with patterns or colors to indicate differenet features in a drawing.    
capping：封顶，为clip plane设置贴膜，使其看起来更像一个实体。
BRepAlgoAPI:
* fuse:merge,融合
* Common：用于intersection 或者overlap，求得2-N个shape交集的volume or area.
* section：用于求2-N个shape的交集，但是返回的是一个面。
Deflection:偏转，用于表示一个面的精度，越小越精确。
## 引用库
Core.gp -> gp.Vec module 生成向量

OCC.Core.Graphic3d -> Graphic3d_ClipPlane module 创建剪切面
B
## 可视化引用库

Core.Quantity -> Quantity_Color,Quantity_TOC_RGB module 声明颜色
Display.SimpleGui -> init_display module 初始化显示窗口
## 代码解释
设置clip_plane的颜色
```
clip_plane_1.SetCapping(True)
clip_plane_1.SetCappingHatch(True)
clip_plane_1.SetOn(True)
```
Seton(True)表示显示clip_plane

## python语法
assert : 用于判断expression的bool类型，如果为False则raise an AssertionError  
* 是keyword。用于debugging code。
```
assert os.path.isfile("D:\\dzg\\090thesis\\091dataset\\test.json")
print ("done.")
```
前后端区别
* front end:allows users to interact with your application,
* backend : the data and infrastructure that make your applicaiton work.
> 有时候也会称为server side,当用户在前端交互式，后端通过HTTP形式返回数值。    

bound method:instance method,需要结合实例才能使用这种方法
# 总结
这篇能够学习的是pythonocc+ifcopenshell的可视化部分。
通过ifcopenshell的geom的create——shape创建BreP类型。
```
 settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_PYTHON_OPENCASCADE, True)

    ifc_file = ifcopenshell.open(file_path)
    products = ifc_file.by_type("IfcProduct")

    for i, product in enumerate(products):
        if product.Representation is not None:
            try:
                created_shape = geom.create_shape(settings, inst=product)
                shape = created_shape.geometry # see #1124
                shape_gpXYZ = shape.Location().Transformation().TranslationPart() # These are methods of the TopoDS_Shape class from pythonOCC
                print(shape_gpXYZ.X(), shape_gpXYZ.Y(), shape_gpXYZ.Z()) # These are methods of the gpXYZ class from pythonOCC
            except:
                print("Shape creation failed")

```
剩下部分可视化内容可以挪用ifc_clip_lane的可视化代码部分。