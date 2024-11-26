import requests   
from flask import Flask, request, jsonify, url_for
import json
import fitz
import pymupdf
from pyresparser import ResumeParser
from uuid import uuid4 
from resumeExtraction import resumeExtraction
from job_extraction import job_extraction
from jd_profile_comparison import jd_profile_comparison
import os

app = Flask(__name__)
resumeExtractor = resumeExtraction()
job_extractor = job_extraction()
obj_jd_profile_comparison = jd_profile_comparison()

# In-memory storage for simplicity (use a database for production)
processed_resumes = {}

@app.route('/working')
def get_working():
    return "Working"


@app.route('/candidates', methods=['POST'])
def process_resume():
    if 'resume' not in request.files or 'job_description' not in request.files:
        return jsonify({"error": "Please upload both resume and job description files"}), 400
    
    resume_file = request.files['resume']
    jd_file = request.files['job_description']
    
    if not os.path.exists('static/resumes'):
        os.makedirs('static/resumes')
    if not os.path.exists('static/Job_Description'):
        os.makedirs('static/Job_Description')   
   
    
    # Save the uploaded files to temporary locations    
    resume_path = 'static/resumes/temp_resume.pdf'
    jd_path = 'static/Job_Description/temp_job_description.pdf'
    resume_file.save(resume_path)
    jd_file.save(jd_path)
    try:
        resume_data = ResumeParser(resume_path).get_extracted_data()
        resume_txt = resumeExtractor.extractorData(pymupdf.open(resume_path), "pdf")
        job_desc = job_extractor.extractorData(pymupdf.open(jd_path), "pdf")
        match_percentage = obj_jd_profile_comparison.match(str(job_desc), resume_txt[5])
        resume_data['Matching Percentage'] = str(match_percentage)
        
        
        resume_id = str(uuid4())
        processed_resumes[resume_id] = resume_data
        
        with open(f'static/json/{resume_id}.json', 'w') as f:
            json.dump(resume_data, f)
        return jsonify({"Id": resume_id, "POST Response": resume_data}), 200 

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(resume_path)
        os.remove(jd_path)
    
        
@app.route('/candidates/all', methods=['GET'])
def get_candidates(): 
    resumes = []   
    try: 
        resume_dir = 'static/json'
        for filename in os.listdir(resume_dir):
            if filename.endswith('.json'):
                with open(os.path.join(resume_dir, filename), 'r') as f:
                    data = json.load(f)
                    resumes.append(data)
        return jsonify(resumes), 200 
    except FileNotFoundError:
        return jsonify({"error": "Candidates not found"}), 404


@app.route('/candidates/<string:resume_id>', methods=['GET'])
def get_candidate(resume_id):
    try: 
        with open(f'static/json/{resume_id}.json', 'r') as f: 
            data = json.load(f)
        return jsonify(data), 200 
    except FileNotFoundError:
        return jsonify({"error": "Candidate not found"}), 404


@app.route('/candidates/<string:resume_id>', methods=['PUT'])
def update_candidate(resume_id):
    try: 
        resume_path = f'static/json/{resume_id}.json'
        if not os.path.exists(resume_path):
            return jsonify({"error": "Candidate not found"}), 404
        
        updated_data = request.get_json()
        
        with open(resume_path, 'r') as f:
            resume_data = json.load(f) 
        
        resume_data.update(updated_data) 
        
        with open(resume_path, 'w') as f:
            json.dump(resume_data, f)
            
        return jsonify({"Id": resume_id, "Updated Response": resume_data}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/candidates/<string:resume_id>', methods=['DELETE'])
def delete_candidate(resume_id):
    try: 
        resume_path = f'static/json/{resume_id}.json'
        if not os.path.exists(resume_path):
            return jsonify({"error": "Candidate not found"}), 404
        os.remove(resume_path)
        return jsonify({"message": "Candidate deleted successfully"}), 200
    except: 
        return jsonify({"error": "Failed to delete candidate"}), 500

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=8000)