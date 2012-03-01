import os
# Global Functions

# CONSTANTS
#
HEADER_ROW = 3
KEY_ROW = 4
DATA_BEGIN = 6

# From experiment 11
PBR_VOID_SPACE = 0.112
# Empty Reactor experiments
PBR_BLANKS = [11,37,62]

def EXPERIMENT_DB():
    if os.environ.get('SYSTEMROOT'):
        return 'F:\\Documents\\projects\\figures\\experiment.xls'
    else:
        return '/home/walesi/projects/figures/experiment.xls'

def DATA_DIR():
    if os.environ.get('SYSTEMROOT'):
        return 'F:\\Documents\\data'
    else:
        return '/home/walesi/data'

