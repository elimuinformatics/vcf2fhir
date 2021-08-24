import os
import json
import fhirclient.models.diagnosticreport as dr
import fhirclient.models.codeableconcept as concept
import fhirclient.models.quantity as quantity
import fhirclient.models.meta as meta
import fhirclient.models.resource as resource
import fhirclient.models.observation as observation
import fhirclient.models.fhirreference as reference
import fhirclient.models.fhirdate as date
import fhirclient.models.range as valRange
import fhirclient.models.medicationstatement as medication
from uuid import uuid4
from .common import *

CG_ORDER = ["system", "code"]
CODE_ORD = ["system", "code", "display"]
VQ_ORD = ["system", "code", "value"]
RS_ORDER = ['resourceType', 'id', 'meta', 'status', 'category', 'code',
            'subject', 'component']
DI_ORDER = ['resourceType', 'id', 'meta', 'status', 'category', 'code',
            'subject', 'component']
DV_ORDER = ['resourceType', 'id', 'meta', 'status', 'category', 'code',
            'subject', 'valueCodeableConcept', 'component']
SID_ORDER = ['resourceType', 'id', 'meta', 'status', 'category',
             'code', 'subject', 'valueCodeableConcept', 'derivedFrom']


class _Fhir_Helper:
    def __init__(self, patientID):
        self.report = dr.DiagnosticReport()
        self.phased_rec_map = {}
        self.result_ids = []
        self.fhir_report = {}
        self.obs_contained = []
        self.patientID = patientID

    def _get_region_studied_component(
            self, reportable_query_regions, nocall_regions):
        observation_rs_components = []
        ranges_examined_component = get_codeable_concept(
            "http://loinc.org", "51959-5",
            "Range(s) of DNA sequence examined"
        )
        if(reportable_query_regions is not None and
           len(reportable_query_regions) == 0):
            obv_comp = observation.ObservationComponent()
            obv_comp.code = ranges_examined_component
            obv_comp\
                .dataAbsentReason = get_codeable_concept(
                    ("http://terminology.hl7.org/" +
                     "CodeSystem/data-absent-reason"), "not-performed",
                    "Not Performed"
                )
            observation_rs_components.append(obv_comp)
            return observation_rs_components
        for _, row in reportable_query_regions.df.iterrows():
            obv_comp = observation.ObservationComponent()
            obv_comp.code = ranges_examined_component
            obv_comp.valueRange = valRange.Range({"low": {"value": float(
                row['Start']) + 1},
                "high": {"value": float(row['End']) + 1}})
            observation_rs_components.append(obv_comp)
        for _, row in nocall_regions.df.iterrows():
            obv_comp = observation.ObservationComponent()
            obv_comp.code = get_codeable_concept(
                ("http://hl7.org/fhir/uv/genomics" +
                 "-reporting/CodeSystem/TbdCodes"), "uncallable-regions",
                "Uncallable Regions"
            )
            obv_comp.valueRange = valRange.Range({"low": {"value": float(
                row['Start']) + 1},
                "high": {"value": float(row['End']) + 1}})
            observation_rs_components.append(obv_comp)
        return observation_rs_components

    def _add_phase_records(self, record):
        if(record.samples[0].phased is False):
            return
        sample_data = record.samples[0].data
        if(sample_data.GT is not None and
           len(sample_data.GT.split('|')) >= 2 and
           'PS' in sample_data._fields):
            self.phased_rec_map.setdefault(sample_data.PS, []).append(record)

    def initalize_report(self):
        patient_reference = reference.FHIRReference(
            {"reference": "Patient/" + self.patientID})
        self.report.id = "dr-" + uuid4().hex[:13]
        self.report.meta = meta.Meta({
                            "profile": [
                                ("http://hl7.org/fhir/uv/genomics-reporting" +
                                 "/StructureDefinition/genomics-report")]})
        self.report.status = "final"
        self.report.category = get_codeable_concept(
            "http://terminology.hl7.org/CodeSystem/v2-0074", "GE"
        )
        self.report.code = get_codeable_concept(
            "http://loinc.org", "81247-9",
            "Master HL7 genetic variant reporting panel"
        )
        self.report.subject = patient_reference
        self.report.issued = date.FHIRDate(get_fhir_date())
        self.report.contained = []

    def add_regionstudied_obv(
            self, ref_seq, reportable_query_regions, nocall_regions):
        if(((not (reportable_query_regions is not None) and
           (len(reportable_query_regions) == 0))) and
           (reportable_query_regions.empty and nocall_regions.empty)):
            return
        patient_reference = reference.FHIRReference(
            {"reference": "Patient/" + self.patientID})
        contained_uid = "rs-" + uuid4().hex[:13]
        self.result_ids.append(contained_uid)
        # Region Studied Obeservation
        observation_rs = observation.Observation()
        contained_rs = observation_rs
        contained_rs.id = contained_uid
        observation_rs.resource_type = "Observation"
        contained_rs.meta = meta.Meta({"profile": [
                                      ("http://hl7.org/fhir/uv/" +
                                       "genomics-reporting/" +
                                       "StructureDefinition/region-studied")]})
        observation_rs.code = get_codeable_concept(
            "http://loinc.org", "53041-0", "DNA region of interest panel"
        )
        observation_rs.status = "final"
        observation_rs.category = [get_codeable_concept(
            "http://terminology.hl7.org/CodeSystem/observation-category",
            "laboratory"
        )]
        observation_rs.subject = patient_reference
        observation_rs_component1 = observation.ObservationComponent()
        observation_rs_component1.code = get_codeable_concept(
            "http://loinc.org", "92822-6", "Genomic coord system"
        )
        observation_rs_component1\
            .valueCodeableConcept = get_codeable_concept(
                "http://loinc.org", "LA30102-0", "1-based character counting"
            )
        observation_rs_component2 = observation.ObservationComponent()
        observation_rs_component2.code = get_codeable_concept(
            "http://loinc.org", "48013-7", "Genomic reference sequence ID"
        )
        observation_rs_component2\
            .valueCodeableConcept = get_codeable_concept(
                "http://www.ncbi.nlm.nih.gov/nuccore", ref_seq
            )
        observation_rs_components = self._get_region_studied_component(
            reportable_query_regions, nocall_regions)
        observation_rs.component = [
            observation_rs_component1,
            observation_rs_component2] + observation_rs_components
        # Observation structure : described-variants
        self.report.contained.append(contained_rs)

    def add_diagnostic_implication(
            self, record, ref_seq, variant_id, annotation_record):
        contained_uid = "di-" + uuid4().hex[:13]
        self.result_ids.append(contained_uid)
        variant_reference = reference.FHIRReference(
            {"reference": f'#{variant_id}'})
        observation_di = observation.Observation()
        observation_di.resource_type = "Observation"
        observation_di.id = contained_uid
        observation_di.meta =\
            meta.Meta({"profile": [("http://hl7.org/fhir/uv/genomics-" +
                                    "reporting/StructureDefinition/" +
                                    "diagnostic-implication")]})
        observation_di.subject = variant_reference
        observation_di.code = get_codeable_concept(
            ("http://hl7.org/fhir/uv/genomics-reporting" +
             "/CodeSystem/TbdCodes"),
            "diagnostic-implication", "Diagnostic Implication")
        observation_di.status = "final"
        observation_di.category = [get_codeable_concept(
            "http://terminology.hl7.org/CodeSystem/observation-category",
            "laboratory"
        )]
        observation_di.component = []

        clin_sig_code = CLIN_SIG_TO_CODE.get(annotation_record['clin_sig'])
        clinical_significance_component = observation.ObservationComponent()
        clinical_significance_component.code = get_codeable_concept(
            "http://loinc.org",
            "53037-8", "Genetic variation clinical significance [Imp]"
        )
        clinical_significance_component\
            .valueCodeableConcept = get_codeable_concept(
                "http://loinc.org",
                clin_sig_code, annotation_record['clin_sig']
            )

        if annotation_record['phenotype'] is not None:
            associated_phenotype_component = observation.ObservationComponent()
            associated_phenotype_component.code = get_codeable_concept(
                "http://loinc.org", "81259-4", "Associated phenotype"
            )
            associated_phenotype_component\
                .valueCodeableConcept = get_codeable_concept(
                    "http://www.ncbi.nlm.nih.gov/medgen",
                    annotation_record['phenotype'].split('^')[0],
                    annotation_record['phenotype'].split('^')[1]
                )

        # The following block of code adds a diagnostic
        # implication component to the listof components based on the
        # DIAGNOSTIC_IMPLICATION_ORDER list if it isdeclared. The
        # declaration of thevariable is ensured using thelocals() dictionary.
        for di_component in DIAGNOSTIC_IMPLICATION_ORDER:
            if di_component in locals():
                observation_di.component.append(locals()[di_component])
        self.report.contained.append(observation_di)

    def add_variant_obv(
            self, record, ref_seq,
            ratio_ad_dp, genomic_source_class, annotation_record):
        # collect all the record with similar position values,
        # to utilized later in phased sequence relationship
        self._add_phase_records(record)
        patient_reference = reference.FHIRReference(
            {"reference": "Patient/" + self.patientID})
        alleles = get_allelic_state(record, ratio_ad_dp)
        dvuid = "dv-" + uuid4().hex[:13]
        self.fhir_report.update({str(record.POS): dvuid})
        self.result_ids.append(dvuid)
        observation_dv = observation.Observation()
        observation_dv.resource_type = "Observation"
        observation_dv.id = dvuid
        observation_dv.meta = meta.Meta(
            {
                "profile": [
                    ("http://hl7.org/fhir/uv/" +
                     "genomics-reporting/StructureDefinition/variant")
                ]
            }
        )
        observation_dv.status = "final"
        observation_dv.category = [get_codeable_concept(
            "http://terminology.hl7.org/CodeSystem/observation-category",
            "laboratory"
        )]
        observation_dv.code = get_codeable_concept(
            "http://loinc.org", "69548-6", "Genetic variant assessment"
        )
        observation_dv.subject = patient_reference
        observation_dv.valueCodeableConcept = get_codeable_concept(
            "http://loinc.org", "LA9633-4", "present"
        )
        observation_dv.component = []

        if record.is_sv:
            dna_chg = get_dna_chg(record.INFO['SVTYPE'])
            dna_change_type_component = observation.ObservationComponent()
            dna_change_type_component.code = get_codeable_concept(
                "http://loinc.org", "48019-4", "DNA Change Type"
            )
            dna_change_type_component\
                .valueCodeableConcept = get_codeable_concept(
                    "http://sequenceontology.org", dna_chg['CODE'],
                    dna_chg['DISPLAY']
                )

            if(record.INFO['SVTYPE'] in list(SVs - {'INV', 'INS'}) and
               hasattr(record.samples[0].data, 'CN')):
                copy_number_component = observation.ObservationComponent()
                copy_number_component.code = get_codeable_concept(
                    "http://loinc.org", "82155-3",
                    "Genomic Structural Variant copy Number"
                )
                copy_number_component\
                    .valueQuantity = quantity.Quantity(
                        {
                            "system": "http://unitsofmeasure.org",
                            "code": '1',
                            "value": record.samples[0]["CN"]
                        }
                    )

            # In the following if-else block we check if there is a CIPOS
            # and a CIEND field in record.INFO and calculate inner and outer
            # start and end based on it, else we ignore the outer-start-end
            # component and populate the inner-start-end component based on
            # only the INFO.END value.
            if hasattr(record.INFO, 'CIPOS') and hasattr(record.INFO, 'CIEND'):
                inner_start = record.POS + record.INFO['CIPOS'][1]
                inner_end = record.INFO['END'] + abs(record.INFO['CIEND'][0])
                outer_start = record.POS - abs(record.INFO['CIPOS'][0])
                outer_end = record.INFO['END'] + record.INFO['CIEND'][1]
                outer_start_end_component = observation.ObservationComponent()
                outer_start_end_component.code = get_codeable_concept(
                    ("http://hl7.org/fhir/uv/genomics-reporting" +
                     "/CodeSystem/TbdCodes"),
                    "outer-start-end", "Variant outer start and end"
                )
                outer_start_end_component\
                    .valueRange = valRange.Range(
                        {
                            "low": {
                                "value": outer_start
                            },
                            "high": {
                                "value": outer_end
                            }
                        }
                    )
            else:
                inner_start = record.POS
                inner_end = record.INFO['END']

            inner_start_end_component = observation.ObservationComponent()
            inner_start_end_component.code = get_codeable_concept(
                ("http://hl7.org/fhir/uv/ge" +
                 "nomics-reporting/CodeSystem/TbdCodes"), "inner-start-end",
                "Variant inner start and end"
            )
            inner_start_end_component\
                .valueRange = valRange.Range(
                    {
                        "low": {
                            "value": inner_start
                        },
                        "high": {
                            "value": inner_end
                        }
                    }
                )
        else:
            if alleles['FREQUENCY'] is not None:
                allelic_frequency_component =\
                    observation.ObservationComponent()
                allelic_frequency_component.code = get_codeable_concept(
                    "http://loinc.org", "81258-6", "Sample VAF"
                )
                allelic_frequency_component\
                    .valueQuantity = quantity.Quantity(
                        {
                            "system": "http://unitsofmeasure.org",
                            "code": "1",
                            "value": alleles['FREQUENCY']
                        }
                    )

            exact_start_end_component = observation.ObservationComponent()
            exact_start_end_component.code = get_codeable_concept(
                ("http://hl7.org/fhir/uv/genomics-reporting/Code" +
                 "System/TbdCodes"), "exact-start-end",
                "Variant exact start and end"
            )
            exact_start_end_component.valueRange = valRange.Range(
                {"low": {"value": int(record.POS)}})

        ref_seq_id_component = observation.ObservationComponent()
        ref_seq_id_component.code = get_codeable_concept(
            "http://loinc.org", "48013-7", "Genomic reference sequence ID"
        )
        ref_seq_id_component\
            .valueCodeableConcept = get_codeable_concept(
                "http://www.ncbi.nlm.nih.gov/nuccore", ref_seq
            )

        if genomic_source_class in Genomic_Source_Class.set_() - {MIXED}:
            source_class = get_genomic_source_class(genomic_source_class)
            genomic_source_class_component = observation.ObservationComponent()
            genomic_source_class_component.code = get_codeable_concept(
                "http://loinc.org", "48002-0", "Genomic Source Class"
            )
            genomic_source_class_component\
                .valueCodeableConcept = get_codeable_concept(
                    "http://loinc.org", source_class["CODE"],
                    source_class["DISPLAY"]
                )

        # The following if condition checks if allelic code or
        # allelic display is not an empty string and genomic source
        # class is 'germline' for simple variants and structural variants
        # with INFO.SVTYPE in ['INS', 'DEL', 'DUP', 'INV']
        if((alleles['CODE'] != "" or alleles['ALLELE'] != "") and
            genomic_source_class == Genomic_Source_Class.GERMLINE.value and
            not (record.is_sv and
                 record.INFO['SVTYPE'] not in list(SVs - {'CNV'}))):
            allelic_state_component = observation.ObservationComponent()
            allelic_state_component.code = get_codeable_concept(
                "http://loinc.org", "53034-5", "Allelic state"
            )
            allelic_state_component\
                .valueCodeableConcept = get_codeable_concept(
                    "http://loinc.org", alleles['CODE'], alleles['ALLELE']
                )

        ref_allele_component = observation.ObservationComponent()
        ref_allele_component.code = get_codeable_concept(
            "http://loinc.org", "69547-8", "Genomic Ref allele [ID]"
        )
        ref_allele_component.valueString = record.REF

        # The following if condition checks if RECORD.ALT is a
        # simple character string, for simple variants and structural
        # variants with INFO.SYTYPE in ['INS'].
        if(len(record.ALT) == 1 and record.ALT[0] is not None and
           record.ALT[0].type in ['SNV', 'MNV'] and
           not (record.is_sv and record.INFO['SVTYPE'] not in ['INS'])):
            alt_allele_component = observation.ObservationComponent()
            alt_allele_component.code = get_codeable_concept(
                "http://loinc.org", "69551-0", "Genomic Alt allele [ID]"
            )
            alt_allele_component.valueString = record.ALT[0].sequence

        genomic_coord_system_component = observation.ObservationComponent()
        genomic_coord_system_component.code = get_codeable_concept(
            "http://loinc.org", "92822-6", "Genomic coord system"
        )
        genomic_coord_system_component\
            .valueCodeableConcept = get_codeable_concept(
                "http://loinc.org", "LA30102-0", "1-based character counting"
            )

        if annotation_record['transcript_ref_seq'] is not None:
            transcript_ref_seq_component =\
                observation.ObservationComponent()
            transcript_ref_seq_component.code = get_codeable_concept(
                "http://loinc.org", "51958-7",
                "Transcript reference sequence [ID]"
            )
            transcript_ref_seq_component\
                .valueCodeableConcept = get_codeable_concept(
                    "http://www.ncbi.nlm.nih.gov/refseq",
                    annotation_record['transcript_ref_seq'],
                    annotation_record['transcript_ref_seq']
                )

        dna_chg_component = observation.ObservationComponent()
        dna_chg_component.code = get_codeable_concept(
            "http://loinc.org", "48004-6",
            "DNA change (c.HGVS)"
        )
        dna_chg_component\
            .valueCodeableConcept = get_codeable_concept(
                "http://varnomen.hgvs.org", annotation_record['dna_change']
            )

        if annotation_record['amino_acid_change'] is not None:
            amino_acid_chg_component = observation.ObservationComponent()
            amino_acid_chg_component.code = get_codeable_concept(
                "http://loinc.org", "48005-3", "Amino acid change (pHGVS)"
            )
            amino_acid_chg_component\
                .valueCodeableConcept = get_codeable_concept(
                    "http://varnomen.hgvs.org",
                    annotation_record['amino_acid_change'],
                    annotation_record['amino_acid_change']
                )

        # The following block of code adds a variant component to the list
        # of components based on the VARIANT_COMPONENTS_ORDER list if it is
        # declared. The declaration of the variable is ensured using the
        # locals() dictionary.
        for variant_component in VARIANT_COMPONENTS_ORDER:
            if variant_component in locals():
                observation_dv.component.append(locals()[variant_component])

        self.report.contained.append(observation_dv)
        self.add_diagnostic_implication(
            record, ref_seq,
            observation_dv.id, annotation_record)

    def add_phased_relationship_obv(self):
        patient_reference = reference.FHIRReference(
            {"reference": "Patient/" + self.patientID})
        self.sequence_rels \
            = get_sequence_relation(self.phased_rec_map)
        for index in self.sequence_rels.index:
            siduid = "sid-" + uuid4().hex[:13]
            self.result_ids.append(siduid)

            observation_sid = observation.Observation()
            observation_sid.resource_type = "Observation"
            observation_sid.id = siduid
            observation_sid.meta = meta.Meta({"profile": [
                                             ("http://hl7.org/fhir/uv/" +
                                              "genomics-reporting/" +
                                              "StructureDefinition/" +
                                              "sequence-phase-relationship")]})
            observation_sid.status = "final"
            observation_sid.category = [get_codeable_concept(
                "http://terminology.hl7.org/CodeSystem/observation-category",
                "laboratory"
            )]
            observation_sid.code = get_codeable_concept(
                "http://loinc.org", "82120-7", "Allelic phase"
            )
            observation_sid.subject = patient_reference
            observation_sid.valueCodeableConcept = get_codeable_concept(
                ("http://hl7.org/fhir/uv/genomics-reporting/CodeSystem/" +
                 "SequencePhaseRelationshipCS"),
                self.sequence_rels.at[index, 'Relation'],
                self.sequence_rels.at[index, 'Relation']
            )
            self.report.contained.append(observation_sid)

    def add_report_result(self):
        report_result = []
        for uid in self.result_ids:
            report_result.append(
                reference.FHIRReference({"reference": f"#{uid}"}))
        self.report.result = report_result

    def generate_final_json(self):
        response = self.report.as_json()
        od = OrderedDict()
        od["resourceType"] = response['resourceType']
        od["id"] = response['id']
        od["meta"] = response['meta']
        if 'contained' in response:
            od["contained"] = response['contained']
        else:
            od["contained"] = []
        od["status"] = response['status']
        od['category'] = []
        od['category'].append(response['category'])
        od['category'][0]['coding'][0] =\
            createOrderedDict(od['category'][0]['coding'][0], CG_ORDER)
        od["code"] = response['code']
        od["subject"] = response['subject']
        od["issued"] = response['issued']
        if 'result' in response:
            od["result"] = response['result']
        else:
            od["result"] = []
        od['code']['coding'][0] =\
            createOrderedDict(od['code']['coding'][0], CODE_ORD)

        sidIndex = 0
        for index, fhirReport in enumerate(od['contained']):
            if (fhirReport['id'].startswith('sid-')):
                sidIndex = index
                break

        for index, (_, fhirReport) in enumerate(
                zip(self.sequence_rels.index,
                    od['contained'][sidIndex:])):
            dvRef1 = self.fhir_report.get(
                str(self.sequence_rels.at[index, 'POS1']))
            dvRef2 = self.fhir_report.get(
                str(self.sequence_rels.at[index, 'POS2']))
            if (fhirReport['id'].startswith('sid-')):
                derived_from_DV1 = {}
                derived_from_DV2 = {}
                derived_from_DV1['reference'] = f"#{dvRef1}"
                derived_from_DV2['reference'] = f"#{dvRef2}"
                derivedFrom = [derived_from_DV1, derived_from_DV2]
                fhirReport['derivedFrom'] = derivedFrom

        for k, i in enumerate(od['contained']):
            od_contained_k = od['contained'][k]
            v_c_c = 'valueCodeableConcept'
            v_q = 'valueQuantity'

            if (i['category'][0]['coding'][0]):
                od_contained_k['category'][0]['coding'][0] =\
                    createOrderedDict(i['category'][0]['coding'][0], CG_ORDER)

            if (i['code']['coding'][0]):
                od_contained_k['code']['coding'][0] =\
                    createOrderedDict(i['code']['coding'][0], CODE_ORD)

            if v_c_c in i.keys():
                od_contained_k[v_c_c]['coding'][0] =\
                    createOrderedDict(i[v_c_c]['coding'][0], CODE_ORD)

            if((i['id'].startswith('dv-')) or
               (i['id'].startswith('rs-')) or
               (i['id'].startswith('di-'))):
                for q, j in enumerate(i['component']):
                    od_contained_k_component_q = od_contained_k['component'][q]
                    if od_contained_k_component_q['code']['coding'][0]:
                        od_contained_k_component_q['code']['coding'][0] =\
                            createOrderedDict(j['code']['coding'][0], CODE_ORD)

                    if v_c_c in j.keys():
                        od_contained_k_component_q[v_c_c]['coding'][0] =\
                            createOrderedDict(j[v_c_c]['coding'][0], CODE_ORD)

                    if v_q in j.keys():
                        od_contained_k_component_q[v_q] =\
                            createOrderedDict(j[v_q], VQ_ORD)

            if (i['id'].startswith('rs-')):
                od['contained'][k] = createOrderedDict(i, RS_ORDER)

            if (i['id'].startswith('dv-')):
                od['contained'][k] = createOrderedDict(i, DV_ORDER)

            if (i['id'].startswith('sid-')):
                od['contained'][k] = createOrderedDict(i, SID_ORDER)

            if (i['id'].startswith('di-')):
                od['contained'][k] = createOrderedDict(i, DI_ORDER)
                od['contained'][k]['derivedFrom'] = [{}]
                od['contained'][k]['derivedFrom'][0]['reference'] =\
                    f"{i['subject']['reference']}"
                od['contained'][k]['subject']['reference'] =\
                    f'Patient/{self.patientID}'
        self.fhir_json = od

    def export_fhir_json(self, output_filename):
        with open(output_filename, 'w') as fp:
            json.dump(self.fhir_json, fp, indent=4)
