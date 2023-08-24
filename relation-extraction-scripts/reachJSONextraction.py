import os, sys
from indra.statements import stmts_from_json_file, stmts_to_json_file
import pandas as pd
from indra.ontology.bio import bio_ontology
import indra.tools.assemble_corpus as ac
import re
import pickle
import requests
from datetime import datetime, timedelta
import time
from indra.sources import reach

predicates_exclude = ['Agent', 'Conversion', 'Complex', 'SelfModification', 'ActiveForm' 'Gef', 'Gap', 'Autophosphorylation', 'Translocation', 'Transphosphorylation']
workingDir = os.getcwd()
reachDir = workingDir + '/output_files/'
#reach_file = sys.argv[1]
logDir = workingDir + '/logs/'
file_umls = workingDir + '/output_files/umls_dict_20230321.pickle'
save_umls = True
logging = True

#np=['ashwaganda', 'cranberry','blackcohosh', 'blackpepper', 'echinacea', 'fenugreek', 'feverfew', 
#'flaxseed', 'garlic', 'ginger', 'ginkgo', 'goldenseal', 'guarana', 'hawthorn', 
#'horsechestnut', 'licorice', 'milkthistle', 'oregano', 'panaxginseng', 
#'rhodiola', 'rosemary', 'scrubpalmetto', 'soybean']

np = ['turmeric', 'valerian']

assemble = False
pub_year_to_pmid_map = {}
pub_type_to_pmid_map = {}


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

def get_publication_year_and_type(pmid):
	pub_year = ''
	pub_type = ''
	if pmid == '':
		return '', ''
	try:
		if pmid in pub_year_to_pmid_map and pmid in pub_type_to_pmid_map:
			if pub_year_to_pmid_map[pmid] != '':
				pub_year = pub_year_to_pmid_map[pmid]
				pub_type = pub_type_to_pmid_map[pmid]
				return pub_year, str(pub_type)
		time.sleep(5)
		uri = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id="+pmid+"&retmode=json"
		response = requests.get(uri)
		if response.status_code == 429:
			time.sleep(5)
			response = requests.get(uri)
		if response.status_code == 200:
			result = response.json()
			pub_year = result['result'][pmid]['pubdate']
			pub_year_to_pmid_map[pmid] = pub_year

			pub_type = result['result'][pmid]['pubtype']
			pub_type_to_pmid_map[pmid] = pub_type
		return pub_year, str(pub_type)
	except Exception as e:
		print('Error in pub type and year for PMID: ', pmid)
		return '', ''

def get_umls_concepts(subject_source, object_source, umls_dict, subj_mapped, obj_mapped):
	count_dict['n_entities_total'] += 2

#(replace spaces with underscores of preferred names in the UMLS)
	subject_dict = {}
	object_dict = {}
	if subject_source in umls_dict:
		subject_dict['cui'] = umls_dict[subject_source]['cui']
		name = umls_dict[subject_source]['umls_term']
		subject_dict['name'] = "_".join(name.split())
		subject_dict['type'] = umls_dict[subject_source]['sem_type']
		subject_dict['score'] = umls_dict[subject_source]['score']
		count_dict['n_entities_mapped'] += 1
	elif subj_mapped in umls_dict:
		subject_dict['cui'] = umls_dict[subj_mapped]['cui']
		name = umls_dict[subj_mapped]['umls_term']
		subject_dict['name'] = "_".join(name.split())
		subject_dict['type'] = umls_dict[subj_mapped]['sem_type']
		subject_dict['score'] = umls_dict[subj_mapped]['score']
		count_dict['n_entities_mapped'] += 1
	else:
		subject_dict['cui'] = ''
		subject_dict['name'] = ''
		subject_dict['type'] = ''
		subject_dict['score'] = ''

	if object_source in umls_dict:
		object_dict['cui'] = umls_dict[object_source]['cui']
		name = umls_dict[object_source]['umls_term']
		object_dict['name'] = "_".join(name.split())
		object_dict['type'] = umls_dict[object_source]['sem_type']
		object_dict['score'] = umls_dict[object_source]['score']
		count_dict['n_entities_mapped'] += 1
	elif obj_mapped in umls_dict:
		object_dict['cui'] = umls_dict[obj_mapped]['cui']
		name = umls_dict[obj_mapped]['umls_term']
		object_dict['name'] = "_".join(name.split())
		object_dict['type'] = umls_dict[obj_mapped]['sem_type']
		object_dict['score'] = umls_dict[obj_mapped]['score']
		count_dict['n_entities_mapped'] += 1
	else:
		object_dict['cui'] = ''
		object_dict['name'] = ''
		object_dict['type'] = ''
		object_dict['score'] = '' 

	return subject_dict, object_dict

