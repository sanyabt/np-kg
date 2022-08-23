## import Sparql-related
from SPARQLWrapper import SPARQLWrapper, JSON
import uuid
## import RDF related
from rdflib import Graph, BNode, Namespace, URIRef, Literal
import json

DIR_OUT = "graphs/"
OUT_GRAPH = DIR_OUT + "chebi-srs-instance-kratom-gt-20220816.xml"

urn_dict = {
	'Mitragyna_speciosa': 'http://napdi.org/napdi_srs_imports:mitragyna_speciosa',
	'Mitragyna_speciosa_whole' :'http://napdi.org/napdi_srs_imports:mitragyna_speciosa_whole',
	'Goldenseal': 'http://napdi.org/napdi_srs_imports:goldenseal',
	'Hydrastis_canadensis_whole': 'http://napdi.org/napdi_srs_imports:hydrastis_canadensis_whole',
	'Camellia_sinensis_leaf': 'http://napdi.org/napdi_srs_imports:camellia_sinensis_leaf',
	'Camellia_sinensis_whole': 'http://napdi.org/napdi_srs_imports:camellia_sinensis_whole',
}

relations = {
"has_component" : "RO_0002180", #instance-instance
"has_functional_parent": "chebi#has_functional_parent", #instance-instance 
"has_role": "RO_0000087",  #instance-instance 
"part_of": "BFO_0000050",  #instance-instance 
"in_taxon": "RO_0002162",  #instance-instance 
"has_participant": "RO_0000057",  #instance-instance 
"participates_in": "RO_0000056",  #instance-instance 
"molecularly_decreases_activity": "RO_0002449", #same as inhibits and directly negatively regulates activity of
"database_cross_reference": "http://purl.obolibrary.org/obo/database_cross_reference"}  #instance-instance 

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

srs_map_dict = {
	'7_hydroxy_mitragynine': SRS_NS['c50748a1-8231-42ad-a263-6abc6bc49005'],
	'Mitragyna_speciosa': SRS_NS['dac1ac7a-f1bb-42d7-ab9c-0bf06d0d9825'],
	'Mitragyna_speciosa_whole' : SRS_NS['d469b67d-e9a6-459f-b209-c59451936336'],
	'Goldenseal': SRS_NS['acd31728-eac3-4005-a80f-aae4689f9eab'],
	'Hydrastis_canadensis_whole': SRS_NS['66690655-f406-4d67-96e3-2066aafee8d5'],
	'Camellia_sinensis_leaf': SRS_NS['44cfdb9d-f504-42d8-ab9d-ab6eb8eebe03'],
	'Camellia_sinensis_whole': SRS_NS['e9698137-24da-46f8-a70e-43e27691491f'],
	'Mitragynine': SRS_NS['22e5b710-9260-4678-9196-ba75d4c38520'],
	'epigallocatechin_gallate': SRS_NS['60a66f64-7eca-4725-87b6-71bf41829f90'],
	'epicatechin': SRS_NS['261f2b07-471b-45d6-b1fc-28b65defbe21'],
	'epigallocatechin': SRS_NS['53d98e02-cd90-4b89-bf72-e31dc1392811'],
	'epicatechin_3_gallate': SRS_NS['5be035c0-63da-4bd6-8ffb-e5dafdc3b3b0'],
	'catechin': SRS_NS['5e3251fe-d591-4ac6-a8ad-679a3fe17e21'],
	'gallocatechin': SRS_NS['515014aa-2dae-464e-9d65-0514f4d6c2f1'],
	'4_methyl_epigallocatechin': SRS_NS['2d9aaf78-36eb-4ce3-a657-830f30512d72']
}

def create_urn(string_literal):
	uuid_new = uuid.uuid4().hex
	urn_dict[string_literal] = 'urn:'+uuid_new

