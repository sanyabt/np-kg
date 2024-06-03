'''
Script to create ontology extensions for natural products (instance-based).
Author: Sanya B. Taneja
Created on: 2023-04-04
Last run: 2024-02-29

Natural product latin binomials are created as classes with cross reference to Global Substance Registration System (GSRS) identifiers. Instances of classes are connected to natural product constituents (depending on whether the 
constituents already exist in ChEBI or not). If constituent exists in ChEBI, an instance of the ChEBI class is created and linked to the natural product instance. Else, a new constituent class is created and linked. All classes 
contain external cross references to GSRS identifiers.

Input is a tab-separated file with natural product latin binomials, GSRS identifiers, NCBI ID and ChEBI identifiers (if available)
after constituent annotation, review, and mapping from GSRS and EMA monographs.
Output is a serialized graph in XML file.
'''
import pandas as pd
## import RDF related
from rdflib import Graph, BNode, Namespace, URIRef, Literal
import json
import logging

DIR_IN = 'resources/'
DIR_OUT = 'graphs/'
FILE_IN = DIR_IN + 'EMA_GSRS_NP_constituents_combined_unique_20240116.tsv'
NP_DICT = DIR_IN + 'np_constituents_reference_dict_20240229.json'
OUTFILE = DIR_OUT + 'chebi-extensions-constituents-20240229.tsv'
OUT_GRAPH = DIR_OUT + "chebi-srs-extensions-instance-all-20240229.xml"
LOG_FILE = "log-ontology-extensions-20240229.txt"
logging.basicConfig(filename=LOG_FILE, filemode='a', level=logging.INFO)

with open(NP_DICT, 'r') as filein:
	np_dict = json.load(filein)

NP_LIST = np_dict.keys()
logging.info('Generating ontology extensions for {} natural products: '.format(len(NP_LIST)))
logging.info('\nNatural products in the list: {}'.format(NP_LIST))

## set up RDF graph
# identify namespaces for other ontologies to be used
LOCAL_NS = Namespace('http://napdi.org/napdi_srs_imports:')
DC_NS = Namespace('http://purl.org/dc/elements/1.1/')
RDF_NS = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
OBO_NS = Namespace('http://purl.obolibrary.org/obo/')
OWL_NS = Namespace('http://www.w3.org/2002/07/owl#')
RDFS_NS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
#RO, BFO, GO CHEBI, NCBITaxon, PRO use the OBO namespace
SRS_NS = Namespace('http://gsrs.ncats.nih.gov/ginas/app/substance/')

relations = {
"has_component" : "RO_0002180", #instance-instance
"has_functional_parent": "chebi#has_functional_parent", #instance-instance 
"has_role": "RO_0000087",  #instance-instance 
"part_of": "BFO_0000050",  #instance-instance 
"in_taxon": "RO_0002162",  #instance-instance 
"has_participant": "RO_0000057",  #instance-instance 
"participates_in": "RO_0000056",  #instance-instance 
"molecularly_decreases_activity": "RO_0002449",
"database_cross_reference": "http://purl.obolibrary.org/obo/database_cross_reference"}  #instance-instance 

def initialGraph(graph):
	graph.namespace_manager.reset()
	graph.namespace_manager.bind('napdi_srs', LOCAL_NS)
	graph.namespace_manager.bind('dc', DC_NS)
	graph.namespace_manager.bind('obo', OBO_NS)
	graph.namespace_manager.bind('rdf', RDF_NS)
	graph.namespace_manager.bind('owl', OWL_NS)
	graph.namespace_manager.bind('rdfs', RDFS_NS)
	graph.namespace_manager.bind('srs', SRS_NS)

	# Ontology - about and imports
	graph.add((URIRef('http://purl.obolibrary.org/obo/napdi-srs-imports'), RDF_NS.type, OWL_NS.Ontology))
	graph.add((URIRef('http://purl.obolibrary.org/obo/napdi-srs-imports'), OWL_NS.imports, URIRef('http://purl.obolibrary.org/obo/iao/2017-03-24/iao.owl')))
	graph.add((URIRef('http://purl.obolibrary.org/obo/napdi-srs-imports'), OWL_NS.imports, URIRef('http://purl.obolibrary.org/obo/bfo/2014-05-03/classes-only.owl')))
	graph.add((URIRef('http://purl.obolibrary.org/obo/napdi-srs-imports'), OWL_NS.imports, URIRef('http://purl.obolibrary.org/obo/ro/core.owl')))
	graph.add((URIRef('http://purl.obolibrary.org/obo/napdi-srs-imports'), DC_NS.creator, Literal('Sanya B. Taneja', lang='en')))
	graph.add((URIRef('http://purl.obolibrary.org/obo/napdi-srs-imports'), DC_NS.contributor, Literal('Richard D. Boyce', lang='en')))
	graph.add((URIRef('http://purl.obolibrary.org/obo/napdi-srs-imports'), RDFS_NS.label, Literal('NaPDI imported entities', lang='en'))) # need to find how to specify XSD type lang=en
	graph.add((URIRef('http://purl.obolibrary.org/obo/napdi-srs-imports'), RDFS_NS.comment, Literal('This ontology contains constituents imported from the GSRS database and EMA monographs', lang='en')))

