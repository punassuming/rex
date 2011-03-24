#!/usr/bin/env python

# settings for use with all modules to allow Global variables between classes
#
import os

HEADER_ROW = 3
DATA_BEGIN = 5
if os.environ.get('SYSTEMROOT'):
    EXPERIMENT_DB = 'F:\\Data\\experiment.xls'
else:
    EXPERIMENT_DB = '/home/walesi/data/experiment.xls'

# From experiment 11
PBR_VOID_SPACE = 0.112
# Empty Reactor experiments
PBR_BLANKS = [11,37,62]
