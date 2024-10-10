from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import fitz 
import re
import nltk
import pymupdf
nltk.download('stopwords')
nltk.download('punkt')
import docx2txt
import pickle

class job_extraction: 
    
    def __init__(self) -> None:
        self.STOPWORDS = set(stopwords.words('english')+['``',"''"])
    
    def __clean_text(self,job_text):
        job_text = re.sub(r'http\S+\s*', ' ', job_text)  # remove URLs
        job_text = re.sub('RT|cc', ' ', job_text)  # remove RT and cc
        job_text = re.sub(r'#\S+', '', job_text)  # remove hashtags
        job_text = re.sub(r'@\S+', '  ', job_text)  # remove mentions
        job_text = re.sub('[%s]' % re.escape(r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', job_text)  # remove punctuations
        job_text = re.sub(r'[^\x00-\x7f]',r' ', job_text) 
        job_text = re.sub(r'\s+', ' ', job_text)  # remove extra whitespace
        job_text = job_text.lower()  # convert to lowercase
        return job_text
    
    def extractorData(self,file,ext): #
        text=""
        if ext=="docx": 
            temp = docx2txt.process(file)
            text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
            text = ' '.join(text)
        if ext=="pdf":
            for page in pymupdf.open(file):
                text = text + str(page.get_text())
            text = " ".join(text.split('\n'))
        text = self.__clean_text(text)
        text1=text
        return text1 
        
job_extractor = job_extraction()

# print(job_extractor.extractorData(fitz.open('static\\Job_Description\\60ae49997be4a46cfe705c98\\Java_Software_Engineer-converted.pdf'),"pdf")) 
job_desc =job_extractor.extractorData(pymupdf.open('static/Job_Description/Nukaraju_Neradabilli_CVD.pdf'),"pdf")
# print(job_desc)
# pickle.dump(job_extractor,open("job_extractor.pkl","wb"))
# print("Job Extraction is working fine")
    
