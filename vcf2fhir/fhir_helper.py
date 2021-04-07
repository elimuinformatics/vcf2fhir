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
from collections import OrderedDict
from uuid import uuid4
from .common import *


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
        for _, row in reportable_query_regions.df.iterrows():
            obv_comp = observation.ObservationComponent()
            obv_comp.code = concept.CodeableConcept(
                {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "51959-5",
                            "display": "Ranges-examined component"
                        }
                    ]
                }
            )
            obv_comp.valueRange = valRange.Range({"low": {"value": np.float(
                row['Start']) + 1},
                "high": {"value": np.float(row['End']) + 1}})
            observation_rs_components.append(obv_comp)
        for _, row in nocall_regions.df.iterrows():
            obv_comp = observation.ObservationComponent()
            obv_comp.code = concept.CodeableConcept(
                {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "TBD-UncallableRegions",
                            "display": "Uncallable region"
                        }
                    ]
                }
            )
            obv_comp.valueRange = valRange.Range({"low": {"value": np.float(
                row['Start']) + 1},
                "high": {"value": np.float(row['End']) + 1}})
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
        if reportable_query_regions.empty and nocall_regions.empty:
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
        observation_rs_component2 = observation.ObservationComponent()
        observation_rs_component2.code = concept.CodeableConcept(
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
        observation_rs_component2\
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
        observation_rs_component3 = observation.ObservationComponent()
        observation_rs_component3.code = concept.CodeableConcept(
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
        observation_rs_component3\
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
            observation_rs_component2,
            observation_rs_component3] + observation_rs_components
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

        observation_dv_component1 = observation.ObservationComponent()
        observation_dv_component1.code = concept.CodeableConcept(
            {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "62374-4",
                        "display": "Human reference sequence assembly version"
                    }
                ]
            }
        )
        observation_dv_component1\
            .valueCodeableConcept = concept.CodeableConcept(
                {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "LA14029-5",
                            "display": "GRCh37"
                        }
                    ]
                }
            )
        observation_dv.component.append(observation_dv_component1)

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
                                   "genomics-reporting/CodeSystem/tbd-codes"),
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
                                       "genomics-reporting/" +
                                       "CodeSystem/seq-phase-relationship"),
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
        od["code"] = response['code']
        od["subject"] = response['subject']
        od["issued"] = response['issued']
        if 'result' in response:
            od["result"] = response['result']
        else:
            od["result"] = []
        od_code_coding = OrderedDict()
        od_code_coding["system"] = od["code"]["coding"][0]["system"]
        od_code_coding["code"] = od["code"]["coding"][0]["code"]
        od_code_coding["display"] = od["code"]["coding"][0]["display"]
        od["code"]["coding"][0] = od_code_coding

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
            if (i['category'][0]['coding'][0]):
                od_category_coding = OrderedDict()
                temp = i['category'][0]['coding'][0]["system"]
                od_category_coding["system"] = temp
                temp = i['category'][0]['coding'][0]["code"]
                od_category_coding["code"] = temp
                temp = od_category_coding
                od['contained'][k]['category'][0]['coding'][0] = temp

            if (i['code']['coding'][0]):
                od_code_coding = OrderedDict()
                od_code_coding["system"] = i['code']['coding'][0]["system"]
                od_code_coding["code"] = i['code']['coding'][0]["code"]
                od_code_coding["display"] = i['code']['coding'][0]["display"]
                od['contained'][k]['code']['coding'][0] = od_code_coding

            if 'valueCodeableConcept' in i.keys():
                od_value_codeable_concept_coding = OrderedDict()
                temp = i['valueCodeableConcept']['coding'][0]["system"]
                od_value_codeable_concept_coding["system"] = temp
                temp = i['valueCodeableConcept']['coding'][0]["code"]
                od_value_codeable_concept_coding["code"] = temp
                temp = i['valueCodeableConcept']['coding'][0]["display"]
                od_value_codeable_concept_coding["display"] = temp
                temp = od_value_codeable_concept_coding
                od['contained'][k]['valueCodeableConcept']['coding'][0] = temp

            if ((i['id'].startswith('dv-')) or (i['id'].startswith('rs-'))):
                for q, j in enumerate(i['component']):
                    od_component_code_coding = OrderedDict()
                    if j['code']['coding'][0]["system"]:
                        temp = j['code']['coding'][0]["system"]
                        od_component_code_coding["system"] = temp
                    if j['code']['coding'][0]["code"]:
                        temp = j['code']['coding'][0]["code"]
                        od_component_code_coding["code"] = temp
                    if j['code']['coding'][0]["display"]:
                        temp = j['code']['coding'][0]["display"]
                        od_component_code_coding["display"] = temp
                    if od['contained'][k]['component'][q]['code']['coding'][0]:
                        temp = od_component_code_coding
                        s1 = 'contained'
                        s2 = 'component'
                        od[s1][k][s2][q]['code']['coding'][0] = temp

                    od_componentvalue_codeable_concept = OrderedDict()
                    if 'valueCodeableConcept' in j.keys():
                        temp = j['valueCodeableConcept']['coding'][0]["system"]
                        od_componentvalue_codeable_concept["system"] = temp
                        if 'code' in j['valueCodeableConcept']['coding'][0]\
                            .keys(
                        ):
                            t = j['valueCodeableConcept']['coding'][0]["code"]
                            od_componentvalue_codeable_concept["code"] = t
                        if 'display' in j['valueCodeableConcept']['coding'][0]\
                            .keys(
                        ):
                            s1 = 'valueCodeableConcept'
                            s2 = 'display'
                            temp = j[s1]['coding'][0]["display"]
                            od_componentvalue_codeable_concept[s2] = temp
                        s1 = 'contained'
                        s2 = 'component'
                        s3 = 'valueCodeableConcept'
                        temp = od_componentvalue_codeable_concept
                        od[s1][k][s2][q][s3]['coding'][0] = temp

            if (i['id'].startswith('rs-')):
                od_RS = OrderedDict()
                od_RS["resourceType"] = i['resourceType']
                od_RS["id"] = i['id']
                od_RS["meta"] = i['meta']
                od_RS["status"] = i['status']
                od_RS["category"] = i['category']
                od_RS["code"] = i['code']
                od_RS["subject"] = i['subject']
                od_RS["component"] = i['component']
                od['contained'][k] = od_RS

            if (i['id'].startswith('dv-')):
                od_DV = OrderedDict()
                od_DV["resourceType"] = i['resourceType']
                od_DV["id"] = i['id']
                od_DV["meta"] = i['meta']
                od_DV["status"] = i['status']
                od_DV["category"] = i['category']
                od_DV["code"] = i['code']
                od_DV["subject"] = i['subject']
                od_DV["valueCodeableConcept"] = i['valueCodeableConcept']
                od_DV["component"] = i['component']
                od['contained'][k] = od_DV

            if (i['id'].startswith('sid-')):
                od_SID = OrderedDict()
                od_SID["resourceType"] = i['resourceType']
                od_SID["id"] = i['id']
                od_SID["meta"] = i['meta']
                od_SID["status"] = i['status']
                od_SID["category"] = i['category']
                od_SID["code"] = i['code']
                od_SID["subject"] = i['subject']
                od_SID["valueCodeableConcept"] = i['valueCodeableConcept']
                od_SID["derivedFrom"] = i['derivedFrom']
                od['contained'][k] = od_SID
        self.fhir_json = od

    def export_fhir_json(self, output_filename):
        with open(output_filename, 'w') as fp:
            json.dump(self.fhir_json, fp, indent=4)
