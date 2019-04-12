# -*- coding: utf-8 -*-
"""
Created on Wed May 18 12:11:47 2016

@author: Chris
"""

import copy
import math
import random
from operator import itemgetter

import networkx as nx
import numpy as np


# This class is going to keep track of the entire graph, it will inherit the methods and variables from networkx

class UAVnet(nx.DiGraph):  # DiGraph is a class in networkx, this makes us inherit the Directed Graph class from networkx

	def __init__(self):
		self.p = .2
		self.node_objs = []
		self.is_markov_graph = False
		self.aux_target_nodes = []  # the list of target nodes that will be updated whenever probabilities are solved
		self.aux_source_nodes = []  # same as above but with the source nodes
		self.aux_self_nodes = []  # same as above, but with self nodes
		self.Markov_Probabilities = {}  # used to save and communicate probabilities and edge numbers
		self.current_period = 0  # the current period of the simulation MIGHT NOT NEED
		self.total_possible_edge_list = []  # the total possible edge list based on the current simulation instance
		self.bid_list = {}  # the list of the bids that need to be send to the uavs that are being asked to connect to
		self.decision_list = []  # the decisions that are returned from uavs that have been bid at
		self.potential_edge_list = []  # the potential edge list. basically the total_possible_edge_list - UAVnet.edges()
		self.round_of_decisions = 0  # this will keep track of how many decisions have been made when deciding the bid lists
		super(UAVnet,self).__init__()  # will give the class all of the other variables and methods that are saved to networkx DiGraph Class

	def UpdatePotentialEdges(self):

		self.potential_edge_list = []  # reset the list
		self.decision_list = []  # resets the decision list
		for possible_edge in self.total_possible_edge_list:  # loop through the possible edges
			if possible_edge not in self.edges():  # if the edge is not in use
				self.potential_edge_list.append(possible_edge)  # add it to the list

	# This method will set up the matrix used to create a markov matrix, this markov matrix will be used
	# To find the probabilities of messages reaching other nodes in the system
	# converts the array of arrays to a numpy matrix? 

	def CreateMarkovDictionary(self):
		self.bid_list = {}
		for node in self.nodes():
			self.bid_list[node] = []
		self.Markov_Probabilities['Total_Lists'] = {}  # create the total probability dictionaries
		self.Markov_Probabilities['Neighbor_Lists'] = {}  # create the neighbor list sub dictionary
		for node in self.nodes():  # create add to the dictionary for every node
			self.Markov_Probabilities['Total_Lists'][node] = [0 for x in range(len(self.nodes()))]  # create the list of probabilities for total probability
			self.Markov_Probabilities['Neighbor_Lists'][node] = {}  # create the neighbor list sub-dictionary
		for node in self.node_objs:  # loop through all the nodes again
			self.Markov_Probabilities['Neighbor_Lists'][node.name] = {}  # create the neighbor sub dictionary
			for neighbor in node.incoming_ties:  # cycle through the list of nodes that are indirected neighbors of the node in question
				self.Markov_Probabilities['Neighbor_Lists'][node.name][neighbor] = [0 for x in range(len(self.nodes()))]  # sets up the probability array for neighbors

	# this method adds the auxiliary nodes to the markov graph, dependent on a source and target node
	def AddAuxNode(self, xsource_node, xtarget_node):  # target and source node have to be objects

		if self.is_markov_graph:  # if the graph is a markov graph
			for out_neigh in xsource_node.outgoing_ties:  # for the out-directed ties
				self.add_node("%s,source,aux" % out_neigh)  # 1012 is node 1 to node 12 , out-directed ties
				self.add_edge(xsource_node.name, "%s,source,aux" % out_neigh)  # this creates the edge between the source and the aux source node
				self.add_edge("%s,source,aux" % out_neigh,out_neigh)  # this adds the edge between the aux and the outward neighbor
				self.remove_edge(xsource_node.name, out_neigh)  # this removes the original edge
				self.aux_source_nodes.append("%s,source,aux" % out_neigh)  # save it to the aux source node list

			for in_neigh in xtarget_node.incoming_ties:  # this creates the in-directed aux nodes

				self.add_node("%s,target,aux" % in_neigh)  # create the aux node for the in-directed neighbor
				if in_neigh == xsource_node.name:
					self.add_edge("%s,source,aux" % xsource_node.name, "%s,target,aux" % in_neigh)  # add the edge between the indirected neighbor and its aux node
				else:
					self.add_edge(in_neigh, "%s,target,aux" % in_neigh)  # add the edge between the indirected neighbor and its aux node

				self.add_edge("%s,target,aux" % in_neigh, "%s,target,aux" % in_neigh)  # make the aux target node absorbing
				if xtarget_node.name in self.nodes():
					self.remove_node(xtarget_node.name)  # this removes the target node
				self.aux_target_nodes.append("%s,target,aux" % in_neigh)  # save it to the aux target node list

			for node in self.nodes():  # create the absorption nodes for the message dying
				self.add_node("%s,absorb" % node)  # create the absorption node
				self.add_edge(node, "%s,absorb" % node)  # create the edge to the absorption node
				self.add_edge("%s,absorb" % node, "%s,absorb" % node)  # create the edge to itself
				self.aux_self_nodes.append("%s,absorb" % node)  # save it to the self aux node list

	# this method will solve the markov matrix for any set of target and source nodes
	# it will also pass the results to the uav objects in the list of objects 
	def Update_MC_Matrix(self, xsource_node, xtarget_node, xUAVnet):
		node_order_list = []

		if self.is_markov_graph:  # if the graph being solved is the markov graph it will pass this test
			self.AddAuxNode(xsource_node, xtarget_node)  # add all of the aux nodes and set the graph up correctly
			number_of_aux_source_nodes = len(xsource_node.outgoing_ties)  # record the number of outgoing aux nodes
			number_of_aux_target_nodes = len(xtarget_node.incoming_ties)  # record the number of incoming aux nodes
			no_nodes_original = len(xUAVnet.nodes()) - 1  # record the number of original nodes 
			l = no_nodes_original + number_of_aux_target_nodes + number_of_aux_source_nodes  # record the number of those three aded togethter
			# this sets up the order list for the matrix, allows me to know where the target nodes are going to be every time that I am solving the equations
			for node in self.node_objs:  # first the original nodes without the current target node is added
				if node.name != xtarget_node.name:
					node_order_list.append(node.name)

			for out_neighbor in xsource_node.outgoing_ties:  # then the source auxiliary nodes are added
				node_order_list.append("%s,source,aux" % out_neighbor)

			for in_neighbor in xtarget_node.incoming_ties:  # then the target aux nodes are added
				node_order_list.append("%s,target,aux" % in_neighbor)
			for node in self.node_objs:  # then the self nodes are added
				if node.name != xtarget_node.name:
					node_order_list.append("%s,absorb" % node.name)

			matrix_A = nx.to_numpy_matrix(self, nodelist=node_order_list)  # the total matrix

			matrix_T = matrix_A[0:no_nodes_original, 0:(
					no_nodes_original + number_of_aux_source_nodes + number_of_aux_target_nodes)]  # the matrix that needs to get the probability of random walk placed in
			matrix_abs = matrix_A[0: no_nodes_original,
						 (no_nodes_original + number_of_aux_source_nodes + number_of_aux_target_nodes):(
								 2 * no_nodes_original + number_of_aux_source_nodes + number_of_aux_target_nodes)]  # the self node ties

			for node in range(len(
					matrix_T)):  # input the probability of a message being passed to any of the outgoing neighbors random walk
				number_of_outward = matrix_T[node].sum()
				for other_node in range(l):
					if matrix_T[node, other_node] > 0:
						matrix_T[node, other_node] = (1 - float(self.p)) / number_of_outward

			for node in range(len(matrix_abs)):  # then input the probability of messages dying
				for other_node in range(no_nodes_original):
					if matrix_abs[node, other_node] > 0:
						matrix_abs[node, other_node] = self.p

			Matrix_t = matrix_A[0: no_nodes_original + number_of_aux_source_nodes,
					   0:no_nodes_original + number_of_aux_source_nodes]  # this is the actual transient matrix
			Identity = np.identity(
				no_nodes_original + number_of_aux_source_nodes)  # the identity matrix that is needed to solve the probability
			matrix_B = copy.deepcopy(matrix_A)
			matrix_solver = Identity - Matrix_t  # the matrix that needs to be inverted
			nodes_that_are_solving = [x for x in node_order_list[
												 no_nodes_original + number_of_aux_source_nodes: no_nodes_original + number_of_aux_source_nodes + number_of_aux_target_nodes]]  # the neighbors of the target nodes, the aux nodes for the target nodes

			for indirected_neighbor in range(
					number_of_aux_target_nodes):  # run it over all in-directed neighbors of the target node
				node_being_grabbed = node_order_list[
					no_nodes_original + number_of_aux_source_nodes + indirected_neighbor]

				split_to_original = node_being_grabbed.split(",")
				neighbor_node = int(split_to_original[0])

				solved_probs = matrix_solver.I * matrix_B[0:no_nodes_original + number_of_aux_source_nodes,
												 no_nodes_original + number_of_aux_source_nodes + indirected_neighbor]  # the list of the total solved probabilities

				solver_tracker = []  # used to save the correct probabilities 
				for node in range(number_of_aux_source_nodes):  # over the number of aux target nodes
					solver_tracker.append((1 / float(number_of_aux_source_nodes)) * solved_probs[
						no_nodes_original + node, 0])  # save the correct probability

				total_prob_to_target = sum(solver_tracker)  # use the sum as the probability saved

				xUAVnet.Markov_Probabilities['Neighbor_Lists'][xtarget_node.name][neighbor_node][
					xsource_node.name] = total_prob_to_target  # save it to the original graphs dictionary

			total_total_tracker = []  # this is used as an intermediate dictionary to save the probabilities of all the aux target nodes
			for node in nodes_that_are_solving:  # for the nodes that we solved for
				second_split_for_neighbor = node.split(",")
				in_neighbor = int(second_split_for_neighbor[0])  # return them back to their original number
				total_total_tracker.append(
					xUAVnet.Markov_Probabilities['Neighbor_Lists'][xtarget_node.name][in_neighbor][
						xsource_node.name])  # append the probability to the intermediate list

			total_total = sum(total_total_tracker)

			xUAVnet.Markov_Probabilities['Total_Lists'][xtarget_node.name][
				xsource_node.name] = total_total  # the total probability

	# this method will take bids from the uavs and communicate to the node being asked to connect to
	# the uav being asked will decide who gets the tie, based on the information passed to it.

	def ModifyGraph(self):
		for node in self.node_objs:
			node.CreateDecisionList()
			node.FinalDecisionList(self)
			self.decision_list.append(node.final_list_of_decisions[0])

		for decision in self.decision_list:  # loop through the decision list

			if decision[2] == 1:  # if the decision is adding a tie
				self.add_edge(decision[1], decision[3])  # add the edge from the bid decider to the the source node
			elif decision[2] == -1:  # if the node is deleting a tie
				self.remove_edge(decision[1], decision[3])  # delete the tie

	# this method will run the simulation based on the number of periods and number of messages to be passed
	# Not sure that this will be the method that I decide to run. Might keep it outside of methods in the simulation function
	##TODO can I remove this method?
	def Simulate_Network_Modification(self, xtotal_number_of_periods, xmessages_per_period):
		while self.current_period <= xtotal_number_of_periods:
			pass
			self.current_period += 1

