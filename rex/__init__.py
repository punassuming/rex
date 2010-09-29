#!/bin/env python

#import pylab as pl
import io
import curves
import type
from rex.experiment import *

__author__ = "Rich Alesi"

__license__ = "GPL"
__version__ = "0.4"
__maintainer__ = "Rich Alesi"
__email__ = "walesi@andrew.cmu.edu"
__status__ = "Processing"

"""
Naming Conventions
Type                            Convention
function                        action_with_underscores
variable                        noun_with_underscores
constant                        NOUN_ALL_CAPS
class                           MixedCaseNoun
public property                 MixedCaseNoun
private property                _noun_with_leading_underscore
public method                   mixedCaseExceptFirstWordVerb
private method                  _verb_with_leading_underscore
really private data             __two_leading_underscores
parameters that match properties    SameAsProperty
factory function                MixedCase
module                          lowercase_with_underscores
global variables                gMixedCaseWithLeadingG
"""

# Global Functions

# CONSTANTS
#
HEADER_ROW = 3
DATA_BEGIN = 5
EXPERIMENT_DB = '/home/walesi/data/experiment.xls'


