import pandas as pd
import networkx as nx
import ifcopenshell
import powerlaw


from matplotlib import pyplot as plt


# 读取 IFC 文件
model = ifcopenshell.open("D:\\dzg\\090thesis\\091dataset\\shuinuan.ifc")

# 获取 IFC 构件列表
IfcPipeSegment_list = model.by_type("IfcPipeSegment")
IfcPipeFitting_list = model.by_type("IfcPipeFitting")

# 记录构件 ID
IfcPipeFitting_list = [i.id() for i in IfcPipeFitting_list]
IfcPipeSegment_list = [i.id() for i in IfcPipeSegment_list]

# 读取空间包含关系，保存为字典
IfcRelContainedInSpatialStructure_list = model.by_type("IfcRelContainedInSpatialStructure")
SpatialStrucutre_dic = {}
for rel in IfcRelContainedInSpatialStructure_list:
    RelatingStructure = rel.RelatingStructure.id()
    RelatedElements = [element.id() for element in rel.RelatedElements]
    SpatialStrucutre_dic[RelatingStructure] = RelatedElements


G=nx.Graph()
G.add_nodes_from(IfcPipeFitting_list)
#节点加上标签即可



SpatialStrucutre_dic_value_list=list(SpatialStrucutre_dic.values())[0]
Storey_id1=list(SpatialStrucutre_dic.keys())[0]
Storey_id2=list(SpatialStrucutre_dic.keys())[1]
Storey_id1_list=SpatialStrucutre_dic.get(Storey_id1)
Storey_id2_list=SpatialStrucutre_dic.get(Storey_id2)
for node in G.nodes():
    if node in Storey_id1_list:

        nx.set_node_attributes(G, {node: {'storey': Storey_id1}})
    if node in Storey_id2_list:
        nx.set_node_attributes(G, {node: {'storey': Storey_id2}})

# print(G.nodes())
#test所有点的属性
# print(nx.get_node_attributes(G,'storey'))

#添加属性完成。


#然后对node之间判断是否有关系，如果有就添加关系
data = pd.read_csv('D:/dzg/090thesis/092output/bnx_graph_mesh_all.csv')
csv_dict={}
index_num=data.index
for i in index_num:
    if data['ID1'][i] not in csv_dict:
        csv_dict[data['ID1'][i]]=[data['ID2'][i]]
    else:
        csv_dict[data['ID1'][i]].append(data['ID2'][i])

    if data['ID2'][i] not in csv_dict:
        csv_dict[data['ID2'][i]]=[data['ID1'][i]]
    else:
        csv_dict[data['ID2'][i]].append(data['ID1'][i])



# 创建多层网络

for i in IfcPipeFitting_list:
    values=csv_dict.get(i)
    if values!=None:
        for j in values:
            #为fitting类型
            if j in IfcPipeFitting_list:
                G.add_edge(i,j)
            else:
                #为segment类型
                Segment_values=csv_dict.get(j)
                if Segment_values !=None:
                    for k in Segment_values:
                        if k in IfcPipeFitting_list:
                            G.add_edge(i,k)
                            break


print(G.nodes)
print(G.edges)

#多层如何可视化？？
#将graph保存为gephi格式
#nx.write_graphml(G, "D:/dzg/090thesis/092output/multiplayer_network1111.graphml")