############################ UAV CLASS ##############################################################
"""
Class Variables:

Name - the name of the UAV (node) (int)
Potential Edges - list of edges that are possible to this node, given the current instance of simulation (list of ints)
Outgoing Ties - list of uavs that are connected in outward ties (list)
Incoming Ties - list of uavs that are connected in inward ties (list)

Alpha - the probability of a message being lost (float) (instance variable?)
P - The weight of a uav's preference between outgoing neighbors preferences and their own (float)(instance variable)
Cost - the cost per tie (member variable)

Beta_own, Beta_Neighbors, Beta_overall - the lists and dictionary of lists that keeps track of a nodes prefrences, and those of the outward ties
(list, dictionary of lists, list)

Number_of_Messages_from_Neighbors - a dictionary of lists, will keep track of the amount of messages received from each source node, through a neighbor node
( dictionary of lists)
Number_of_Messages_total - a list of all the messages received from every source node include itself (list)

Objective_Value - the current "happiness level" based on the total number of received messages and the beta values
Addition_estimates - a list of the objective equation after making any valid addition estimate, if any (list of tuples)
Subtraction_estimates - a list of the objective equation value after making any valid subtraction of tie, if any (list of tuples )

Bid Decision - a tuple that keeps track of the randomly decided bid decision, based on the objective value of that decision (tuple)
Node Decision - the final decision the node makes after bidding is complete, and a valid decision has been made (tuple)
Modification_Track - will keep track of whether or not the node has made a modification, if there is one to be made (boolean)

list_of_messages - a list of the message objects currently at the UAV, used in the dynamic simulation only
"""

