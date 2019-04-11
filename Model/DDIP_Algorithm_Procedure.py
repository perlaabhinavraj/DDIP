# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 13:53:26 2017

@author: Chris
"""
from DDIP_Model_Classes import UAVnet
from DDIP_Model_Classes import UAV
from DDIP_Model_Classes import FinalResults
import random 
import copy
def runsimulation(xnode_number, xgamma, xscaling_factor,xfeasible_edge_set, xnumber_of_periods, xgraph_name,xseed, xefficiency_scale = 2 ,xedge_number = 0):
	############################ THIS FIRST SECTION WILL INITIALIZE THE UAV NETWORK GRAPH #############################	
	#if xnumber_of_periods <= 0 or xmax_outgoing_ties < int(.2*xnode_number)  or xcost_of_ties <= 0 or xmessage_number <= 0: 
	#	return [2000,20000,2000]
	
	UAVnetwork = UAVnet()
	UAVnetwork.add_nodes_from([x for x in range(xnode_number)])
	
	UAVnetwork.total_possible_edge_list = copy.deepcopy(xfeasible_edge_set)

	UAV_list = [UAV(node, UAVnetwork.total_possible_edge_list, xscaling_factor, xgamma) for node in range(len(UAVnetwork.nodes()))]
	for node in UAV_list:
		UAVnetwork.node_objs.append(node)

		#MAKE SURE TO RESTRICT THE CHOICES TO THOSE WITHIN THE POSSIBLE EDGE SET
	if xedge_number != 0: # if there is an input for the number of starting edges on the initial graph
		number_of_edges_added = 0 # start with no edges added
		while number_of_edges_added < xedge_number: # keep adding new edges until there are the amount requested
			chosen_source = random.choice([x for x in range(xnode_number)])
			chosen_target= random.choice([x for x in range(xnode_number) if x != chosen_source])
			if (chosen_source, chosen_target) not in UAVnetwork.edges():
				UAVnetwork.add_edge(chosen_source, chosen_target)
				number_of_edges_added +=1 # only increase the counter if the edge is new
	else:# if there is no edge parameter set 
		for node in UAVnetwork.node_objs: # make sure that the nodes communicate their choices for the seed 
			node.UnisolateUAV(UAVnetwork, xseed) # un-isolate any nodes that have no in-directed communication network

	UAVnetwork.UpdatePotentialEdges() 
	for node in UAV_list:
		node.CreateAttributes(UAVnetwork) # create the attributes for all of the uavs in the list 
		
	UAVnetwork.CreateMarkovDictionary() # set up the markov probability dictionaries

	for uav in UAVnetwork.node_objs:
		uav.AttachNeighborObjects(UAVnetwork)
		
	##################################### THIS SECOND SECTION WILL START THE ACTUAL SIMULATION ####################################

	current_period = 0
	number_of_periods = int(xnumber_of_periods)
	while current_period < xnumber_of_periods:
		
		#print "UAV network edges period :", current_period
		#print UAVnetwork.edges()
		#print "" 
		for source_node in UAVnetwork.node_objs:
			for target_node in UAVnetwork.node_objs:
				MarkovNet = UAVnetwork.copy() # create the copy of the uavnetwork to be used to run the markov chain simulation
				MarkovNet.is_markov_graph = True # set it to be a markov graph allows the mc simulation methods to be ran. Safe gaurds
				MarkovNet.Update_MC_Matrix(source_node,target_node,UAVnetwork)
		for node in UAVnetwork.node_objs: # loop over the list of nodes 
			for source_nodes in UAVnetwork.nodes(): # loop over the list of nodes again
				
				node.prob_list_total[source_nodes] = UAVnetwork.Markov_Probabilities['Total_Lists'][node.name][source_nodes]# pass the number of messages simulated to the uavs
				for neighbors in node.incoming_ties: # loop over the list of neighbors
					node.prob_list_neighbors[neighbors][source_nodes]  = UAVnetwork.Markov_Probabilities['Neighbor_Lists'][node.name][neighbors][source_nodes]# pass the information of messages through neighbors to the uavs 

		for node in UAVnetwork.node_objs:
			node.UpdateBetaOwn() # update the beta own attribute

		for node in UAVnetwork.node_objs: # loop over the nodes again 
			node.UpdateBetaNeighbors(UAVnetwork) # update the beta neighbors
			node.UpdateBetaOverall() # update the beta overall

		for node in UAVnetwork.node_objs:
		
			node.CalculateObjective() # Calculate the current objective
			node.EstimateAdditions() # Calculate addition estimates
			node.EstimateSubtraction() # calculate subtraction estimates
			node.CreateDecisionList() # append all of the decisions estimates to a single list
			node.FinalDecisionList(UAVnetwork) # sort the decisions based on the estimated objective equation
		UAVnetwork.round_of_decisions = 0  # set the number of decision round to 0
		
		UAVnetwork.ModifyGraph() # modify the graph
		UAVnetwork.UpdatePotentialEdges() # update the potential edge list again
		for node in UAVnetwork.node_objs: # loop through the nodes
			node.UpdateEdgesandAttributes(UAVnetwork) # update the attributes of each node
			node.AttachNeighborObjects(UAVnetwork)
		UAVnetwork.CreateMarkovDictionary() # update the markov things 
		
		current_period += 1 
		
	#return FinalResults(xfeasible_edge_set,UAVnetwork.edges(),len(UAVnetwork.nodes()),xnumber_of_periods, xgraph_name,xgamma, xscaling_factor)
	#List_of_Results.append(FinalResults(xfeasible_edge_set,UAVnetwork.edges(),len(UAVnetwork.nodes()),xcost_of_ties,xnumber_of_periods, xgraph_name, xmax_outgoing_ties))
	
	result = FinalResults(xfeasible_edge_set,UAVnetwork.edges(),len(UAVnetwork.nodes()),xnumber_of_periods, xgraph_name,xgamma, xscaling_factor, xefficiency_scale)
	return [[result.ratio_of_edges, result.average_inverse_distance, 1/result.edge_efficiency,result.edge_number, result.efficiency_scale],result]

