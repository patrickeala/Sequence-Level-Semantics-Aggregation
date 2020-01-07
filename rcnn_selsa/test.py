# --------------------------------------------------------
# Sequence Level Semantics Aggregation
# Copyright (c) 2016 by Contributors
# Copyright (c) 2017 Microsoft
# Copyright (c) 2019 by Contributors
# Licensed under The Apache-2.0 License [see LICENSE for details]
# Modified by Yuwen Xiong
# Modified by Haiping Wu
# --------------------------------------------------------
#ADDING TEST
import _init_paths

import cv2
import argparse
import os
import sys
import time
import logging
from config.config import config, update_config


def parse_args():
    parser = argparse.ArgumentParser(description='Test a Faster R-CNN network')
    # general
    parser.add_argument('--cfg', help='experiment configure file name', required=True, type=str)

    args, rest = parser.parse_known_args()
    update_config(args.cfg)

    # rcnn
    parser.add_argument('--vis', help='turn on visualization', action='store_true')
    parser.add_argument('--ignore_cache', help='ignore cached results boxes', action='store_true')
    parser.add_argument('--thresh', help='valid detection threshold', default=1e-3, type=float)
    parser.add_argument('--shuffle', help='shuffle data on visualization', action='store_true')
    parser.add_argument('--sample-stride', help='sample stride', default=-1, type=int)
    parser.add_argument('--key-frame-interval', help='key frame interval', default=-1, type=int)
    parser.add_argument('--video-shuffle', help='video shuffle', action='store_true')
    parser.add_argument('--test-pretrained', help='test pretrained model', type=str)
    args = parser.parse_args()
    return args


args = parse_args()
curr_path = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(curr_path, '../external/mxnet', config.MXNET_VERSION))

import mxnet as mx
from function.test_rcnn import test_rcnn
from utils.create_logger import create_logger

def main():
    ctx = [mx.gpu(int(i)) for i in config.gpus.split(',')]
    print(args)

    if args.sample_stride != -1:
        config.TEST.sample_stride = args.sample_stride
    if args.key_frame_interval != -1:
        config.TEST.KEY_FRAME_INTERVAL = args.key_frame_interval
    if args.video_shuffle:
        config.TEST.video_shuffle = args.video_shuffle


    logger, final_output_path, tb_log_path = create_logger(config.output_path, config.log_path, args.cfg,
                                                           config.dataset.test_image_set)

    trained_model = os.path.join(final_output_path, '..', '_'.join(
        [iset for iset in config.dataset.image_set.split('+')]),
                                 config.TRAIN.model_prefix)
    test_epoch = config.TEST.test_epoch
    if args.test_pretrained:
        trained_model = args.test_pretrained
        test_epoch = 0

    test_rcnn(config, config.dataset.dataset, config.dataset.test_image_set, config.dataset.root_path,
              config.dataset.dataset_path, config.dataset.motion_iou_path,
              ctx,
              trained_model,
              test_epoch,
              args.vis, args.ignore_cache, args.shuffle, config.TEST.HAS_RPN, config.dataset.proposal, args.thresh,
              logger=logger, output_path=final_output_path,
              enable_detailed_eval=config.dataset.enable_detailed_eval)


if __name__ == '__main__':
    main()
