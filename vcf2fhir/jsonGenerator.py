import logging
from .fhir_helper import _Fhir_Helper

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s -%(message)s', datefmt='%d-%b-%y %H:%M')

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
    return True  

def _getFhirJSON(vcf_reader, ref_build, patientID, gender, output_filename, no_call_filename, conv_region_filename):
    phasedRecMap = {}
    fhir_helper = _Fhir_Helper()
    fhir_helper.initalizeReport(patientID)  

    # add RegionStudied Observation
    fhir_helper.add_regionstudied_obv(no_call_filename, conv_region_filename, patientID)

    # Add Variant Observations
    for record in vcf_reader:
        if(_validRecord(record) == True):
            fhir_helper.add_variant_obv(record,ref_build, gender, patientID)

    # Add phased relationship observations
    fhir_helper.add_phased_relationship_obv(patientID)

    # Add All Observation unique IDs in report result.
    fhir_helper.add_report_result()

    fhir_helper.generate_final_json()

    fhir_helper.export_fhir_json(output_filename)


