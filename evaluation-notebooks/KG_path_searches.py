'''
Author: Sanya B Taneja
Date: 2021-09-29

KG path search functions to generate and save paths:
1. Single source shortest path: save_k_single_source_shortest_paths(G, source, k, filepath)
2. Bidirectional shortest path: get_bidirectional_shortest_paths(G, source, target)
3. k shortest paths: get_k_shortest_paths(G, source, target, k, weight='weight'), 
4. k simple paths (nodes and edges), with and without cutoff: 
	get_k_simple_paths(G, source, target, k, cutoff)
	save_k_simple_paths(G, source, target, k, cutoff, filepath)
5. print_graph_statistics(nx_graph): number of nodes, edges, average degree and density
'''

import os
import os.path
import networkx as nx
import json
import urllib
import traceback
from itertools import islice
from rdflib import Graph, URIRef, BNode, Namespace, Literal
from rdflib.namespace import RDF, OWL
from tqdm import tqdm

import pickle
import pandas as pd
import numpy as np
import sys

combine_graph = True
#change graph names and paths
KG_PATH = '../resources/knowledge_graphs/'
KG_NAME = 'PheKnowLator_machine_read_merged_instance_based_OWLNETS_v1.0.gpickle'

NodeLabelsFile = '../resources/nodeLabels_v1.0.pickle'
DIR_OUT = '../output_files/'

#read nodeLabels dictionary
with open(NodeLabelsFile, 'rb') as filep:
	nodeLabels = pickle.load(filep)

#define namespaces
obo = Namespace('http://purl.obolibrary.org/obo/')
napdi = Namespace('http://napdi.org/napdi_srs_imports:')

node_dict = {
	'EGCG': obo.CHEBI_4806,
	'CATECHIN': obo.CHEBI_23053,
	'GREENTEA': napdi.camellia_sinensis_leaf,
	'KRATOM': napdi.mitragyna_speciosa,
	'MITRAGYNINE': obo.CHEBI_6956,
	'HYDROXY_MITRAGYNINE': napdi['7_hydroxy_mitragynine']
}

nodes_to_filter = [obo.CHEBI_24431, obo.CHEBI_25367, obo.SO_0000704, obo.PR_000029067, obo.PR_000000001, obo.GO_0008152, obo.SO_0000673,
					URIRef('https://reactome.org/content/detail/R-HSA-1643685'), URIRef('https://reactome.org/content/detail/R-HSA-1430728')]

def save_k_single_source_shortest_paths(G, source, k, filepath):
	paths = nx.single_source_shortest_path(G, source)
	#if returned paths are dictionary
	count = 0
	file_save = open(filepath, 'w')
	print('Saving path from {}'.format(str(source)))
	for target, node_list in paths.items():
		count += 1
		if target != source:
			if str(target) not in nodeLabels:
				target_label = str(target).split('/')[-1]
			else:
				target_label = nodeLabels[str(target)]
			file_save.write('\n{} - {} Path:\n'.format(str(source).split('/')[-1], target_label))
			path_labels = get_path_labels(G, node_list)
			for triples in path_labels:
				for item in triples:
					file_save.write(str(item)+' ')
				file_save.write('\n')
		if count == k:
			break
	file_save.close()

'''
print bidirectional shortest path between source and target
and return length of shortest path
'''
def get_bidirectional_shortest_path(G, source, target, nodeLabels):
	print('Searching for path from {} - {}'.format(str(source), str(target)))
	pathx = nx.bidirectional_shortest_path(G, source, target)

	path_labels = get_path_labels(G, pathx, nodeLabels)
	path_uri = get_path_uri(G, pathx)
	for triples in zip(path_labels, path_uri):
		print(triples)
	return path_labels, path_uri

