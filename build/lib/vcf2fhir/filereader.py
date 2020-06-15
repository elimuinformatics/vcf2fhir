import os
import pandas as pd
import re
import numpy as np
from itertools import cycle
from .common import *
pd.options.mode.chained_assignment = None

def getNoCallableData(NO_CALL_FILE,QUERY_RANGE_FILE):
    rawNoCallData = pd.read_csv(NO_CALL_FILE,sep='\t',names=["CHROM","START","END","COVERAGE"])
    queryRange = pd.read_csv(QUERY_RANGE_FILE,sep='\t',names=["CHROM","START","END"])

    return rawNoCallData,queryRange