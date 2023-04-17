import os
import librosa
import numpy as np
import torch
import pickle
from torch.utils.data import Dataset
from IPython.display import Audio, display


LABELS = ['yes', 'no', 'up', 'down', 'left', 'right', 'on', 'off', 'stop', 'go']


class SpeechDataset(Dataset):
    
    def __init__(self, data_dir='train\\audio', labels=LABELS, labels_path='train\\testing_list.txt'):
        self.data_dir = data_dir
        self.labels_path = labels_path
        self.labels = labels
        self.labels_dict = {label: i for i, label in enumerate(self.labels)}
        self.file_paths = []
        self.labels_int = []
        self.sr = 16000
        self.duration = 1 
        
        with open(labels_path, "r") as f:
            lines = f.readlines()
        self.file_paths = [line.strip() for line in lines]
        for file in self.file_paths:
            label = file.split('/')[0]
            if label in self.labels:
                self.labels_int.append(self.labels_dict[label])
            else:
                self.labels_int.append(len(self.labels))
    
    def __len__(self):
        return len(self.file_paths)
    
    def __getitem__(self, idx):
        file_path = self.file_paths[idx]
        label = self.labels_int[idx]
        
        audio, sr = librosa.load(os.path.join(self.data_dir, file_path), sr=self.sr, duration=self.duration, mono=True)
        
        audio = torch.FloatTensor(audio)
        
        label = torch.LongTensor([label])
        
        return audio, label
    
    def listen_to_random_sample(self, sample_size=1):
        sample = np.random.randint(0, len(self), sample_size)
        for idx in sample:
            audio, label = self[idx]
            if label == len(self.labels):
                print('Label: unknown')
            else:
                print('Label:', self.labels[label])
            display(Audio(audio, rate=self.sr))

class ProcessedSpeechDataset(Dataset):
    
    def __init__(self, feature_list='features_training.pkl', labels=LABELS):
        self.feature_list = feature_list
        self.labels = labels
        self.features = None
        self.labels_dict = {label: i for i, label in enumerate(self.labels)}
        
        with open(feature_list, "rb") as f:
            self.features = pickle.load(f)

    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        feature = self.features[idx]
        
        audio = torch.FloatTensor(feature[0])
        
        if feature[1] in self.labels_dict:
            label = torch.LongTensor([self.labels_dict[feature[1]]])
        else:
            label = torch.LongTensor([len(self.labels)])
        
        return audio, label



training_dataset = SpeechDataset(labels_path='train\\testing_list.txt')
validation_dataset = SpeechDataset(labels_path='train\\validation_list.txt')
training_dataloader = torch.utils.data.DataLoader(training_dataset, batch_size=1, shuffle=True)
validation_dataloader = torch.utils.data.DataLoader(validation_dataset, batch_size=1, shuffle=True)

processed_training_dataset = ProcessedSpeechDataset(feature_list='features_training.pkl')
processed_validation_dataset = ProcessedSpeechDataset(feature_list='features_validation.pkl')

if __name__=='__main__':
    dataset = SpeechDataset('train\\audio')
    print(len(dataset))
    dataset.listen_to_random_sample()