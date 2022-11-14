'''
Script to extract predications from SemRep for full texts of articles (already processed from PDF to text)
MetaMap, WordSenseDisambiguation Server, and SemRep are running locally.
'''
import sys, os
from datetime import datetime, timedelta
import pandas as pd
import subprocess
from nltk import tokenize
import requests
import time
from pdf_to_text import read_PDF_file, process_PDF_file
import logging

workingDir = os.getcwd()
log_dir = workingDir + '/logs/'
utf_path = 'replace_utf8.jar'

np = []

extraction = True

count_dict = {
			'n_total_pmid': 0,
			'n_success': 0,
			'n_error': 0,
			'n_statements':0,
			'n_files_processed': 0,
			'n_pdf': 0
			}

start_pmid = int(sys.argv[1])
end_pmid = int(sys.argv[2])

pub_year_to_pmid_map = {}

def read_and_write_file(file, filepath_in, filepath_out):
	filepath = filepath_in+file
	
	fileascii = filepath_out+file.split('_')[0]+'_ascii.txt'
	convert_to_ascii = subprocess.run(["java", "-jar", utf_path, filepath], capture_output=True, text=True)
	if convert_to_ascii:
		result = convert_to_ascii.stdout
		sentences = tokenize.sent_tokenize(result)
		fileo = open(fileascii, 'w', encoding='ascii', errors='backslashreplace')
		for item in sentences:
			if sentences.index(item) % 5 == 0:
				fileo.write('\n\n')
			if len(item) > 1000:
				fileo.write('\n\n')
				#continue
			fileo.write(str(item))
		fileo.write('\n')
		fileo.close()
		count_dict['n_files_processed'] += 1 
		return fileascii
	else:
		return None

def process_with_semrep(infile, outfile):
	try:
		result = subprocess.run(['/usr/local/bin/semrep.v1.8', '-L', '2018', '-Z', '2018AA', infile, outfile], check=True, timeout=1800)

		return result
	except Exception as e:
		logging.info('SemRep error in processing %s', str(e))
		return None

def get_publication_year(pmid):
	if pmid == '':
		return ''
	if pmid in pub_year_to_pmid_map:
		if pub_year_to_pmid_map[pmid] != '':
			return pub_year_to_pmid_map[pmid]
	time.sleep(5)
	uri = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id="+pmid+"&retmode=json"
	pub_year = ''
	response = requests.get(uri)
	if response.status_code == 429:
		time.sleep(5)
		response = requests.get(uri)
	if response.status_code == 200:
		result = response.json()
		pub_year = result['result'][pmid]['pubdate']
		pub_year_to_pmid_map[pmid] = pub_year
	return pub_year

###counting of statements is incorrect and being done per file not all - last reported is for the file not the entire set in count dict or log
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
		'sentence': []
	}
	index = 0
	semrep_files = os.listdir(filepath)
	for file in semrep_files:
		pmid = file.split('.')[0]
		sem_relations = {
			'items': [],
			'source_sentence': []
		}
		with open(filepath+file, 'r', errors='ignore') as file_sem:
			lines = file_sem.readlines()
		
		last_non_empty = ''

		for item in lines:
			if '|relation|' in item:
				sem_relations['items'].append(item)
				sem_relations['source_sentence'].append(last_non_empty)
			elif item == '\n' or item == '':
				continue
			else:
				last_non_empty = item
		
		count_dict['n_statements'] += len(sem_relations)
		for rel in sem_relations['items']:
			result_dict['index'].append(index)
			result_dict['pmid'].append(pmid)
			fields = rel.split('|')
			result_dict['subject_cui'].append(fields[2])
			result_dict['object_cui'].append(fields[9])
			result_dict['subject_name'].append(fields[3])
			result_dict['object_name'].append(fields[10])
			result_dict['relation'].append(fields[8])
			result_dict['subject_type'].append(fields[4])
			result_dict['object_type'].append(fields[11])
			pub_year = get_publication_year(pmid)
			result_dict['year'].append(pub_year)
			relation_index = sem_relations['items'].index(rel)
			result_dict['sentence'].append(sem_relations['source_sentence'][relation_index])
			index += 1

	return result_dict

