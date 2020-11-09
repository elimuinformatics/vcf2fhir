import logging
from .gene_ref_seq import _get_ref_seq_by_chrom
from .fhir_helper import _Fhir_Helper
from .common import _Utilities

invalid_record_logger = logging.getLogger("vcf2fhir.invalidrecord")
general_logger = logging.getLogger("vcf2fhir.general")


def _valid_record(record):
    if(record.is_sv == True):
        invalid_record_logger.debug("Reason: VCF INFO.SVTYPE is present. (Structural variants are excluded), Record: %s, considered sample: %s", record, record.samples[0].data)
        return False
    if(record.FILTER is not None and len(record.FILTER) != 0):
        invalid_record_logger.debug("Reason: VCF FILTER does not equal 'PASS' or '.', Record: %s, considered sample: %s", record, record.samples[0].data)
        return False
    if(len(record.samples) == 0 or record.samples[0].gt_type is None):
        invalid_record_logger.debug("Reason: VCF FORMAT.GT is null ('./.', '.|.', '.', etc), Record: %s, considered sample: %s", record, record.samples[0].data)
        return False
    if(len(record.ALT) != 1 or (record.ALT[0].type != 'SNV' and record.ALT[0].type != 'MNV')):
        invalid_record_logger.debug("Reason: ALT is not a simple character string, comma-separated character string or '.' (Rows where ALT is a token (e.g. 'DEL') are excluded), Record: %s, considered sample: %s", record, record.samples[0].data)
        return False
    if record.CHROM == "M" and ((len(record.samples[0].gt_alleles) == 1 and record.samples[0].gt_alleles[0] == "0") or len(record.samples[0].gt_alleles) == 2):
        invalid_record_logger.debug("Reason: Mitochondrial DNA with GT = 0 or its diploid, Record: %s, considered sample: %s", record, record.samples[0].data)
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

def _fix_regions_chrom(region):
    if region:
        region.Chromosome = region.Chromosome.apply(_Utilities.extract_chrom_identifier)


def _add_record_variants(record, ref_seq, patientID, fhir_helper):
    if(_valid_record(record) == True):
        fhir_helper.add_variant_obv(record, ref_seq)
        
def _add_region_studied(region_studied, nocall_region, fhir_helper, chrom, ref_seq, patientID):
    if((region_studied and not region_studied[chrom].empty) or (nocall_region and not nocall_region[chrom].empty)):
        general_logger.info("Adding region Studied observation for %s", chrom)
        general_logger.debug("Region Examined %s", region_studied[chrom])
        general_logger.debug("Region Uncallable %s", nocall_region[chrom])
        fhir_helper.add_regionstudied_obv(ref_seq, region_studied[chrom], nocall_region[chrom])


def _get_fhir_json(vcf_reader, ref_build, patientID, has_tabix, conversion_region, region_studied, nocall_region, output_filename):
    fhir_helper = _Fhir_Helper(patientID)
    fhir_helper.initalizeReport()
    general_logger.debug("Finished Initializing empty report")
    _fix_regions_chrom(conversion_region)
    _fix_regions_chrom(region_studied)
    _fix_regions_chrom(nocall_region)
    if conversion_region:
        if region_studied:
            region_studied = region_studied.intersect(conversion_region)
            general_logger.debug("Final Conmputed Reportable Query Regions: %s", region_studied)
        if nocall_region:
            nocall_region = nocall_region.intersect(conversion_region)
            general_logger.debug("Final Conmputed NoCall Query Regions: %s", nocall_region)
    general_logger.info("Start adding Region studied observation followed by Variant observation corresponding to that region")
    if has_tabix == True:
        for chrom_index in range(1, 26):
            chrom = _get_chrom(chrom_index)
            ref_seq = _get_ref_seq_by_chrom(ref_build , _Utilities.extract_chrom_identifier(chrom))
            _add_region_studied(region_studied, nocall_region, fhir_helper, chrom, ref_seq, patientID)
            if conversion_region and not conversion_region[chrom].empty:
                for _, row in conversion_region[chrom].df.iterrows():
                    vcf_iterator = None
                    try:
                        vcf_iterator = vcf_reader.fetch(chrom, int(row['Start']), int(row['End']))
                    except ValueError:
                        pass
                    if vcf_iterator:
                        for record in vcf_iterator:
                            record.CHROM = _Utilities.extract_chrom_identifier(record.CHROM)
                            _add_record_variants(record, ref_seq, patientID, fhir_helper)
            elif not conversion_region:
                vcf_iterator = None
                try:
                    vcf_iterator = vcf_reader.fetch(chrom)
                except ValueError:
                    pass
                if vcf_iterator:
                    for record in vcf_iterator:
                        record.CHROM = _Utilities.extract_chrom_identifier(record.CHROM)
                        _add_record_variants(record, ref_seq, patientID, fhir_helper)
    else:
        chrom_index = 1
        prev_add_chrom = ""    
        for record in vcf_reader:
            record.CHROM = _Utilities.extract_chrom_identifier(record.CHROM)
            if not (conversion_region and conversion_region[record.CHROM].empty):
                if prev_add_chrom != record.CHROM and (region_studied or nocall_region):
                    chrom = _get_chrom(chrom_index)
                    while prev_add_chrom != record.CHROM:
                        current_ref_seq = _get_ref_seq_by_chrom(ref_build, chrom)
                        _add_region_studied(region_studied, nocall_region, fhir_helper, chrom, current_ref_seq, patientID)
                        prev_add_chrom = chrom
                        chrom_index += 1
                        chrom = _get_chrom(chrom_index)
                ref_seq = _get_ref_seq_by_chrom(ref_build, record.CHROM)
                if not conversion_region or conversion_region[record.CHROM, record.POS -1: record.POS].empty == False:       
                    _add_record_variants(record, ref_seq, patientID, fhir_helper)

    general_logger.info("Adding all the phased sequence relationship found")
    fhir_helper.add_phased_relationship_obv()

    general_logger.info("Adding all the observation Ids to result block")
    fhir_helper.add_report_result()

    fhir_helper.generate_final_json()
    general_logger.info(f"Export the FHIR object to the file {output_filename}")
    fhir_helper.export_fhir_json(output_filename)
    general_logger.info("Completed conversion")


