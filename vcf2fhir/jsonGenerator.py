import logging
from .geneRefSeq import _getRefSeqByChrom
from .fhir_helper import _Fhir_Helper

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s -%(message)s', datefmt='%d-%b-%y %H:%M')

def _validRecord(record, query_regions):
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
    return True  

def _getFhirJSON(vcf_reader, ref_build, patientID, output_filename, conversion_region, region_studied, nocall_region):
    phasedRecMap = {}
    query_regions = None
    ref_seq = ""
    prev_var_chrom = ""
    fhir_helper = _Fhir_Helper()
    fhir_helper.initalizeReport(patientID)
    if nocall_region and conversion_region and region_studied:
        query_regions = region_studied.subtract(nocall_region).intersect(conversion_region)
    # Add Variant Observations
    for record in vcf_reader:
        if prev_var_chrom != record.CHROM:
            ref_seq = _getRefSeqByChrom(ref_build, record.CHROM)
            if query_regions is not None:
                # add RegionStudied Observation
                fhir_helper.add_regionstudied_obv(patientID, ref_seq, record, query_regions)
            prev_var_chrom = record.CHROM
        if(_validRecord(record, query_regions) == True):
            fhir_helper.add_variant_obv(record, ref_seq, patientID)

    # Add phased relationship observations
    fhir_helper.add_phased_relationship_obv(patientID)

    # Add All Observation unique IDs in report result.
    fhir_helper.add_report_result()

    fhir_helper.generate_final_json()

    fhir_helper.export_fhir_json(output_filename)


