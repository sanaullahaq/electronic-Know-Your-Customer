import onnx
import torch
import numpy as np
import onnxruntime
from PIL import Image
import torch as nn
from torchvision import transforms as trans
from sklearn.preprocessing import normalize

import cv2 
from PIL import Image 

class FaceModel:
    
    def __init__(self, face_bank_path = "checkpoints/facebank", init_facebank=False, 
                        new_arcface=False, arc_path="checkpoints/new_arcface/backbone_100.pth"):

        self.new_arcface = new_arcface
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.face_bank_path = face_bank_path
        self.test_transform = trans.Compose([
                            trans.ToTensor(),
                            trans.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
                        ])
        self.threshold = 0.93
        if init_facebank:
            self.names, self.facebank = None, None
        else:
            self.names, self.facebank = self.load_facebank(face_bank_path)
        self.ort_session = onnxruntime.InferenceSession(face_bank_path+"/arcface.onnx")
 
    
    def add_face(self, x_img, name, save_path=None):
        '''
            name : Name of the person (str)
            x_img: numpy RGB img list
        '''
        embedding = []
        for img in x_img:
            embeds = self.get_embeddings(img, save_path=save_path)
            embeds = torch.from_numpy(embeds)
            embedding.append(embeds)
            
        embedding = torch.cat(embedding).mean(0,keepdim=True)   
        if self.names is not None:
            names = np.array(self.names.tolist()+[name])
            embedding = torch.cat([self.facebank, embedding])
        else:
            names = np.array([name])
        torch.save(embedding, self.face_bank_path+'/facebank.pth')
        np.save(self.face_bank_path+'/names.npy', names)
        self.names, self.facebank = names, embedding
        print("Face Registered in the system")
        return True


    def load_facebank(self, path):
        embeddings = torch.load(self.face_bank_path+'/facebank.pth', map_location=self.device)
        names = np.load(self.face_bank_path+'/names.npy', allow_pickle=True)
        return names, embeddings
    
    def to_numpy(self,tensor):
        return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()
    
    
    def preprocess(self,x_image):
        x = self.test_transform(x_image).unsqueeze(0)
        return x
    
    def l2_norm(self, input,axis=1):
        norm = torch.norm(input,2,axis,True)
        output = torch.div(input, norm)
        return output
    
    def get_embeddings(self, x_image, save_path=None):
        """
            x_image     : numpy RGB image
        """
        if self.new_arcface:
            #x_image = cv2.cvtColor(x_image, cv2.COLOR_BGR2RGB)
            x_image = Image.fromarray(x_image)
            x_image = self.preprocess(x_image)
            # compute ONNX Runtime output prediction
            ort_inputs = {self.ort_session.get_inputs()[0].name: self.to_numpy(x_image)}
            ort_embeds = self.ort_session.run(None, ort_inputs)
            return ort_embeds[0]
        else:
            #x_image = cv2.cvtColor(x_image, cv2.COLOR_BGR2RGB)
            x_image = Image.fromarray(x_image)
            x_image = self.preprocess(x_image)
            # compute ONNX Runtime output prediction
            ort_inputs = {self.ort_session.get_inputs()[0].name: self.to_numpy(x_image)}
            ort_embeds = self.ort_session.run(None, ort_inputs)
            return ort_embeds[0]

    
    def infer(self,faces, save_path=None):
        '''
            faces       : list of numpy RGB image. eg: [im1,im2,im3]
            target_embs : [n, 512] computed embeddings of faces in facebank
            names       : recorded names of faces in facebank
        '''
        embs = []
        for img in faces:
            out = self.get_embeddings(img, save_path=save_path)
            out = torch.from_numpy(out)
            embs.append(out)
        source_embs = torch.cat(embs)
        norm_sorc_emb=self.l2_norm(source_embs)
        Normalize_f_bank = self.l2_norm(self.facebank) #516,512 
        diff = norm_sorc_emb.unsqueeze(-1) - Normalize_f_bank.transpose(1,0).unsqueeze(0)        
        dist = torch.sum(torch.pow(diff, 2), dim=1)
        minimum, min_idx = torch.min(dist, dim=1)
        if float(minimum) > self.threshold:
            return "unknown", float(minimum)
        else:  
            return self.names.tolist()[min_idx], float(minimum)

    def infer_with_selected_user(self,face, user_id, save_path=None):
        '''
            faces       : list of numpy RGB image. eg: [112,112,3]
        '''
        source_embs = self.get_embeddings(face, save_path=save_path)
        source_embs = torch.from_numpy(source_embs).view(-1)
        source_embs = self.l2_norm(source_embs,0)
        # getting the index of that user
        target_user = self.names.tolist().index(user_id)
        target_embs = self.facebank[target_user]
        target_embs = self.l2_norm(target_embs,0)
        dot_result = torch.dot(source_embs.view(-1), target_embs.view(-1)).numpy()
        #print("DOT", dot_result)
        diff = source_embs - target_embs
        dist = torch.sum(torch.pow(diff, 2), dim=0)
        if dot_result<=0:
            dot_result=0.
        else:
            dot_result = dot_result*100
        if float(dist) > self.threshold:
            return "unknown", float(dist), dot_result
        else:  
            return self.names.tolist()[target_user], float(dist), dot_result


    def face_varify(self,faces, target_embs):
        '''
            faces       : list of numpy RGB image. eg: [im1,im2,im3]
            target_embs : [n, 512] computed embeddings (tensor)
            names       : recorded names of faces in facebank
        '''
        embs = []
        for img in faces:
            out = self.get_embeddings(img)
            out = torch.from_numpy(out)
            embs.append(out)
        source_embs = torch.cat(embs)
        diff = source_embs.unsqueeze(-1) - target_embs.transpose(1,0).unsqueeze(0)
        dist = torch.sum(torch.pow(diff, 2), dim=1)
        minimum, min_idx = torch.min(dist, dim=1)
        min_idx[minimum > self.threshold] = -1 # if no match, set idx to -1
        if int(min_idx.tolist()[0]) == -1:
            return "Do Not Matched", minimum
        else:
            return "Matched", minimum
