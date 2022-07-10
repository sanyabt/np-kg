'''
Script to use REACH from INDRA interface to extract statements from the full text of articles given a list of PMIDs.
This script uses process_text function from the REACH API after extracting the full text instead of the INDRA pmc_client.
Used by the machineReadMain script to read with REACH (not an independent script - see indraREACH_new for that version)
Author: Sanya B. Taneja
Date: 05-28-2021
'''
import os, sys
import indra.literature.pmc_client as pmc_client
import indra.literature.pubmed_client as pubmed_client
from indra.sources import reach
from indra.ontology.bio import bio_ontology
import indra.tools.assemble_corpus as ac
import pickle
import xml.etree.ElementTree as ET

#True if running assembly pipeline on individual papers
run_assembly = True

#function to extract reach statements from server running through local server
def process_with_reach(text, pmid, output_dir):

	outFname = output_dir + pmid + '_reach.json'
	file_o = open(output_dir + pmid + '_reach_statements.txt', 'w')
	rp = reach.process_text(text, citation=pmid, output_fname=outFname, url='http://localhost:8000/api/text')
	print('Saving raw REACH output to file: ' + outFname)
	if rp is not None:
		for stmt in rp.statements:
			file_o.write('\n'+ str(stmt))
		return rp.statements
	else:
		return None

#get xml string of article using indra.pmc_client from the PMCID
def get_xml_from_pmcid(pmcid, pmid, dirOut_xml, dirOut_txt):
	try:
		xml_str = pmc_client.get_xml(pmcid)
	except Exception as e:
		print('Cannot extract full text from PMCID with PMID: ', pmid)
		print(e)
	if xml_str is None:
		return None
	fname = dirOut_xml + pmid + '.nxml'
	with open(fname, 'wb') as fh:
		fh.write(xml_str.encode('utf-8'))
	return xml_str

#extract plaintext from the xml string of article and save in separate text file (only if save_full_text=True)
def get_text_from_xml(pmid, xml_data, dirOut_xml, dirOut_txt):
	fname = dirOut_txt + pmid + '.txt'
	if xml_data is None:
		print('XML is empty')
		return None
	try:
		content_str = pmc_client.extract_text(xml_data)
	except Exception as e:
		print(e)
		print('XML error for pmid: ', pmid)
		content_str = None
	if content_str is None:
		return None
	else:
		print('Saving full text of XML file')
		with open(fname, 'w') as file_o:
			file_o.write(content_str)
		return content_str

'''
Steps to be modified based on use case and required output and processing
'''
def run_assembly_pipeline(statements):
	statements = ac.filter_no_hypothesis(statements)  # Filter out hypothetical statements
	statements = ac.map_grounding(statements, gilda_mode='local')         # Map grounding
	statements = ac.run_preassembly(statements,
		return_toplevel=False,
		ontology=bio_ontology,
		normalize_equivalences=True,     # Optional: rewrite equivalent groundings to one standard
		normalize_opposites=True,        # Optional: rewrite opposite groundings to one standard
		normalize_ns='OBO')  # WM = world modelers, OBO = Bio_Ontology
	return statements

def get_text_from_pmid(pmid, dirOut_xml, dirOut_txt):
	xml_str = None
	ids = pmc_client.id_lookup(pmid, idtype='pmid')
	pmcid = ids['pmcid']
	if pmcid is not None:
		xml_str = get_xml_from_pmcid(pmcid, pmid, dirOut_xml, dirOut_txt)
		if xml_str is not None:
			content = get_text_from_xml(pmid, xml_str, dirOut_xml, dirOut_txt)
			return content
	if pmcid is None or xml_str is None:
		return None
	return None