def create_constituent_chebi(constituent_name, chebi_id, constituent_gsrs_id, graph, NP, NP_instance):
	##constituent exists in CHEBI
	##convert chebi id from float to string
	chebi_id = str(int(chebi_id))
	constituent_class = OBO_NS['CHEBI_'+chebi_id]
	#constituent_class = URIRef(constituent_id)
	constituent_instance = BNode()
	
	#Constituent of NP as instance in CHEBI, subClass of chemical entity, cross reference to SRS (if exists)
	#this creates an instance of existing class CHEBI_*
	#NP has_component NP_constituent (in ChEBI)
	graph.add((constituent_class, RDFS_NS.subClassOf, OBO_NS.CHEBI_24431))
	graph.add((constituent_class, RDFS_NS.subClassOf, OBO_NS.CHEBI_24431))
	graph.add((constituent_instance, RDF_NS.type, constituent_class))
	graph.add((constituent_instance, RDF_NS.type, OWL_NS.NamedIndividual))	
	if pd.notna(constituent_gsrs_id):
		graph.add((constituent_class, OBO_NS.database_cross_reference, SRS_NS[constituent_gsrs_id]))

	bn = BNode()
	graph.add((NP, RDFS_NS.subClassOf, bn))
	graph.add((bn, RDF_NS.type, OWL_NS.Restriction))
	graph.add((bn, OWL_NS.onProperty, OBO_NS.RO_0002180))
	graph.add((bn, OWL_NS.someValuesFrom, constituent_class))
		
	graph.add((NP_instance, OBO_NS.RO_0002180, constituent_instance))
	return graph, constituent_class

def create_constituent_no_chebi(constituent_name, constituent_gsrs_id, graph, NP, NP_instance):
	constituent_name_new = constituent_name.lower().replace('.', '').replace('>', '').replace('(-)', '').replace('(+)', '').replace('\'', '').replace('/', '').replace(',', '_').replace('(', '').replace(')', '').replace('[', '').replace(']', '')
	constituent_name_new = constituent_name_new.replace(' ', '_').replace('-', '_')
	constituent_class = LOCAL_NS[constituent_name_new]
	constituent_instance = BNode()
			
	graph.add((constituent_class, RDFS_NS.subClassOf, OBO_NS.CHEBI_24431))
	graph.add((constituent_class, RDF_NS.type, OWL_NS.Class))
	graph.add((constituent_instance, RDF_NS.type, constituent_class))
	graph.add((constituent_instance, RDF_NS.type, OWL_NS.NamedIndividual))
	graph.add((constituent_class, RDFS_NS.label, Literal(constituent_name.lower(), lang='en')))

	if pd.notna(constituent_gsrs_id):
		graph.add((constituent_instance, OBO_NS.database_cross_reference, SRS_NS[constituent_gsrs_id]))
	
	bn = BNode()
	graph.add((NP, RDFS_NS.subClassOf, bn))
	graph.add((bn, RDF_NS.type, OWL_NS.Restriction))
	graph.add((bn, OWL_NS.onProperty, OBO_NS.RO_0002180))
	graph.add((bn, OWL_NS.someValuesFrom, constituent_class))
		
	graph.add((NP_instance, OBO_NS.RO_0002180, constituent_instance))
	return graph, constituent_class

