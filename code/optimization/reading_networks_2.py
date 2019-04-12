# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 15:44:30 2016

@author: cmdiaz93
"""

import copy
import zipfile 
import platform 
import networkx as nx 
import matplotlib.pyplot as plt
import os

def mapping(x):
	return int(x)-1

list_of_samples = [] 
dict_of_nets = {}
list_of_node_numbers = [10,15,20,25,30,40]

for node_numb in list_of_node_numbers:
	list_of_samples_by_node_number = []
	list_of_nets = []
	list_of_txts= []
	with zipfile.ZipFile('unit_disk_%s_con.zip' %node_numb, 'r') as myzip:
		file_name_list = myzip.namelist()
		for files in file_name_list:
			if files[-3:] == 'net':
				list_of_nets.append(files)
			elif files[-3:] == 'txt':
				list_of_txts.append(files)
				
	for name in range(len(list_of_nets)):
		if list_of_nets[name][-6:] == '10.net':
			list_of_nets[name] = list_of_nets[name][-22:]
		else:
			list_of_nets[name] = list_of_nets[name][-21:]
	
	for fyle in range(len(list_of_nets)):
			list_of_samples.append(list_of_nets[fyle])
			list_of_samples_by_node_number.append(list_of_nets[fyle])
	#print list_of_samples

	dict_of_nets[node_numb] = {}
	
	
	## CHANGE THIS TO MAKE IT NOT REQUIRE ALL OF THE FILES TO BE UNZIPPED IN THE DIRECTORY 

	for samples in list_of_samples_by_node_number:
		dict_of_nets[node_numb][samples] = {}
		if platform.system() == "Windows":
			G = nx.read_pajek('unit_disk_%s_con/%s' % (node_numb,samples))
			

		else:
			G = nx.read_pajek('unit_disk_%s_con/%s' % (node_numb,samples))
		
		G1 = nx.Graph(G, directed = False)
		G1 = G1.to_directed()
		G1 = nx.relabel_nodes(G1,mapping,copy=False)
		x_dict = nx.get_node_attributes(G1, 'x')
		y_dict = nx.get_node_attributes(G1, 'y')
		pos = {}
		for node in x_dict:
			pos[node] = (x_dict[node],y_dict[node])
		dict_of_nets[node_numb][samples]['edge_set'] = G1.edges()
		dict_of_nets[node_numb][samples]['pos'] = pos
		

sample_list_by_node_number = [] 
for sample in range(0,len(list_of_samples),10):
	sample_list_by_node_number.append([x for x in list_of_samples[sample:sample+10]])

#print sample_list_by_node_number
#print dict_of_nets