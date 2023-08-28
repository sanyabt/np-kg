import sys, os
from datetime import datetime, timedelta
import pandas as pd
import subprocess
from nltk import tokenize
import requests
import time
import logging

'''
Script to handle all errors in SemRep processing - including missing text file and SemRep timeout errors
ToDO:
1. Input PMIDs that gave errors (compiled from log files)
2. Once text available - use the updated text files with individual sentences to process with SemRep
'''

workingDir = os.getcwd()
log_dir = workingDir + '/logs/'
np = ['list of NPs']

extraction = True

count_dict = {
			'n_total_pmid': 0,
			'n_success': 0,
			'n_error': 0,
			'n_statements':0,
			'n_files_processed': 0
			}
pub_year_to_pmid_map = {}

def process_with_semrep(infile, outfile):
	try:
		result = subprocess.run(['/usr/local/bin/semrep.v1.8', '-L', '2018', '-Z', '2018AA', infile, outfile], check=True, timeout=1800)

		return result
	except Exception as e:
		logging.info('SemRep error in processing %s', str(e))
		return None

def get_publication_year_and_type(pmid):
	pub_year = ''
	pub_type = ''
	if pmid == '':
		return pub_year, pub_type
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

def semrep_extract(filepath):
	result_dict = {
		'index': [],
		'pmid': [],
		'relation': [],
		'year': [],
		'subject_cui': [],
		'object_cui': [],
		'subject_name': [],
		'object_name': [],
		'subject_type': [],
		'object_type': [],
		'sentence': [],
		'source_section': [],
		'pub_type': []
	}
	index = 0
	semrep_files = os.listdir(filepath)
	for file in semrep_files:
		pmid = file.split('.')[0]
		sem_relations = {
			'items': [],
			'source_sentence': [],
			'source_section': []
		}
		with open(filepath+file, 'r', errors='ignore') as file_sem:
			lines = file_sem.readlines()
		
		last_non_empty = ''
		section_match = ''
		for item in lines:
			if any(s in item for s in section_tags):
				#assign section
				section_match = next((sec for sec in section_tags if sec in item), False)
			if '|relation|' in item:
				sem_relations['items'].append(item)
				sem_relations['source_sentence'].append(last_non_empty)
				sem_relations['source_section'].append(section_match)
			elif item == '\n' or item == '':
				continue
			else:
				last_non_empty = item
			
		count_dict['n_statements'] += len(sem_relations)
		for rel in sem_relations['items']:
			fields = rel.split('|')
			if len(fields) < 5:
				continue
			result_dict['index'].append(index)
			result_dict['pmid'].append(pmid)
			result_dict['subject_cui'].append(fields[2])
			result_dict['object_cui'].append(fields[9])
			result_dict['subject_name'].append(fields[3])
			result_dict['object_name'].append(fields[10])
			result_dict['relation'].append(fields[8])
			result_dict['subject_type'].append(fields[4])
			result_dict['object_type'].append(fields[11])
			pub_year, pub_type = get_publication_year_and_type(pmid)
			result_dict['year'].append(pub_year)
			result_dict['pub_type'].append(pub_type)
			relation_index = sem_relations['items'].index(rel)
			result_dict['sentence'].append(sem_relations['source_sentence'][relation_index])
			result_dict['source_section'].append(sem_relations['source_section'][relation_index])
			index += 1

	return result_dict

if __name__ == '__main__':
	for item in np:
		
		inputPMID_file = workingDir + '/input_files/'+item+'/'+item+'_pmid_errors.txt'
		inputDir = workingDir + '/output_files/' + item + '/Corrected/'
		outputDir = workingDir + '/output_files/'+item+'/semrepOutput/'
		
		t0=datetime.now()
		
		log_file = log_dir+item + '_semrep_fix_errors_log'+str(t0)+'.txt'
		logging.basicConfig(filename=log_file, filemode='a', level=logging.INFO)
		logging.info('Log for %s. PMIDs with errors in processing from iteration 1', item)
		logging.info('\nInput file: %s', inputPMID_file)

		with open(inputPMID_file, 'r') as file_input:
			pmids = file_input.readlines()

		text_files = os.listdir(inputDir)

		for pmid in pmids:
			pmid = pmid.strip()
			logging.info('\n\nProcessing PMID: %s', pmid)
			count_dict['n_total_pmid'] += 1
			file = str(pmid) + '_ascii.txt'
			print(file)
			if file in text_files:
				filename = inputDir+file

				semrep_process = process_with_semrep(filename, outputDir+file.split('_')[0]+'.txt')
				if semrep_process is not None:
					logging.info('\nFile processed: %s', file)
					count_dict['n_success'] += 1 

				else:
					logging.info('\nError in processing: %s',file)
					count_dict['n_error'] += 1
			else:
				logging.info('\nText unavailable: %s',file)
				count_dict['n_error'] +=1

		if extraction:
			result_dict = semrep_extract(outputDir)

		semrep_result = pd.DataFrame(result_dict)
		semrep_result_unique = semrep_result.drop_duplicates(subset=['subject_cui', 'subject_name', 'subject_type',
					'relation', 'object_cui', 'object_name', 'object_type', 'year', 'sentence'])
		semrep_result_unique.to_csv(workingDir+'/output_files/'+item+'/' +item+'_pmid_all_predicates_semrep-errors-fixed.tsv', sep='\t', index=False,
					columns=['index', 'pmid', 'subject_cui', 'subject_name', 'subject_type',
					'relation', 'object_cui', 'object_name', 'object_type', 'year', 'sentence'])

		t1 = datetime.now()
		seconds=timedelta.total_seconds(t1-t0)
		logging.info('\nTotal time: %s seconds', str(seconds))
		logging.info('\nTotal PMIDs: %s',str(count_dict['n_total_pmid']))
		logging.info('\nN_file_hits: %s',str(count_dict['n_files_processed']))
		logging.info('\nN_semrep_hits: %s',str(count_dict['n_success']))
		logging.info('\nN_errors: %s',str(count_dict['n_error']))
		logging.info('\nN_statements: %s',str(count_dict['n_statements']))

		os.system("pkill semrep")

		logging.info('\nTerminated subprocesses')