'''
returns path labels and URIs for simple paths from source to target that have length greater than shortest path
k = number of paths
cutoff = maximum length of path
shortestLens = length of shortest path between source and target
'''
def get_k_simple_paths(G, source, target, k, cutoff, shortestLens):
	print('Searching for paths from {} - {}'.format(str(source), str(target)))
	paths = nx.all_simple_edge_paths(G, source, target, cutoff=cutoff)
	path_l = []
	path_n = []
	i = 0
	while i<k:
		try:
			print('[info] applying next operator to search for a simple path of max length {}'.format(cutoff))
			path = next(paths)
		except StopIteration:
			break
		print('[info] Simple path found of length {}'.format(len(path))) 
		if len(path) > shortestLens:
			print('[info] Simple path length greater than shortest path length ({}) so adding to results'.format(shortestLens))
			path_n.append(path)
		i += 1

	for newpath in path_n:
		triple_list = []
		for triple in newpath:
			subj_lab = ''
			pred_lab = ''
			obj_lab = ''
			subj = str(triple[0])
			pred = str(triple[2])
			obj = str(triple[1])
			if subj in nodeLabels:
				subj_lab = nodeLabels[subj]
			if obj in nodeLabels:
				obj_lab = nodeLabels[obj]
			if pred in nodeLabels:
				pred_lab = nodeLabels[pred]
			triple_labels = (subj_lab, pred_lab, obj_lab)
			triple_list.append(triple_labels)
		path_l.append(triple_list)
	return path_l, path_n

'''
returns path labels and URIs for simple paths from source to target that have length greater than shortest path
skips paths that contain nodes from the filtered list defined above - []
k = number of paths
cutoff = maximum length of path
shortestLens = length of shortest path between source and target
There is a loop filter cutoff that decides how many paths to search without filtered nodes before moving on to the next.
Currently filter_cutoff = 50

'''
def get_k_simple_paths_filtered(G, source, target, k, cutoff, shortestLens, nodes_to_filter):
	
	filter_cutoff = 50
	print('Searching for filtered paths from {} - {}'.format(str(source), str(target)))
	paths = nx.all_simple_edge_paths(G, source, target, cutoff=cutoff)
	path_l = []
	path_n = []
	i = 0
	filter_count = 0
	while i<k:
		try:
			print('[info] applying next operator to search for a simple path of max length {}'.format(cutoff))
			path = next(paths)
		except StopIteration:
			break
		print('[info] Simple path found of length {}'.format(len(path))) 
		if len(path) > shortestLens:
			print('[info] Simple path length greater than shortest path length ({})'.format(shortestLens))
			flag = True
			triples = [item for sublist in path for item in sublist]
			for node in triples:
				if node in nodes_to_filter:
					filter_count += 1
					flag = False
					break
			if flag:
				path_n.append(path)
				i += 1
			else:
				print('Path contains filtered node, skipping path in results')
				if filter_count >= filter_cutoff:
					print('No path found without filtered nodes, moving to next iteration')
					i += 1
			
	for newpath in path_n:
		triple_list = []
		for triple in newpath:
			subj_lab = ''
			pred_lab = ''
			obj_lab = ''
			subj = str(triple[0])
			pred = str(triple[2])
			obj = str(triple[1])
			if subj in nodeLabels:
				subj_lab = nodeLabels[subj]
			if obj in nodeLabels:
				obj_lab = nodeLabels[obj]
			if pred in nodeLabels:
				pred_lab = nodeLabels[pred]
			triple_labels = (subj_lab, pred_lab, obj_lab)
			triple_list.append(triple_labels)
		path_l.append(triple_list)
	return path_l, path_n

'''
returns list of k shortest paths from source to target
'''
def get_k_shortest_paths_filtered(G, source, target, k, weight='weight'):
	print('Searching for shortest paths from {} - {}'.format(str(source), str(target)))
	shortest_paths_filtered = []
	i = 0
	for path in paths:
		for node in path:
			if node in nodes_to_filter:
				continue
			else:
				shortest_paths_filtered.append(path)
	return shortest_paths_filtered

'''
returns list of k shortest paths from source to target but removes paths with nodes in filtered list above from results
'''
def get_k_shortest_paths(G, source, target, k, weight='weight'):
	print('Searching for shortest paths from {} - {}'.format(str(source), str(target)))
	paths = nx.all_shortest_paths(G, source, target, weight=weight)
	return list(islice(nx.all_shortest_paths(G, source, target, weight=weight), k))