def create_np_extentions(np_name, graph, df_np):

	#defining NP names and IDs
	#common_name = np_dict[np_name]['common_name'].lower()
	latin_binomial = np_dict[np_name]['latin_binomial'].lower()
	parent_name = np_dict[np_name]['parent_name'].lower()
	NCBI_ID = 'NCBITaxon_'+np_dict[np_name]['NCBI_ID']
	GSRS_substance_ID = np_dict[np_name]['GSRS_substance_ID']
	GSRS_parent_ID = np_dict[np_name]['GSRS_parent_ID']

	##reset index and get number of constituents
	df = df_np.reset_index(drop=True)
	n_gsrs_constituents = len(df.loc[df['source'] == 'GSRS'])
	n_ema_constituents = len(df.loc[df['source'] == 'EMA'])
	logging.info('\nGSRS constituents: {}'.format(n_gsrs_constituents))
	logging.info('\nEMA constituents: {}'.format(n_ema_constituents))

	#create namespaced identifiers and instances
	NP_whole = LOCAL_NS[parent_name]
	NP = LOCAL_NS[latin_binomial]
	NP_instance = BNode()
	NP_whole_instance = BNode()
	
	#NP subClassOf plant anatomical entity, create instance, cross reference in SRS
	graph.add((NP, RDFS_NS.subClassOf, OBO_NS.PO_0025131))
	graph.add((NP, RDF_NS.type, OWL_NS.Class))
	graph.add((NP, OBO_NS.database_cross_reference, SRS_NS[GSRS_substance_ID]))
	graph.add((NP, RDFS_NS.label, Literal(np_name.replace(' ', '_'), lang='en')))

	graph.add((NP_instance, RDF_NS.type, NP))
	graph.add((NP_instance, RDF_NS.type, OWL_NS.NamedIndividual))

	#NP whole substance subClassOf plant anatomical entity, create instance, cross reference in SRS 
	graph.add((NP_whole, RDFS_NS.subClassOf, OBO_NS.PO_0025131))
	graph.add((NP_whole, RDF_NS.type, OWL_NS.Class))
	graph.add((NP_whole_instance, RDF_NS.type, NP_whole))
	graph.add((NP_whole_instance, RDF_NS.type, OWL_NS.NamedIndividual))

	graph.add((NP_whole, OBO_NS.database_cross_reference, SRS_NS[GSRS_parent_ID]))
	graph.add((NP_whole, RDFS_NS.label, Literal(parent_name, lang='en')))

	#NP in taxon organism (NCBI Taxon) - class-class relationship
	pgt1 = BNode()
	graph.add((NP, RDFS_NS.subClassOf, pgt1))
	graph.add((pgt1, RDF_NS.type, OWL_NS.Restriction))
	graph.add((pgt1, OWL_NS.onProperty, OBO_NS.RO_0002162))
	graph.add((pgt1, OWL_NS.someValuesFrom, OBO_NS[NCBI_ID]))

	#NP part of NP parent
	pgt2 = BNode()
	graph.add((NP, RDFS_NS.subClassOf, pgt2))
	graph.add((pgt2, RDF_NS.type, OWL_NS.Restriction))
	graph.add((pgt2, OWL_NS.onProperty, OBO_NS.BFO_0000050))
	graph.add((pgt2, OWL_NS.someValuesFrom, NP_whole))
	graph.add((NP_instance, OBO_NS.BFO_0000050, NP_whole_instance))

	#creating dataframe of constituent name and URIs for mapping purposes
	dfoutnp = pd.DataFrame(columns=['constituent_name', 'URI'])
	
	for i in range(len(df.index)):
		uri = ''
		constituent_name = df.at[i, 'constituent_name']
		constituent_gsrs_id = df.at[i, 'constituent_uuid']
		chebi_id = df.at[i, 'chebi_id']
		if pd.notna(chebi_id):
			graph, uri = create_constituent_chebi(constituent_name, chebi_id, constituent_gsrs_id, graph, NP, NP_instance)
		else:
			graph, uri = create_constituent_no_chebi(constituent_name, constituent_gsrs_id, graph, NP, NP_instance)
		dfoutnp = dfoutnp.append({'constituent_name': constituent_name.lower(), 'URI': str(uri)}, ignore_index=True)
	return graph, dfoutnp

if __name__ == "__main__":

	## default settings
	graph = Graph()
	initialGraph(graph)

	df = pd.read_csv(FILE_IN, sep='\t')
	#logging.info('Total constituents: %s', len(df))

	dfout = pd.DataFrame(columns=['constituent_name', 'URI'])
	##add to graph here
	for np_name in NP_LIST:
		df_np = df.loc[df['related_latin_binomial'] == np_name]
		logging.info('\nTotal constituents for %s: %d', np_name, len(df_np))
		graph, dfoutnp = create_np_extentions(np_name, graph, df_np)
		dfout = pd.concat([dfout, dfoutnp], ignore_index=True)

	logging.info('\nTotal constituents added to graph: %d', len(dfout))
	dfout = dfout.drop_duplicates()
	logging.info('\nUnique constituents: %d', len(dfout))
	dfout.to_csv(OUTFILE, sep='\t', index=False)

	f = open(OUT_GRAPH,"w")
	graph_str = graph.serialize(format='xml').decode('utf-8')
	f.write(graph_str)
	f.close()

	graph.close()