
Welcome to VCF to FHIR documentation!
=======================================

Release v0.0.16


.. image:: https://img.shields.io/pypi/l/requests.svg
    :target: https://pypi.org/project/vcf2fhir/

.. image:: https://img.shields.io/pypi/wheel/requests.svg
    :target: https://pypi.org/project/vcf2fhir/


**vcf2fhir** is an elegant and simple library for Python, built for translating vcf files to FHIR diagnostic reports.

-------------------

**Quick Examples**::

    >>> import vcf2fhir
    >>> Vcf2Fhir = vcf2fhir.Converter('sample.vcf', 'GRCh37')
    >>> Vcf2Fhir.convert()


**vcf2fhir** 
===========
The User Guide
--------------

This part of the documentation, which is mostly prose, begins with some
background information about Requests, then focuses on step-by-step
instructions for getting the most out of Requests.

.. toctree::
   :maxdepth: 2

   user/install
   user/quickstart

Parameters
---------

-  **vcf\_reader** (required): Path to a text-based or bgzipped VCF
   file. Valid path and filename without whitespace must be provided.
   VCF file must conform to VCF Version 4.1 or later. FORMAT.GT must be
   present. Multi-sample VCFs are allowed, but only the first sample
   will be converted.

-  **has\_tabix** (required if VCF file is bgzipped): Set to 'True' if
   there is a tabix index. Tabix file must have the same name as the
   bgzipped VCF file, with a '.tbi' extension, and must be in the same
   folder.

-  **ref\_build** (required): Genome Reference Consortium genome
   assembly to which variants in the VCF were called. Must be one of
   'GRCh37' or 'GRCh38'.

-  **patient\_id** (required): Supplied patient ID is inserted into
   generated FHIR output. Alphanumeric string without whitespace.

-  **Conversion region** (optional): Subset of the VCF file to be
   converted into FHIR. If absent, the entire VCF file is converted. Can
   be supplied as either a parameter (conv\_region\_dict) or as a BED
   file (conv\_region\_filename):

   -  **conv\_region\_dict**: Array of regions (e.g. '{"Chromosome":
      ["X", "X", "M"],"Start": [50001, 55001, 50001],"End": [52001,
      60601, 60026]}'). Values for Chromosome must align with values in
      VCF #CHROM field. Ranges must be
      `0-based <https://www.biostars.org/p/84686/>`__ (or 0-start,
      half-open) and based on GRCh37 or GRCh38 reference sequences.

   -  **conv\_region\_filename**: Valid path and filename without
      whitespace must be provided. Must be a valid BED file with first 3
      columns: <chr> <start> <stop>. Values in <chr> field must align
      with values in VCF #CHROM field. Ranges must be based on GRCh37 or
      GRCh38 reference sequences. Note that BED files are
      `0-based <https://www.biostars.org/p/84686/>`__ (or 0-start,
      half-open) whereas VCF files and FHIR output are 1-based (or
      1-start, fully-closed).

-  **region\_studied\_filename** (optional): Subset of patient's genome
   that was studied in the generation of the VCF file. Valid path and
   filename without whitespace must be provided. Must be a valid BED
   file, with first 3 columns: <chr> <start> <stop>. Values in <chr>
   field must align with values in VCF #CHROM field. Ranges must be
   based on GRCh37 or GRCh38 reference sequences. Note that BED files
   are `0-based <https://www.biostars.org/p/84686/>`__ (or 0-start,
   half-open) whereas VCF files and FHIR output are 1-based (or 1-start,
   fully-closed).

-  **nocall\_filename** (optional): Subset of studied region that is
   deemed noncallable. Valid path and filename without whitespace must
   be provided. Must be a valid BED file, with first 3 columns: <chr>
   <start> <stop>. Values in <chr> field must align with values in VCF
   #CHROM field. Ranges must be based on GRCh37 or GRCh38 reference
   sequences. Note that BED files are
   `0-based <https://www.biostars.org/p/84686/>`__ (or 0-start,
   half-open) whereas VCF files and FHIR output are 1-based (or 1-start,
   fully-closed).


Conversion Examples
------------------

-  Converts all variants in VCF. FHIR report contains no region-studied
   observation.

   ::

       vcf2fhir.Converter('vcftests.vcf','GRCh37', 'aabc')

-  Submitting only noncallable region without other regions generates an
   error.

   ::

       vcf2fhir.Converter('vcftests.vcf','GRCh37', 'babc', nocall_filename='WGS_b37_region_noncallable.bed')

-  Converts all variants in VCF. FHIR report contains one region-studied
   observation per studied chromosome.

   ::

       vcf2fhir.Converter('vcftests.vcf','GRCh37', 'cabc', region_studied_filename='WGS_b37_region_studied.bed')

-  Converts all variants in VCF. FHIR report contains one region-studied
   observation per studied chromosome.

   ::

       vcf2fhir.Converter('vcftests.vcf','GRCh37', 'dabc', region_studied_filename='WGS_b37_region_studied.bed', nocall_filename='WGS_b37_region_noncallable.bed')

-  Converts all variants in conversion region. FHIR report contains no
   region-studied observation.

   ::

       vcf2fhir.Converter('vcftests.vcf','GRCh37', 'eabc', conv_region_filename='WGS_b37_convert_everything.bed')

-  Submitting only noncallable region without other regions generates an
   error.

   ::

       vcf2fhir.Converter('vcftests.vcf','GRCh37', 'fabc', conv_region_filename='WGS_b37_convert_everything.bed', nocall_filename='WGS_b37_region_noncallable.bed')

-  Converts all variants in conversion region. FHIR report contains one
   region-studied observation per studied chromosome, intersected with
   conversion region.

   ::

       vcf2fhir.Converter('vcftests.vcf','GRCh37', 'gabc', conv_region_filename='WGS_b37_convert_everything.bed', region_studied_filename='WGS_b37_region_studied.bed')

-  Converts all variants in conversion region. FHIR report contains one
   region-studied observation per studied chromosome, intersected with
   conversion region.

   ::

       vcf2fhir.Converter('vcftests.vcf','GRCh37', 'habc', conv_region_filename='WGS_b37_convert_everything.bed', region_studied_filename='WGS_b37_region_studied.bed', nocall_filename='WGS_b37_region_noncallable.bed')

-  Conversion of a bgzipped VCF

   ::

       vcf2fhir.Converter('vcf_example4.vcf.gz','GRCh37', 'kabc', has_tabix=True)

