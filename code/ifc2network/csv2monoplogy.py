import numpy as np
import pandas as pd
import networkx as nx
import ifcopenshell
import powerlaw
from matplotlib import pyplot as plt
from scipy import stats
#读取ifc文件
model=ifcopenshell.open("D:\\dzg\\090thesis\\091dataset\\shuinuan.ifc")

#IfcValue_list=model.by_type("IfcValue")
IfcPipeSegment_list=model.by_type("IfcPipeSegment")
IfcPipeFitting_list=model.by_type("IfcPipeFitting")
#读取id——list
IfcPipeFitting_list=[i.id() for i in IfcPipeFitting_list]
IfcPipeSegment_list=[i.id() for i in IfcPipeSegment_list]



#读取csv保存为一个字典,依次读取data['ID1'][i] 何data['ID2'][i]，如果字典中没有就加入两个作为key，将value加入
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

print(csv_dict.__len__())


"""
读取fifting列表，
1.访问它的value，value是是否也为fitting类型，是的画就添加边关系。
2.访问它的value，value如果是segment类型，访问segment在csv_dict的values，如果不为空且有value为fitting类型，则认为存在边关系
"""

G=nx.Graph()
G.add_nodes_from(IfcPipeFitting_list)#只添加fitting

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
print(G.nodes.__len__())
print(G.edges.__len__())


# #将graph保存为csv
#nx.write_graphml(G, "D:/dzg/090thesis/092output/monoplogy_network1111.graphml")





# 检测网络结构测度，幂律分布特性
# 度分布计算
degree_dict = dict(G.degree())
#print("Degree for each node:", degree_dict)

# 平均度系数
average_degree = sum(degree_dict.values()) / len(degree_dict)
print("Average degree:", average_degree)

# 计算每个node的路径长度
path_length_dict = dict(nx.all_pairs_shortest_path_length(G))
print("Path length for each pair of nodes:", path_length_dict)

# 计算平均路径
subgraph = max(nx.connected_components(G), key=len)
largest_component = G.subgraph(subgraph)
avg_path_length = nx.average_shortest_path_length(largest_component)
print("Average path length:", avg_path_length)

# 计算 betweenness centrality
betweenness_centrality = nx.betweenness_centrality(G)
#print("Betweenness centrality:", betweenness_centrality)

# 计算集聚系数clustering coefficient for each node
clustering_coefficient = nx.clustering(G)
#print("Clustering coefficient for each node:", clustering_coefficient)

# 计算平均集聚系数
average_clustering_coefficient = nx.average_clustering(G)
print("Average clustering coefficient:", average_clustering_coefficient)

#度分布测试
# Calculate the degree distribution
degree_sequence = [d for n, d in G.degree()]

# Plot the degree distribution as a histogram
plt.figure(figsize=(10, 6))
plt.hist(degree_sequence, bins=range(min(degree_sequence),max(degree_sequence)+2,1), edgecolor='black', alpha=0.7)#bins，直方图的箱数
plt.title('Degree Distribution Histogram')
plt.xlabel('Degree')
plt.ylabel('Frequency')
plt.show()




# 幂律分布检测
fit = powerlaw.Fit(degree_sequence)
alpha = fit.power_law.alpha
xmin = fit.power_law.xmin
sigma = fit.power_law.sigma
print('alpha= ', alpha, '  Xmin= ', xmin, '  sigma= ', sigma)

# # Plot the degree distribution with power-law fit
# """
# alpha=  69.73843095951912   Xmin=  4.0   sigma=  6.583947597788678,alpha大，不符合幂律分布，alpha大部分为2-3
# """
# fig1 = fit.plot_pdf(linewidth=3, color='blue', linestyle='solid', label='empirical pdf')
# fit.power_law.plot_pdf(linewidth=1, color='blue', linestyle='dashed', ax=fig1, label='powerlaw pdf')
# fit.plot_ccdf(linewidth=3, color='red', linestyle='solid', ax=fig1, label='empirical ccdf')
# fit.power_law.plot_ccdf(linewidth=1, color='red', linestyle='dashed', ax=fig1, label='powerlaw ccdf')
# plt.legend()
# plt.title('Degree Distribution')
# plt.show()
#
# fig2 = fit.plot_ccdf(linewidth=3, color='blue', linestyle='solid', label='empirical ccdf')
# fit.power_law.plot_ccdf(linewidth=1, color='red', linestyle='dashed', label='powerlaw ccdf', ax=fig2)
# fit.lognormal.plot_ccdf(linewidth=1, color='green', linestyle='dashed', label='lognormal ccdf', ax=fig2)
# plt.legend()
# plt.title('Degree Distribution')
# plt.show()

# 绘制 PDF 和 CCDF 以比较经验数据和幂律、对数正态、指数分布拟合效果
fig, ax = plt.subplots(1, 2, figsize=(14, 6))

# 绘制 PDF 图
fig1 = fit.plot_pdf(linewidth=3, color='blue', linestyle='solid', ax=ax[0], label='Empirical PDF')
fit.power_law.plot_pdf(linewidth=1, color='blue', linestyle='dashed', ax=fig1, label='Power-law PDF')
fit.lognormal.plot_pdf(linewidth=1, color='green', linestyle='dashed', ax=fig1, label='Log-normal PDF')
fit.exponential.plot_pdf(linewidth=1, color='purple', linestyle='dashed', ax=fig1, label='Exponential PDF')
ax[0].legend()
ax[0].set_title('Degree Distribution - PDF')

# 绘制 CCDF 图
fig2 = fit.plot_ccdf(linewidth=3, color='red', linestyle='solid', ax=ax[1], label='Empirical CCDF')
fit.power_law.plot_ccdf(linewidth=1, color='blue', linestyle='dashed', ax=fig2, label='Power-law CCDF')
fit.lognormal.plot_ccdf(linewidth=1, color='green', linestyle='dashed', ax=fig2, label='Log-normal CCDF')
fit.exponential.plot_ccdf(linewidth=1, color='purple', linestyle='dashed', ax=fig2, label='Exponential CCDF')
ax[1].legend()
ax[1].set_title('Degree Distribution - CCDF')

plt.suptitle('Degree Distribution Comparison for Different Fits')
plt.show()

