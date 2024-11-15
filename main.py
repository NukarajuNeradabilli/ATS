# import pickle
import fitz
import json 
import pymupdf
from pyresparser import ResumeParser
from resumeExtraction import resumeExtraction
from job_extraction import job_extraction
from jd_profile_comparison import jd_profile_comparison 
# from resumeScreener import resumeScreener 


resumeExtractor = resumeExtraction()
job_extractor = job_extraction()
obj_jd_profile_comparison = jd_profile_comparison()
# resumeScreen = resumeScreener() 

# resume_role = resumeScreen.extractorData(fitz.open('static/resumes/Nukaraju_Neradabilli_CVD.pdf'),"pdf")
# print(resume_role)
resume_txt = resumeExtractor.extractorData(pymupdf.open('static/resumes/Nukaraju_Neradabilli_CVD.pdf'),"pdf")
# job_desc =job_extractor.extractorData(pymupdf.open('static/Job_Description/60ae49997be4a46cfe705c98/Java_Software_Engineer-converted.pdf'),"pdf")
job_desc =job_extractor.extractorData(pymupdf.open('static/Job_Description/Nukaraju_Neradabilli_CVD.pdf'),"pdf")


data = ResumeParser('static/resumes/Nukaraju_Neradabilli_CVD.pdf').get_extracted_data()
with open('static/json/data.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)


# Compare job description and resume
match_percentage = obj_jd_profile_comparison.match(str(job_desc),resume_txt[5])
with open('static/json/data.json', 'r') as json_file:
    data = json.load(json_file)
    data['Matching Percentage'] = str(match_percentage) 
    
    with open('static/json/data.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
# print(f"Matching Percentage: {type(str(match_percentage))}%")



