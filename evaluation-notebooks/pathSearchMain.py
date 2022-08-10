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
import KG_path_searches

combine_graph = False
#change graph names and paths
KG_PATH = '../resources/knowledge_graphs/'
KG_NAME_MERGED = 'PheKnowLator_machine_read_merged_instance_based_OWLNETS_v1.0.gpickle'
NodeLabelsFile = '../resources/nodeLabels_v1.0.pickle'
DIR_OUT = '../output_files/'

#set to false for no filtering
filter_nodes = True
time_slicing = True
MAXNUMPATHS = 10

#define namespaces
obo = Namespace('http://purl.obolibrary.org/obo/')
napdi = Namespace('http://napdi.org/napdi_srs_imports:')

#read nodeLabels dictionary
with open(NodeLabelsFile, 'rb') as filep:
	nodeLabels = pickle.load(filep)

node_dict = {
	'EGCG': obo.CHEBI_4806,
	'ECG': obo.CHEBI_70255,
	'EPICATECHIN': obo.CHEBI_90,
	'CATECHIN': obo.CHEBI_23053,
	'GREENTEA': napdi.camellia_sinensis_leaf,
	'KRATOM': napdi.mitragyna_speciosa,
	'MITRAGYNINE': obo.CHEBI_6956,
	'HYDROXY_MITRAGYNINE': napdi['7_hydroxy_mitragynine'],
	'CYP3A4': obo.PR_P08684,
	'CYP2D6': obo.PR_P10635,
	'CYP2C19': obo.PR_P33261,
	'UGT1A1_protein': obo.PR_P22309,
	'UGT1A8_protein': obo.PR_Q9HAW9,
	'UGT1A10_protein': obo.PR_Q9HAW8,
	'buspirone': obo.CHEBI_3223,
	'nadolol': obo.CHEBI_7444,
	'raloxifene': obo.CHEBI_8772,
	'midazolam': obo.CHEBI_6931,
	'dextromethorphan': obo.CHEBI_4470,
	'seizure': obo.HP_0001250
}

greentea_tuples = [
	(node_dict['GREENTEA'], node_dict['CYP3A4']),
	(node_dict['GREENTEA'], node_dict['CYP2D6']),
	(node_dict['GREENTEA'], node_dict['UGT1A1_protein']),
	(node_dict['GREENTEA'], node_dict['UGT1A8_protein']),
	(node_dict['GREENTEA'], node_dict['UGT1A10_protein']),
	(node_dict['EGCG'], node_dict['CYP3A4']),
	(node_dict['EGCG'], node_dict['CYP2C19']),
	(node_dict['EGCG'], node_dict['CYP2D6']),
	(node_dict['EGCG'], node_dict['UGT1A1_protein']),
	(node_dict['EGCG'], node_dict['UGT1A8_protein']),
	(node_dict['EGCG'], node_dict['UGT1A10_protein']),
	(node_dict['ECG'], node_dict['CYP3A4']),
	(node_dict['ECG'], node_dict['UGT1A1_protein']),
	(node_dict['ECG'], node_dict['UGT1A8_protein']),
	(node_dict['ECG'], node_dict['UGT1A10_protein']),
	(node_dict['CATECHIN'], node_dict['UGT1A1_protein']),
	(node_dict['CATECHIN'], node_dict['UGT1A8_protein']),
	(node_dict['CATECHIN'], node_dict['UGT1A10_protein']),
	(node_dict['EPICATECHIN'], node_dict['UGT1A1_protein']),
	(node_dict['EPICATECHIN'], node_dict['UGT1A8_protein']),
	(node_dict['EPICATECHIN'], node_dict['UGT1A10_protein']),
	(node_dict['GREENTEA'], node_dict['raloxifene']),
	(node_dict['GREENTEA'], node_dict['nadolol']),
	(node_dict['GREENTEA'], node_dict['buspirone'])
]

kratom_tuples = [
	(node_dict['KRATOM'], node_dict['CYP2D6']),
	(node_dict['KRATOM'], node_dict['CYP3A4']),
	(node_dict['MITRAGYNINE'], node_dict['CYP3A4']),
	(node_dict['MITRAGYNINE'], node_dict['CYP2D6']),
	(node_dict['MITRAGYNINE'], node_dict['CYP2C19']),
	(node_dict['HYDROXY_MITRAGYNINE'], node_dict['UGT1A1_protein']),
	(node_dict['HYDROXY_MITRAGYNINE'], node_dict['CYP2C19']),
	(node_dict['KRATOM'], node_dict['midazolam']),
	(node_dict['KRATOM'], node_dict['dextromethorphan']),
	(node_dict['KRATOM'], node_dict['seizure'])
]

nodes_to_filter = [obo.CHEBI_24431, obo.CHEBI_25367, obo.SO_0000704, obo.PR_000029067, obo.PR_000000001, obo.GO_0008152, obo.SO_0000673,
					URIRef('https://reactome.org/content/detail/R-HSA-1643685'), URIRef('https://reactome.org/content/detail/R-HSA-1430728')]


