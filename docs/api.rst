.. _api:

Developer Interface
===================

vcf2fhir
~~~~~~~~~~

This part of the documentation covers all the interfaces of vcf2fhir. For
parts where vcf2fhir depends on external libraries, we document the most
important right here and provide links to the canonical documentation.


Main Interface
--------------

All of Requests' functionality can be accessed by these 5 modules.

========
vcf2fhir
========

***********************************************************************
common.py
***********************************************************************
converter.py
***********************************************************************
fhir_helper.py
***********************************************************************
gene_ref_seq.py
***********************************************************************
json_generator.py
***********************************************************************

common.py
~~~~~~~~~

This module contains the helper functions for generating the fhir response.

**Usage from vcf2fhir.common import _Utilities**

**_Utilities.getFhirDate():**
This function returns the current date into fhir format i.e 2020-09-30T13:00:00Z

**_Utilities.getSequenceRelation(phasedRecMap): **
This function takes an argument of Phase Records and returns the Sequence relations in the form of a dataframe of a Relation Table with columns,'POS1','POS2', and 'Relation'.

**_Utilities.getAllelicState(record):**
This function takes an argument of vcf file records as a data frame and returns a dictionary of allelic state and allelic code as {'ALLELE': allelicState, 'CODE' : allelicCode}

**_Utilities.extract_chrom_identifier(chrom):**
This function takes an argument of chromosome and in case of “CHR” returns “” and in case of “MT” returns “M” to normalise the regions in FHIR response.

**_Utilities._error_log_allelicstate(record):**
This function takes an argument of vcf file records as a dataframe and logs an error in case Allelic State cannot be determined.
 
converter.py
~~~~~~~~~~~~~~~~~

This module contains the converter methods to convert a vcf file to FHIR response

Usage from vcf2fhir.converter import Converter

**Converter.convert(output_filename='fhir.json'):**
This function takes in a default argument as output_filename=’fhir.json’ and returns True on a successful conversion.

**Converter._fix_conv_region_zero_based(conv_region_dict):**

This function takes an argument of the conversion region as a dataframe and fixes the “Start” and “End” of the same.

**Converter._generate_exception(msg):**
This function takes an argument as a message to be shown as a custom error log.

fhir_helper.py
~~~~~~~~~~~~~~~~~~~~~

This Module contain helper functions for generating the FHIR response, it includes fhir client library components which helps in translating vcf file to a fhir response

**Usage from vcf2fhir.fhir_helper import _Fhir_Helper**

**_get_region_studied_component(reportable_query_regions,nocall_regions): **      
This function takes two arguments as reportable query regions and no callable regions and returns observation rs component of the FHIR response

**_addPhaseRecords(record):**
This function takes an argument of a vcf file dataframe record and sets the PS of the record to phased record and in case it the record is not phased, it returns null

**initalizeReport():**
This function initializes the fhir report with the report components like report id, meta, status, code, subject, issued and contained

**add_regionstudied_obv(ref_seq, reportable_query_regions, nocall_regions):**
This function takes reference sequence, reportable query region as well as no callable regions as arguments and appends region studied to the contained object for the fhir report  

**add_variant_obv(record, ref_seq):**
This function takes reference sequence and data frame of vcf records as arguments and appends region studied and description variants to the observation object for the fhir report   

**add_phased_relationship_obv():**
This function internally fetches sequence relationships from the phased records and appends their observation sid to the contained object of the fhr report
 
**add_report_result():**
This function appends the fhir reference of the report to the report object of fhir report
 
**generate_final_json():**
This method builds an ordered dictionary having resourceType, id, meta, contained, status ,code, subject , issued and result objects for the final fhir response object. This final report object is then converted to a json fhir response.

**export_fhir_json(self, output_filename):**
This function takes an argument of filename and exports the json fhir response to the argument of filename.

gene_ref_seq.py
~~~~~~~~~~~~~~~~~

This module has the gene table for build 37 and build 38 for each chromosome
**Usage from vcf2fhir.gene_ref_seq import ***

**_get_ref_seq_by_chrom(build,chrom):**
This function takes build number and chromosome as arguments and returns the corresponding reference sequence by the build number and chromosome.


json_generator.py
~~~~~~~~~~~~~~~~~

This module has helper functions and methods to generate json response for the fhir diagnostic report.
 
**Usage from vcf2fhir.json_generator import ***

**_valid_record(record):**
This function takes a dataframe record and checks for its validity according to FHIR rules and standards. It returns False in case of an invalid record.
 
**_get_chrom(chrom_index):**
This function takes chromosome index as an argument and returns its corresponding character equivalent for chromosome index 23, 24 and 25.
 
**_fix_regions_chrom(region):**
This function takes the region studied as an argument and fixes the chromosome in case of “M“ and “MT” using a helper function from Utilities.

**_add_record_variants(record, ref_seq, patientID, fhir_helper):**
This function takes a dataframe of vcf record, reference sequence, patient ID and a fhir helper object as arguments to add valid variant observations of the record and reference sequence 

**_add_region_studied(region_studied, nocall_region, fhir_helper, chrom, ref_seq, patientID):**
This function takes records of region studied, no callable regions, chromosomes, reference sequences, patient ID and a fhir helper object to add the arguments to the region studied observations for generating a fhir response.

**_get_fhir_json(vcf_reader, ref_build, patientID, has_tabix, conversion_region, region_studied, nocall_region, output_filename):**
This function is responsible to get the fhir helper object for a patient ID as an argument of conversion_region, region studied and no callable regions ,which fixes chromosome regions before proceeding for the report generation.
This function has tabix support as wel which can be used by passing has_tabix=True.
The additional parameters contribute to the internal helper function calls to generate a json for FHIR diagnostic report.



Licensing
~~~~~~~~~

One key difference that has nothing to do with the API is a change in the
license from the ISC_ license to the `Apache 2.0`_ license. The Apache 2.0
license ensures that contributions to Requests are also covered by the Apache
2.0 license.

.. _ISC: https://opensource.org/licenses/ISC
.. _Apache 2.0: https://opensource.org/licenses/Apache-2.0

