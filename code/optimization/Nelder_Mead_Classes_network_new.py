# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 18:05:41 2017

@author: cmdiaz93
"""
import copy
from operator import itemgetter

from code.model import DDIP_Algorithm_Procedure as model
from code.optimization.ergm_sample_set_creator import ergm_samples_dict  # set of ergm sample graphs
# from ergm_sample_set_creator import ergm_file_dict # set of file names for the ergm graphs
from code.optimization.reading_networks_2 import dict_of_nets  # set of graphs for unit disk samples


class AlgorithmVertices(object):
	
	def __init__(self, xsize, xstarting_gammas, xstarting_scaling_factor, xnode_num, xperiods):
		self.size = xsize # number of parameters being tested in the simplex
		self.starting_gammas = xstarting_gammas # change to gamma
		self.starting_scaling_factor = xstarting_scaling_factor # change to scaling factor 
		self.parameter_list = [] 
		self.centroid = None
		self.reflection = None 
		self.worst_parameter = None
		self.second_worst_parameter = None 
		self.best_parameter = None 
		self.number_of_nodes = xnode_num
		self.periods = xperiods
		
	
	def CreateParameters(self):
		for parameter in xrange(self.size): # change to gamma and scaling factor parameters !!!!!!!!!!
			gamma = self.starting_gammas[parameter] # pull out gamma for this parameter
			scaling_factor = self.starting_scaling_factor[parameter] # pull out starting scaling_factor for this parameter
			
			self.parameter_list.append(TestParameter(gamma,scaling_factor, parameter + 1))
			
	def sortSimplex(self): # no change needed 
		sorting_list = [] # list used to sort
		for parameter in self.parameter_list: # pull out the parameter objects
			sorting_list.append([parameter.edge_efficiency,parameter.index]) # add the values we want to look at to the sorting list
		
		sorting_list = sorted(sorting_list, key = itemgetter(0)) #sort the list by the edge efficiency
		print sorting_list
		for index in xrange(len(sorting_list)): # reassign the indeces for each parameter
			for parameter in self.parameter_list:
				if parameter.edge_efficiency == sorting_list[index][0]:
					parameter.updateIndex(index+1)
		for parameter in self.parameter_list:
			#print parameter.index
			if parameter.index == self.size: # now that it has a new parameter
				self.worst_parameter = parameter
			elif parameter.index == self.size-1:
				self.second_worst_parameter = parameter
			elif parameter.index == 1:
				self.best_parameter = parameter

	def getCentroid(self): # change to get the centroid of the scaling parameter and gammas 
		
		eligible_parameters = [self.parameter_list[x] for x in xrange(len(self.parameter_list)) if self.parameter_list[x].index <= self.size - 1  ] # leaves off worst parameter
		#print eligible_parameters
		
		eligible_gammas = [x.gamma for x in eligible_parameters] # get list of gammas 
		cent_gamma = sum(eligible_gammas)/float(self.size - 1) # centroid for gamma		
		print "eligible_gammas = ", eligible_gammas


		eligible_scaling_factors = [x.scaling_factor for x in eligible_parameters] # get list of ms
		cent_scaling_factor = sum(eligible_scaling_factors)/float(self.size - 1 )# centroid for message numbers
		print "scaling factors = ",eligible_scaling_factors
		self.centroid = TestParameter(cent_gamma, cent_scaling_factor,0)

		return TestParameter(cent_gamma, cent_scaling_factor, 0) # return the parameter for the centroid 

	def getReflection(self, xalpha,xfile_name_list, xnode_number): # calculate and return the reflection point 
		print self.centroid.returnParameterList()
		print self.worst_parameter.returnParameterList()
		r_gamma  = self.centroid.gamma + xalpha*(self.centroid.gamma - self.worst_parameter.gamma) # gamma 
		r_scaling_factor = self.centroid.scaling_factor + xalpha*(self.centroid.scaling_factor - self.worst_parameter.scaling_factor) # scaling factor 
		self.reflection = TestParameter(r_gamma, r_scaling_factor, 'r')
		self.reflection.getModelValues( xfile_name_list, xnode_number, self.periods)
		reflection = self.reflection
		print "Reflection Parameters = ", reflection.returnParameterList()
		return reflection


	def getExpansion(self, xgamma,xfile_name_list,xnode_number): # calculate and return the expansion point
		e_gamma  = self.centroid.gamma + xgamma*(self.reflection.gamma - self.centroid.gamma) #gamma
		e_scaling_factor = self.centroid.scaling_factor + xgamma*(self.reflection.scaling_factor - self.centroid.scaling_factor)#scaling Factor 
		expansion = TestParameter(e_gamma, e_scaling_factor, 'e')
		expansion.getModelValues( xfile_name_list, xnode_number, self.periods)
		print "Expansion Parameters = ",
		print expansion.returnParameterList()
		return expansion


	def getContraction(self, xrho, xfile_name_list, xnode_number): # calculate and return the contraction point
		c_gamma  = self.centroid.gamma + xrho*(self.worst_parameter.gamma - self.centroid.gamma)
		c_scaling_factor = self.centroid.scaling_factor + xrho*(self.worst_parameter.scaling_factor - self.centroid.scaling_factor)
		contraction = TestParameter(c_gamma, c_scaling_factor, 'c')
		contraction.getModelValues( xfile_name_list, xnode_number, self.periods)
		print "Contraction Parameters = ", contraction.returnParameterList()
		return contraction


	def computeShrink(self,xsigma):
		for parameter in(x for x in self.parameter_list if x.index != 1):
			parameter.gamma = self.best_parameter.gamma + xsigma*(parameter.gamma - self.best_parameter.gamma)
			parameter.scaling_factor = self.best_parameter.scaling_factor + xsigma*(parameter.scaling_factor - self.best_parameter.scaling_factor)

	def insertNewParameter(self, newParameter, xbest = False):
		self.parameter_list.remove(self.worst_parameter) # remove the occurence of the worst parameter from the paramter list
		newParameter.updateIndex(self.size) # set the index of the new parameter to the worst index
		self.parameter_list.append(newParameter) # add the new parameter to the list of parameters
		if xbest:
			self.best_parameter = newParameter
		
class TestParameter(object):
	
	def __init__(self, xgamma, xscaling_factor, xindex,xmodel_runs = 1):
		self.gamma = xgamma
		self.scaling_factor = xscaling_factor
		self.model_runs = xmodel_runs
		self.index = xindex
		self.edge_efficiency = None
		self.inverse_distance = None
		self.edge_ratio = None
		#self.calculated = 0
		self.list_of_efficiencies = []
		
	
	def getModelValues(self, xfile_name_list, xnode_number,xperiods):
		edge_ratios = [] # intermediate to hold for average edge ratio
		edge_efficiencies = [] #intermediate to hold for efficiency calculation
		inverse_distances = [] # intermediate to hold for
		scaling_factor = self.scaling_factor
		max_periods = xperiods
		gammas = self.gamma
		edge_numbers = [] 

		for file_name in xfile_name_list:
			if file_name[-2] == 'x':
				xtest_list = ergm_samples_dict[xnode_number][file_name]['edge_set']
			else:
				xtest_list= dict_of_nets[xnode_number][file_name]['edge_set']
			model_results = model.runsimulation(xnode_number,gammas,scaling_factor,xtest_list,max_periods,file_name)[0]

			edge_ratios.append(model_results[0])
			edge_efficiencies.append(model_results[2])
			inverse_distances.append(model_results[1])
			edge_numbers.append(model_results[3])
			
		self.inverse_distance = sum(inverse_distances)/float(len(xfile_name_list)) # update the inverse distance value
		self.edge_ratio =sum(edge_ratios)/float(len(xfile_name_list))  # update the edge ratio value
		self.list_of_efficiencies.append( sum(edge_efficiencies)/float(len(xfile_name_list))) # update the edge efficiency value 
		self.edge_efficiency = float(sum(self.list_of_efficiencies))/float(len(self.list_of_efficiencies))
		self.edge_number = float(sum(edge_numbers))/float(len(edge_numbers))
		print "" 
		print "index", self.index
		print "gamma,w", self.gamma, self.scaling_factor
		print "inverse distance", self.inverse_distance
		print "edges used ", self.edge_number
		print "edge ratio: ", self.edge_ratio
		print "edge efficiency", self.edge_efficiency
		print "" 
		

	def updateIndex(self,new_index):
		self.index = new_index
	
	def returnParameterList(self):
		return [self.gamma, self.scaling_factor, self.edge_efficiency]

def NelderMeadAlgorithm( xtest_file_list, xnode_number,xstarting_parameters,xperiods = 10,xstalling_parameter = 5, xrho = .5, xalpha = 1, xgamma = 2, xsigma = .5):
	number_of_vertices = len(xstarting_parameters['gammas'])
	list_of_vertices = AlgorithmVertices(number_of_vertices, xstarting_parameters['gammas'],xstarting_parameters['scaling_factor'],xnode_number, xperiods)
	list_of_vertices.CreateParameters() # create the vertices object and the parameters
	list_of_best_parameters = [] # will keep track of the history of the best parameters as the best parameter is updated 
	best_efficiency = 100000  # tracks best value during this iteration of the algorithm
	best_parameter_setting = None # tracks the best parameter during this iteration of the algorithm
	stalling_count = 0
	periods = xperiods

	
	while stalling_count < xstalling_parameter: # start the algorithm iterations 

		for parameter in list_of_vertices.parameter_list: # calculate the values for all of the parameters
			parameter.getModelValues(xtest_file_list, xnode_number,periods) 

		list_of_vertices.sortSimplex() # sort the simplex
		list_of_vertices.getCentroid() # calculate the centroid 

		reflection_point = list_of_vertices.getReflection(xalpha,xtest_file_list, xnode_number) # calculate the value of the reflection point
		
		if reflection_point.edge_efficiency < list_of_vertices.second_worst_parameter.edge_efficiency and reflection_point.edge_efficiency > list_of_vertices.best_parameter.edge_efficiency:
			list_of_vertices.insertNewParameter(reflection_point) # add the reflection point to the simplex. Remove worst paramter
			print "Iteration Stopped at Reflection"
		elif reflection_point.edge_efficiency < list_of_vertices.best_parameter.edge_efficiency:
			expansion_point = list_of_vertices.getExpansion(xgamma, xtest_file_list, xnode_number)
			
			if expansion_point.edge_efficiency < reflection_point.edge_efficiency: # if the expansion point is better 
				list_of_vertices.insertNewParameter(expansion_point, True) # add it to the simplex, update best parameter
				print "Iteration Stopped at Expansion"
			else:
				list_of_vertices.insertNewParameter(reflection_point, True) # add reflection point to simplex, add it to the simplex
				print "Iteration Stopped at Expansion"
		else:
			contraction_point = list_of_vertices.getContraction(xrho, xtest_file_list, xnode_number)
			if contraction_point.edge_efficiency < list_of_vertices.worst_parameter.edge_efficiency:
				list_of_vertices.insertNewParameter(contraction_point)
				print "Iteration Stopped at Contraction"
			else:
				list_of_vertices.computeShrink(xsigma)
				print "Iteration Stopped At Shrink"


		if list_of_vertices.best_parameter.edge_efficiency < best_efficiency: # if there is a new best global value
			best_efficiency = list_of_vertices.best_parameter.edge_efficiency
			list_of_best_parameters.append(copy.deepcopy(list_of_vertices.best_parameter))
			best_parameter_setting = copy.deepcopy(list_of_vertices.best_parameter)
			stalling_count = 0
			
		else:
			stalling_count += 1 
		
		print ""
		print list_of_vertices.best_parameter.returnParameterList()
		print "Current Stalling Count = ", stalling_count
		print "Best Value History = ", [x.edge_efficiency for x  in list_of_best_parameters]
		print ""
	output_dictionary = {'best_parameter': list_of_vertices.best_parameter, 'run_history':list_of_best_parameters,\
	'global min':best_efficiency, 'global min parameter': best_parameter_setting}
	
	return output_dictionary
	
