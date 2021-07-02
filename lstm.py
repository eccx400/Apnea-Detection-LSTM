
import os
import numpy as np
import csv
from dataloader import ApneaDataloader

import torch
from torch import nn
from torch.optim import Adam
from torch.optim.lr_scheduler import ReduceLROnPlateau

import matplotlib.pyplot as plt
import argparse
from datetime import datetime

np.set_printoptions(suppress=True) # don't use scientific notation


'''LSTM model to classify time series signals as apnea/non-apnea events'''

class LSTM_Module(nn.Module):
    
    def __init__(self,input_dim,hidden_dim,num_layers,timesteps,output_dim=1):
        super(LSTM_Module,self).__init__()
        self.input_dim  = input_dim     # timesteps
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers 
        self.output_dim = output_dim
        self.timesteps = timesteps
        self.lstm = nn.LSTM(input_dim,hidden_dim,num_layers,dropout=0.2)
        self.fc = nn.Linear(hidden_dim,output_dim)
        self.softmax = nn.Softmax(dim=-1)
        # hidden_dim -> output_dim
        # self.bn = nn.BatchNorm1d(self.timesteps)
        
    def forward(self,inputs):
        # x = self.bn(inputs)
        output, _ = self.lstm(inputs)
        #print("Output of LSTM: ", output.shape)
        output = self.fc(output)
        # print("after fc", output.shape)
        output = self.softmax(output)
        # print("after sm", output)
        output = output.permute(1,0,2) # 120, 64, 1
        output = output[:,-1,0]
        return output