def initialGraph(graph):
	graph.namespace_manager.reset()
	graph.namespace_manager.bind('napdi_srs', LOCAL_NS)
	graph.namespace_manager.bind('dc', DC_NS)
	graph.namespace_manager.bind('obo', OBO_NS)
	graph.namespace_manager.bind('rdf', RDF_NS)
	graph.namespace_manager.bind('owl', OWL_NS)
	graph.namespace_manager.bind('rdfs', RDFS_NS)
	graph.namespace_manager.bind('srs', SRS_NS)
# TODO: add qnames 
	
	#graph.namespace_manager.bind('','')
	
#def addAssertion(graph, item)
	# graph.add((poc[currentAnnotationMaterial], RDF.type, mp["Material"])) 

if __name__ == "__main__":

	## default settings

	graph = Graph()
	initialGraph(graph)
		
	# Ontology - about and imports
	graph.add((URIRef('http://purl.obolibrary.org/obo/napdi-srs-imports'), RDF_NS.type, OWL_NS.Ontology))
	graph.add((URIRef('http://purl.obolibrary.org/obo/napdi-srs-imports'), OWL_NS.imports, URIRef('http://purl.obolibrary.org/obo/iao/2017-03-24/iao.owl')))
	graph.add((URIRef('http://purl.obolibrary.org/obo/napdi-srs-imports'), OWL_NS.imports, URIRef('http://purl.obolibrary.org/obo/bfo/2014-05-03/classes-only.owl')))
	graph.add((URIRef('http://purl.obolibrary.org/obo/napdi-srs-imports'), OWL_NS.imports, URIRef('http://purl.obolibrary.org/obo/ro/core.owl')))
	graph.add((URIRef('http://purl.obolibrary.org/obo/napdi-srs-imports'), DC_NS.creator, Literal('Sanya B. Taneja', lang='en')))
	graph.add((URIRef('http://purl.obolibrary.org/obo/napdi-srs-imports'), DC_NS.contributor, Literal('Richard D. Boyce', lang='en')))
	graph.add((URIRef('http://purl.obolibrary.org/obo/napdi-srs-imports'), RDFS_NS.label, Literal('NaPDI SRS imported entities', lang='en'))) # need to find how to specify XSD type lang=en

	#-------------------------KRATOM----------------------------

	#NP, NP constituent blank nodes and NP parent class and instance
	NP_kratom = URIRef(urn_dict['Mitragyna_speciosa'])
	NP_kratom_instance = BNode()
	Mitragynine_instance = BNode()
	NP_parent_kratom = URIRef(urn_dict['Mitragyna_speciosa_whole'])
	NP_parent_kratom_instance = BNode()
	hydroxy_mitragynine_instance = BNode()
 
	#NP subClassOf plant anatomical entity, create instance, cross reference in SRS
	graph.add((NP_kratom, RDFS_NS.subClassOf, OBO_NS.PO_0025131))
	graph.add((NP_kratom, RDF_NS.type, OWL_NS.Class))
	graph.add((NP_kratom, OBO_NS.database_cross_reference, srs_map_dict['Mitragyna_speciosa']))
	graph.add((NP_kratom, RDFS_NS.label, Literal('Mitragyna_speciosa', lang='en')))

	graph.add((NP_kratom_instance, RDF_NS.type, NP_kratom))
	graph.add((NP_kratom_instance, RDF_NS.type, OWL_NS.NamedIndividual))

	#Constituent of NP as instance in CHEBI, subClass of chemical entity, cross reference to SRS
	#this creates an instance of existing class CHEBI_6956
	graph.add((OBO_NS.CHEBI_6956, RDFS_NS.subClassOf, OBO_NS.CHEBI_24431))
	graph.add((Mitragynine_instance, RDF_NS.type, OBO_NS.CHEBI_6956))
	graph.add((Mitragynine_instance, RDF_NS.type, OWL_NS.NamedIndividual))
	graph.add((OBO_NS.CHEBI_6956, OBO_NS.database_cross_reference, srs_map_dict['Mitragynine']))
	
	#NP parent subClassOf plant anatomical entity, create instance, cross reference in SRS
	graph.add((NP_parent_kratom, RDFS_NS.subClassOf, OBO_NS.PO_0025131))
	graph.add((NP_parent_kratom, RDF_NS.type, OWL_NS.Class))
	graph.add((NP_parent_kratom_instance, RDF_NS.type, NP_parent_kratom))
	graph.add((NP_parent_kratom_instance, RDF_NS.type, OWL_NS.NamedIndividual))

	graph.add((NP_parent_kratom, OBO_NS.database_cross_reference, srs_map_dict['Mitragyna_speciosa_whole']))
	graph.add((NP_parent_kratom, RDFS_NS.label, Literal('Mitragyna_speciosa_whole', lang='en')))

	#NP parent in taxon organism (NCBI Taxon) - class-class relationship
	pk1 = BNode()
	graph.add((NP_parent_kratom, RDFS_NS.subClassOf, pk1))
	graph.add((pk1, RDF_NS.type, OWL_NS.Restriction))
	graph.add((pk1, OWL_NS.onProperty, OBO_NS.RO_0002162))
	graph.add((pk1, OWL_NS.someValuesFrom, OBO_NS.NCBITaxon_170351))

	#NP has_component NP_constituent (in ChEBI)
	#Object property or restriction defined between the 2 classes (for which instances are created)
	pk2 = BNode()
	graph.add((NP_kratom, RDFS_NS.subClassOf, pk2))
	graph.add((pk2, RDF_NS.type, OWL_NS.Restriction))
	graph.add((pk2, OWL_NS.onProperty, OBO_NS.RO_0002180))
	graph.add((pk2, OWL_NS.someValuesFrom, OBO_NS.CHEBI_6956))
	graph.add((NP_kratom_instance, OBO_NS.RO_0002180, Mitragynine_instance))

	##NP part_of NP_parent 

	pk3 = BNode()
	graph.add((NP_kratom, RDFS_NS.subClassOf, pk3))
	graph.add((pk3, RDF_NS.type, OWL_NS.Restriction))
	graph.add((pk3, OWL_NS.onProperty, OBO_NS.BFO_0000050))
	graph.add((pk3, OWL_NS.someValuesFrom, NP_parent_kratom))
	graph.add((NP_kratom_instance, OBO_NS.BFO_0000050, NP_parent_kratom_instance))

	#Metabolite with cross-ref in SRS
	
	graph.add((OBO_NS.CHEBI_180536, RDFS_NS.subClassOf, OBO_NS.CHEBI_24431))
	graph.add((hydroxy_mitragynine_instance, RDF_NS.type, OBO_NS.CHEBI_180536))
	graph.add((hydroxy_mitragynine_instance, RDF_NS.type, OWL_NS.NamedIndividual))
	graph.add((OBO_NS.CHEBI_180536, OBO_NS.database_cross_reference, srs_map_dict['7_hydroxy_mitragynine']))

	#NP_metabolite has_functional_parent NP_constituent
	pk4 = BNode()
	graph.add((OBO_NS.CHEBI_180536, RDFS_NS.subClassOf, pk4))
	graph.add((pk4, RDF_NS.type, OWL_NS.Restriction))
	graph.add((pk4, OWL_NS.onProperty, OBO_NS['chebi#has_functional_parent']))
	graph.add((pk4, OWL_NS.someValuesFrom, OBO_NS.CHEBI_6956))
	graph.add((hydroxy_mitragynine_instance, OBO_NS['chebi#has_functional_parent'], Mitragynine_instance))
	
	#NP_metabolite has_role Metabolite
	pk5 = BNode()
	graph.add((OBO_NS.CHEBI_180536, RDFS_NS.subClassOf, pk5))
	graph.add((pk5, RDF_NS.type, OWL_NS.Restriction))
	graph.add((pk5, OWL_NS.onProperty, OBO_NS.RO_0000087))
	graph.add((pk5, OWL_NS.someValuesFrom, OBO_NS.CHEBI_25212))

	'''cyp3a4_instance = BNode()
	graph.add((cyp3a4_instance, RDF_NS.type, OBO_NS.PR_P08684))
	graph.add((cyp3a4_instance, RDF_NS.type, OWL_NS.NamedIndividual))
	graph.add((Mitragynine_instance, OBO_NS.RO_0002449, cyp3a4_instance))

	cyp2d6_instance = BNode()
	graph.add((cyp2d6_instance, RDF_NS.type, OBO_NS.PR_P10635))
	graph.add((cyp2d6_instance, RDF_NS.type, OWL_NS.NamedIndividual))
	graph.add((Mitragynine_instance, OBO_NS.RO_0002449, cyp2d6_instance))

	cyp2c9_instance = BNode()
	graph.add((cyp2c9_instance, RDF_NS.type, OBO_NS.PR_P11712))
	graph.add((cyp2c9_instance, RDF_NS.type, OWL_NS.NamedIndividual))
	graph.add((Mitragynine_instance, OBO_NS.RO_0002449, cyp2c9_instance))

	pgp_instance = BNode()
	graph.add((pgp_instance, RDF_NS.type, OBO_NS.PR_P000001891))
	graph.add((pgp_instance, RDF_NS.type, OWL_NS.NamedIndividual))
	graph.add((Mitragynine_instance, OBO_NS.RO_0002449, pgp_instance))'''

	#NP has_component NP_constituent (not in CHEBI, cross-ref in SRS) [role, subclass, cross-ref already defined above]
	#create another instance of 7-hydroxy-mitragynine (k_k)

