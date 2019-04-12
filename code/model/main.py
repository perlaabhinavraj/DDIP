from code.model.DDIP_Algorithm_Procedure import runsimulation

'''Based on the network size (n) and the type of network (ERGM or Unit Disk), Uncomment and run to get the results.'''

n = 10
possible_edge_list = []

# ergm reading
file_name = "10_uav_sample_graph_2.txt"
f = open(file_name, 'r' ) # open the file in the set
set_of_edges = f.readlines()# read it by lines
for edge_group in set_of_edges: # foreach line
	a = edge_group.split() # split the number strings out
	possible_edge_list.append((int(a[0]) - 1, int(a[1]) - 1))
	possible_edge_list.append((int(a[1]) - 1, int(a[0]) - 1))# append the edges into lists, does not have to be a tuple to work with networkx
f.close() # close out the file
# ergm reading end

# # unit disk reading
# file_name = "unit_disk_10_50_9.txt"
# f = open(file_name, 'r' ) # open the file in the set
# set_of_edges = f.readlines()# read it by lines
# for edge_group in set_of_edges: # foreach line
# 	a = edge_group.split() # split the number strings out
# 	possible_edge_list.append((int(a[1]) - 1, int(a[2]) - 1))
# 	possible_edge_list.append((int(a[2]) - 1, int(a[1]) - 1))# append the edges into lists, does not have to be a tuple to work with networkx
# f.close() # close out the file
# # unit disk reading end

for xseed in range(10):
	print runsimulation(n, 0.642, 1.096, possible_edge_list, 10, file_name, xseed)

#####################################################################################

# n = 15
# possible_edge_list = []
#
# # ergm reading
# file_name = "15_uav_sample_graph_5.txt"
# f = open(file_name, 'r' ) # open the file in the set
# set_of_edges = f.readlines()# read it by lines
# for edge_group in set_of_edges: # foreach line
# 	a = edge_group.split() # split the number strings out
# 	possible_edge_list.append((int(a[0]) - 1, int(a[1]) - 1))
# 	possible_edge_list.append((int(a[1]) - 1, int(a[0]) - 1))# append the edges into lists, does not have to be a tuple to work with networkx
# f.close() # close out the file
# # ergm reading end
#
# # unit disk reading
# file_name = "unit_disk_15_34_7.txt"
# f = open(file_name, 'r' ) # open the file in the set
# set_of_edges = f.readlines()# read it by lines
# for edge_group in set_of_edges: # foreach line
# 	a = edge_group.split() # split the number strings out
# 	possible_edge_list.append((int(a[1]) - 1, int(a[2]) - 1))
# 	possible_edge_list.append((int(a[2]) - 1, int(a[1]) - 1))# append the edges into lists, does not have to be a tuple to work with networkx
# f.close() # close out the file
# # unit disk reading end
#
# for xseed in range(10):
# 	print runsimulation(n, 0.555, 1.21, possible_edge_list, 10, file_name, xseed)

#####################################################################################

# n = 20
# possible_edge_list = []
#
# # ergm reading
# file_name = "20_uav_sample_graph_1.txt"
# f = open(file_name, 'r' ) # open the file in the set
# set_of_edges = f.readlines()# read it by lines
# for edge_group in set_of_edges: # foreach line
# 	a = edge_group.split() # split the number strings out
# 	possible_edge_list.append((int(a[0]) - 1, int(a[1]) - 1))
# 	possible_edge_list.append((int(a[1]) - 1, int(a[0]) - 1))# append the edges into lists, does not have to be a tuple to work with networkx
# f.close() # close out the file
# # ergm reading end
#
# # unit disk reading
# file_name = "unit_disk_20_44_6.txt"
# f = open(file_name, 'r' ) # open the file in the set
# set_of_edges = f.readlines()# read it by lines
# for edge_group in set_of_edges: # foreach line
# 	a = edge_group.split() # split the number strings out
# 	possible_edge_list.append((int(a[1]) - 1, int(a[2]) - 1))
# 	possible_edge_list.append((int(a[2]) - 1, int(a[1]) - 1))# append the edges into lists, does not have to be a tuple to work with networkx
# f.close() # close out the file
# # unit disk reading end

for xseed in range(10):
	print runsimulation(n, 1.288, 0.863, possible_edge_list, 10, file_name, xseed)