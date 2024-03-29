import argparse
import os
from time import sleep

import infolog
import tensorflow as tf
from hparams import hparams
from infolog import log
from tacotron.synthesize import tacotron_synthesize
from tacotron.train import tacotron_train

log = infolog.log


def save_seq(file, sequence, input_path):
	'''Save Tacotron-2 training state to disk. (To skip for future runs)
	'''
	sequence = [str(int(s)) for s in sequence] + [input_path]
	with open(file, 'w') as f:
		f.write('|'.join(sequence))

def read_seq(file):
	'''Load Tacotron-2 training state from disk. (To skip if not first run)
	'''
	if os.path.isfile(file):
		with open(file, 'r') as f:
			sequence = f.read().split('|')

		return [bool(int(s)) for s in sequence[:-1]], sequence[-1]
	else:
		return [0, 0, 0], ''

def prepare_run(args):
	modified_hp = hparams.parse(args.hparams)
	os.environ['TF_CPP_MIN_LOG_LEVEL'] = str(args.tf_log_level)
	#os.environ['CUDA_VISIBLE_DEVICES'] = ''
	run_name = args.name or args.model
	log_dir = os.path.join(args.base_dir, 'logs-{}'.format(run_name))
	os.makedirs(log_dir, exist_ok=True)
	infolog.init(os.path.join(log_dir, 'Terminal_train_log'), run_name, args.slack_url)
	return log_dir, modified_hp

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--base_dir', default='')
	parser.add_argument('--hparams', default='',
		help='Hyperparameter overrides as a comma-separated list of name=value pairs')
	parser.add_argument('--tacotron_input', default='training_data/train.txt')
	parser.add_argument('--wavenet_input', default='tacotron_output/gta/map.txt')
	parser.add_argument('--name', help='Name of logging directory.')
	parser.add_argument('--model', default='Tacotron')
	parser.add_argument('--input_dir', default='training_data', help='folder to contain inputs sentences/targets')
	parser.add_argument('--output_dir', default='output', help='folder to contain synthesized mel spectrograms')
	parser.add_argument('--mode', default='synthesis', help='mode for synthesis of tacotron after training')
	parser.add_argument('--GTA', default='True', help='Ground truth aligned synthesis, defaults to True, only considered in Tacotron synthesis mode')
	parser.add_argument('--restore', type=bool, default=True, help='Set this to False to do a fresh training')
	parser.add_argument('--summary_interval', type=int, default=250,
		help='Steps between running summary ops')
	parser.add_argument('--checkpoint_interval', type=int, default=500,
		help='Steps between writing checkpoints')
	parser.add_argument('--eval_interval', type=int, default=500,
		help='Steps between eval on test data')
	parser.add_argument('--tacotron_train_steps', type=int, default=200000, help='total number of tacotron training steps')
	parser.add_argument('--wavenet_train_steps', type=int, default=1300000, help='total number of wavenet training steps')
	parser.add_argument('--tf_log_level', type=int, default=1, help='Tensorflow C++ log level.')
	parser.add_argument('--slack_url', default=None, help='slack webhook notification destination link')
	args = parser.parse_args()

	log_dir, hparams = prepare_run(args)

	tacotron_train(args, log_dir, hparams)

if __name__ == '__main__':
	#os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"  
	os.environ["CUDA_VISIBLE_DEVICES"] = "0,1,2,3"
	main()
