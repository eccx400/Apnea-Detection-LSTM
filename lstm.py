'''LSTM model to classify time series signals as apnea/non-apnea events'''
import torch
from torch import nn

class LSTM(nn.Module):
    
    def __init__(self,input_size=1, 
                    hidden_size=64,
                    num_layers=4,
                    output_dim=2,
                    dropout=0.1):
        super(LSTM,self).__init__()

        self.lstm = nn.LSTM(input_size,hidden_size,num_layers,dropout=dropout,batch_first=True)
        self.relu = nn.ReLU(hidden_size)
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size, output_dim,)
        self.softmax = nn.Softmax(-1)
        
    def forward(self,inp):
        x, _ = self.lstm(inp)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc(x)
        x = x[:, -1, :].squeeze()
        x = self.softmax(x)
        return x