#-------------------------GREEN TEA----------------------------

	NP_gt = URIRef(urn_dict['Camellia_sinensis_leaf'])
	NP_gt_instance = BNode()
	NP_parent_gt = URIRef(urn_dict['Camellia_sinensis_whole'])
	NP_parent_gt_instance = BNode()
	catechin_instance = BNode()
	gallocatechin_instance = BNode()
	epigallocatechin_gallate_instance = BNode()
	epicatechin_instance = BNode()
	epigallocatechin_instance = BNode()
	epicatechin_3_gallate_instance = BNode()
	methyl_epigallocatechin_instance = BNode()

	ugt1a1_instance = BNode()
	ugt1a8_instance = BNode()
	ugt1a10_instance = BNode()

	graph.add((ugt1a10_instance, RDF_NS.type, OBO_NS.PR_Q9HAW8))
	graph.add((ugt1a10_instance, RDF_NS.type, OWL_NS.NamedIndividual))

	graph.add((ugt1a1_instance, RDF_NS.type, OBO_NS.PR_P22309))
	graph.add((ugt1a1_instance, RDF_NS.type, OWL_NS.NamedIndividual))

	graph.add((ugt1a8_instance, RDF_NS.type, OBO_NS.PR_Q9HAW9))
	graph.add((ugt1a8_instance, RDF_NS.type, OWL_NS.NamedIndividual))

	#NP subClassOf plant anatomical entity, create instance, cross reference in SRS
	graph.add((NP_gt, RDFS_NS.subClassOf, OBO_NS.PO_0025131))
	graph.add((NP_gt, RDF_NS.type, OWL_NS.Class))
	graph.add((NP_gt, OBO_NS.database_cross_reference, srs_map_dict['Camellia_sinensis_leaf']))
	graph.add((NP_gt, RDFS_NS.label, Literal('Camellia_sinensis_leaf', lang='en')))
	
	graph.add((NP_gt_instance, RDF_NS.type, NP_gt))
	graph.add((NP_gt_instance, RDF_NS.type, OWL_NS.NamedIndividual))
	
	#NP parent subClassOf plant anatomical entity, create instance, cross reference in SRS
	graph.add((NP_parent_gt, RDFS_NS.subClassOf, OBO_NS.PO_0025131))
	graph.add((NP_parent_gt, RDF_NS.type, OWL_NS.Class))
	graph.add((NP_parent_gt_instance, RDF_NS.type, NP_parent_gt))
	graph.add((NP_parent_gt_instance, RDF_NS.type, OWL_NS.NamedIndividual))

	graph.add((NP_parent_gt, OBO_NS.database_cross_reference, srs_map_dict['Camellia_sinensis_whole']))
	graph.add((NP_parent_gt, RDFS_NS.label, Literal('Camellia_sinensis_whole', lang='en')))

	#NP parent in taxon organism (NCBI Taxon) - class-class relationship
	pgt1 = BNode()
	graph.add((NP_parent_gt, RDFS_NS.subClassOf, pgt1))
	graph.add((pgt1, RDF_NS.type, OWL_NS.Restriction))
	graph.add((pgt1, OWL_NS.onProperty, OBO_NS.RO_0002162))
	graph.add((pgt1, OWL_NS.someValuesFrom, OBO_NS.NCBITaxon_4442))

	#NP part of NP parent
	pgt2 = BNode()
	graph.add((NP_gt, RDFS_NS.subClassOf, pgt2))
	graph.add((pgt2, RDF_NS.type, OWL_NS.Restriction))
	graph.add((pgt2, OWL_NS.onProperty, OBO_NS.BFO_0000050))
	graph.add((pgt2, OWL_NS.someValuesFrom, NP_parent_gt))
	graph.add((NP_gt_instance, OBO_NS.BFO_0000050, NP_parent_gt_instance))

	#Constituent of NP as instance in CHEBI, subClass of chemical entity, cross reference to SRS
	#this creates an instance of existing class CHEBI_*
	#NP has_component NP_constituent (in ChEBI)

	#epicatechin-3-gallate
	graph.add((OBO_NS.CHEBI_70255, RDFS_NS.subClassOf, OBO_NS.CHEBI_24431))
	graph.add((epicatechin_3_gallate_instance, RDF_NS.type, OBO_NS.CHEBI_70255))
	graph.add((epicatechin_3_gallate_instance, RDF_NS.type, OWL_NS.NamedIndividual))
	graph.add((OBO_NS.CHEBI_70255, OBO_NS.database_cross_reference, srs_map_dict['epicatechin_3_gallate']))

	pgt3 = BNode()
	graph.add((NP_gt, RDFS_NS.subClassOf, pgt3))
	graph.add((pgt3, RDF_NS.type, OWL_NS.Restriction))
	graph.add((pgt3, OWL_NS.onProperty, OBO_NS.RO_0002180))
	graph.add((pgt3, OWL_NS.someValuesFrom, OBO_NS.CHEBI_70255))
	
	graph.add((NP_gt_instance, OBO_NS.RO_0002180, epicatechin_3_gallate_instance))

	'''graph.add((epicatechin_instance, OBO_NS.RO_0002449, ugt1a1_instance))
	graph.add((epicatechin_instance, OBO_NS.RO_0002449, ugt1a8_instance))
	graph.add((epicatechin_instance, OBO_NS.RO_0002449, ugt1a10_instance))'''

	#gallocatechin
	graph.add((OBO_NS.CHEBI_68330, RDFS_NS.subClassOf, OBO_NS.CHEBI_24431))
	graph.add((gallocatechin_instance, RDF_NS.type, OBO_NS.CHEBI_68330))
	graph.add((gallocatechin_instance, RDF_NS.type, OWL_NS.NamedIndividual))
	graph.add((OBO_NS.CHEBI_68330, OBO_NS.database_cross_reference, srs_map_dict['gallocatechin']))

	pgt4 = BNode()
	graph.add((NP_gt, RDFS_NS.subClassOf, pgt4))
	graph.add((pgt4, RDF_NS.type, OWL_NS.Restriction))
	graph.add((pgt4, OWL_NS.onProperty, OBO_NS.RO_0002180))
	graph.add((pgt4, OWL_NS.someValuesFrom, OBO_NS.CHEBI_68330))
	
	graph.add((NP_gt_instance, OBO_NS.RO_0002180, gallocatechin_instance))

	#epicatechin
	graph.add((OBO_NS.CHEBI_90, RDFS_NS.subClassOf, OBO_NS.CHEBI_24431))
	graph.add((epicatechin_instance, RDF_NS.type, OBO_NS.CHEBI_90))
	graph.add((epicatechin_instance, RDF_NS.type, OWL_NS.NamedIndividual))
	graph.add((OBO_NS.CHEBI_90, OBO_NS.database_cross_reference, srs_map_dict['epicatechin']))

	pgt5 = BNode()
	graph.add((NP_gt, RDFS_NS.subClassOf, pgt5))
	graph.add((pgt5, RDF_NS.type, OWL_NS.Restriction))
	graph.add((pgt5, OWL_NS.onProperty, OBO_NS.RO_0002180))
	graph.add((pgt5, OWL_NS.someValuesFrom, OBO_NS.CHEBI_90))
	
	graph.add((NP_gt_instance, OBO_NS.RO_0002180, epicatechin_instance))

	'''graph.add((epicatechin_instance, OBO_NS.RO_0002449, ugt1a1_instance))
	graph.add((epicatechin_instance, OBO_NS.RO_0002449, ugt1a8_instance))
	graph.add((epicatechin_instance, OBO_NS.RO_0002449, ugt1a10_instance))'''

	#epigallocatechin
	graph.add((OBO_NS.CHEBI_42255, RDFS_NS.subClassOf, OBO_NS.CHEBI_24431))
	graph.add((epigallocatechin_instance, RDF_NS.type, OBO_NS.CHEBI_42255))
	graph.add((epigallocatechin_instance, RDF_NS.type, OWL_NS.NamedIndividual))
	graph.add((OBO_NS.CHEBI_42255, OBO_NS.database_cross_reference, srs_map_dict['epigallocatechin']))

	pgt6 = BNode()
	graph.add((NP_gt, RDFS_NS.subClassOf, pgt6))
	graph.add((pgt6, RDF_NS.type, OWL_NS.Restriction))
	graph.add((pgt6, OWL_NS.onProperty, OBO_NS.RO_0002180))
	graph.add((pgt6, OWL_NS.someValuesFrom, OBO_NS.CHEBI_42255))
	
	graph.add((NP_gt_instance, OBO_NS.RO_0002180, epigallocatechin_instance))

	graph.add((OBO_NS.CHEBI_70253, RDFS_NS.subClassOf, OBO_NS.CHEBI_24431))
	graph.add((methyl_epigallocatechin_instance, RDF_NS.type, OBO_NS.CHEBI_70253))
	graph.add((methyl_epigallocatechin_instance, RDF_NS.type, OWL_NS.NamedIndividual))
	graph.add((OBO_NS.CHEBI_70253, OBO_NS.database_cross_reference, srs_map_dict['4_methyl_epigallocatechin']))

	graph.add((methyl_epigallocatechin_instance, OBO_NS['chebi#has_functional_parent'], epigallocatechin_instance))

	'''graph.add((epigallocatechin_instance, OBO_NS.RO_0002449, ugt1a1_instance))
	graph.add((epigallocatechin_instance, OBO_NS.RO_0002449, ugt1a8_instance))
	graph.add((epigallocatechin_instance, OBO_NS.RO_0002449, ugt1a10_instance))'''

	#catechin

	graph.add((OBO_NS.CHEBI_23053, RDFS_NS.subClassOf, OBO_NS.CHEBI_24431))
	graph.add((catechin_instance, RDF_NS.type, OBO_NS.CHEBI_23053))
	graph.add((catechin_instance, RDF_NS.type, OWL_NS.NamedIndividual))
	graph.add((OBO_NS.CHEBI_23053, OBO_NS.database_cross_reference, srs_map_dict['catechin']))

	pgt7 = BNode()
	graph.add((NP_gt, RDFS_NS.subClassOf, pgt7))
	graph.add((pgt7, RDF_NS.type, OWL_NS.Restriction))
	graph.add((pgt7, OWL_NS.onProperty, OBO_NS.RO_0002180))
	graph.add((pgt7, OWL_NS.someValuesFrom, OBO_NS.CHEBI_23053))
	
	graph.add((NP_gt_instance, OBO_NS.RO_0002180, catechin_instance))

	'''graph.add((catechin_instance, OBO_NS.RO_0002449, ugt1a10_instance))
	graph.add((catechin_instance, OBO_NS.RO_0002449, ugt1a1_instance))
	graph.add((catechin_instance, OBO_NS.RO_0002449, ugt1a8_instance))'''
	#has metabolite catechin sulfate (not in any source) --- FIGURE OUT

	'''catechin_sulfate = BNode()
	catechine_sulfate_instance = BNode()
	graph.add((catechin_sulfate, RDFS_NS.subClassOf, OBO_NS.CHEBI_24431))
	graph.add((catechin_sulfate_instance, RDF_NS.type, catechin_sulfate))
	graph.add((catechin_sulfate_instance, RDF_NS.type, OWL_NS.NamedIndividual))
	#external reference?'''

	#NP has_component NP_constituent
	#epigallocatechin gallate
	graph.add((OBO_NS.CHEBI_4806, RDFS_NS.subClassOf, OBO_NS.CHEBI_24431))
	graph.add((epigallocatechin_gallate_instance, RDF_NS.type, OBO_NS.CHEBI_4806))
	graph.add((epigallocatechin_gallate_instance, RDF_NS.type, OWL_NS.NamedIndividual))
	graph.add((OBO_NS.CHEBI_4806, OBO_NS.database_cross_reference, srs_map_dict['epigallocatechin_gallate']))

	pgt8 = BNode()
	graph.add((NP_gt, RDFS_NS.subClassOf, pgt8))
	graph.add((pgt8, RDF_NS.type, OWL_NS.Restriction))
	graph.add((pgt8, OWL_NS.onProperty, OBO_NS.RO_0002180))
	graph.add((pgt8, OWL_NS.someValuesFrom, OBO_NS.CHEBI_4806))
	
	graph.add((NP_gt_instance, OBO_NS.RO_0002180, epigallocatechin_gallate_instance))

	##epigallocatechin gallate in vitro enzymes/transporters
	'''graph.add((epigallocatechin_gallate_instance, OBO_NS.RO_0002449, ugt1a1_instance))
	graph.add((epigallocatechin_gallate_instance, OBO_NS.RO_0002449, ugt1a8_instance))
	graph.add((epigallocatechin_gallate_instance, OBO_NS.RO_0002449, ugt1a10_instance))'''

	'''##NP inhibition (in vivo) - enzyme and transporter
	gt_b = BNode()
	graph.add((URIRef(urn_dict['Camellia_sinensis_leaf']), RDFS_NS.subClassOf, gt_b))
	graph.add((gt_b, RDF_NS.type, OWL_NS.Restriction))
	graph.add((gt_b, OWL_NS.onProperty, OBO_NS.RO_0000056))
	graph.add((gt_b, OWL_NS.someValuesFrom, OBO_NS.GO_0009892))
	graph.add((OBO_NS.GO_0009892, OBO_NS.RO_0000057, OBO_NS.PR_P08684))

	gt_c = BNode()
	graph.add((URIRef(urn_dict['Camellia_sinensis_leaf']), RDFS_NS.subClassOf, gt_c))
	graph.add((gt_c, RDF_NS.type, OWL_NS.Restriction))
	graph.add((gt_c, OWL_NS.onProperty, OBO_NS.RO_0000056))
	graph.add((gt_c, OWL_NS.someValuesFrom, OBO_NS.GO_0032410))
	graph.add((OBO_NS.GO_0032410, OBO_NS.RO_0000057, OBO_NS.PR_P46721))
	##add in vitro results for (-)-epigallocatechin gallate (slides 36, 39, 40)'''

	f = open(OUT_GRAPH,"w")
	graph_str = graph.serialize(format='xml').decode('utf-8')
	f.write(graph_str)
	f.close()

	graph.close()
