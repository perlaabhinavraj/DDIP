# -*- coding: utf-8 -*-
"""
Created on Tue Dec 27 15:12:31 2016

@author: cmdiaz93
"""
import networkx as nx
import matplotlib.pyplot as plt 

list_of_node_sizes = [10,15,20,25,30,40]
#list_of_node_sizes = [10]

def get_file_names(): # function that will extract the names and extensions of all R graphs from ERGM
	file_names = {} # output dictionary, key = node size sample
	for node_size in list_of_node_sizes: # loop through completed node size ERGM sample sets
		
		file_names[node_size] = [] # create seperate list for each size
		for sample_num in range(1,11): # append all 10 sample file names into the dictionary list
		
		# NEED TO CHANGE THIS TO AN IF STATEMENT AND CHANGE THE PATH DEPENDING ON THE OS
		
			file_names[node_size].append("uav_ergm_samples_2/%s_nodes/%s_uav_sample_graph_%s.txt" % (node_size,node_size,sample_num))
		
	return file_names # return the dict of the file names keyed by node size 
	
ergm_file_dict = get_file_names()# run the function, empty no parameter needed, could potentially have it take set size
# ergm_file_dict will be imported into the model, similar to the way that the other unit disk file runs 

def read_each_file(dict_of_files): # function that will return the edge sets for each file
	output_dict = {} # output dictionary will be set up the same as the unit dict ones to make it easy to run with existing programs

	for node_size in dict_of_files: # loop over the node size sets that have been completed 
		output_dict[node_size] = {} # create the node size key, just like the unit disk extraction file
		
		for file_name in dict_of_files[node_size]: # loop through the file set in the node size we are looking at 
			output_dict[node_size][file_name] = {}# create the dictionary that will store edge set data
			output_dict[node_size][file_name]['edge_set'] = [] # key the edge set dictionary by node size, file name, then the edge set
			#output_list[node_size][file_name]['pos'] = [] # not used right now, ergm graphs do not have unit locations  
			f = open(file_name, 'r' ) # open the file in the set 
			set_of_edges = f.readlines()# read it by lines
			for edge_group in set_of_edges: # foreach line 
				a = edge_group.split() # split the number strings out 
				output_dict[node_size][file_name]['edge_set'].append((int(a[0])-1,int(a[1])-1))
				output_dict[node_size][file_name]['edge_set'].append((int(a[1])-1,int(a[0])-1))# append the edges into lists, does not have to be a tuple to work with networkx
			f.close() # close out the file
	return output_dict # return the dictionary of edge sets 
	
ergm_samples_dict = read_each_file(ergm_file_dict) # run the function, this ergm_samples_dict will be imported into the other files to be ran on it 
#print ergm_samples_dict
"""
for size in list_of_node_sizes:
	for name in ergm_file_dict[size]:
		edge_set = ergm_samples_dict[size][name]['edge_set']
		node_set = [x for x in range(size)]
		if int(name[-5]) == 0:
			index = 10
		else:
			index = name[-5]
		G = nx.DiGraph()
		G.add_nodes_from(node_set)
		G.add_edges_from(edge_set)
		
		pos = nx.spring_layout(G, k = .3, iterations = 20, scale = 100)
		ergm_samples_dict[size][name]['pos'] = pos
		nx.set_node_attributes(G, 'pos' , pos)
		nx.draw_networkx(G, pos = pos,with_labels = False, node_size = 20, width = .1, node_color = 'r')
		plt.show()
		limits=plt.axis('off')
		plt.savefig('%s_node_results_ergm/%s_ergm_%s_con_2.png' % (size, size, index), transparent = True, bbox_inches = 'tight')
		plt.close()

		nx.write_pajek(G, "%s_node_results_ergm/%s_ergm_%s_con_2.net" %(size,size,index))

ten_node_edges = [[1,9],[1,5],[1,2],[2,9],[2,3],[2,5],[3,4],[4,5],[4,6],[4,7],\
[5,6],[5,9],[5,10],[5,8],[6,8],[6,7],[8,9],[8,10],[9,10]]

ten_node_closeness = [5,9,1,2,10,8,6,4,7,3]

pos_10 ={1:(1,7),2:(3,4), 3:(3,1), 4:(7,2), 5:(5.5,6), 6:(8,4), 7:(11,2.5), 8:(9.5,8.5), 9:(4,8), 10:(7,10)}

K = nx.Graph()
K.add_edges_from(ten_node_edges)
K = K.to_directed()
K.add_nodes_from([x for x in range(1,11)])

nx.set_node_attributes(K,'pos',pos_10)
nx.draw_networkx(K, pos=pos_10,width = .4, with_labels = False, arrows = True, node_size = 40, font_size = 8, node_color = 'r')

limits=plt.axis('off')
plt.savefig('10_node_observed.png',transparent = True, bbox_inches = 'tight')
plt.show()
plt.close()

dict_30_neighbors = {1:[2,3,4,7], 2:[3,4,6,7],3:[4,5,6,7],4:[5],5:[6,10,11],6:[7,8,10,11],7:[8,9,10,15],\
8:[10,12,13,14,15],9:[14,15,16],10:[11,12,13,23],11:[12,26,23],12:[13,21,23,24],13:[14,15,17,18,20,21],\
14:[15,16,17,18,19],15:[16],16:[19,30,18],17:[18,19,20,28,29],18:[19,29,30],19:[29,30],20:[21,22,28,27,29],\
21:[22,23,24],22:[27,28],23:[24,25,26],24:[25],25:[26],27:[28],28:[29],29:[30]}

thirty_node_edges = [] 

for node in dict_30_neighbors:
	for neighbor in dict_30_neighbors[node]:
		thirty_node_edges.append([node,neighbor])
		thirty_node_edges.append([neighbor,node])

thirty_pos = {1:(3,16), 2:(3,14), 3:(2,13),4:(1,15), 5:(1,11), 6:(4,11), 7:(5.5,13), 8:(8,11), 9:(9,15), 10:(6,9),\
11:(3,8), 12:(7,7), 13:(10,9), 14:(11,12), 15:(9,13), 16:(12,15), 17:(13,11), 18:(14,12), 19:(14,14), 20:(14,7),\
21:(10,5), 22:(13,4), 23:(5,4), 24:(8,2), 25:(3,2), 26:(1,5), 27:(16,3), 28:(17,7), 29:(17,11), 30:(17,15)}

L = nx.Graph()
L = L.to_directed()
L.add_nodes_from([x for x in range(1,31)])
L.add_edges_from(thirty_node_edges)
nx.set_node_attributes(L, 'pos', thirty_pos)
nx.draw_networkx(L, pos=thirty_pos,width = .4, with_labels = False, arrows = True, node_size = 40, font_size = 8, node_color = 'r')

limits=plt.axis('off')
plt.savefig('30_node_observed_test.png',transparent = True, bbox_inches = 'tight')
plt.show()
plt.close()
"""