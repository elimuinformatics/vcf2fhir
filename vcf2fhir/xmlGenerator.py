import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import xmltodict
import pprint
import json
import subprocess
import pickle
from uuid import uuid4
from collections import OrderedDict
from xmljson import Parker, parker
from uuid import uuid4
from .filereader import getNoCallableData#, getAllelicState, cleanVcf, nextelem, start
from .allelicstate import getAllelicState
from .phaseswapsort import getSequenceRelation
from .jsonGenerator import getFhirJSON,getEmptyFhirJSON
import logging
from .common import *

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s -%(message)s', datefmt='%d-%b-%y %H:%M')

drValue = uuid4().hex[:13]

rsuid = uuid4().hex[:13]

def prettify(elem):
    """
        Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

def getFhirXML(cleanVcf,nextelem,patientID,gender,refSeq,nocall=False):
    logging.info("[Generating FHIR XML]")
    dvuids = {}
    siduids = []

    noCallRegion,queryRange = getNoCallableData(NO_CALL_FILE,QUERY_RANGE_FILE)
    if not noCallRegion.empty:
        if noCallRegion['START'].iloc[0] <= queryRange['START'].iloc[0]:
            noCallRegion['START'].iloc[0] = queryRange['START'].iloc[0]

        if noCallRegion['END'].iloc[-1] >= queryRange['END'].iloc[0]:
            noCallRegion['END'].iloc[-1] = queryRange['END'].iloc[0]
    else:
        nocall = False    

    alleles = getAllelicState(cleanVcf,nextelem,gender)
    sequenceRels = getSequenceRelation(cleanVcf,nextelem)

    # DiagnosticReport structure
    data = ET.Element('DiagnosticReport',xmlns="http://hl7.org/fhir")
    id_node = ET.SubElement(data,'id',value="dr-"+uuid4().hex[:13])
    meta_node = ET.SubElement(data,'meta')
    profile_node = ET.SubElement(meta_node,'profile',value="http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/diagnosticreport")  
    contained_node_rs = ET.SubElement(data,'contained')   

    # Observation structure
    #region-studied
    rsuid = uuid4().hex[:13]
    observation_node_rs = ET.SubElement(contained_node_rs,'Observation')  
    observation_id_node_rs = ET.SubElement(observation_node_rs,'id',value="rs-"+rsuid)  
    observation_meta_node_rs = ET.SubElement(observation_node_rs,'meta')
    observation_meta_profile_node_rs = ET.SubElement(observation_meta_node_rs,'profile',value="http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/obs-region-studied")
    observation_status_node_rs =  ET.SubElement(observation_node_rs,'status',value="final")
    observation_category_node_rs = ET.SubElement(observation_node_rs,'category')
    observation_category_coding_node_rs = ET.SubElement(observation_category_node_rs,'coding')
    observation_category_coding_system_node = ET.SubElement(observation_category_coding_node_rs,'system',value="http://terminology.hl7.org/CodeSystem/observation-category")
    observation_category_coding_code_node = ET.SubElement(observation_category_coding_node_rs,'code',value="laboratory")
    observation_code_node_rs = ET.SubElement(observation_node_rs,'code')
    observation_code_coding_node_rs = ET.SubElement(observation_code_node_rs,'coding')
    observation_code_coding_system_node = ET.SubElement(observation_code_coding_node_rs,'system',value="http://loinc.org")
    observation_code_coding_code_node = ET.SubElement(observation_code_coding_node_rs,'code',value="53041-0")
    observation_code_coding_display_node = ET.SubElement(observation_code_coding_node_rs,'display',value="DNA region of interest panel")
    observation_subject_node_rs = ET.SubElement(observation_node_rs,'subject')
    observation_subject_reference_node_rs = ET.SubElement(observation_subject_node_rs,'reference',value="Patient/"+patientID)

    #component 1 Region-studied
    observation_component1_node_rs = ET.SubElement(observation_node_rs,'component')
    observation_component1_code_node_rs = ET.SubElement(observation_component1_node_rs,'code')
    observation_component1_code_coding_node_rs = ET.SubElement(observation_component1_code_node_rs,'coding')
    observation_component1_code_coding_system_node_rs = ET.SubElement(observation_component1_code_coding_node_rs,'system',value="http://loinc.org")
    observation_component1_code_coding_code_node_rs = ET.SubElement(observation_component1_code_coding_node_rs,'code',value="51959-5")
    observation_component1_code_coding_display_node_rs = ET.SubElement(observation_component1_code_coding_node_rs,'display',value="Range(s) of DNA sequence examined")
    observation_component1_valueRange_node_rs = ET.SubElement(observation_component1_node_rs,'valueRange')
    observation_component1_valueRange_low_node_rs = ET.SubElement(observation_component1_valueRange_node_rs,'low')
    observation_component1_valueRange_low_value_node_rs = ET.SubElement(observation_component1_valueRange_low_node_rs,'value',value=str(queryRange.at[0,"START"]))
    observation_component1_valueRange_high_node_rs = ET.SubElement(observation_component1_valueRange_node_rs,'high')
    observation_component1_valueRange_high_value_node_rs = ET.SubElement(observation_component1_valueRange_high_node_rs,'value',value=str(queryRange.at[0,"END"]))

    #component 2 Region-studied
    observation_component2_node_rs = ET.SubElement(observation_node_rs,'component')
    observation_component2_code_node_rs = ET.SubElement(observation_component2_node_rs,'code')
    observation_component2_code_coding_node_rs = ET.SubElement(observation_component2_code_node_rs,'coding')
    observation_component2_code_coding_system_node_rs = ET.SubElement(observation_component2_code_coding_node_rs,'system',value="http://loinc.org")
    observation_component2_code_coding_code_node_rs = ET.SubElement(observation_component2_code_coding_node_rs,'code',value="tbd-coordinate system")
    observation_component2_code_coding_display_node_rs = ET.SubElement(observation_component2_code_coding_node_rs,'display',value="Genomic coordinate system")
    observation_component2_valueCodeableConcept_node_rs = ET.SubElement(observation_component2_node_rs,'valueCodeableConcept')
    observation_component2_valueCodeableConcept_coding_node_rs = ET.SubElement(observation_component2_valueCodeableConcept_node_rs,'coding')
    observation_component2_valueCodeableConcept_coding_system_node_rs = ET.SubElement(observation_component2_valueCodeableConcept_coding_node_rs,'system',value="http://hl7.org/fhir/uv/genomics-reporting/CodeSystem/genetic-coordinate-system")
    observation_component2_valueCodeableConcept_coding_code_node_rs = ET.SubElement(observation_component2_valueCodeableConcept_coding_node_rs,'code',value="1")

    #component 3 Region-studied
    observation_component3_node_rs = ET.SubElement(observation_node_rs,'component')
    observation_component3_code_node_rs = ET.SubElement(observation_component3_node_rs,'code')
    observation_component3_code_coding_node_rs = ET.SubElement(observation_component3_code_node_rs,'coding')
    observation_component3_code_coding_system_node_rs = ET.SubElement(observation_component3_code_coding_node_rs,'system',value="http://loinc.org")
    observation_component3_code_coding_code_node_rs = ET.SubElement(observation_component3_code_coding_node_rs,'code',value="48013-7")
    observation_component3_code_coding_display_node_rs = ET.SubElement(observation_component3_code_coding_node_rs,'display',value="Genomic reference sequence ID")
    observation_component3_valueCodeableConcept_node_rs = ET.SubElement(observation_component3_node_rs,'valueCodeableConcept')
    observation_component3_valueCodeableConcept_coding_node_rs = ET.SubElement(observation_component3_valueCodeableConcept_node_rs,'coding')
    observation_component3_valueCodeableConcept_coding_system_node_rs = ET.SubElement(observation_component3_valueCodeableConcept_coding_node_rs,'system',value="http://www.ncbi.nlm.nih.gov/nuccore")
    observation_component3_valueCodeableConcept_coding_code_node_rs = ET.SubElement(observation_component3_valueCodeableConcept_coding_node_rs,'code',value=refSeq)


    dvuids = {}

    for index in alleles.index:
        # Observation structure
        #described-variants
        dvuid = uuid4().hex[:13]
        dvuids.update({ str(alleles.at[index,'POS']) : dvuid})
        contained_node_dv = ET.SubElement(data,'contained') 
        observation_node_dv = ET.SubElement(contained_node_dv,'Observation')  
        observation_id_node_dv = ET.SubElement(observation_node_dv,'id',value="dv-"+dvuid)  
        observation_meta_node_dv = ET.SubElement(observation_node_dv,'meta')
        observation_meta_profile_node_dv = ET.SubElement(observation_meta_node_dv,'profile',value="http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/obs-variant")
        observation_status_node_dv =  ET.SubElement(observation_node_dv,'status',value="final")
        observation_category_node_dv = ET.SubElement(observation_node_dv,'category')
        observation_category_coding_node_dv = ET.SubElement(observation_category_node_dv,'coding')
        observation_category_coding_system_node = ET.SubElement(observation_category_coding_node_dv,'system',value="http://terminology.hl7.org/CodeSystem/observation-category")
        observation_category_coding_code_node = ET.SubElement(observation_category_coding_node_dv,'code',value="laboratory")
        observation_code_node_dv = ET.SubElement(observation_node_dv,'code')
        observation_code_coding_node_dv = ET.SubElement(observation_code_node_dv,'coding')
        observation_code_coding_system_node = ET.SubElement(observation_code_coding_node_dv,'system',value="http://loinc.org")
        observation_code_coding_code_node = ET.SubElement(observation_code_coding_node_dv,'code',value="69548-6")
        observation_code_coding_display_node = ET.SubElement(observation_code_coding_node_dv,'display',value="Genetic variant assessment")
        observation_subject_node_dv = ET.SubElement(observation_node_dv,'subject')
        observation_subject_reference_node_dv = ET.SubElement(observation_subject_node_dv,'reference',value="Patient/"+patientID)
        observation_valueCodeableConcept_node_dv = ET.SubElement(observation_node_dv,'valueCodeableConcept')
        observation_valueCodeableConcept_coding_node_dv = ET.SubElement(observation_valueCodeableConcept_node_dv,'coding')
        observation_valueCodeableConcept_system_system_node_dv = ET.SubElement(observation_valueCodeableConcept_coding_node_dv,'system',value="http://loinc.org")
        observation_valueCodeableConcept_code_code_node_dv = ET.SubElement(observation_valueCodeableConcept_coding_node_dv,'code',value="LA9633-4")
        observation_valueCodeableConcept_display_display_node_dv = ET.SubElement(observation_valueCodeableConcept_coding_node_dv,'display',value="Present")

        #Component1 Described-variant
        observation_component1_node_dv = ET.SubElement(observation_node_dv,'component')
        observation_component1_code_node_dv = ET.SubElement(observation_component1_node_dv,'code')
        observation_component1_code_coding_node_dv = ET.SubElement(observation_component1_code_node_dv,'coding')
        observation_component1_code_coding_system_node_dv = ET.SubElement(observation_component1_code_coding_node_dv,'system',value="http://loinc.org")
        observation_component1_code_coding_code_node_dv = ET.SubElement(observation_component1_code_coding_node_dv,'code',value="62374-4")
        observation_component1_code_coding_display_node_dv = ET.SubElement(observation_component1_code_coding_node_dv,'display',value="Human reference sequence assembly version")
        observation_component1_valueCodeableConcept_node_dv = ET.SubElement(observation_component1_node_dv,'valueCodeableConcept')
        observation_component1_valueCodeableConcept_coding_node_dv = ET.SubElement(observation_component1_valueCodeableConcept_node_dv,'coding')
        observation_component1_valueCodeableConcept_coding_system_node_dv = ET.SubElement(observation_component1_valueCodeableConcept_coding_node_dv,'system',value="http://loinc.org")
        observation_component1_valueCodeableConcept_coding_code_node_dv = ET.SubElement(observation_component1_valueCodeableConcept_coding_node_dv,'code',value="LA14029-5")
        observation_component1_valueCodeableConcept_coding_display_node_dv = ET.SubElement(observation_component1_valueCodeableConcept_coding_node_dv,'display',value="GRCh37")

        #Component2 Described-variant
        observation_component2_node_dv = ET.SubElement(observation_node_dv,'component')
        observation_component2_code_node_dv = ET.SubElement(observation_component2_node_dv,'code')
        observation_component2_code_coding_node_dv = ET.SubElement(observation_component2_code_node_dv,'coding')
        observation_component2_code_coding_system_node_dv = ET.SubElement(observation_component2_code_coding_node_dv,'system',value="http://loinc.org")
        observation_component2_code_coding_code_node_dv = ET.SubElement(observation_component2_code_coding_node_dv,'code',value="48013-7")
        observation_component2_code_coding_display_node_dv = ET.SubElement(observation_component2_code_coding_node_dv,'display',value="Genomic reference sequence ID")
        observation_component2_valueCodeableConcept_node_dv = ET.SubElement(observation_component2_node_dv,'valueCodeableConcept')
        observation_component2_valueCodeableConcept_coding_node_dv = ET.SubElement(observation_component2_valueCodeableConcept_node_dv,'coding')
        observation_component2_valueCodeableConcept_coding_system_node_dv = ET.SubElement(observation_component2_valueCodeableConcept_coding_node_dv,'system',value="http://www.ncbi.nlm.nih.gov/nuccore")
        observation_component2_valueCodeableConcept_coding_code_node_dv = ET.SubElement(observation_component2_valueCodeableConcept_coding_node_dv,'code',value=refSeq)

        #Component3 Described-variant
        observation_component3_node_dv = ET.SubElement(observation_node_dv,'component')
        observation_component3_code_node_dv = ET.SubElement(observation_component3_node_dv,'code')
        observation_component3_code_coding_node_dv = ET.SubElement(observation_component3_code_node_dv,'coding')
        observation_component3_code_coding_system_node_dv = ET.SubElement(observation_component3_code_coding_node_dv,'system',value="http://loinc.org")
        observation_component3_code_coding_code_node_dv = ET.SubElement(observation_component3_code_coding_node_dv,'code',value="53034-5")
        observation_component3_code_coding_display_node_dv = ET.SubElement(observation_component3_code_coding_node_dv,'display',value="Allelic state")
        observation_component3_valueCodeableConcept_node_dv = ET.SubElement(observation_component3_node_dv,'valueCodeableConcept')
        observation_component3_valueCodeableConcept_coding_node_dv = ET.SubElement(observation_component3_valueCodeableConcept_node_dv,'coding')
        observation_component3_valueCodeableConcept_coding_system_node_dv = ET.SubElement(observation_component3_valueCodeableConcept_coding_node_dv,'system',value="http://loinc.org")
        observation_component3_valueCodeableConcept_coding_code_node_dv = ET.SubElement(observation_component3_valueCodeableConcept_coding_node_dv,'code',value=alleles.at[index,'CODE'])
        observation_component3_valueCodeableConcept_coding_display_node_dv = ET.SubElement(observation_component3_valueCodeableConcept_coding_node_dv,'display',value=alleles.at[index,'ALLELE'])

        #Component4 Described-variant
        observation_component4_node_dv = ET.SubElement(observation_node_dv,'component')
        observation_component4_code_node_dv = ET.SubElement(observation_component4_node_dv,'code')
        observation_component4_code_coding_node_dv = ET.SubElement(observation_component4_code_node_dv,'coding')
        observation_component4_code_coding_system_node_dv = ET.SubElement(observation_component4_code_coding_node_dv,'system',value="http://loinc.org")
        observation_component4_code_coding_code_node_dv = ET.SubElement(observation_component4_code_coding_node_dv,'code',value="69547-8")
        observation_component4_code_coding_display_node_dv = ET.SubElement(observation_component4_code_coding_node_dv,'display',value="Genomic Ref allele")
        observation_component4_valueString_node_dv = ET.SubElement(observation_component4_node_dv,'valueString', value=alleles.at[index,'REF'])

        #Component5 Described-variant
        observation_component5_node_dv = ET.SubElement(observation_node_dv,'component')
        observation_component5_code_node_dv = ET.SubElement(observation_component5_node_dv,'code')
        observation_component5_code_coding_node_dv = ET.SubElement(observation_component5_code_node_dv,'coding')
        observation_component5_code_coding_system_node_dv = ET.SubElement(observation_component5_code_coding_node_dv,'system',value="http://loinc.org")
        observation_component5_code_coding_code_node_dv = ET.SubElement(observation_component5_code_coding_node_dv,'code',value="69551-0")
        observation_component5_code_coding_display_node_dv = ET.SubElement(observation_component5_code_coding_node_dv,'display',value="Genomic Alt allele")
        observation_component5_valueString_node_dv = ET.SubElement(observation_component5_node_dv,'valueString', value=alleles.at[index,'ALT'])


        #component6 Described-variant
        observation_component6_node_dv = ET.SubElement(observation_node_dv,'component')
        observation_component6_code_node_dv = ET.SubElement(observation_component6_node_dv,'code')
        observation_component6_code_coding_node_dv = ET.SubElement(observation_component6_code_node_dv,'coding')
        observation_component6_code_coding_system_node_dv = ET.SubElement(observation_component6_code_coding_node_dv,'system',value="http://loinc.org")
        observation_component6_code_coding_code_node_dv = ET.SubElement(observation_component6_code_coding_node_dv,'code',value="tbd-coordinate system")
        observation_component6_code_coding_display_node_dv = ET.SubElement(observation_component6_code_coding_node_dv,'display',value="Genomic coordinate system")
        observation_component6_valueCodeableConcept_node_dv = ET.SubElement(observation_component6_node_dv,'valueCodeableConcept')
        observation_component6_valueCodeableConcept_coding_node_dv = ET.SubElement(observation_component6_valueCodeableConcept_node_dv,'coding')
        observation_component6_valueCodeableConcept_coding_system_node_dv = ET.SubElement(observation_component6_valueCodeableConcept_coding_node_dv,'system',value="http://hl7.org/fhir/uv/genomics-reporting/CodeSystem/genetic-coordinate-system")
        observation_component6_valueCodeableConcept_coding_code_node_dv = ET.SubElement(observation_component6_valueCodeableConcept_coding_node_dv,'code',value="1")

        #component7 Described-variant 
        observation_component7_node_dv = ET.SubElement(observation_node_dv,'component')
        observation_component7_code_node_dv = ET.SubElement(observation_component7_node_dv,'code')
        observation_component7_code_coding_node_dv = ET.SubElement(observation_component7_code_node_dv,'coding')
        observation_component7_code_coding_system_node_dv = ET.SubElement(observation_component7_code_coding_node_dv,'system',value="http://loinc.org")
        observation_component7_code_coding_code_node_dv = ET.SubElement(observation_component7_code_coding_node_dv,'code',value="81254-5")
        observation_component7_code_coding_display_node_dv = ET.SubElement(observation_component7_code_coding_node_dv,'display',value="Genomic Allele start-end")
        observation_component7_valueRange_node_dv = ET.SubElement(observation_component7_node_dv,'valueRange')
        observation_component7_valueRange_low_node_dv = ET.SubElement(observation_component7_valueRange_node_dv,'low')
        observation_component7_valueRange_low_value_node_dv = ET.SubElement(observation_component7_valueRange_low_node_dv,'value',value=str(alleles.at[index,'POS']))


    if nocall:
        #component Region-studied (No call region)
        for index in noCallRegion.index:
            observation_component4_node_rs = ET.SubElement(observation_node_rs,'component')
            observation_component4_code_node_rs = ET.SubElement(observation_component4_node_rs,'code')
            observation_component4_code_coding_node_rs = ET.SubElement(observation_component4_code_node_rs,'coding')
            observation_component4_code_coding_system_node_rs = ET.SubElement(observation_component4_code_coding_node_rs,'system',value="http://loinc.org")
            observation_component4_code_coding_code_node_rs = ET.SubElement(observation_component4_code_coding_node_rs,'code',value="TBD-noCallRegion")
            observation_component4_code_coding_display_node_rs = ET.SubElement(observation_component4_code_coding_node_rs,'display',value="No call region")
            observation_component4_valueRange_node_rs = ET.SubElement(observation_component4_node_rs,'valueRange')
            observation_component4_valueRange_low_node_rs = ET.SubElement(observation_component4_valueRange_node_rs,'low')
            observation_component4_valueRange_low_value_node_rs = ET.SubElement(observation_component4_valueRange_low_node_rs,'value',value=str(noCallRegion.at[index,'START']))
            observation_component4_valueRange_high_node_rs = ET.SubElement(observation_component4_valueRange_node_rs,'high')
            observation_component4_valueRange_high_value_node_rs = ET.SubElement(observation_component4_valueRange_high_node_rs,'value',value=str(noCallRegion.at[index,'END']))
    
    siduids = []
    
    for index in sequenceRels.index:
        dvRef1 = dvuids.get(str(sequenceRels.at[index,'POS1']))
        dvRef2 = dvuids.get(str(sequenceRels.at[index,'POS2']))
        siduid = uuid4().hex[:13]
        siduids.append(siduid)
        contained_node_sid = ET.SubElement(data,'contained') 
        observation_node_sid = ET.SubElement(contained_node_sid,'Observation')  
        observation_id_node_sid = ET.SubElement(observation_node_sid,'id',value="sid-"+siduid)  
        observation_meta_node_sid = ET.SubElement(observation_node_sid,'meta')
        observation_meta_profile_node_sid = ET.SubElement(observation_meta_node_sid,'profile',value="http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/obs-sequence-phase-reltn")
        observation_status_node_sid =  ET.SubElement(observation_node_sid,'status',value="final")
        observation_category_node_sid = ET.SubElement(observation_node_sid,'category')
        observation_category_coding_node_sid = ET.SubElement(observation_category_node_sid,'coding')
        observation_category_coding_system_node = ET.SubElement(observation_category_coding_node_sid,'system',value="http://terminology.hl7.org/CodeSystem/observation-category")
        observation_category_coding_code_node = ET.SubElement(observation_category_coding_node_sid,'code',value="laboratory")
        observation_code_node_sid = ET.SubElement(observation_node_sid,'code')
        observation_code_coding_node_sid = ET.SubElement(observation_code_node_sid,'coding')
        observation_code_coding_system_node = ET.SubElement(observation_code_coding_node_sid,'system',value="http://loinc.org")
        observation_code_coding_code_node = ET.SubElement(observation_code_coding_node_sid,'code',value="82120-7")
        observation_code_coding_display_node = ET.SubElement(observation_code_coding_node_sid,'display',value="Sequence phase relationship")
        observation_subject_node_sid = ET.SubElement(observation_node_sid,'subject')
        observation_subject_reference_node_sid = ET.SubElement(observation_subject_node_sid,'reference',value="Patient/"+patientID)
        observation_valueCodeableConcept_node_sid = ET.SubElement(observation_node_sid,'valueCodeableConcept')
        observation_valueCodeableConcept_coding_node_sid = ET.SubElement(observation_valueCodeableConcept_node_sid,'coding')
        observation_valueCodeableConcept_system_system_node_sid = ET.SubElement(observation_valueCodeableConcept_coding_node_sid,'system',value="http://loinc.org")
        observation_valueCodeableConcept_code_code_node_sid = ET.SubElement(observation_valueCodeableConcept_coding_node_sid,'code',value="TBD-cisTrans")
        observation_valueCodeableConcept_display_display_node_sid = ET.SubElement(observation_valueCodeableConcept_coding_node_sid,'display',value=sequenceRels.at[index,'Relation'])
        observation_derivedFrom_node_sid = ET.SubElement(observation_node_sid,'derivedFrom')
        observation_derivedFrom_reference_node_sid = ET.SubElement(observation_derivedFrom_node_sid,'reference',value="#dv-"+dvRef1)
        observation_reference_node_sid = ET.SubElement(observation_node_sid,'reference',value="#dv-"+dvRef2)
        observation_derivedFrom_node_sid = ET.SubElement(observation_node_sid,'derivedFrom')


    #Final status and issued values
    status_node = ET.SubElement(data,'status',value="final")
    code_node = ET.SubElement(data,'code')
    code_coding_node = ET.SubElement(code_node,'coding')
    code_coding_system_node = ET.SubElement(code_coding_node,'system',value="http://loinc.org")
    code_coding_code_node = ET.SubElement(code_coding_node,'code',value="51969-4")
    code_coding_display_node = ET.SubElement(code_coding_node,'display',value="Genetic analysis report") 
    subject_node = ET.SubElement(data,'subject')
    subject_reference_node_rs = ET.SubElement(subject_node,'reference',value="Patient/"+patientID)
    issued_node = ET.SubElement(data,'issued',value=Utilities.getFhirDate()) 
    result_node = ET.SubElement(data,'result')
    result_reference_node_rs = ET.SubElement(result_node,'reference',value="#rs-"+rsuid)

    for pos,uid in dvuids.items():
        result_node = ET.SubElement(data,'result')
        result_reference_node_dv = ET.SubElement(result_node,'reference',value="#dv-"+uid)

    for uid in siduids:
        result_node = ET.SubElement(data,'result')
        result_reference_node_sid = ET.SubElement(result_node,'reference',value="#sid-"+uid)

    # create a new XML file with the results
    fhirXMLReport = ET.tostring(data).decode('utf-8')
    fhirXMLReport =prettify(data)

    with open(FHIR_XML_RESULT, "w") as fhirXML:
        fhirXML.write(fhirXMLReport)

    try:
        getFhirJSON(cleanVcf,nextelem,patientID,gender,refSeq,nocall)

    except Exception as e:
        logging.error(e)

    return FHIR_JSON_RESULT


def getEmptyFhirXML(patientID,gender,refSeq,nocall=False):
    logging.info("[Generating empty FHIR report]")

    noCallRegion,queryRange = getNoCallableData(NO_CALL_FILE,QUERY_RANGE_FILE)
    start = queryRange.at[0,"START"]
    end = queryRange.at[0,"END"]

    if not noCallRegion.empty:
        if noCallRegion['START'].iloc[0] <= queryRange['START'].iloc[0]:
            noCallRegion['START'].iloc[0] = queryRange['START'].iloc[0]

        if noCallRegion['END'].iloc[-1] >= queryRange['END'].iloc[0]:
            noCallRegion['END'].iloc[-1] = queryRange['END'].iloc[0]
    else:
        nocall = False

    # DiagnosticReport structure
    data = ET.Element('DiagnosticReport',xmlns="http://hl7.org/fhir")
    id_node = ET.SubElement(data,'id',value="dr-"+uuid4().hex[:13])
    meta_node = ET.SubElement(data,'meta')
    profile_node = ET.SubElement(meta_node,'profile',value="http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/diagnosticreport")  
    contained_node_rs = ET.SubElement(data,'contained')   

    # Observation structure
    #region-studied
    rsuid = uuid4().hex[:13]
    observation_node_rs = ET.SubElement(contained_node_rs,'Observation')  
    observation_id_node_rs = ET.SubElement(observation_node_rs,'id',value="rs-"+rsuid)  
    observation_meta_node_rs = ET.SubElement(observation_node_rs,'meta')
    observation_meta_profile_node_rs = ET.SubElement(observation_meta_node_rs,'profile',value="http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/obs-region-studied")
    observation_status_node_rs =  ET.SubElement(observation_node_rs,'status',value="final")
    observation_category_node_rs = ET.SubElement(observation_node_rs,'category')
    observation_category_coding_node_rs = ET.SubElement(observation_category_node_rs,'coding')
    observation_category_coding_system_node = ET.SubElement(observation_category_coding_node_rs,'system',value="http://terminology.hl7.org/CodeSystem/observation-category")
    observation_category_coding_code_node = ET.SubElement(observation_category_coding_node_rs,'code',value="laboratory")
    observation_code_node_rs = ET.SubElement(observation_node_rs,'code')
    observation_code_coding_node_rs = ET.SubElement(observation_code_node_rs,'coding')
    observation_code_coding_system_node = ET.SubElement(observation_code_coding_node_rs,'system',value="http://loinc.org")
    observation_code_coding_code_node = ET.SubElement(observation_code_coding_node_rs,'code',value="53041-0")
    observation_code_coding_display_node = ET.SubElement(observation_code_coding_node_rs,'display',value="DNA region of interest panel")
    observation_subject_node_rs = ET.SubElement(observation_node_rs,'subject')
    observation_subject_reference_node_rs = ET.SubElement(observation_subject_node_rs,'reference',value="Patient/"+patientID)

    # #component 1 Region-studied
    observation_component1_node_rs = ET.SubElement(observation_node_rs,'component')
    observation_component1_code_node_rs = ET.SubElement(observation_component1_node_rs,'code')
    observation_component1_code_coding_node_rs = ET.SubElement(observation_component1_code_node_rs,'coding')
    observation_component1_code_coding_system_node_rs = ET.SubElement(observation_component1_code_coding_node_rs,'system',value="http://loinc.org")
    observation_component1_code_coding_code_node_rs = ET.SubElement(observation_component1_code_coding_node_rs,'code',value="51959-5")
    observation_component1_code_coding_display_node_rs = ET.SubElement(observation_component1_code_coding_node_rs,'display',value="Range(s) of DNA sequence examined")
    observation_component1_valueRange_node_rs = ET.SubElement(observation_component1_node_rs,'valueRange')
    observation_component1_valueRange_low_node_rs = ET.SubElement(observation_component1_valueRange_node_rs,'low')
    observation_component1_valueRange_low_value_node_rs = ET.SubElement(observation_component1_valueRange_low_node_rs,'value',value=str(queryRange.at[0,"START"]))
    observation_component1_valueRange_high_node_rs = ET.SubElement(observation_component1_valueRange_node_rs,'high')
    observation_component1_valueRange_high_value_node_rs = ET.SubElement(observation_component1_valueRange_high_node_rs,'value',value=str(queryRange.at[0,"END"]))

    # #component 2 Region-studied
    observation_component2_node_rs = ET.SubElement(observation_node_rs,'component')
    observation_component2_code_node_rs = ET.SubElement(observation_component2_node_rs,'code')
    observation_component2_code_coding_node_rs = ET.SubElement(observation_component2_code_node_rs,'coding')
    observation_component2_code_coding_system_node_rs = ET.SubElement(observation_component2_code_coding_node_rs,'system',value="http://loinc.org")
    observation_component2_code_coding_code_node_rs = ET.SubElement(observation_component2_code_coding_node_rs,'code',value="tbd-coordinate system")
    observation_component2_code_coding_display_node_rs = ET.SubElement(observation_component2_code_coding_node_rs,'display',value="Genomic coordinate system")
    observation_component2_valueCodeableConcept_node_rs = ET.SubElement(observation_component2_node_rs,'valueCodeableConcept')
    observation_component2_valueCodeableConcept_coding_node_rs = ET.SubElement(observation_component2_valueCodeableConcept_node_rs,'coding')
    observation_component2_valueCodeableConcept_coding_system_node_rs = ET.SubElement(observation_component2_valueCodeableConcept_coding_node_rs,'system',value="http://hl7.org/fhir/uv/genomics-reporting/CodeSystem/genetic-coordinate-system")
    observation_component2_valueCodeableConcept_coding_code_node_rs = ET.SubElement(observation_component2_valueCodeableConcept_coding_node_rs,'code',value="1")

    # #component 3 Region-studied
    observation_component3_node_rs = ET.SubElement(observation_node_rs,'component')
    observation_component3_code_node_rs = ET.SubElement(observation_component3_node_rs,'code')
    observation_component3_code_coding_node_rs = ET.SubElement(observation_component3_code_node_rs,'coding')
    observation_component3_code_coding_system_node_rs = ET.SubElement(observation_component3_code_coding_node_rs,'system',value="http://loinc.org")
    observation_component3_code_coding_code_node_rs = ET.SubElement(observation_component3_code_coding_node_rs,'code',value="48013-7")
    observation_component3_code_coding_display_node_rs = ET.SubElement(observation_component3_code_coding_node_rs,'display',value="Genomic reference sequence ID")
    observation_component3_valueCodeableConcept_node_rs = ET.SubElement(observation_component3_node_rs,'valueCodeableConcept')
    observation_component3_valueCodeableConcept_coding_node_rs = ET.SubElement(observation_component3_valueCodeableConcept_node_rs,'coding')
    observation_component3_valueCodeableConcept_coding_system_node_rs = ET.SubElement(observation_component3_valueCodeableConcept_coding_node_rs,'system',value="http://www.ncbi.nlm.nih.gov/nuccore")
    observation_component3_valueCodeableConcept_coding_code_node_rs = ET.SubElement(observation_component3_valueCodeableConcept_coding_node_rs,'code',value=refSeq)


    if nocall:
        #component Region-studied (No call region)
        for index in noCallRegion.index:
            observation_component4_node_rs = ET.SubElement(observation_node_rs,'component')
            observation_component4_code_node_rs = ET.SubElement(observation_component4_node_rs,'code')
            observation_component4_code_coding_node_rs = ET.SubElement(observation_component4_code_node_rs,'coding')
            observation_component4_code_coding_system_node_rs = ET.SubElement(observation_component4_code_coding_node_rs,'system',value="http://loinc.org")
            observation_component4_code_coding_code_node_rs = ET.SubElement(observation_component4_code_coding_node_rs,'code',value="TBD-noCallRegion")
            observation_component4_code_coding_display_node_rs = ET.SubElement(observation_component4_code_coding_node_rs,'display',value="No call region")
            observation_component4_valueRange_node_rs = ET.SubElement(observation_component4_node_rs,'valueRange')
            observation_component4_valueRange_low_node_rs = ET.SubElement(observation_component4_valueRange_node_rs,'low')
            observation_component4_valueRange_low_value_node_rs = ET.SubElement(observation_component4_valueRange_low_node_rs,'value',value=str(noCallRegion.at[index,'START']))
            observation_component4_valueRange_high_node_rs = ET.SubElement(observation_component4_valueRange_node_rs,'high')
            observation_component4_valueRange_high_value_node_rs = ET.SubElement(observation_component4_valueRange_high_node_rs,'value',value=str(noCallRegion.at[index,'END']))


    fhirXMLReport = ET.tostring(data).decode('utf-8')
    fhirXMLReport =prettify(data) 

    with open(FHIR_XML_RESULT, "w") as fhirXML:
        fhirXML.write(fhirXMLReport)

    FHIR_JSON_RESULT = getEmptyFhirJSON(patientID,start,end,refSeq,nocall)
    return FHIR_JSON_RESULT