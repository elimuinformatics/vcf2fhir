import pandas as pd
from collections import OrderedDict
import numpy as np
import re
from itertools import cycle
import logging
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s -%(message)s', datefmt='%d-%b-%y %H:%M')


def _getSequenceRelation(phasedRecMap):
    RelationTable= pd.DataFrame(columns=['POS1','POS2','Relation'])
    for key in phasedRecMap:
        prev_record = None
        for record in phasedRecMap[key]:
            if prev_record is None:
                prev_record = record
                continue
            prev_data = prev_record.samples[0].data
            record_data = record.samples[0].data
            if(prev_data.PS == record_data.PS):
                if prev_data.GT == record_data.GT:
                    RelationTable = RelationTable.append({'POS1': prev_record.POS, 'POS2': record.POS, 'Relation': 'Cis'}, ignore_index=True)
                else:
                    RelationTable = RelationTable.append({'POS1': prev_record.POS, 'POS2': record.POS, 'Relation': 'Trans'}, ignore_index=True)
            prev_record = record
    return RelationTable 

def _addPhaseRecords(f, phasedRecMap):
    if(f.samples[0].phased == False):
        return 
    sampleData = f.samples[0].data
    if(sampleData.GT != None and len(sampleData.GT.split('|')) >= 2 and sampleData.PS != None):
        phasedRecMap.setdefault(sampleData.PS, []).append(f)
