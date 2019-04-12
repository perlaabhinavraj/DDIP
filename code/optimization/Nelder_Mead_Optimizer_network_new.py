# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 20:26:41 2017

@author: cmdiaz93
"""

import random
# import UAV_network_model as model
import time

from code.optimization.Nelder_Mead_Classes_network_new import NelderMeadAlgorithm
from code.optimization.ergm_sample_set_creator import ergm_file_dict  # set of file names for the ergm graphs
from code.optimization.reading_networks_2 import sample_list_by_node_number  # set of file names for ergm graphs


def avg(xlist):
	return sum(xlist)/float(len(xlist))
	
starting_time = time.clock()
for  i in range(10):
	results_by_sample_size = {}
	individual_results_by_file = {}
	

	 # loop for the node size 
	node_sizes = [10,15,20,25]
	node_index = 0
	for node_num in node_sizes:
		iteration = 0
	
		results_keys = ['final best parameter', 'global min parameter', 'final best value', 'global min value', 'algorithm history']
		results_dicts = {}
		for key in results_keys:
			results_dicts[key] = None
		
		list_of_parameter_keys = ['gammas','scaling_factor'] # change to gamma and scaling factor 
		starting_parameter_dictionary = {}
		for key in list_of_parameter_keys:
			starting_parameter_dictionary[key] = [] 
			
		
		parameter_set_size = 6
	
		
		for x in range(parameter_set_size):
			gamma = random.uniform(.1,1.2)
			scaling_factor = random.uniform(.1,2)
			starting_parameter_dictionary['gammas'].append(gamma)
			starting_parameter_dictionary['scaling_factor'].append(scaling_factor)
	
		
		iteration += 1
		current_time = time.clock()
		print "iteration for node size = ", iteration
		print "Time Elapsed = ", (current_time - starting_time)/60
	
		
		
		file_list = sample_list_by_node_number[node_index][0:5]
		for x in range(5):
			file_list.append(ergm_file_dict[node_num][x])
		print file_list 
		file_not_work = True
		while file_not_work:
			try:
				
				file_results = NelderMeadAlgorithm( file_list,node_num,starting_parameter_dictionary)
				file_not_work = False
			except AttributeError:
				for key in list_of_parameter_keys:
					starting_parameter_dictionary[key] = [] 

				for x in range(parameter_set_size):
					gamma = random.uniform(.1,1.2)
					scaling_factor = random.uniform(.1,2)
					starting_parameter_dictionary['gammas'].append(gamma)
					starting_parameter_dictionary['scaling_factor'].append(scaling_factor)
				continue
	
		fout = open("%s_Nelder_Mead_New_Parameters.txt" % node_num, 'a')
		results_dicts['final best parameter'] = file_results['best_parameter'].returnParameterList()
		results_dicts['global min parameter']= file_results['global min parameter'].returnParameterList()
		results_dicts['algorithm history'] = [x.returnParameterList() for x in file_results['run_history']]
		fout.write("Best Parameter = " + str(results_dicts['final best parameter']) + "\n")
		fout.write("global min parameter = " + str(results_dicts['global min parameter']) + "\n")
		fout.write("Best Parameter History = " + str(results_dicts['algorithm history']) + "\n")
		fout.write("Starting Pameters = " + str(starting_parameter_dictionary) + "\n")
		fout.write("\n")
		fout.close()
		

		node_index += 1 
