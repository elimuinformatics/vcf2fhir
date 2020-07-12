import logging
from .geneRefSeq import _getRefSeqByChrom
from .fhir_helper import _Fhir_Helper
from .common import _Utilities

invalid_record_logger = logging.getLogger("vcf2fhir.invalidrecord")
general_logger = logging.getLogger("vcf2fhir.general")

def _modify_chrom_series(df):
    df.Chromosome = df.Chromosome.apply(lambda val: _Utilities.extract_chrom_identifier(val))
    return df

def _fix_region_chrom(regions):
    return regions.apply(_modify_chrom_series)

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
    if record.CHROM == "M" and len(record.samples[0].gt_alleles) == 1 and record.samples[0].gt_alleles[0] == "0":
        return False
    return True  

def _getFhirJSON(vcf_reader, ref_build, patientID, output_filename, conversion_region, region_studied, nocall_region):
    phasedRecMap = {}
    query_regions = None
    ref_seq = ""
    prev_var_chrom = ""
    fhir_helper = _Fhir_Helper()
    fhir_helper.initalizeReport(patientID)
    general_logger.debug("Finished Initializing empty report")
    if conversion_region:
        conversion_region = _fix_region_chrom(conversion_region)
        nocall_region = _fix_region_chrom(nocall_region)
        if not region_studied:
            query_regions = conversion_region.subtract(nocall_region)
        else:            
            region_studied = _fix_region_chrom(region_studied)
            query_regions = region_studied.subtract(nocall_region).intersect(conversion_region)
        general_logger.debug("Final Conmputed Reportable Query Regions: %s", query_regions)
    general_logger.info("Start adding Region studied observation followed by Variant observation corresponding to that region")
    for record in vcf_reader:
        record.CHROM = _Utilities.extract_chrom_identifier(record.CHROM)
        if(_validRecord(record, query_regions) == True):
            if prev_var_chrom != record.CHROM:
                ref_seq = _getRefSeqByChrom(ref_build, record.CHROM)
                general_logger.debug(f"Reference sequence for CHROM %s is %s", {record.CHROM}, ref_seq)
                if query_regions and query_regions[record.CHROM].empty == False:
                    general_logger.info("Adding region Studied observation for %s", record.CHROM)
                    fhir_helper.add_regionstudied_obv(patientID, ref_seq, record, query_regions)
                prev_var_chrom = record.CHROM
            if not query_regions or query_regions[record.CHROM, record.POS -1: record.POS].empty == False:
                fhir_helper.add_variant_obv(record, ref_seq, patientID)
            else:
                general_logger.debug("Record not in Reportable Query Region %s ,with considered sample: %s", record, record.samples[0].data)
        else:
            invalid_record_logger.debug("Record: %s, considered sample: %s", record, record.samples[0].data)

    general_logger.info("Adding all the phased sequence relationship found")
    fhir_helper.add_phased_relationship_obv(patientID)

    general_logger.info("Adding all the observation Ids to result block")
    fhir_helper.add_report_result()

    fhir_helper.generate_final_json()
    general_logger.info(f"Export the FHIR object to the file {output_filename}")
    fhir_helper.export_fhir_json(output_filename)
    general_logger.info("Completed conversion")


