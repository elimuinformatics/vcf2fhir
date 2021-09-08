import logging
from .gene_ref_seq import _get_ref_seq_by_chrom
from .fhir_helper import _Fhir_Helper
from .common import *
import vcf

invalid_record_logger = logging.getLogger("vcf2fhir.invalidrecord")
general_logger = logging.getLogger("vcf2fhir.general")


def _valid_record(record, genomic_source_class):
    if len(record.samples) < 1:
        invalid_record_logger.debug(
            ("Reason: Atleast one sample is required for VCF " +
             "to FHIR conversion, Record: %s"),
            record)
        return False
    if not (validate_chrom_identifier(record.CHROM)):
        invalid_record_logger.debug(
            ("Reason: VCF CHROM is not recognized, " +
             "Record: %s, considered sample: %s"),
            record,
            record.samples[0].data)
        return False
    if not hasattr(record.samples[0].data, "GT"):
        invalid_record_logger.debug(
            ("Reason: FORMAT.GT is not present." +
             "Record: %s, considered sample: %s"),
            record,
            record.samples[0].data)
        return False
    if record.is_sv:
        if len(record.samples) > 1:
            invalid_record_logger.debug(
                ("Reason: Multi-sample VCFs for SVs are not allowed, " +
                 "Record: %s, considered sample: %s"),
                record,
                record.samples[0].data)
            return False
        if(record.INFO['SVTYPE'] not in list(SVs)):
            invalid_record_logger.debug(
                ("Reason: VCF INFO.SVTYPE must be in ['INS', 'DEL', " +
                 "'DUP', 'CNV', 'INV']. Record: %s, considered sample: %s"),
                record,
                record.samples[0].data)
            return False
        # The following if condition checks if RECORD.ALT is a
        # '.' or simple character string or comma-separated character string or
        # angle-bracketed token or comma separated angle-bracketed token,
        # for structural variants.
        if(not all(alt is None or alt.type in ['SNV', 'MNV'] or
           isinstance(alt, vcf.model._SV) for alt in record.ALT)):
            invalid_record_logger.debug(
                ("Reason: ALT is not a simple character string, " +
                 "comma-separated character string, angle-bracketed token, " +
                 "comma separated angle-bracketed token " +
                 "list or '.', Record: %s, considered sample: %s"),
                record,
                record.samples[0].data)
            return False
        if(record.INFO['SVTYPE'] in list(SVs - {'DUP', 'CNV'}) and
           '.' in record.samples[0]["GT"] and
           genomic_source_class == Genomic_Source_Class.GERMLINE.value):
            invalid_record_logger.debug(
                ("Reason: FORMAT.GT should not contain '.' when " +
                 "INFO.SVTYPE in [INV, DEL, INS] and Genomic Source " +
                 "Class is Germline, Record: %s, considered sample: %s"),
                record,
                record.samples[0].data)
            return False
    else:
        # The following if condition checks if RECORD.ALT is a
        # '.' or simple character string or comma-separated character string,
        # for simple variants.
        if(not all(alt is None or alt.type in ['SNV', 'MNV']
           for alt in record.ALT)):
            invalid_record_logger.debug(
                ("Reason: ALT is not a simple character string, " +
                 "comma-separated character string " +
                 "or '.', Record: %s, considered sample: %s"),
                record,
                record.samples[0].data)
            return False
        if('.' in record.samples[0]["GT"] and
           genomic_source_class == Genomic_Source_Class.GERMLINE.value):
            invalid_record_logger.debug(
                ("Reason: FORMAT.GT should not contain '.' for " +
                 "simple variants when Genomic Source " +
                 "Class is Germline, Record: %s, considered sample: %s"),
                record,
                record.samples[0].data)
            return False
    if(record.FILTER is not None and len(record.FILTER) != 0):
        invalid_record_logger.debug(
            ("Reason: VCF FILTER does not equal " +
             "'PASS' or '.', Record: %s, considered sample: %s"),
            record,
            record.samples[0].data)
        return False
    if record.samples[0]["GT"] in ['0/0', '0|0', '0']:
        invalid_record_logger.debug(
            ("Reason: VCF FORMAT.GT is in ['0/0','0|0','0'], " +
             "Record: %s, considered sample: %s"),
            record,
            record.samples[0].data)
        return False
    if not record.REF.isalpha():
        invalid_record_logger.debug(
            ("Reason: REF is not a simple character string. " +
             "Record: %s, considered sample: %s"),
            record,
            record.samples[0].data)
        return False
    if record.CHROM == "M" and (
        (len(
            record.samples[0].gt_alleles) == 1 and
            record.samples[0].gt_alleles[0] == "0") or len(
            record.samples[0].gt_alleles) == 2):
        invalid_record_logger.debug(
            ("Reason: Mitochondrial DNA with GT = 0 or its diploid, " +
             "Record: %s, considered sample: %s"),
            record,
            record.samples[0].data)
        return False
    return True


def _get_chrom(chrom_index):
    switcher = {
        23: 'X',
        24: 'Y',
        25: 'M'
    }
    return switcher.get(chrom_index, str(chrom_index))


def _fix_regions_chrom(region):
    if region:
        region.Chromosome = region.Chromosome.apply(
            extract_chrom_identifier)


