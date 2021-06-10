import os
import json
import fhirclient.models.diagnosticreport as dr
import fhirclient.models.codeableconcept as concept
import fhirclient.models.meta as meta
import fhirclient.models.resource as resource
import fhirclient.models.observation as observation
import fhirclient.models.fhirreference as reference
import fhirclient.models.fhirdate as date
import fhirclient.models.range as valRange
import fhirclient.models.medicationstatement as medication
import numpy as np
from uuid import uuid4
from .common import *

CG_ORDER = ["system", "code"]
CODE_ORD = ["system", "code", "display"]
RS_ORDER = ['resourceType', 'id', 'meta', 'status', 'category', 'code',
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
            self,
            reportable_query_regions,
            nocall_regions):
        observation_rs_components = []
        ranges_examined_component = concept.CodeableConcept(
            {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "51959-5",
                        "display": "Range(s) of DNA sequence examined"
                    }
                ]
            }
        )
        if (
                reportable_query_regions is not None and
                len(reportable_query_regions) == 0):
            obv_comp = observation.ObservationComponent()
            obv_comp.code = ranges_examined_component
            obv_comp\
                .dataAbsentReason = concept.CodeableConcept(
                    {
                        "coding": [
                            {
                                "system": ("http://terminology.hl7.org/" +
                                           "CodeSystem/data-absent-reason"),
                                "code": "not-performed",
                                "display": "Not Performed"
                            }
                        ]
                    }
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
            obv_comp.code = concept.CodeableConcept(
                {
                    "coding": [
                        {
                            "system": ("http://hl7.org/fhir/uv/genomics" +
                                       "-reporting/CodeSystem/TbdCodes"),
                            "code": "uncallable-regions",
                            "display": "Uncallable Regions"
                        }
                    ]
                }
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
        if(
                sample_data.GT is not None and
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
        self.report.category = concept.CodeableConcept(
            {
                "coding": [
                    {
                        "system": ("http://terminology.hl7.org/" +
                                   "CodeSystem/v2-0074"),
                        "code": "GE"
                    }
                ]
            }
        )
        self.report.code = concept.CodeableConcept(
            {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "81247-9",
                        "display": "Master HL7 genetic variant reporting panel"
                    }
                ]
            }
        )
        self.report.subject = patient_reference
        self.report.issued = date.FHIRDate(get_fhir_date())
        self.report.contained = []

    def add_regionstudied_obv(
            self,
            ref_seq,
            reportable_query_regions,
            nocall_regions):
        if(((
                not (reportable_query_regions is not None) and
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
        observation_rs.code = concept.CodeableConcept(
            {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "53041-0",
                        "display": "DNA region of interest panel"
                    }
                ]
            }
        )
        observation_rs.status = "final"
        observation_rs.category = [concept.CodeableConcept(
            {
                "coding": [
                    {
                        "system": ("http://terminology.hl7.org/" +
                                   "CodeSystem/observation-category"),
                        "code": "laboratory"
                    }
                ]
            }
        )]
        observation_rs.subject = patient_reference
        observation_rs_component1 = observation.ObservationComponent()
        observation_rs_component1.code = concept.CodeableConcept(
            {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "92822-6",
                        "display": "Genomic coord system"
                    }
                ]
            }
        )
        observation_rs_component1\
            .valueCodeableConcept = concept.CodeableConcept(
                {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "LA30102-0",
                            "display": "1-based character counting"
                        }
                    ]
                }
            )
        observation_rs_component2 = observation.ObservationComponent()
        observation_rs_component2.code = concept.CodeableConcept(
            {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "48013-7",
                        "display": "Genomic reference sequence ID"
                    }
                ]
            }
        )
        observation_rs_component2\
            .valueCodeableConcept = concept.CodeableConcept(
                {
                    "coding": [
                        {
                            "system": "http://www.ncbi.nlm.nih.gov/nuccore",
                            "code": ref_seq
                        }
                    ]
                }
            )
        observation_rs_components = self._get_region_studied_component(
            reportable_query_regions, nocall_regions)
        observation_rs.component = [
            observation_rs_component1,
            observation_rs_component2] + observation_rs_components
        # Observation structure : described-variants
        self.report.contained.append(contained_rs)

    def add_variant_obv(self, record, ref_seq, ratio_ad_dp):
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
        observation_dv.category = [concept.CodeableConcept(
            {
                "coding": [
                    {
                        "system": ("http://terminology.hl7.org/" +
                                   "CodeSystem/observation-category"),
                        "code": "laboratory"
                    }
                ]
            }
        )]
        observation_dv.code = concept.CodeableConcept(
            {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "69548-6",
                        "display": "Genetic variant assessment"
                    }
                ]
            }
        )
        observation_dv.subject = patient_reference
        observation_dv.valueCodeableConcept = concept.CodeableConcept(
            {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "LA9633-4",
                        "display": "present"
                    }
                ]
            }
        )
        observation_dv.component = []

        observation_dv_component2 = observation.ObservationComponent()
        observation_dv_component2.code = concept.CodeableConcept(
            {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "48013-7",
                        "display": "Genomic reference sequence ID"
                    }
                ]
            }
        )
        observation_dv_component2\
            .valueCodeableConcept = concept.CodeableConcept(
                {
                    "coding": [
                        {
                            "system": "http://www.ncbi.nlm.nih.gov/nuccore",
                            "code": ref_seq
                        }
                    ]
                }
            )
        observation_dv.component.append(observation_dv_component2)

        if alleles['CODE'] != "" or alleles['ALLELE'] != "":
            observation_dv_component3 = observation.ObservationComponent()
            observation_dv_component3.code = concept.CodeableConcept(
                {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "53034-5",
                            "display": "Allelic state"
                        }
                    ]
                }
            )
            observation_dv_component3\
                .valueCodeableConcept = concept.CodeableConcept(
                    {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": alleles['CODE'],
                                "display": alleles['ALLELE']
                            }
                        ]
                    }
                )
            observation_dv.component.append(observation_dv_component3)

        observation_dv_component4 = observation.ObservationComponent()
        observation_dv_component4.code = concept.CodeableConcept(
            {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "69547-8",
                        "display": "Genomic Ref allele [ID]"
                    }
                ]
            }
        )
        observation_dv_component4.valueString = record.REF
        observation_dv.component.append(observation_dv_component4)

        observation_dv_component5 = observation.ObservationComponent()
        observation_dv_component5.code = concept.CodeableConcept(
            {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "69551-0",
                        "display": "Genomic Alt allele [ID]"
                    }
                ]
            }
        )
        observation_dv_component5.valueString = record.ALT[0].sequence
        observation_dv.component.append(observation_dv_component5)

        observation_dv_component6 = observation.ObservationComponent()
        observation_dv_component6.code = concept.CodeableConcept(
            {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "92822-6",
                        "display": "Genomic coord system"
                    }
                ]
            }
        )
        observation_dv_component6\
            .valueCodeableConcept = concept.CodeableConcept(
                {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "LA30102-0",
                            "display": "1-based character counting"
                        }
                    ]
                }
            )
        observation_dv.component.append(observation_dv_component6)

        observation_dv_component7 = observation.ObservationComponent()
        observation_dv_component7.code = concept.CodeableConcept(
            {
                "coding": [
                    {
                        "system": ("http://hl7.org/fhir/uv/" +
                                   "genomics-reporting/CodeSystem/TbdCodes"),
                        "code": "exact-start-end",
                        "display": "Variant exact start and end"}]})
        observation_dv_component7.valueRange = valRange.Range(
            {"low": {"value": int(record.POS)}})
        observation_dv.component.append(observation_dv_component7)

        self.report.contained.append(observation_dv)

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
            observation_sid.category = [concept.CodeableConcept(
                {
                    "coding": [
                        {
                            "system": ("http://terminology.hl7.org/" +
                                       "CodeSystem/observation-category"),
                            "code": "laboratory"
                        }
                    ]
                }
            )]
            observation_sid.code = concept.CodeableConcept(
                {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "82120-7",
                            "display": "Allelic phase"
                        }
                    ]
                }
            )
            observation_sid.subject = patient_reference
            observation_sid.valueCodeableConcept = concept.CodeableConcept(
                {
                    "coding": [
                        {
                            "system": ("http://hl7.org/fhir/uv/" +
                                       "genomics-reporting/CodeSystem/" +
                                       "SequencePhaseRelationshipCS"),
                            "code": self.sequence_rels.at[index, 'Relation'],
                            "display":self.sequence_rels.at[index, 'Relation']
                        }
                    ]
                }
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

            if (i['category'][0]['coding'][0]):
                od_contained_k['category'][0]['coding'][0] =\
                    createOrderedDict(i['category'][0]['coding'][0], CG_ORDER)

            if (i['code']['coding'][0]):
                od_contained_k['code']['coding'][0] =\
                    createOrderedDict(i['code']['coding'][0], CODE_ORD)

            if v_c_c in i.keys():
                od_contained_k[v_c_c]['coding'][0] =\
                    createOrderedDict(i[v_c_c]['coding'][0], CODE_ORD)

            if ((i['id'].startswith('dv-')) or (i['id'].startswith('rs-'))):
                for q, j in enumerate(i['component']):
                    od_contained_k_component_q = od_contained_k['component'][q]
                    if od_contained_k_component_q['code']['coding'][0]:
                        od_contained_k_component_q['code']['coding'][0] =\
                            createOrderedDict(j['code']['coding'][0], CODE_ORD)

                    if v_c_c in j.keys():
                        od_contained_k_component_q[v_c_c]['coding'][0] =\
                            createOrderedDict(j[v_c_c]['coding'][0], CODE_ORD)

            if (i['id'].startswith('rs-')):
                od['contained'][k] = createOrderedDict(i, RS_ORDER)

            if (i['id'].startswith('dv-')):
                od['contained'][k] = createOrderedDict(i, DV_ORDER)

            if (i['id'].startswith('sid-')):
                od['contained'][k] = createOrderedDict(i, SID_ORDER)
        self.fhir_json = od

    def export_fhir_json(self, output_filename):
        with open(output_filename, 'w') as fp:
            json.dump(self.fhir_json, fp, indent=4)
