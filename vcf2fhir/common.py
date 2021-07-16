import os
import datetime
import pandas as pd
import fhirclient.models.codeableconcept as concept
import pytz
import logging
import re
from collections import OrderedDict
from enum import Enum


general_logger = logging.getLogger("vcf2fhir.general")
SVs = {'INS', 'DEL', 'DUP', 'CNV', 'INV'}
VARIANT_COMPONENTS_ORDER = [
    'dna_change_type_component',
    'ref_seq_id_component', 'genomic_source_class_component',
    'allelic_state_component', 'allelic_frequency_component',
    'copy_number_component', 'ref_allele_component', 'alt_allele_component',
    'genomic_coord_system_component', 'exact_start_end_component',
    'outer_start_end_component', 'inner_start_end_component',
]
GERMLINE = 'Germline'
SOMATIC = 'Somatic'
MIXED = 'Mixed'
SVTYPE_TO_DNA_CHANGE_TYPE = {
    'CNV': ['SO:0001019', 'copy_number_variation'],
    'DUP': ['SO:1000035', 'duplication'],
    'INV': ['SO:1000036', 'inversion'],
    'DEL': ['SO:0000159', 'deletion'],
    'INS': ['SO:0000667', 'insertion']
}
GENOMIC_SOURCE_CLASS_TO_CODE = {
    GERMLINE: 'LA6683-2',
    SOMATIC: 'LA6684-0'
}

"""
/**
 * generates current date into fhir format
 * @return date
 */
"""


class Genomic_Source_Class(Enum):

    @classmethod
    def set_(cls):
        return set(map(lambda c: c.value, cls))

    GERMLINE = GERMLINE
    SOMATIC = SOMATIC
    MIXED = MIXED


def get_fhir_date():
    z = datetime.datetime.now(pytz.timezone(
        'UTC')).strftime("%Y-%m-%dT%H:%M:%S%z")
    return z[:-2] + ':' + z[-2:]


def get_sequence_relation(phased_rec_map):
    Relation_table = pd.DataFrame(columns=['POS1', 'POS2', 'Relation'])
    for key in phased_rec_map:
        prev_record = None
        for record in phased_rec_map[key]:
            if prev_record is None:
                prev_record = record
                continue
            prev_data = prev_record.samples[0].data
            record_data = record.samples[0].data
            if(prev_data.PS == record_data.PS):
                if prev_data.GT == record_data.GT:
                    Relation_table = Relation_table.append(
                        {
                            'POS1': prev_record.POS,
                            'POS2': record.POS,
                            'Relation': 'Cis'
                        },
                        ignore_index=True
                    )
                else:
                    Relation_table = Relation_table.append(
                        {
                            'POS1': prev_record.POS,
                            'POS2': record.POS,
                            'Relation': 'Trans'
                        },
                        ignore_index=True
                    )
            prev_record = record
    return Relation_table


def get_allelic_state(record, ratio_ad_dp):
    allelic_state = ''
    allelic_code = ''
    allelic_frequency = None
    # Using  the first sample
    sample = record.samples[0]
    alleles = sample.gt_alleles
    if record.CHROM != 'M':
        if len(alleles) >= 2 and sample.gt_type == 1:
            allelic_state = 'heterozygous'
            allelic_code = 'LA6706-1'
        elif len(alleles) >= 2:
            allelic_state = 'homozygous'
            allelic_code = 'LA6705-3'
        elif sample.gt_type is not None and len(alleles) == 1:
            allelic_state = 'hemizygous'
            allelic_code = 'LA6707-9'
        else:
            _error_log_allelicstate(record)
    elif (sample.gt_type is not None and
          len(alleles) == 1 and
          alleles[0] == '1'):
        if hasattr(sample.data, 'AD') and hasattr(sample.data, 'DP'):
            try:
                if(isinstance(sample.data.AD, list) and
                   len(sample.data.AD) > 0):
                    ratio = float(
                        sample.data.AD[0]) / float(sample.data.DP)
                    allelic_frequency = ratio
                else:
                    ratio = float(sample.data.AD) / float(sample.data.DP)
                    allelic_frequency = ratio
                if ratio > ratio_ad_dp:
                    allelic_state = "homoplasmic"
                    allelic_code = "LA6704-6"
                else:
                    allelic_state = "heteroplasmic"
                    allelic_code = "LA6703-8"
            except Exception as e:
                general_logger.debug(e)
                _error_log_allelicstate(record)
                pass
        else:
            _error_log_allelicstate(record)
    else:
        _error_log_allelicstate(record)
    return {
                'ALLELE': allelic_state,
                'CODE': allelic_code,
                'FREQUENCY': allelic_frequency
            }


def extract_chrom_identifier(chrom):
    chrom = chrom.upper().replace("CHR", "")
    if chrom == "MT":
        chrom = "M"
    return chrom


def validate_chrom_identifier(chrom):
    chrom = extract_chrom_identifier(chrom)
    pattern = '^[1-9]$|^1[0-9]$|^2[0-2]$|^[XYM]$'
    result = re.match(pattern, chrom)
    return bool(result)


def validate_ratio_ad_dp(ratio_ad_dp):
    if not (ratio_ad_dp):
        return False
    if not isinstance(ratio_ad_dp, float):
        return False
    if ratio_ad_dp < 0 or ratio_ad_dp >= 1:
        return False
    return True


def validate_has_tabix(has_tabix):
    if not isinstance(has_tabix, bool):
        return False
    return True


def get_codeable_concept(system, code, display=None):
    codeable_concept = {"coding": [{}]}
    codeable_concept['coding'][0]['system'] = system
    codeable_concept['coding'][0]['code'] = code
    if display is not None:
        codeable_concept['coding'][0]['display'] = display
    return concept.CodeableConcept(codeable_concept)


def _error_log_allelicstate(record):
    general_logger.error(
        "Cannot Determine AllelicState for: %s , considered sample: %s",
        record,
        record.samples[0].data)


def get_dna_chg(svtype):
    dna_chg = SVTYPE_TO_DNA_CHANGE_TYPE.get(svtype)
    return {"CODE": dna_chg[0], "DISPLAY": dna_chg[1]}


def get_genomic_source_class(genomic_source_class):
    source_class_code = GENOMIC_SOURCE_CLASS_TO_CODE.get(genomic_source_class)
    return {"CODE": source_class_code, "DISPLAY": genomic_source_class}


def createOrderedDict(value_from, order):
    value_to = OrderedDict()
    for key in order:
        if key in value_from.keys():
            value_to[key] = value_from[key]
    return value_to
