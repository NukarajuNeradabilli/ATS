import gensim
from nltk.tokenize import word_tokenize
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import torch
import pickle
import numpy as np

class jd_profile_comparison:
    def __init__(self):
        pass
      
    #Mean Pooling - Take attention mask into account for correct averaging
    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0] #First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


    def get_HF_embeddings(self,sentences):

      # Load model from HuggingFace Hub
      tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-mpnet-base-v2')
      model = AutoModel.from_pretrained('sentence-transformers/all-mpnet-base-v2')
      # Tokenize sentences
      encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt', max_length=512)
      # Compute token embeddings
      with torch.no_grad():
          model_output = model(**encoded_input)
      # Perform pooling. In this case, max pooling.
      embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])

      # print("Sentence embeddings:")
      # print(embeddings)
      return embeddings

    def cosine(self, embeddings1, embeddings2):
        # get the match percentage
        matchPercentage = cosine_similarity(embeddings1.detach().numpy(), embeddings2.detach().numpy())
        matchPercentage = np.round(matchPercentage * 100, 4)  # round to two decimal
        return matchPercentage[0][0]
    
    def match(self, job_desc, resume_text):
        # Get embeddings for both job description and resume
        job_desc_embeddings = self.get_HF_embeddings([job_desc])
        resume_embeddings = self.get_HF_embeddings([resume_text])
        # Calculate cosine similarity and return the matching percentage
        match_percentage = self.cosine(resume_embeddings, job_desc_embeddings)
        return match_percentage

obj_jd_profile_comparison = jd_profile_comparison()
# pickle.dump(obj_jd_profile_comparison,open("jd_profile_comparison.pkl","wb"))