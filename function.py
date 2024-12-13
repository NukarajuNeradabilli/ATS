import os
import json
from resumeExtraction import resumeExtraction
from job_extraction import job_extraction
from jd_profile_comparison import jd_profile_comparison
from pyresparser import ResumeParser
from uuid import uuid4
import pymupdf

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def process_resumes_and_jd(resumes_path, jd_path, output_json_path):
    try:
        ensure_directory_exists('static/resumes')
        ensure_directory_exists('static/Job_Description')

        # Extract Job Description
        job_extractor = job_extraction()
        job_desc = job_extractor.extractorData(pymupdf.open(jd_path), "pdf")

        results = []
        resumeExtractor = resumeExtraction()
        obj_jd_profile_comparison = jd_profile_comparison()

        # Process each resume in the given directory
        for resume_filename in os.listdir(resumes_path):
            resume_file_path = os.path.join(resumes_path, resume_filename)

            if not resume_filename.endswith('.pdf'):
                results.append({
                    "Resume Filename": resume_filename,
                    "Error": "Only PDF files are allowed"
                })
                continue

            try:
                # Parse Resume
                resume_data = ResumeParser(resume_file_path).get_extracted_data()
                resume_txt = resumeExtractor.extractorData(pymupdf.open(resume_file_path), "pdf")
                match_percentage = obj_jd_profile_comparison.match(str(job_desc), resume_txt[5])
                resume_data['Matching Percentage'] = str(match_percentage)
                resume_id = str(uuid4())
                results.append({"Id": resume_id, "Resume Data": resume_data})
            except Exception as resume_error:
                results.append({
                    "Resume Filename": resume_filename,
                    "Error": str(resume_error)
                })

        # Store results in JSON file
        with open(output_json_path, 'w') as json_file:
            json.dump({"Results": results}, json_file, indent=4)

        return {"Message": "Processing completed. Results stored in JSON file."}

    except Exception as e:
        return {"Error": str(e)}

# Example Usage
if __name__ == "__main__":
    resumes_directory = "source/resumes"
    job_description_path = "source/job_description/Nukaraju_Neradabilli_CV_22.pdf"
    output_json_file = "output_results.json"
    output = process_resumes_and_jd(resumes_directory, job_description_path, output_json_file)
    print(output)