# batch_size = 10
# n_timesteps = 128
# n_outputs = 1
# input = torch.randn(batch_size, n_timesteps, n_outputs)
# n_layers = 3
# n_hidden = 64
# lstm = LSTM(1,n_hidden,n_layers,n_outputs).to(device)
# # batch_size, seq_len,hidden_dim -> batch_size, seq_len, 1
# lstm(input)




    
class LSTM:
    def __init__(self, root_dir, dataset, apnea_type, excerpt, batch_size, epochs):
        # hyper-parameters
        self.init_lr = 0.01
        self.decay_factor = 0.7
        self.pos_pred_threshold = 0.7

        self.dataset = dataset
        self.apnea_type = apnea_type
        self.excerpt = excerpt
        self.batch_size = batch_size
        self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')



        # directories 
        self.root_dir = root_dir

        self.data_root = os.path.join(self.root_dir, "data/")
        self.results_root = os.path.join(self.root_dir, "results/")

        self.save_model_root = os.path.join(self.root_dir, "saved_models/")
        self.epochs = epochs

        # dataset 
        self.data = ApneaDataloader(self.data_root,self.dataset,self.apnea_type,self.excerpt, self.batch_size)
        self.train_loader = self.data.get_train()
        self.test_loader = self.data.get_test()

        self.num_train = len(self.data.train_data)
        self.num_test = len(self.data.test_data)
        print('Train dataset size: ', self.num_train)
        print('Test dataset size: ', self.num_test)

        
        # Model 
        n_timesteps = self.data.dataset.timesteps 
        n_outputs = 2
        n_layers = 3
        n_hidden = 64
        self.model = LSTM_Module(1,n_hidden,n_layers,n_timesteps,n_outputs).double()
        self.model.to(self.device)

        # Loss 
        self.criterion = nn.BCELoss()
        # Optimizer
        self.optim = Adam(self.model.parameters(), lr=self.init_lr)
        # LR scheduler 
        self.scheduler = ReduceLROnPlateau(self.optim, 'min',  factor=self.decay_factor, patience=2)
        
        self.save_base_path = f"{self.save_model_root}{self.dataset}/excerpt{self.excerpt}/{self.dataset}_{self.apnea_type}_ex{self.excerpt}_ep{self.epochs}_b{self.batch_size}_lr{self.init_lr}" 

        if not os.path.isdir(self.save_base_path):
            os.makedirs(self.save_base_path)
        self.save_model_path = self.save_base_path + ".ckpt"

    def train(self, save_model=False):
        self.model.train()
        training_losses = []
        training_errors = []
        for epoch in range(self.epochs):
            print(f"epoch #{epoch}")
            train_loss = 0.0
            train_errors = 0.0

            for n_batch, (seq, label, file) in enumerate(self.train_loader):
                self.optim.zero_grad()
            
                seq = seq.permute(1,0,2)
                
                pred = self.model(seq).unsqueeze(-1).double() # bs x 1 
                label = label.unsqueeze(-1).double()
            
                loss = self.criterion(pred.double(), label.double())

                train_loss += loss.item()
                # writer.add_scalar("Loss/train", train_loss, epoch)
                pred_bin = torch.where(pred > self.pos_pred_threshold, 1, 0)
                N = len(pred)
                errs = torch.count_nonzero(pred_bin - label)
                err_rate = errs/N
                train_errors += err_rate

                
                loss.backward()
                self.optim.step() 
                self.scheduler.step(loss)
                if (n_batch) % 5 == 0:
                    print("Epoch: [{}/{}], Batch: {}, Loss: {}, Acc: {}".format(
                        epoch, self.epochs, n_batch, loss.item(), 1-err_rate))

            # writer.flush()
            # append training loss for each epoch 
            training_losses.append(train_loss/n_batch) 
            training_errors.append(train_errors/n_batch)      
            print(f"Loss for epoch {epoch}: {train_loss/n_batch}")
        

        self.train_loss = train_loss # last train loss
        # Visualize loss history
        plt.plot(range(self.epochs), training_losses, 'r--')
        plt.plot(range(self.epochs), training_errors, 'b-')

        plt.legend(['Training Loss', 'Training error'])
        plt.xlabel('Epoch')
        plt.ylabel('Metric')
        # save model
        plt.savefig(self.save_base_path + ".png")
        plt.show()

        if save_model:
            print("Saving to... ", self.save_model_path)
            torch.save(self.model.state_dict(), self.save_model_path)

        print('Finished training')
        # return self.save_model_path, training_losses[-1]

    #     ############################################################################
    # def test(self):
    
    #     # load trained model
    #     self.model.load_state_dict(torch.load(self.save_model_path))
        # begin test 
        self.model.eval()
        test_losses = []
        test_errors = []
        print("Testing")
        with torch.no_grad():
            
            for n_batch, (seq, label, file) in enumerate(self.test_loader):
                seq = seq.permute(1,0,2)
                pred = self.model(seq).unsqueeze(-1).double() # bs x 1 
                label = label.unsqueeze(-1).double()

                loss = self.criterion(pred.double(), label.double())

                test_losses += [loss.item()]
                pred_bin = torch.where(pred > 0.5, 1, 0)
                N = len(pred)

                errs = torch.count_nonzero(pred_bin - label)
                err_rate = errs/N
                test_errors.append(err_rate)
                if n_batch % 5 == 0:
                    # np.savetxt(f"{self.save_base_path}test_batch{n_batch}.csv", np.hstack((pred.detach().numpy(), pred_bin.detach().numpy(), label.detach().numpy())), delimiter=",")
                    print(f"batch #{n_batch} loss: {loss.item()}, acc: {1-err_rate}")

            print('n_batch', n_batch)
            self.avg_test_error = np.mean(test_errors)
            print(f"Average test accuracy: {1-self.avg_test_error}")



        # write new row to log.txt 
        results_file = self.results_root + "results.csv"
        file_relpath = os.path.relpath(results_file, self.root_dir)
        with open(results_file, 'a', newline='\n') as results:
            fieldnames = ['time','dataset','apnea_type','excerpt', \
                      'file','test_acc','n_train','n_test','epochs']
            writer = csv.DictWriter(results, fieldnames=fieldnames)
            print('Writing row....\n')
            time_format = '%m/%d/%Y %H:%M %p'
            writer.writerow({'time': datetime.now().strftime(time_format),
                            'dataset': self.dataset,
                            'apnea_type': self.apnea_type,
                            'excerpt': self.excerpt,
                            # 'sample_rate': self.sample_rate,
                            # 'scale_factor': self.scale_factor,
                            'test_acc': 1-self.avg_test_error,
                            'file': file_relpath,
                            'n_train': self.num_train,
                            'n_test': self.num_test,
                            'epochs': self.epochs})

        return self.train_loss, self.avg_test_error


# l = LSTM('dreams','osa',1,64, 10)
# # l.train()
# l.test()