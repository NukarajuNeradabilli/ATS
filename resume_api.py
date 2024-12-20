from flask import Flask, request, jsonify
from resumeExtraction import resumeExtraction
from job_extraction import job_extraction
from jd_profile_comparison import jd_profile_comparison
from pyresparser import ResumeParser
from uuid import uuid4
import pymupdf
import os
import threading

app = Flask(__name__)
resumeExtractor = resumeExtraction()
job_extractor = job_extraction()
obj_jd_profile_comparison = jd_profile_comparison()

lock = threading.Lock()  # To manage concurrent access to shared resources

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

processed_resumes = []  # List to track resumes added in POST requests

@app.route('/')
def get_working():
    return jsonify({"message": "API is working fine"}), 200

@app.route('/candidates', methods=['POST', 'GET'])
def process_resume():
    global processed_resumes

    try:
        ensure_directory_exists('static/resumes')
        ensure_directory_exists('static/Job_Description')
        
        if request.method == 'POST':
            if 'resumes' not in request.files or 'job_description' not in request.files:
                return jsonify({"error": "Please upload resume files and a job description file"}), 400
            
            resumes = request.files.getlist('resumes')
            jd_file = request.files['job_description']
            jd_path = 'static/Job_Description/temp_job_description.pdf'
            jd_file.save(jd_path)
            
            results = []
            try:
                job_desc = job_extractor.extractorData(pymupdf.open(jd_path), "pdf")
                for resume_file in resumes:
                    if not resume_file.filename.endswith('.pdf'):
                        results.append({
                            "Resume Filename": resume_file.filename,
                            "Error": "Only PDF files are allowed"
                        })
                        continue
                    resume_path = f'static/resumes/{resume_file.filename}'
                    resume_file.save(resume_path)
                    
                    try:
                        resume_data = ResumeParser(resume_path).get_extracted_data()
                        resume_txt = resumeExtractor.extractorData(pymupdf.open(resume_path), "pdf")
                        match_percentage = obj_jd_profile_comparison.match(str(job_desc), resume_txt[5])
                        resume_data['Matching Percentage'] = str(match_percentage)
                        resume_id = str(uuid4())
                        
                        with lock:  # Lock to ensure thread-safe access
                            processed_resumes.append({"Id": resume_id, "Resume Data": resume_data})
                        
                        results.append({"Id": resume_id, "Resume Data": resume_data})
                    except Exception as resume_error:
                        results.append({
                            "Resume Filename": resume_file.filename,
                            "Error": str(resume_error)
                        })
                    finally:
                        os.remove(resume_path)
                return jsonify({"POST Response": results}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
            finally:
                os.remove(jd_path)
        
        elif request.method == 'GET':
            with lock:  # Lock to ensure thread-safe access
                if not processed_resumes:
                    return jsonify({"message": "No new resumes to process"}), 200
                
                # Return and delete all processed resumes
                unique_resumes = processed_resumes[:]
                processed_resumes.clear()  # Clear after serving
                return jsonify({"GET Response": unique_resumes}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
