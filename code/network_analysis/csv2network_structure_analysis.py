import powerlaw
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx

# Load the CSV file
data = pd.read_csv('D:/dzg/090thesis/092output/bnx_graph_mesh_all.csv')

# Create an undirected graph
G = nx.Graph()

# Add edges to the graph
G.add_edges_from(zip(data['ID1'], data['ID2']))

# Find the largest connected component
largest_cc = max(nx.connected_components(G), key=len)

# Create a subgraph of the largest connected component
large_G = G.subgraph(largest_cc)


# 度分布计算
degree_dict = dict(G.degree())
#print("Degree for each node:", degree_dict)

# 平均度系数
average_degree = sum(degree_dict.values()) / len(degree_dict)
print("Average degree:", average_degree)

# 计算每个node的路径长度
path_length_dict = dict(nx.all_pairs_shortest_path_length(G))
#print("Path length for each pair of nodes:", path_length_dict)

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

# Plot the degree distribution with power-law fit
"""
alpha=  69.73843095951912   Xmin=  4.0   sigma=  6.583947597788678,alpha大，不符合幂律分布，alpha大部分为2-3
"""
fig1 = fit.plot_pdf(linewidth=3, color='blue', linestyle='solid', label='empirical pdf')
fit.power_law.plot_pdf(linewidth=1, color='blue', linestyle='dashed', ax=fig1, label='powerlaw pdf')
fit.plot_ccdf(linewidth=3, color='red', linestyle='solid', ax=fig1, label='empirical ccdf')
fit.power_law.plot_ccdf(linewidth=1, color='red', linestyle='dashed', ax=fig1, label='powerlaw ccdf')
plt.legend()
plt.title('Degree Distribution')
plt.show()

fig2 = fit.plot_ccdf(linewidth=3, color='blue', linestyle='solid', label='empirical ccdf')
fit.power_law.plot_ccdf(linewidth=1, color='red', linestyle='dashed', label='powerlaw ccdf', ax=fig2)
fit.lognormal.plot_ccdf(linewidth=1, color='green', linestyle='dashed', label='lognormal ccdf', ax=fig2)
plt.legend()
plt.title('Degree Distribution')
plt.show()