def extract_statements(file_path, umls_dict, count_dict):

	result_dict = {
		'seq': [],
		'pmid': [],
		'subject_source': [],
		'object_source': [],
		'belief': [],
		'predicate': [],
		'sentence': [],
		'subj_map_reach': [],
		'obj_map_reach': [],
		'year': [],
		'subject_cui': [],
		'object_cui': [],
		'subject_name': [],
		'object_name': [],
		'subject_type': [],
		'object_type': [],
		'subject_score': [],
		'object_score': [],
		'umls_flag': [],
		'subj_reach_grounding': [],
		'obj_reach_grounding': [],
		'pub_type': [],
		'source_section': []
	}

	stmts = stmts_from_json_file(file_path)
	count_dict['n_statements'] += len(stmts)
	seq = 0
	for statement in stmts:
		predicate = type(statement).__name__
		fields = dir(statement.evidence[0])
		if predicate not in predicates_exclude:
			try:
				result_dict['seq'].append(seq)
				if 'pmid' in fields:
					pmid = statement.evidence[0].pmid
				else:
					pmid = ''
				result_dict['pmid'].append(pmid)

				if 'subj' in dir(statement):
					if statement.subj:
						subject_source = str(statement.subj.name)
						if statement.subj.db_refs:
							if 'TEXT' in statement.subj.db_refs:
								subject_source_text = str(statement.subj.db_refs['TEXT'])
							else:
								subject_source_text = subject_source
						else:
							subject_source_text = subject_source
					else:
						subject_source = ''
						subject_source_text = ''
					if statement.obj:
						object_source = str(statement.obj.name)
						if statement.obj.db_refs:
							if 'TEXT' in statement.obj.db_refs:
								object_source_text = str(statement.obj.db_refs['TEXT'])
							else:
								object_source_text = object_source
						else:
							object_source_text = object_source
					else:
						object_source = ''
						object_source_text = ''
				elif 'enz' in dir(statement):
					if statement.enz:
						subject_source = str(statement.enz.name)
						if statement.enz.db_refs:
							if 'TEXT' in statement.enz.db_refs:
								subject_source_text = str(statement.enz.db_refs['TEXT'])
							else:
								subject_source_text = subject_source
						else:
							subject_source_text = subject_source
					else:
						subject_source = ''
						subject_source_text = ''
					if statement.sub:
						object_source = str(statement.sub.name)
						if statement.sub.db_refs:
							if 'TEXT' in statement.sub.db_refs:
								object_source_text = str(statement.sub.db_refs['TEXT'])
							else:
								object_source_text = object_source
						else:
							object_source_text = object_source
					else:
						object_source = ''
						object_source_text = ''
				else:
					subject_source = ''
					object_source = ''
					subject_source_text = ''
					object_source_text = ''
				subject_source = re.sub(r'\(|\)', '', subject_source)
				subject_source = re.sub(r'[^\x00-\x7F]+',' ', subject_source)
				object_source = re.sub(r'\(|\)', '', object_source)
				object_source = re.sub(r'[^\x00-\x7F]+',' ', object_source)
				subject_source = subject_source.strip()
				object_source = object_source.strip()
				result_dict['subject_source'].append(subject_source)
				result_dict['object_source'].append(object_source)
				result_dict['belief'].append(statement.belief)
				result_dict['predicate'].append(predicate)
				result_dict['sentence'].append(statement.evidence[0].text)
				#confirm path of section type
				if 'section_type' in statement.evidence[0].epistemics:
					source_section = statement.evidence[0].epistemics['section_type']
				else:
					source_section = ''
				result_dict['source_section'].append(source_section)

				#query umls dictionary to get CUIs etc. Will save empty strings if unmapped
				if save_umls:
					subject_source_text = re.sub(r'\(|\)', '', subject_source_text)
					subject_source_text = re.sub(r'[^\x00-\x7F]+',' ', subject_source_text)
					object_source_text = re.sub(r'\(|\)', '', object_source_text)
					object_source_text = re.sub(r'[^\x00-\x7F]+',' ', object_source_text)
					subject_source_text = subject_source_text.strip()
					object_source_text = object_source_text.strip()
					subj, obj = get_umls_concepts(subject_source_text, object_source_text, umls_dict, subject_source, object_source)
					result_dict['subject_cui'].append(subj['cui'])
					result_dict['subject_name'].append(subj['name'])
					result_dict['subject_type'].append(subj['type'])
					result_dict['subject_score'].append(subj['score'])
					result_dict['object_cui'].append(obj['cui'])
					result_dict['object_name'].append(obj['name'])
					result_dict['object_type'].append(obj['type'])
					result_dict['object_score'].append(obj['score'])

				if result_dict['subject_cui']:
					result_dict['umls_flag'].append(1)
				else:
					result_dict['umls_flag'].append(0)

				groundings = statement.evidence[0].annotations['agents']['raw_grounding']
				if len(groundings):
					result_dict['subj_map_reach'].append(groundings[0])
					if len(groundings) == 2:
						result_dict['obj_map_reach'].append(groundings[1])
				
				agent_list = statement.agent_list()
				if len(agent_list):
					if agent_list[0]:
						result_dict['subj_reach_grounding'].append(agent_list[0].get_grounding())
					else:
						result_dict['subj_reach_grounding'].append('')
					if len(agent_list) == 2:
						if agent_list[1]:
							result_dict['obj_reach_grounding'].append(agent_list[1].get_grounding())
						else:
							result_dict['obj_reach_grounding'].append('')
				else:
					result_dict['subj_reach_grounding'].append('')
					result_dict['obj_reach_grounding'].append('')
				pub_year, pub_type = get_publication_year_and_type(pmid)
				result_dict['year'].append(pub_year)
				result_dict['pub_type'].append(pub_type)

				seq += 1

				count_dict['n_statements_extracted'] += 1
			except Exception as e:
				print(filepath)
				print(e)

	return result_dict, count_dict

