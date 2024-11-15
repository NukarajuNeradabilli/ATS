from flask import Flask, request, jsonify
import json
import fitz
import pymupdf
from pyresparser import ResumeParser
from resumeExtraction import resumeExtraction
from job_extraction import job_extraction
from jd_profile_comparison import jd_profile_comparison
import os

app = Flask(__name__)

# Initialize your objects for extracting and comparing
resumeExtractor = resumeExtraction()
job_extractor = job_extraction()
obj_jd_profile_comparison = jd_profile_comparison()

@app.route('/process_resume', methods=['POST'])
def process_resume():
    # Check if resume and job description files are in the request
    if 'resume' not in request.files or 'job_description' not in request.files:
        return jsonify({"error": "Please upload both resume and job description files"}), 400

    # Save files temporarily
    resume_file = request.files['resume']
    jd_file = request.files['job_description']
    resume_path = 'static/resumes/temp_resume.pdf'
    jd_path = 'static/Job_Description/temp_job_description.pdf'
    resume_file.save(resume_path)
    jd_file.save(jd_path)

    try:
        # Extract resume data
        resume_data = ResumeParser(resume_path).get_extracted_data()

        # Extract job description and resume text content
        resume_txt = resumeExtractor.extractorData(pymupdf.open(resume_path), "pdf")
        job_desc = job_extractor.extractorData(pymupdf.open(jd_path), "pdf")

        # Calculate matching percentage
        match_percentage = obj_jd_profile_comparison.match(str(job_desc), resume_txt[5])

        # Add matching percentage to resume data
        resume_data['Matching Percentage'] = str(match_percentage)

        # Return the JSON response
        return jsonify(resume_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up temporary files
        os.remove(resume_path)
        os.remove(jd_path)

if __name__ == '__main__':
    # app.run(debug=True)
    app.run()