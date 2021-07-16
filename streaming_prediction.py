
import os
import pandas as pd
import numpy as np
import csv
from dataloader import ApneaDataloader

from cnn import CNN
import torch
from torch import nn

import matplotlib.pyplot as plt
import argparse
from datetime import datetime
from scipy.stats import zscore
np.set_printoptions(suppress=True) # don't use scientific notation


def rolling_window(x, window_size, step_size=1):
    # unfold dimension to make our rolling window
    return x.unfold(0,window_size,step_size)

class StreamPrediction():
    def __init__(self, root_dir, dataset, apnea_type, excerpt, sample_rate, scale_factor):
        self.dataset = dataset
        self.apnea_type  = apnea_type
        self.excerpt   = excerpt
        self.sample_rate = int(sample_rate)
        self.scale_factor = int(scale_factor)

        # directories 
        self.root_dir = root_dir
        self.data_dir = os.path.join(self.root_dir, "data")
        self.info_dir = os.path.join(self.root_dir, "info")

        self.base_path = f"{self.data_dir}/{self.dataset}/preprocessing/excerpt{self.excerpt}/{self.dataset}_{self.apnea_type}_ex{self.excerpt}_sr{self.sample_rate}"
        # path to unnormalized, normalized files 
        self.in_file     = f"{self.base_path}_sc{self.scale_factor}.csv"
        # default parameters 
        self.seconds_before_apnea = 10
        self.seconds_after_apnea = 5

        self.timesteps = self.sample_rate * (self.seconds_before_apnea + self.seconds_after_apnea)

    def setup(self, model, save_model_path):
        # Set up sequence 
        self.df = pd.read_csv(self.in_file, delimiter=",")
        # self.df["Value"] = zscore(self.df["Value"])
        self.seq = torch.from_numpy(self.df["Value"].to_numpy())
        self.time = torch.from_numpy(self.df["Time"].to_numpy())

        # slide offset: 1 sec
        self.values = rolling_window(self.seq, self.timesteps, self.sample_rate*10).unsqueeze(-1)
        self.times = rolling_window(self.time, self.timesteps, self.sample_rate*10).unsqueeze(-1)


        self.seq_len = len(self.df)
        self.start = 0

        # Model
        self.model = model.double()
        self.model.load_state_dict(torch.load(save_model_path))
        
    def predict_next(self):
        batch_size = 4

        figure, axes = plt.subplots(nrows=1, ncols=4, figsize=(12,2), sharey=True)

        # batch windows, slide vertically 
        inp =  self.values[self.start:self.start + batch_size, :, :]
        pred = self.model(inp)
        pred_bin = pred_bin = torch.argmax(pred, dim=1)
        
        # plot 
        for i in range(batch_size):
            t = self.times[self.start+i, :, :]
            v = self.values[self.start+i, :, :]
            axes[i].plot(t.squeeze().numpy(), v.squeeze().numpy())
            axes[i].set_title(f'{pred_bin[i]}')
        plt.show()
        self.start += 4
        return pred_bin

        # curr_window = torch.Tensor(curr_window.to_numpy())
        # curr_window = curr_window.unsqueeze(0).unsqueeze(-1).double()

        # print(curr_window)
        # print(curr_window.shape)
        # pred, label = self.model(curr_window)
        # window_offset = self.sample_rate * 1 # Sample rate * num seconds
        # self.start += window_offset # shift one second 

        # # pd.options.plotting.backend = "plotly"
        # title = f"Pred: {pred}, label: {label}"
        # fig = curr_window.plot(x='Time', y="Value", title=title)
        # fig.show()

        # return pred, label


def main(args):
    sp = StreamPrediction(root_dir=".",
                        dataset=args.dataset,
                        apnea_type=args.apnea_type,
                        excerpt= args.excerpt,
                        sample_rate=args.sample_rate,
                        scale_factor=args.scale_factor)
    
    model =  CNN(input_size=1, \
                output_size=2).double()
    sp.setup(model=model, save_model_path='base_model.ckpt')
    
    while True:
        pred = sp.predict_next()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--root_dir",    default=".", help="root directory (parent folder of data/)")
    parser.add_argument("-d", "--dataset",    default="dreams", help="dataset (dreams, dublin, or mit)")
    parser.add_argument("-a", "--apnea_type", default="osa",    help="type of apnea (osa, osahs, or all)")
    parser.add_argument("-ex","--excerpt",    default=1,        help="excerpt number to use")
    parser.add_argument("-sr","--sample_rate",    default=10,        help="number of samples per second")
    parser.add_argument("-sc","--scale_factor",    default=10,        help="scale factor for normalization")

    # parse args 
    args = parser.parse_args()
    main(args)