if __name__ == '__main__':

	for item in np:
		inputPMID_file = workingDir + '/input_files/' + item + '/' + item + '_pmid.txt'
		#inputPMID_file = workingDir + '/input_files/' + item + '/' + item + '_pmid_PDF.txt'
		inputDirRaw = workingDir + '/output_files/' + item + '/PDFoutput/'
		inputDir = workingDir + '/output_files/'+item+'/semrepInput/'
		outputDir = workingDir + '/output_files/'+item+'/semrepOutput/'
		PDF_inputDir = workingDir + '/input_files/'+item+'/FullTextPDFs/'
		PDF_outputDir = inputDirRaw
		
		t0=datetime.now()
		
		log_file = log_dir+item + '_semrep_log'+str(t0)+'.txt'
		logging.basicConfig(filename=log_file, filemode='a', level=logging.INFO)
		logging.info('Log for %s. PMIDS: %s to %s', item, str(start_pmid), str(end_pmid))
		
		
		with open(inputPMID_file, 'r') as file_input:
			pmids = file_input.readlines()

		text_files = os.listdir(inputDirRaw)
		
		for line_no in range(start_pmid, end_pmid):
			pmid = pmids[line_no].strip()
			logging.info('\n\nProcessing PMID: %s', pmid)
			count_dict['n_total_pmid'] += 1
			file = str(pmid) + '_processed.txt' 
			file_alternate = str(pmid) + '.txt'
			
			text_files = os.listdir(inputDirRaw)
			if file not in text_files and file_alternate not in text_files:
				logging.info('\nText unavailable: %s', file_alternate)
				#extract text from PDF
				logging.info('\nChecking for PDF:')
				pdf_files = os.listdir(PDF_inputDir)
				if pmid + '.pdf' in pdf_files:
					logging.info('\nPDF found')
					count_dict['n_pdf'] += 1
					pdf_in_file = PDF_inputDir+pmid+'.pdf'
					pdf_out_file = PDF_outputDir+pmid+'.txt'
					pdf_txt_file = PDF_outputDir+pmid+'_processed.txt'
					pdf_text_val = read_PDF_file(pdf_in_file, pdf_out_file)
					if pdf_text_val:
						pdf_text_process_val = process_PDF_file(pdf_out_file, pdf_txt_file)	
					else:
						count_dict['n_error'] += 1
						logging.info('\nUnable to extract from PDF: %s',pmid)
				else:
					logging.info('\nPDF unavailable')
			
			#update to include new files
			text_files = os.listdir(inputDirRaw)
			if file not in text_files:
				file = file_alternate

			if file in text_files:
				filename = read_and_write_file(file, inputDirRaw, inputDir)
				if filename is not None:
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
					
			else:
				logging.info('\nPDF file unavailable: %s', file)

		if extraction:
			result_dict = semrep_extract(outputDir)

		semrep_result = pd.DataFrame(result_dict)
		semrep_result_unique = semrep_result.drop_duplicates(subset=['subject_cui', 'subject_name', 'subject_type',
					'relation', 'object_cui', 'object_name', 'object_type', 'year', 'sentence'])
		semrep_result_unique.to_csv(workingDir+'/output_files/'+item+'/' +item+'_pmid_all_predicates_semrep-'+str(start_pmid)+'-'+str(end_pmid)+'.tsv', sep='\t', index=False,
					columns=['index', 'pmid', 'subject_cui', 'subject_name', 'subject_type',
					'relation', 'object_cui', 'object_name', 'object_type', 'year', 'sentence'])

		t1 = datetime.now()
		seconds=timedelta.total_seconds(t1-t0)
		logging.info('\nTotal time: %s seconds', str(seconds))
		logging.info('\nPMIDs: %s to %s', str(start_pmid), str(end_pmid-1))
		logging.info('\nTotal PMIDs: %s',str(count_dict['n_total_pmid']))
		logging.info('\nN_file_hits: %s',str(count_dict['n_files_processed']))
		logging.info('\nN_semrep_hits: %s',str(count_dict['n_success']))
		logging.info('\nN_errors: %s',str(count_dict['n_error']))
		logging.info('\nN_statements: %s',str(count_dict['n_statements']))

		os.system("pkill semrep")

		logging.info('\nTerminated subprocesses')