def save_k_shortest_paths(G, source, target, k, filepath, weight='weight'):
	paths = get_k_shortest_paths(G, source, target, k, weight='weight')
	#print()
	file_save = open(filepath, 'w')
	source = str(source)
	target = str(target)
	source_label = source
	target_label = target
	if source in nodeLabels:
		source_label = nodeLabels[source]
	if target in nodeLabels:
		target_label = nodeLabels[target]
	file_save.write('\n{} - {} Shortest Path:\n'.format(source_label, target_label))
	i = 0
	for node_list in paths:
		file_save.write('\nPATH: '+str(i)+'\n')
		path_labels = get_path_labels(G, node_list, nodeLabels)
		for triples in path_labels:
			for item in triples:
				file_save.write(str(item)+' ')
			file_save.write('\n')
		i += 1
	file_save.close()

def save_k_simple_paths(G, source, target, k, cutoff, filepath):
	path_l, path_n = get_k_simple_paths(G, source, target, k, cutoff)
	source = str(source)
	target = str(target)
	#print()
	file_save = open(filepath, 'w')
	
	if source in nodeLabels:
		source_label = nodeLabels[source]
	if target in nodeLabels:
		target_label = nodeLabels[target]
	file_save.write('\n{} - {} Simple Path (cutoff= {} ):\n'.format(source_label, target_label, cutoff))
	i = 0
	for path_list in path_n:
		file_save.write('\nPATH: '+str(i)+'\n')
		for triples in path_list:
			for item in triples:
				file_save.write(str(item)+' ')
			file_save.write('\n')
		i += 1
	file_save.close()

def get_path_labels(nx_graph, path, nodeLabels):
	path_labels = []
	if len(path) < 1:
		print('Path length 1, skipping')
		return
	for edge in zip(path, path[1:]):
		data = nx_graph.get_edge_data(*edge)
		pred = list(data.keys())[0]
		node1_lab = str(edge[0])
		node2_lab = str(edge[1])
		if node1_lab in nodeLabels:
			node1_lab = nodeLabels[node1_lab]
		if node2_lab in nodeLabels:
			node2_lab = nodeLabels[node2_lab]
		pred_lab = nodeLabels[str(pred)]
		if list(data.values())[0]:
			if 'source_graph' in list(data.values())[0]:
				source_graph = 'machine_read'
			else:
				source_graph = ''
		else:
			source_graph = ''
		labels = [node1_lab, pred_lab, node2_lab, source_graph]
		path_labels.append(labels)
	return path_labels

def get_path_uri(nx_graph, path):
	path_uri = []
	if len(path) < 1:
		print('Path length 1, skipping')
		return
	for edge in zip(path, path[1:]):
		data = nx_graph.get_edge_data(*edge)
		pred = list(data.keys())[0]
		attribute = list(data.values())
		uri = [str(edge[0]), str(pred), str(edge[1]), attribute]
		path_uri.append(uri)
	return path_uri

'''
prints common statistics for the graph passed to function including number of nodes, edges
average degree, node density and nodes with the highest degree
'''
def print_graph_statistics(nx_graph):
	# get the number of nodes, edges, and self-loops
	nodes = nx.number_of_nodes(nx_graph)
	edges = nx.number_of_edges(nx_graph)
	self_loops = nx.number_of_selfloops(nx_graph)

	print('There are {} nodes, {} edges, and {} self-loop(s)'.format(nodes, edges, self_loops))
	# get degree information
	avg_degree = float(edges) / nodes

	print('The Average Degree is {}'.format(avg_degree))
	# get 5 nodes with the highest degress
	n_deg = sorted([(str(x[0]), x[1]) for x in  nx_graph.degree], key=lambda x: x[1], reverse=1)[:6]

	for x in n_deg:
		print('{} (degree={})'.format(x[0], x[1]))
	# get network density
	density = nx.density(nx_graph)

	print('The density of the graph is: {}'.format(density))

