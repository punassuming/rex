#!/usr/bin/env python

# settings for use with all modules to allow Global variables between classes
#
import os

HEADER_ROW = 3
KEY_ROW = 4
DATA_BEGIN = 6

if os.environ.get('SYSTEMROOT'):
    DATA_DIR = 'F:\\Documents\\data'
    EXPERIMENT_DB = 'F:\\Documents\\projects\\_figures\\experiment.xls'
else:
    DATA_DIR = '/home/walesi/data'
    EXPERIMENT_DB = '/home/walesi/projects/_figures/experiment.xls'

# From experiment 11
PBR_VOID_SPACE = 0.112
# Empty Reactor experiments
PBR_BLANKS = [11,37,62]
