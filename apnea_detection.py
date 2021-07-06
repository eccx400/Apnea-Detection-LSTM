import argparse
from onset_detection import OnsetDetection
from train import Model
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import plotly
from plotly.subplots import make_subplots

import wandb 

'''
Program to run end-to-end onset detection (non-GUI)
To view args: python3 apnea_detection.py -h 
Example command: python3 apnea_detection.py -d dreams -a osa -ex 1 -sr 8 -sc 1 -b 64 -ep 10
'''
def main(args):
    print('********************************')
    print(f'****  Dataset: {args.dataset}  ****')
    print(f'****  Apnea type: {args.apnea_type}  ****')
    print(f'****  Excerpt: {args.excerpt}  ****')
    print(f'****  Sample rate: {args.sample_rate}  ****')
    print(f'****  Scale factor: {args.scale_factor}  ****')
    print('*********************************')

    if args.logger: 
        config = args
        tags = [args.dataset, args.apnea_type, args.excerpt]
        if 'Box' in args.excerpt:
            tags.append('box')
        wandb.init(project="apnea_detection", 
                config=config,
                tags=tags)

   
        wandb.run.name = f'{args.dataset}_{args.apnea_type}_{args.excerpt}'
        wandb.run.save()
    else:
        config = None

    if args.preprocess: 
        # visualize original data
        od = OnsetDetection(root_dir=".",
                            dataset=args.dataset,
                            apnea_type=args.apnea_type,
                            excerpt= args.excerpt,
                            sample_rate=args.sample_rate,
                            scale_factor=args.scale_factor)

        # print('----------------Visualize original signal--------------------')

        # fig = od.visualize()
        # print('----------------Plot detected onset, nononset events ------------------')


        onset_fig, onset_times, nononset_fig, nononset_times = od.annotate_events(float(args.threshold))
        # fig = make_subplots(rows=2, cols=1)

        # for i in range(len(onset_fig['data'])):
        #     fig.add_trace(onset_fig['data'][i], row=1, col=1)
        # for i in range(len(nononset_fig['data'])):
        #     fig.add_trace(nononset_fig['data'][i], row=2, col=1)
        # fig.show()
        od.output_apnea_files(onset_times, nononset_times)

    print('----------------Train and test -------------------')

    model = Model(root_dir=args.root_dir, 
                dataset=args.dataset,
                apnea_type=args.apnea_type,
                excerpt=args.excerpt,
                batch_size=int(args.batch_size),
                epochs=int(args.epochs),
                config=config)

    train_losses, val_losses, final_val_acc = model.train(save_model=False,
                                                                plot_loss=False)

    wandb.finish()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--root_dir",    default=".", help="root directory (parent folder of data/)")
    parser.add_argument("-d", "--dataset",    default="dreams", help="dataset (dreams, dublin, or mit)")
    parser.add_argument("-a", "--apnea_type", default="osa",    help="type of apnea (osa, osahs, or all)")
    parser.add_argument("-ex","--excerpt",        help="excerpt number to use")
    parser.add_argument("-sr","--sample_rate",    default=8,        help="number of samples per second")
    parser.add_argument("-sc","--scale_factor",    default=1,        help="scale factor for normalization")
    parser.add_argument("-b","--batch_size",    default=16,        help="batch size")    
    parser.add_argument("-ep","--epochs",    default=15,        help="num epochs to train")
    parser.add_argument("-th","--threshold",       help="flatline detection threshold")
    parser.add_argument("-p", "--preprocess",  default=False,  help="only train/test, no need to extract flatline/create + and - files", action='store_true')
    parser.add_argument("-l", "--logger",  default=False,   help="log run", action='store_true')


    # parse args 
    args = parser.parse_args()

    main(args)
