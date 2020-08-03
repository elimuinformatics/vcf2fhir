import logging
from .geneRefSeq import _getRefSeqByChrom
from .fhir_helper import _Fhir_Helper
from .common import _Utilities

invalid_record_logger = logging.getLogger("vcf2fhir.invalidrecord")
general_logger = logging.getLogger("vcf2fhir.general")


def _validRecord(record):
    if(record.is_sv == True):
        return False
    if(record.is_deletion):
        return False
    if(record.FILTER is not None and record.FILTER != 'PASS'):
        return False
    if(len(record.samples) == 0 or record.samples[0].gt_type is None):
        return False
    if(len(record.ALT) != 1 or record.ALT[0].type != 'SNV'):
        return False
    if record.CHROM == "M" and len(record.samples[0].gt_alleles) == 1 and record.samples[0].gt_alleles[0] == "0":
        return False
    return True  

def _get_chrom(chrom_index):
    if chrom_index == 23:
        return "X"
    elif chrom_index == 24:
        return "Y"
    elif chrom_index == 25:
        return "M"
    return str(chrom_index)

def _add_record_variants(record, ref_seq, patientID, fhir_helper):
    if(_validRecord(record) == True):
        fhir_helper.add_variant_obv(record, ref_seq)
    else:
        invalid_record_logger.debug("Record: %s, considered sample: %s", record, record.samples[0].data)

def _add_region_studied(region_studied, nocall_region, fhir_helper, chrom, ref_seq, patientID):
    if((region_studied and not region_studied[chrom].empty) or (nocall_region and not nocall_region[chrom].empty)):
        fhir_helper.add_regionstudied_obv(ref_seq, region_studied[chrom], nocall_region[chrom])


def _getFhirJSON(vcf_reader, ref_build, patientID, output_filename, conversion_region, region_studied, nocall_region):
    fhir_helper = _Fhir_Helper(patientID)
    fhir_helper.initalizeReport()
    general_logger.debug("Finished Initializing empty report")
    if conversion_region:
        if region_studied:
            region_studied = region_studied.intersect(conversion_region)
            general_logger.debug("Final Conmputed Reportable Query Regions: %s", region_studied)
        if nocall_region:
            nocall_region = nocall_region.intersect(conversion_region)
            general_logger.debug("Final Conmputed NoCall Query Regions: %s", nocall_region)
    general_logger.info("Start adding Region studied observation followed by Variant observation corresponding to that region")
    
    for chrom_index in range(1, 26):
        chrom = _get_chrom(chrom_index)
        ref_seq = _getRefSeqByChrom(ref_build , _Utilities.extract_chrom_identifier(chrom))
        if conversion_region and not conversion_region[chrom].empty:
            _add_region_studied(region_studied, nocall_region, fhir_helper, chrom, ref_seq, patientID)
            for index, row in conversion_region[chrom].df.iterrows():
                for record in vcf_reader.fetch(chrom, row['Start'], row['End']):
                    _add_record_variants(record, ref_seq, patientID, fhir_helper)
        else:
            _add_region_studied(region_studied, nocall_region, fhir_helper, chrom, ref_seq, patientID)
            for record in vcf_reader.fetch(chrom):
                _add_record_variants(record, ref_seq, patientID, fhir_helper)

    general_logger.info("Adding all the phased sequence relationship found")
    fhir_helper.add_phased_relationship_obv()

    general_logger.info("Adding all the observation Ids to result block")
    fhir_helper.add_report_result()

    fhir_helper.generate_final_json()
    general_logger.info(f"Export the FHIR object to the file {output_filename}")
    fhir_helper.export_fhir_json(output_filename)
    general_logger.info("Completed conversion")