# Methods for UAVS
class UAV(object):
	# cost = 100.0 # find a better value for this? just a place holder
	def __init__(self, xname, xpotential_edge_list, xscaling_factor, xgamma):
		self.name = xname
		self.potential_edges = xpotential_edge_list  # This is overidden by attribute creating functions
		self.alpha = .2  # placeholder, might need to be changed
		self.P = .5  # placeholder, might need to be changed
		self.scaling_factor = xscaling_factor
		self.gamma_cost = None
		self.gamma = xgamma
		self.outgoing_ties = []
		self.incoming_ties = []
		self.incoming_objects = []
		self.outgoing_objects = []
		self.potential_objects = []
		self.prob_list_neighbors = {}
		self.prob_list_total = []
		self.Beta_own = []
		self.Beta_Overall = []
		self.Beta_neighbors = []
		self.addition_estimates = []
		self.subtraction_estimates = []
		self.decision_list = []
		self.modification_track = False
		self.objective_value = -100000000000.000  # just a placeholder, will be changed to reflect something else
		self.too_isolated = False
		self.probability_list = []
		self.total_pull_cost = None  # will be used to keep track of the cost of pulling from the node

	def CreateAttributes(self, xUAVnet):
		self.potential_edges = []
		for edge in xUAVnet.potential_edge_list:
			if edge[1] == self.name and edge not in self.potential_edges:
				self.potential_edges.append(edge)

		for edge in xUAVnet.edges():
			if edge[0] == self.name:  # if the tie is first on the list its outgoing
				self.outgoing_ties.append(edge[1])  # append the node to the list of outgoing neighbors
			elif edge[1] == self.name:  # if the tie is second on the tuple its incoming
				self.incoming_ties.append(edge[0])  # append the node to the list of in-directed neighbors

		if len(self.incoming_ties) > 0:  # if the number of incoming ties is >0
			for node in self.incoming_ties:  # loop over the in-directed ties
				self.prob_list_neighbors[node] = [0 for x in range(
					len(xUAVnet.nodes()))]  # create the message from neighbors dictionary

		for node in range(len(xUAVnet.nodes())):  # create the lists to the correct lengths
			self.prob_list_total.append(0)
			self.Beta_own.append(0)
			self.Beta_Overall.append(0)
			self.Beta_neighbors.append(0)

		if len(self.incoming_ties) <= 2:
			self.too_isolated = True
		else:
			self.too_isolated = False

		self.gamma_cost = len(self.outgoing_ties) * self.gamma  # make this different. Gamma has to

	# Add logic that will take the edges in use off of the potential edge list for the uav, once the edge is added it should not be used again
	# this method will be used to update the variable potential edge_lists 
	def UpdateEdgesandAttributes(self, xuavnetwork):
		self.potential_edges = []
		for edge in xuavnetwork.potential_edge_list:
			if edge[1] == self.name and edge not in self.potential_edges:
				self.potential_edges.append(edge)
		self.outgoing_ties = []  # reset the outgoing ties
		self.incoming_ties = []  # reset the incoming_ties
		self.prob_list_total = []  # reset the message lists
		self.prob_list_neighbors = {}
		self.Beta_neighbors = []  # reset the beta attributes
		self.Beta_own = []
		self.Beta_Overall = []
		# The rest of this code is the same as the code used to create the attributes
		for edge in xuavnetwork.edges():
			if edge[0] == self.name:
				self.outgoing_ties.append(edge[1])
			elif edge[1] == self.name:
				self.incoming_ties.append(edge[0])

		if len(self.incoming_ties) > 0:
			for node in self.incoming_ties:
				self.prob_list_neighbors[node] = [0 for x in range(len(xuavnetwork.nodes()))]

		for node in range(len(xuavnetwork.nodes())):
			self.prob_list_total.append(0)
			self.Beta_own.append(0)
			self.Beta_Overall.append(0)
			self.Beta_neighbors.append(0)
		self.modification_track = False
		if len(self.incoming_ties) <= 2:
			self.too_isolated = True
		else:
			self.too_isolated = False
		self.probability_list = []

		self.decision_list = []
		self.modification_track = False
		self.addition_estimates = []
		self.subtraction_estimates = []
		self.potential_objects = []
		self.outgoing_objects = []
		self.incoming_objects = []
		self.final_list_of_decisions = None
		self.gamma_cost = len(self.outgoing_ties) * self.gamma

	def AttachNeighborObjects(self, xUAVnet):  # this goes through and saves the uav objects to each nodes lists. There are two lists
		for node in xUAVnet.node_objs:
			if node.name in self.outgoing_ties:
				self.outgoing_objects.append(node)
			if node.name in self.incoming_ties:
				self.incoming_objects.append(node)
			for potential_edge in self.potential_edges:
				if node.name == potential_edge[0] and node not in self.potential_objects:
					self.potential_objects.append(node)

	# this method will update the beta overall values as well as the beta neighbors attributes 
	def UpdateBetaOwn(self):
		for source in range(len(self.prob_list_total)):  # update the beta own
			self.Beta_own[source] = 1 / math.exp(-(1 - (self.prob_list_total[
				source])))  # beta own for ever source is equal to the negative exponent of the messages received from the source

	def UpdateBetaNeighbors(self, xUAVnet):  # update the beta neighbors
		if len(self.outgoing_ties) > 0:
			total_list = [0] * len(self.prob_list_total)  # keeps a sum of the betas for all the neighbors of the node
			Neighbor_object_list = []  # holds the node objects
			for node in xUAVnet.node_objs:  # appends the node objects into the list
				if node.name in self.outgoing_ties:  # if the node in question is a neighbor
					Neighbor_object_list.append(node)  # append the object to the list
			for neighbor in Neighbor_object_list:  # for the neighbor objects
				for source in range(len(self.prob_list_total)):  # for all the sources
					total_list[source] += neighbor.Beta_own[
						source]  # add their beta own values to the intermediate list
			for item in range(len(total_list)):  # take the average of each item from the toal intermediate sum list
				total_list[item] = total_list[item] / float(len(self.outgoing_ties))
			for item in range(len(total_list)):
				self.Beta_neighbors[item] = total_list[item]
		else:
			for item in range(len(self.Beta_own)):
				self.Beta_neighbors[item] = self.Beta_own[item]

	def UpdateBetaOverall(self):  # separate but doesnt need to be from update beta neighbors
		for item in range(len(self.Beta_Overall)):  # loop over every node in the list
			self.Beta_Overall[item] = (1 - self.P) * self.Beta_neighbors[item] + self.P * self.Beta_own[item]  # take the weighted average to find the beta overall for the node

	# this method will calculate the current objective value after a round of message passing 
	def CalculateObjective(self):

		objective_tracker = 0  # set an intermediate tracker for the value of the objective
		for node in range(len(self.prob_list_total)):  # loop over all nodes
			objective_tracker += self.Beta_Overall[node] * self.prob_list_total[node]  # take the weighted sum of all message counts, weighted by the beta overall value at that

		cost_tracker = 0  # set an intermediate tracker that tracks the value of the cost
		for neighbor in self.incoming_objects:  # for each neighbor that the agent is pulling from
			cost_tracker += neighbor.gamma_cost  # add their pull cost to the total cost
		self.total_pull_cost = self.scaling_factor * cost_tracker
		self.objective_value = objective_tracker - self.total_pull_cost  # this is the current objective function

	# this method will update the list of estimates for adding a valid node to the incoming ties
	def EstimateAdditions(self):
		self.addition_estimates = []
		if len(self.potential_objects) > 0:
			for node in self.potential_objects:
				neighbor_cost = node.gamma * (len(node.outgoing_ties) + 1)
				neighbor_outgoing_ties = len(node.outgoing_ties)  # save amount of outgoing ties the neighbor already has
				neighbor_prob_list = node.prob_list_total  # save the message counts from the last round
				intermediate_prob_list = [0] * len(self.prob_list_total)  # save an intermediate list that will sum lists
				for index in range(len(self.prob_list_total)):  # loop over the message indexes
					intermediate_prob_list[index] = self.prob_list_total[index] + neighbor_prob_list[index] * (1 / float(neighbor_outgoing_ties + 1))  # estimate the messages received from the neighbor
					intermediate_prob_list[index] = intermediate_prob_list[index] * self.Beta_Overall[index]  # weight it
				updated_objective = sum(intermediate_prob_list) - (self.total_pull_cost + (self.scaling_factor * neighbor_cost))

				delta_obj = updated_objective - self.objective_value  # find the change in objective

				# FIGURE OUT HOW TO FIX THIS
				if not self.too_isolated:  # the node will lie if it is too isolated
					self.addition_estimates.append(
						[self.objective_value + delta_obj, node.name, 1])  # if it isn't isolated just report normal
				else:
					self.addition_estimates.append([self.objective_value + 2 * delta_obj, node.name, 1])  # report twice the value if it is too isolated

	# this method will update the list of estimates for subtraction a valid node from the current incoming ties
	def EstimateSubtraction(self):
		self.subtraction_estimates = []
		if not self.too_isolated:  # if current node is not too isolated
			# print self.incoming_objects[0].name,self.name
			for node in self.incoming_objects:  # look at currently connected nodes

				neighbor_prob_list = self.prob_list_neighbors[
					node.name]  # extract the message list from the neighbor node
				prob_list_without_neighbor = [0] * len(
					self.prob_list_total)  # create list to use for updating information
				for index in range(len(self.prob_list_total)):  # loop over the list indexes
					prob_list_without_neighbor[index] = self.prob_list_total[index] - neighbor_prob_list[index]  # save the message count without the neighbors messages
					prob_list_without_neighbor[index] = prob_list_without_neighbor[index] * self.Beta_Overall[index]  # multiply by the weights
				cost_without_neighbor = self.total_pull_cost - (self.scaling_factor * (node.gamma_cost))  # find the new total pull cost if the neighbor is deleted
				updated_objective = sum(prob_list_without_neighbor) - cost_without_neighbor  # find the updated objective
				self.subtraction_estimates.append([updated_objective, node.name, -1])
		else:
			self.subtraction_estimates = []

	# this method will create the random bid choice, 
	def CreateDecisionList(self):
		self.decision_list = []
		self.decision_list.append(
			[self.objective_value, self.name, 0])  # th do nothing decision is added to the decision list
		if len(self.addition_estimates) > 0:  # if there are addition estimates
			for addition_estimate in self.addition_estimates:  # add the addition estimate to the decision list
				self.decision_list.append(addition_estimate)
		if len(self.subtraction_estimates) > 0:  # if there are subtraction estimates
			for subtraction_estimate in self.subtraction_estimates:  # add the subtraction estimate to the decision list
				self.decision_list.append(subtraction_estimate)

	# this method will pass the final decision of the uav
	def FinalDecisionList(self, xUAVnet):
		self.final_list_of_decisions = None
		self.final_list_of_decisions = sorted(self.decision_list, key=itemgetter(0),
											  reverse=True)  # sort the decisions by their effect on the objective

		for decision in self.final_list_of_decisions:
			decision.append(self.name)

	# f3 = open("15_Testing_decision_lists.txt" ,"a")
	# f3.write("Node" + str(self.name) + "\n")
	# f3.write("Decision List " + str(self.final_list_of_decisions) +"\n")
	# f3.write("Possible Edges " + str(self.potential_edges)+"\n")
	# f3.write("Connections " + str(self.incoming_ties) +"\n")
	# f3.write("\n")
	# f3.write("\n")
	# f3.close()

	# this method will initialize the first connections for the graph if the initial simulation graph is empty
	# this method will also run if a UAV has decided to delete its ties incoming and has isolated itself
	def UnisolateUAV(self, xUAVnet, seed):
		edge_choices = []  # saves the list of possible edges to add to un-isolate itself

		for edge in self.potential_edges:  # looks at all the possible edges in the graph
			if edge[1] == self.name:  # if the edge is an in-directed edge and shares the same name as the node
				edge_choices.append(edge[0])  # add it to the list of choices for the node

		random.seed(seed)
		edge_to_add = random.choice(edge_choices)  # make a random choice of the edge to add to the graph
		xUAVnet.add_edge(edge_to_add, self.name)  # add the edge to the graph


