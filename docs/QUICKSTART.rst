.. _quickstart:

Quickstart
==========

Eager to get started? This page gives a good introduction in how to get started
with vcf2fhir.

Installation
---------------------

Installing vcf2fhir is pretty simple. Here is a step by step plan on how to do it.

.. note::
    vcf2fhir is available on Pypi as ``vcf2fhir``.

Before installing vcf2fhir you need to install cython and wheel:

.. code-block:: bash
    
    pip install cython wheel  
    pip install vcf2fhir

This will install vcf2fhir library.
 
Examples
---------------------

(some sample VCF files are `here <https://github.com/elimuinformatics/vcf2fhir/tree/master/vcf2fhir/test>`_)

Quick example

.. code-block:: python

    import vcf2fhir
    vcf_fhir_converter = vcf2fhir.Converter('sample.vcf', 'GRCh37')
    vcf_fhir_converter.convert()

More Example to instantiate Converter

-  Converts all variants in VCF. FHIR report contains no region-studied
   observation.

.. code-block:: python

       vcf2fhir.Converter('vcftests.vcf','GRCh37', 'aabc')

-  Converts all variants in VCF. FHIR report assign homoplasmic vs.
   heteroplasmic based on:

   If allelic depth (FORMAT.AD)/ read depth (FORMAT.DP) is greater than 0.89
   then allelic state is homoplasmic; else heteroplasmic.

   **Note** : default value of ratio_ad_dp = 0.99 and ratio_ad_dp is considered valid only when value lies between 0 and 1

    .. code-block:: python

        vcf2fhir.Converter('vcftests.vcf','GRCh37', 'aabc', ratio_ad_dp = 0.89)

-  Submitting only noncallable region without other regions generates an
   error.

.. code-block:: python

       vcf2fhir.Converter('vcftests.vcf','GRCh37', 'babc', nocall_filename='WGS_b37_region_noncallable.bed')

-  Converts all variants in VCF. FHIR report contains one region-studied
   observation per studied chromosome.

.. code-block:: python

       vcf2fhir.Converter('vcftests.vcf','GRCh37', 'cabc', region_studied_filename='WGS_b37_region_studied.bed')

-  Converts all variants in VCF. FHIR report contains one region-studied
   observation per studied chromosome.

.. code-block:: python

       vcf2fhir.Converter('vcftests.vcf','GRCh37', 'dabc', region_studied_filename='WGS_b37_region_studied.bed', nocall_filename='WGS_b37_region_noncallable.bed')

-  Converts all variants in conversion region. FHIR report contains no
   region-studied observation.

.. code-block:: python

       vcf2fhir.Converter('vcftests.vcf','GRCh37', 'eabc', conv_region_filename='WGS_b37_convert_everything.bed')

-  Submitting only noncallable region without other regions generates an
   error.

.. code-block:: python

       vcf2fhir.Converter('vcftests.vcf','GRCh37', 'fabc', conv_region_filename='WGS_b37_convert_everything.bed', nocall_filename='WGS_b37_region_noncallable.bed')

-  Converts all variants in conversion region. FHIR report contains one
   region-studied observation per studied chromosome, intersected with
   conversion region.

.. code-block:: python

       vcf2fhir.Converter('vcftests.vcf','GRCh37', 'gabc', conv_region_filename='WGS_b37_convert_everything.bed', region_studied_filename='WGS_b37_region_studied.bed')

-  Converts all variants in conversion region. FHIR report contains one
   region-studied observation per studied chromosome, intersected with
   conversion region.

.. code-block:: python

       vcf2fhir.Converter('vcftests.vcf','GRCh37', 'habc', conv_region_filename='WGS_b37_convert_everything.bed', region_studied_filename='WGS_b37_region_studied.bed', nocall_filename='WGS_b37_region_noncallable.bed')

-  Conversion of a bgzipped VCF

.. code-block:: python

       vcf2fhir.Converter('vcf_example4.vcf.gz','GRCh37', 'kabc', has_tabix=True)

Logging
---------------------
You can use python standard `logging <https://docs.python.org/3/library/logging.html>`_ to enable logs. Two logger ('vcf2fhir.general') and ('vcf2fhir.invalidrecord') are avialble to configure.

-  **vcf2fhir.general**: standard library logs. 

-  **vcf2fhir.invalidrecord**: logs all the records from vcf file which are in conversion region but are not converted to fhir format.

.. code-block:: python

    >>> import logging
    # create logger
    >>> logger = logging.getLogger('vcf2fhir.invalidrecord')
    >>> logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    >>> ch = logging.FileHandler('invalidrecord.log')
    >> ch.setLevel(logging.DEBUG)
    # create formatter
    >>> formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    >>> ch.setFormatter(formatter)
    # add ch to logger
    >>> logger.addHandler(ch)