def get_all_paths(nx_graph, tuples):
	
	df = pd.DataFrame(columns = ['path_type','path_start', 'path_start_label', 'path_end', 'path_end_label', 'path_count','path_step','subject_label','predicate_label',
							'object_label','subject_uri','predicate_uri','object_uri','source_data', 'pub_year', 'pmid'])
	shortestLens = 0
	for tpl in tuples:
		(s,o) = tpl
		startNd = s
		endNd = o
		try:
			shortestPathLabels, shortestPathUri = KG_path_searches.get_bidirectional_shortest_path(nx_graph, startNd, endNd, nodeLabels)
			shortestLens = len(shortestPathLabels)
		except:
			print('Could not find bidirectional shortest path between {} and {}'.format(startNd, endNd))
			shortestLens = 2
		
		if shortestLens == 0:
			print('Shortest path between {} and {} not found. Setting shortest path length=2.'.format(startNd, endNd))
			shortestLens = 2

		stepCount = 0

		for triples in zip(shortestPathLabels, shortestPathUri):
							
				attribute_dict = triples[1][3][0]

				if 'source_graph' in attribute_dict:
					source_data = 'machine_read'
				else:
					source_data = ''
				if 'timestamp' in attribute_dict:
					pub_year = attribute_dict['timestamp']
				else:
					pub_year = ''
				if 'pmid' in attribute_dict:
					pmid = attribute_dict['pmid']
				else:
					pmid = ''

				df_temp = {
					'path_type': 'bi_shortest',
					'path_start': str(startNd),
					'path_start_label': nodeLabels[str(startNd)],
					'path_end': str(endNd),
					'path_end_label': nodeLabels[str(endNd)],
					'path_count': 1,
					'path_step': stepCount,
					'path_length': len(shortestPathLabels),
					'subject_label': triples[0][0],
					'predicate_label': triples[0][1],
					'object_label': triples[0][2],
					'subject_uri': str(triples[1][0]),
					'predicate_uri': str(triples[1][1]),
					'object_uri': str(triples[1][2]),
					'source_data': source_data,
					'pub_year': pub_year,
					'pmid': pmid
				}

				df = df.append(df_temp, ignore_index=True)
				stepCount += 1

		#path_s = KG_path_searches.get_k_shortest_paths(nx_graph, startNd, endNd, MAXNUMPATHS)
		MAXPATHLENGTH = shortestLens + 10
		
		#shortestCount = 0
		
		#save shortest path as dictionary and add to dataframe -- running longer than few hours so commented out for now
		'''for node_list in path_s:
			stepCount = 0
			path_labels = KG_path_searches.get_path_labels(nx_graph, node_list, nodeLabels)
			path_uri = KG_path_searches.get_path_uri(nx_graph, node_list)
			for triples in zip(path_labels, path_uri):
				
				if 'timestamp' in triples[1][3][0]:
					pub_year = triples[1][3][0]['timestamp']
				else:
					pub_year = ''

				df_temp = {
					'path_type': 'shortest',
					'path_start': str(startNd),
					'path_start_label': nodeLabels[str(startNd)],
					'path_end': str(endNd),
					'path_end_label': nodeLabels[str(endNd)],
					'path_count': shortestCount,
					'path_step': stepCount,
					'path_length': len(path_labels),
					'subject_label': triples[0][0],
					'predicate_label': triples[0][1],
					'object_label': triples[0][2],
					'subject_uri': triples[1][0],
					'predicate_uri': triples[1][1],
					'object_uri': triples[1][2],
					'source_data': triples[0][3],
					'pub_year': pub_year,
					'pmid': pmid
				}
				df.append(df_temp, ignore_index=True)
				stepCount += 1
			
			shortestCount += 1
'''
		pathCount = 0
		#get simple paths and add to dataframe
		for i in range(shortestLens, MAXPATHLENGTH+1):
			cutoff = i
			
			if filter_nodes:
				path_l, path_n = KG_path_searches.get_k_simple_paths_filtered(nx_graph, startNd, endNd, MAXNUMPATHS, cutoff,
																			shortestLens, nodes_to_filter)
			else:
				path_l, path_n = KG_path_searches.get_k_simple_paths(nx_graph, startNd, endNd, 
																		MAXNUMPATHS, cutoff, shortestLens)
			#create dataframe from path results and append to main dataframe at end of loop
			for item in zip(path_l, path_n):

				pathStep = 0
				for triples in zip(item[0], item[1]):

					s = triples[1][0]
					p = triples[1][2]
					o = triples[1][1]
					
					attribute_dict = nx_graph[s][o][p]

					if 'source_graph' in attribute_dict:
						source_data = 'machine_read'
					else:
						source_data = ''
					if 'timestamp' in attribute_dict:
						pub_year = attribute_dict['timestamp']
					else:
						pub_year = ''
					if 'pmid' in attribute_dict:
						pmid = attribute_dict['pmid']
					else:
						pmid = ''

					df_temp = {
						'path_type': 'simple',
						'path_start': str(startNd),
						'path_start_label': nodeLabels[str(startNd)],
						'path_end': str(endNd),
						'path_end_label': nodeLabels[str(endNd)],
						'path_count': pathCount,
						'path_step': pathStep,
						'path_length': len(item[0]),
						'subject_label': triples[0][0],
						'predicate_label': triples[0][1],
						'object_label': triples[0][2],
						'subject_uri': str(triples[1][0]),
						'predicate_uri': str(triples[1][2]),
						'object_uri': str(triples[1][1]),
						'source_data': source_data,
						'pub_year': pub_year,
						'pmid': pmid
					}

					df = df.append(df_temp, ignore_index=True)
					pathStep += 1
				pathCount += 1
	return df

if __name__ == '__main__':

	##READ MERGED GRAPH (PL + REACH + SEMREP + INFERRED)
	nx_graph = nx.read_gpickle(KG_PATH+KG_NAME_MERGED)

	df_gt = get_all_paths(nx_graph, greentea_tuples)
	df_gt = df_gt.fillna('')
	
	if filter_nodes:
		outfilegt = outfilegt_filtered

	df_gt.to_csv(outfilegt, sep='\t', index=False)

	df_kt = get_all_paths(nx_graph, kratom_tuples)
	df_kt = df_kt.fillna('')

	if filter_nodes:
		outfilekt = outfilekt_filtered
	df_kt.to_csv(outfilekt, sep='\t', index=False)