# To avoid complicated logic here, the unisolate function does not currently take into account restrictions on the number of outward ties nodes can have
# If the simulation is not performing well then I can add the logic in to make sure that it will only add outdirected ties to eligible nodes


# This classs will save the results
class FinalResults(object):
	def __init__(self, xpossible_edge_list, xfinal_edge_list, xnumber_of_nodes, xnumber_of_rounds, xgraph_name, xgamma,
				 xscaling_factor, xefficiency_scale):
		self.possible_edge_list = xpossible_edge_list
		self.final_edge_list = xfinal_edge_list
		self.number_of_nodes = xnumber_of_nodes
		self.gamma = xgamma
		self.scaling_factor = xscaling_factor
		self.number_of_rounds = xnumber_of_rounds
		self.graph_name = xgraph_name
		self.efficiency_scale = xefficiency_scale

		final_graph = UAVnet()  # saves the final graph
		final_graph.add_nodes_from(range(self.number_of_nodes))  # creates the nodes for the final graph
		final_graph.add_edges_from(self.final_edge_list)  # creates the edges for the final graph
		distance_list = []  # tracks the distance
		shortest_path_dicts = nx.shortest_path(final_graph)  # create the shortest path dictionary
		for node in range(self.number_of_nodes):  # loop through all nodes
			for target in range(self.number_of_nodes):  # loop through all nodes
				if target in shortest_path_dicts[
					node] and target != node:  # if there is a path from the target to the source
					distance_list.append(1 / float(
						len(shortest_path_dicts[node][target]) - 1))  # save the inverse distance to that target
				elif target != node and target not in shortest_path_dicts[node]:  # if there is no path save o
					distance_list.append(0)

		fully_connected_graph = UAVnet()  # save th fully connected graph
		fully_connected_graph.add_nodes_from(range(self.number_of_nodes))  # add the nodes to the fully connected graph
		fully_connected_graph.add_edges_from(self.possible_edge_list)  # add the edges from the total possible edge set
		fully_connected_distance_list = []  # tracks the inverse distances
		fully_connected_path_dicts = nx.shortest_path(
			fully_connected_graph)  # same procedure as above, saves the optimal aver inverse distance
		for source in range(self.number_of_nodes):
			for target in range(self.number_of_nodes):
				if target in fully_connected_path_dicts[source] and target != source:
					fully_connected_distance_list.append(1 / float(len(fully_connected_path_dicts[source][target]) - 1))
				elif target != source and target not in fully_connected_path_dicts[source]:
					fully_connected_distance_list.append(0)

		self.fully_connected_inverse_distance = float(sum(fully_connected_distance_list)) / float(
			len(fully_connected_distance_list))  # save the average inverse distance
		self.average_inverse_distance = float(
			float(sum(distance_list)) / float(len(distance_list)))  # save the instance average inverse distance
		self.ratio_of_edges = float(
			float(len(self.final_edge_list)) / float(len(self.possible_edge_list)))  # save the ratio of edges
		self.edge_inverse_distance_ratio = self.ratio_of_edges / self.average_inverse_distance

		try:
			self.average_distance = nx.average_shortest_path_length(final_graph)
		except nx.NetworkXError:
			self.average_distance = "BAD GRAPH UNCONNECTED"

		self.fully_connected_graph_distance = nx.average_shortest_path_length(fully_connected_graph)
		self.pos = nx.spring_layout(final_graph)
		nx.set_node_attributes(final_graph, 'pos', self.pos)
		self.final_graph = final_graph

		self.edge_efficiency = math.exp(
			self.average_inverse_distance * self.efficiency_scale) * self.number_of_nodes / float(
			len(self.final_edge_list))
		self.fully_connected_edge_efficiency = math.exp(
			self.fully_connected_inverse_distance * self.efficiency_scale) * self.number_of_nodes / float(
			len(self.possible_edge_list))
		self.edge_number = len(self.final_edge_list)

		if self.average_distance == "BAD GRAPH UNCONNECTED":
			self.unpenalized_efficiency = self.edge_efficiency
			self.edge_efficiency = (self.edge_efficiency) / 100.0  # penalize the graphs that are unconnected

	def ReportResults(self):  # write the detailed results to a file
		# f2 = open("/Users/cmdiaz93/Documents/%s_node_results_ergm/%s_node_results_lists_final.txt" % (self.number_of_nodes, self.number_of_nodes),'a')
		# f2 = open("%s_node_restriction_analysis.txt" % self.number_of_nodes, 'a')
		f2 = open("%s_node_newest_model_results_analysis.txt" % self.number_of_nodes, 'a')
		f2.write("Possible Starting Edge List = " + str(self.possible_edge_list) + "\n")
		f2.write("Edge Number of Nodes = " + str(self.number_of_nodes) + "\n")
		f2.write("Number of Possible Edges = " + str(len(self.possible_edge_list)) + "\n")
		f2.write("\n")
		f2.write("Final Edge List = " + str(self.final_edge_list) + "\n")
		f2.write("Number of Edges Used= " + str(len(self.final_edge_list)) + "\n")
		f2.write("\n")
		f2.write("Gamma Parameter = " + str(self.gamma) + "\n")
		f2.write("Scaling Factor = " + str(self.scaling_factor) + "\n")
		f2.write("\n")

		f2.write("Average Distance = " + str(self.average_distance) + "\n")
		f2.write("Average Fully Connected Distance = " + str(self.fully_connected_graph_distance) + "\n")
		f2.write("Average Inverse Distance = " + str(self.average_inverse_distance) + "\n")
		f2.write("All Eligible Ties Connected Average Inverse Distance = " + str(
			self.fully_connected_inverse_distance) + "\n")
		f2.write("Percentage of Edges Used = " + str(self.ratio_of_edges) + "\n")
		f2.write("\n")
		f2.write("Final Graph Edge Efficiency = " + str(self.edge_efficiency) + "\n")
		f2.write("Fully Connected Edge Efficiency = " + str(self.fully_connected_edge_efficiency) + "\n")
		f2.write("\n")
		f2.write("Sample File Name =  " + str(self.graph_name) + "\n")
		f2.write("\n")
		f2.write("===========================")
		f2.write("\n")

		f2.close()
	"""
	This is something that I would like to explore, using a json representation of the results 
	that way I should be able to save and load objects faster 
	
		try:
			to_unicode = unicode
		except NameError:
			to_unicode = str
		with io.open("%s_node_newest_model_results_analysis.json" % self.number_of_nodes,'a',encoding='utf8') as outfile:
			str_ = json.dumps(vars(self),indent=4,sort_keys=True,
							  separators=(',',':'), ensure_ascii=False)
			outfile.write(to_unicode(str_))
			"""



# if(self.graph_name[-2] == 'e'):

# nx.write_pajek(self.final_graph,"/Users/cmdiaz93/Documents/%s_node_results_ergm/%s" % (self.number_of_nodes,self.graph_name))
# else:
#		if(int(self.graph_name[-5])== 0):
#			nx.write_pajek(self.final_graph,"/Users/cmdiaz93/Documents/%s_node_results_ergm/%s_ergm_10.net" % (self.number_of_nodes,self.number_of_nodes))
#		else:
#			nx.write_pajek(self.final_graph,"/Users/cmdiaz93/Documents/%s_node_results_ergm/%s_ergm_%s.net" % (self.number_of_nodes,self.number_of_nodes,self.graph_name[-5]))