if __name__ == '__main__':

	t0=datetime.now()
	log_file = open(logDir+'json_extract_log'+str(t0)+'.txt', 'a')
	file_d = open(file_umls, 'rb')
	umls_dict = pickle.load(file_d)
	for np_name in np:
		count_dict = {
		'n_files_processed': 0,
		'n_statements': 0,
		'n_statements_extracted': 0,
		'n_entities_total': 0,
		'n_entities_mapped': 0
		}

		outputDir = reachDir + np_name + '/'
		reach_file = outputDir+'reachOutput/'+np_name+'_reach_output_assembly.json'
		log_file.write('\nStarting REACH files extraction for '+np_name)
		log_file.write('\n'+reach_file)
		
	
		#Option 1: use assembled file
		if '.' in reach_file:
			reach_dict, count_dict = extract_statements(reach_file, umls_dict, count_dict)
		#Option 2: separate option for multiple files
		else:
			reach_statements = []
			reach_files = os.listdir(reach_file)
			for file in reach_files:
				if file.endswith(".json"):
					pmid = file.split('_')[0]
					filepath = reach_file+file
					rp = reach.process_json_file(filepath, citation=pmid)
					count_dict['n_files_processed'] += 1
					if rp is not None:
						reach_statements += rp.statements
			reach_statements_assembled = run_assembly_pipeline(reach_statements)
			outJSONFname = outputDir + np_name + '_reach_output_assembly_all.json'
			stmts_to_json_file(reach_statements_assembled, outJSONFname)
			reach_dict, count_dict = extract_statements(outJSONFname, umls_dict, count_dict)
		
		outfilename = outputDir+np_name+'_pmid_reach_all_predicates_umls_20230322.tsv'
		reach_result = pd.DataFrame(data=reach_dict)
		reach_result.to_csv(outfilename, sep='\t', index=False,
						columns=['seq', 'pmid', 'subject_cui', 'subject_name', 'subject_type', 'subject_source', 'subj_map_reach',
						'predicate', 'object_source', 'object_cui', 'object_name', 'object_type', 'obj_map_reach', 'belief',
						'sentence', 'year', 'subject_score', 'object_score', 'umls_flag', 'subj_reach_grounding', 'obj_reach_grounding',
						'pub_type', 'source_section'])
		t1=datetime.now()
		seconds=timedelta.total_seconds(t1-t0)
		log_file.write('\nTotal time: '+ str(seconds)+' seconds')
		#print count dictionary to log file
		log_file.write('\nNumber of files processed: '+str(count_dict['n_files_processed']))
		log_file.write('\nStatements: '+str(count_dict['n_statements']))
		log_file.write('\nStatements_extracted: '+str(count_dict['n_statements_extracted']))
		log_file.write('\nEntities: '+str(count_dict['n_entities_total']))
		log_file.write('\nEntities_mapped: '+str(count_dict['n_entities_mapped'])+'\n')