def _add_record_variants(
        record, ref_seq, patientID, fhir_helper,
        ratio_ad_dp, genomic_source_class, annotations):
    spdi_representation = (f'{ref_seq}:{record.POS - 1}:{record.REF}:' +
                           f'{"".join(list(map(str, list(record.ALT))))}')
    annotation_record =\
        get_annotations(record, annotations, spdi_representation)
    if(annotation_record is not None and
       _valid_record(record, genomic_source_class)):
        fhir_helper.add_variant_obv(record, ref_seq, ratio_ad_dp,
                                    genomic_source_class, annotation_record)


def _add_region_studied(
        region_studied, conversion_region,
        nocall_region, fhir_helper, chrom, ref_seq, patientID):
    if(((region_studied and not region_studied[chrom].empty) or
       (nocall_region and not nocall_region[chrom].empty)) or
       ((region_studied is not None and len(region_studied) == 0) and
       (conversion_region and not conversion_region[chrom].empty))):
        general_logger.info("Adding region Studied observation for %s", chrom)
        general_logger.debug("Region Examined %s", region_studied[chrom])
        general_logger.debug("Region Uncallable %s", nocall_region[chrom])
        fhir_helper.add_regionstudied_obv(
            ref_seq, region_studied[chrom], nocall_region[chrom])


def _get_fhir_json(
        vcf_reader,
        ref_build, patientID, has_tabix, conversion_region, region_studied,
        nocall_region, ratio_ad_dp, genomic_source_class,
        annotations, output_filename):
    fhir_helper = _Fhir_Helper(patientID)
    fhir_helper.initalize_report()
    general_logger.debug("Finished Initializing empty report")
    _fix_regions_chrom(conversion_region)
    _fix_regions_chrom(region_studied)
    _fix_regions_chrom(nocall_region)
    if conversion_region:
        if region_studied:
            region_studied = region_studied.intersect(conversion_region)
            general_logger.debug(
                "Final Conmputed Reportable Query Regions: %s", region_studied)
        if nocall_region:
            nocall_region = nocall_region.intersect(conversion_region)
            general_logger.debug(
                "Final Conmputed NoCall Query Regions: %s", nocall_region)
    general_logger.info(
        ("Start adding Region studied observation followed by " +
         "Variant observation corresponding to that region"))
    if has_tabix:
        for chrom_index in range(1, 26):
            chrom = _get_chrom(chrom_index)
            ref_seq = _get_ref_seq_by_chrom(
                ref_build, extract_chrom_identifier(chrom))
            _add_region_studied(
                region_studied, conversion_region,
                nocall_region, fhir_helper, chrom, ref_seq, patientID
            )
            if conversion_region and not conversion_region[chrom].empty:
                for _, row in conversion_region[chrom].df.iterrows():
                    vcf_iterator = None
                    try:
                        vcf_iterator = vcf_reader.fetch(
                            chrom, int(row['Start']), int(row['End']))
                    except ValueError:
                        pass
                    if vcf_iterator:
                        for record in vcf_iterator:
                            record.CHROM = extract_chrom_identifier(
                                record.CHROM)
                            _add_record_variants(
                                record, ref_seq, patientID,
                                fhir_helper, ratio_ad_dp,
                                genomic_source_class, annotations
                            )
            elif not conversion_region:
                vcf_iterator = None
                try:
                    vcf_iterator = vcf_reader.fetch(chrom)
                except ValueError:
                    pass
                if vcf_iterator:
                    for record in vcf_iterator:
                        record.CHROM = extract_chrom_identifier(
                            record.CHROM)
                        _add_record_variants(
                            record, ref_seq, patientID,
                            fhir_helper, ratio_ad_dp,
                            genomic_source_class, annotations
                        )
    else:
        chrom_index = 1
        prev_add_chrom = ""
        for record in vcf_reader:
            record.CHROM = extract_chrom_identifier(record.CHROM)
            if not (
                    conversion_region and
                    conversion_region[record.CHROM].empty):
                if prev_add_chrom != record.CHROM and (
                        region_studied or nocall_region):
                    chrom = _get_chrom(chrom_index)
                    while prev_add_chrom != record.CHROM:
                        current_ref_seq = _get_ref_seq_by_chrom(
                            ref_build, chrom)
                        _add_region_studied(
                            region_studied, conversion_region, nocall_region,
                            fhir_helper, chrom, current_ref_seq, patientID)
                        prev_add_chrom = chrom
                        chrom_index += 1
                        chrom = _get_chrom(chrom_index)
                ref_seq = _get_ref_seq_by_chrom(ref_build, record.CHROM)
                end = record.POS + len(record.REF) - 1
                if record.is_sv and hasattr(record.INFO, 'END'):
                    end = record.INFO['END']
                if(not conversion_region or
                   conversion_region[
                        record.CHROM, record.POS - 1: end
                   ].empty is False):
                    _add_record_variants(
                        record, ref_seq, patientID,
                        fhir_helper, ratio_ad_dp,
                        genomic_source_class, annotations)

    general_logger.info("Adding all the phased sequence relationship found")
    fhir_helper.add_phased_relationship_obv()

    general_logger.info("Adding all the observation Ids to result block")
    fhir_helper.add_report_result()

    fhir_helper.generate_final_json()
    general_logger.info(
        f"Export the FHIR object to the file {output_filename}")
    fhir_helper.export_fhir_json(output_filename)
    general_logger.info("Completed conversion")
