'''
Script to convert PDF to plain text using pdfminer. 
Adapted from Linh Huang notebook - https://github.com/infoqualitylab/DDI_Evidence_Classification/blob/b515b659ac7ad0c695dee9e36d63c9ed5777b7ed/Scripts/Preprocess_fulltext_papers.ipynb.
Can be run independently or with machineReadMain.py
Author: Sanya B. Taneja
Date: 05-28-2021
'''
import pdfminer
from six import StringIO
import re, sys, os
from io import BytesIO as StringIO

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

from nltk.tokenize import word_tokenize

def read_PDF_file(filename, filename_out):

	try:
		fp = open(filename, 'rb')
		# Create a PDF parser object associated with the file object.
		parser = PDFParser(fp)
		# Create a PDF document object that stores the document structure.
		# Supply the password for initialization.
		document = PDFDocument(parser)
		# Check if the document allows text extraction. If not, abort.
		if not document.is_extractable:
			raise PDFTextExtractionNotAllowed
		# Create a PDF resource manager object that stores shared resources.
		rsrcmgr = PDFResourceManager()
		# Set parameters for analysis.
		laparams = LAParams()
		# Create a PDF page aggregator object.
		device = PDFPageAggregator(rsrcmgr, laparams=laparams)
		interpreter = PDFPageInterpreter(rsrcmgr, device)
		extracted_text = ''
		for page in PDFPage.create_pages(document):
			interpreter.process_page(page)
			layout = device.get_result()
			for lt_obj in layout:
				if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
					extracted_text = extracted_text + " "
					extracted_text += lt_obj.get_text()

		with open(filename_out, "wb") as txt_file:
			txt_file.write(extracted_text.encode("utf-8"))
		return True
	except Exception as e:
		print('Unable to process PDF file')
		print(e)
		return False

def process_PDF_file(file, outputFile):
	
	start_pattern = ["Abstract", "ABSTRACT", "INTRODUCTION", "Introduction", "BACKGROUND", "Background"]
	stop_pattern = ["Acknowledgement", "ACKNOWLEDGEMENT", "REFERENCES", "References", "Supplementary Material", "Conflict of Interest statement"]
	alternate_start_pattern = ["METHODS", "Methods","Subjects and methods","Subjects and Methods", "MATERIALS AND METHODS","Materials and methods", 
					"METHODS AND MATERIALS","PATIENTS  AND  METHODS", "PARTICIPANTS AND METHODS", "SUBJECTS AND METHODS", "Materials and Methods"]
	try:
		if file.endswith(".txt") and 'processed' not in file:
			with open(file, 'r') as article_plaintext_file:
				recording = False
				output_section = []
				for line in article_plaintext_file:
					line = line.replace("\n", "")
					line_sans_num = re.sub(r'[^A-Za-z ]+', '', line)
					line_sans_num = line_sans_num.strip()
					if recording is False:
						#If the line contains "METHODS" header, start record the text, change the flag to "TRUE"
						if line_sans_num in start_pattern:
							print(line)
							recording = True
							output_section.append(line.strip())
					elif recording is True:
					#If the line contains "RESULTS" header, stop record the text, change the flag to "FALSE"
						if line_sans_num in stop_pattern:
							print(line)
							recording = False
						else:
							output_section.append(line.strip())   
				#Save the text into file
				outfile = open(outputFile, 'w')
				for line in output_section:
					line = line.strip()
					line = line.replace("\n", " ")
					line = line.replace("- ", "")
					line = line + " "
					outfile.write(line)
				outfile.close()
			return True
	except Exception as e:
		print('Unable to process text file from PDF')
		print(e)
		return False
