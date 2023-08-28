'''
Main script to run the INDRA/REACH relation extraction system on full text articles. Script reads PDF files, converts
to text, processes text, and generates output.
Author: Sanya B. Taneja
'''
import os, sys
from pdf_to_text import read_PDF_file, process_PDF_file
from indraREACH_extract import process_with_reach, get_text_from_pmid, run_assembly_pipeline, process_with_reach_nxml
from datetime import datetime, timedelta
from indra.statements import stmts_to_json_file 

working_dir = os.getcwd()
DIR_IN = working_dir + '/input_files/'
DIR_OUT = working_dir + '/output_files/'
DIR_LOG = working_dir + '/logs/'

logging = True
#True if running assembly pipeline on individual papers
run_assembly = True

#start_line = int(sys.argv[1])
#end_line = int(sys.argv[2])

NP = ['cranberry',  'fenugreek',  'flaxseed', 'ginger', 'ginkgo', 'goldenseal',  'guarana', 'horsechestnut', 
'licorice', 'oregano',  'scrubpalmetto',  'valerian', 'ashwaganda', 'blackpepper', 'blackcohosh', 'cannabis', 'echinacea', 'feverfew', 'garlic', 'grapefruit', 'milkthistle',
'panaxginseng', 'rhodiola', 'rosemary', 'soybean', 'hawthorn']

pmid_list = []

if __name__ == '__main__':
	for item in NP:
		t0 = datetime.now()
		log_file = open(DIR_LOG + item + str(t0) + '_log.txt', 'w')
		input_dir = DIR_IN + item +'/'
		input_dir_pdf = DIR_IN + item + '/FullTextPDFs/'
		output_dir = DIR_OUT + item + '/reachOutput/'
		output_dir_pdf = DIR_OUT + item + '/PDFoutput/'
		output_dir_xml = DIR_OUT + item + '/xmlTexts/'
		file_i = input_dir + item + '_pmid.txt'
		log_file.write('Log for '+ item)
		with open(file_i, 'r') as file_input:
			pmids = file_input.readlines()
		count_dict = {
			'n_pmid': 0,
			'n_pdf': 0,
			'n_output_reach': 0,
			'n_statements': 0,
			'n_error': 0
		}
		stmts = []
		#to track if pdf extract required for PMID
		pdf_flag = True
		for line in pmids:
			pmid = line.strip()
			if pmid in pmid_list:
				continue
			pmid_list.append(pmid)
			count_dict['n_pmid'] += 1
			log_file.write('\n\nPMID: '+pmid)
			#check for  full text from PMC and get text
			text = get_text_from_pmid(pmid, output_dir_xml, output_dir)

			if text is not None:
				#full text available in PMC
				pmc_statements = process_with_reach_nxml(pmid, output_dir_xml, output_dir)
				if pmc_statements is not None:
					pdf_flag = False
					count_dict['n_output_reach'] += 1
					log_file.write('\nNumber of statements (PMC): '+str(len(pmc_statements)))
					stmts += pmc_statements
				else:
					pmc_statements = process_with_reach(text, pmid, output_dir)
					if pmc_statements is not None:
						pdf_flag = False
						count_dict['n_output_reach'] += 1
						log_file.write('\nNumber of statements (PMC-text): '+str(len(pmc_statements)))
						stmts += pmc_statements
				
			elif pdf_flag or text is None:
				#check for PDF file and get text
				pdf_files = os.listdir(input_dir_pdf)
				if pmid + '.pdf' in pdf_files:
					count_dict['n_pdf'] += 1
					pdf_in_file = input_dir_pdf+pmid+'.pdf'
					pdf_out_file = output_dir_pdf+pmid+'.txt'
					pdf_txt_file = output_dir_pdf+pmid+'_processed.txt'
					pdf_text_val = read_PDF_file(pdf_in_file, pdf_out_file)
					if pdf_text_val:
						pdf_text_process_val = process_PDF_file(pdf_out_file, pdf_txt_file)
						if pdf_text_process_val:
							if os.path.getsize(pdf_txt_file) == 0:
								pdf_txt_file = pdf_out_file
							with open(pdf_txt_file, 'r') as file_txt:
								pdf_text = file_txt.read()
							pdf_statements = process_with_reach(pdf_text, pmid, output_dir)
							if pdf_statements is not None:
								count_dict['n_output_reach'] += 1
								log_file.write('\nNumber of statements (PDF): '+str(len(pdf_statements)))
								stmts += pdf_statements
							else:
								log_file.write('\nREACH returned None for PMID: '+ pmid)
					else:
						count_dict['n_error'] += 1
						log_file.write('\nUnable to extract from PDF: '+pmid)
						#process abstract in this case
				
				else:
					log_file.write('\nPMC or PDF not available for PMID: '+pmid)
					count_dict['n_error'] += 1
					#process abstract in this case

		if run_assembly:
			stmts = run_assembly_pipeline(stmts)
			outJSONFname = output_dir + item+ '_reach_output_assembly.json'
		
		else:
			outJSONFname = output_dir + item +'_reach_output_no_assembly.json'
		count_dict['n_statements'] = len(stmts)
		print('Saving combined output:')
		stmts_to_json_file(stmts, outJSONFname)

		if logging:
			t1 = datetime.now()
			seconds=timedelta.total_seconds(t1-t0)
			log_file.write('\nTotal time: '+ str(seconds)+' seconds')
			log_file.write('\nInput file: '+file_i)
			log_file.write('\nPMIDs: '+ str(len(pmids)))
			log_file.write('\nN_pmid_hits: '+str(count_dict['n_pmid']))
			log_file.write('\nN_pdf_hits: '+str(count_dict['n_pdf']))
			log_file.write('\nN_reach_hits: '+str(count_dict['n_output_reach']))
			log_file.write('\nN_errors: '+str(count_dict['n_error']))
			log_file.write('\nN_statements: '+str(count_dict['n_statements']))



