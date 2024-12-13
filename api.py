from flask import Flask, request, jsonify
from resumeExtraction import resumeExtraction
from job_extraction import job_extraction
from jd_profile_comparison import jd_profile_comparison
from pyresparser import ResumeParser
from uuid import uuid4
import pymupdf
import tempfile 
import base64 
import json
import os

app = Flask(__name__)
resumeExtractor = resumeExtraction()
job_extractor = job_extraction()
obj_jd_profile_comparison = jd_profile_comparison()

@app.route('/')
def get_working():
    return "API is working fine"

processed_resumes = {}

@app.route('/candidates', methods=['POST', 'GET'])
def process_resume():
    try:  
        if request.method == 'POST':
            data = request.get_json() 
            if not data: 
                return jsonify({"error": "Invalid or missing JSON data"}), 400  
            
            resumes_folder_path = data.get('resumes_folder_path')
            job_description_path = data.get('job_description_path')
            
            if not resumes_folder_path:
                return jsonify({"error": "Missing resumes_folder_path"}), 400
            if not os.path.exists(resumes_folder_path) or not os.path.isdir(resumes_folder_path):
                return jsonify({"error": f"Folder path '{resumes_folder_path}' does not exist or is not a directory"}), 400
            
            if not job_description_path:
                return jsonify({"error": "Missing job_description_path"}), 400
            if not os.path.exists(job_description_path):
                return jsonify({"error": f"Path '{job_description_path}' does not exist"}), 400
            
            # is_job_description_folder = os.path.exists(job_description_path) 
            job_descriptions = []
            
            if os.path.isdir(job_description_path):
                job_descriptions = [
                    os.path.join(job_description_path, f) for f in os.listdir(job_description_path) if f.endswith('.pdf')
                ]
            elif job_description_path.endswith('.pdf'):
                job_descriptions.append(job_description_path)
            else:
                return jsonify({"error": f"Path '{job_description_path}' is not a folder or a valid PDF file"}), 400
            
            resumes = [
                os.path.join(resumes_folder_path, f) for f in os.listdir(resumes_folder_path) if f.endswith('.pdf')
            ]
            if not resumes:
                return jsonify({"error": "No valid PDF resumes found in the specified folder"}), 400
            
            results = [] 
            
            for jd_path in job_descriptions: 
                try: 
                    job_desc = job_extractor.extractorData(pymupdf.open(jd_path), "pdf")
                    for resume_path in resumes:
                        try: 
                            resume_data = ResumeParser(resume_path).get_extracted_data()
                            resume_txt = resumeExtractor.extractorData(pymupdf.open(resume_path), "pdf")
                            match_percentage = obj_jd_profile_comparison.match(str(job_desc), resume_txt[5])
                            resume_data['Matching Percentage'] = str(match_percentage)
                            resume_id = str(uuid4()) 
                            processed_resumes[resume_id] = resume_data
                            results.append({"Id": resume_id, "Resume Data": resume_data})
                            
                            # if os.path.exists(resume_path):
                            #     os.remove(resume_path)
                                
                        except Exception as e:
                            return jsonify({"error": f"Error processing resume '{resume_path}': {str(e)}"}), 500
                except Exception as e:
                    return jsonify({"error": f"Error processing job description '{jd_path}': {str(e)}"}), 500 
                
            return jsonify({"message": "Resumes processed successfully", "Results": results}), 200
        
        
        elif request.method == 'GET':
            seen = set()
            unique_resumes = {}
            
            for resume_id, resume in processed_resumes.items(): 
                
                name = str(resume.get('name', '')).strip() if resume.get('name') else ''
                email = str(resume.get('email', '')).strip() if resume.get('email') else ''
                mobile_number = str(resume.get('mobile_number', '')).strip() if resume.get('mobile_number') else ''

                unique_key = (name, email, mobile_number)
                
                if not any(unique_key):
                    continue

                if unique_key not in seen: 
                    seen.add(unique_key)
                    unique_resumes[resume_id] = resume 
                    
                    
            return jsonify({"Unique Resumes": unique_resumes}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500  

        
if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=8002)
    
    
    