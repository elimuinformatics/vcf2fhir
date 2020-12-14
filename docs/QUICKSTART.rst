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

 
- Directly install vcf2fhir from Pypi:

    pip install vcf2fhir

- Or, For isolated installtion:

First, obtain Python_ and virtualenv_ if you do not already have them. Using a
virtual environment will make the installation easier, and will help to avoid
clutter in your system-wide libraries. You will also need Git_ in order to
clone the repository.

.. _Python: http://www.python.org/
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _Git: http://git-scm.com/

Once you have these, create a virtual environment somewhere on your disk, then
activate it::

    virtualenv vcf2fhir
    source vcf2fhir/bin/activate


    pip install vcf2fhir



Examples
---------------------

Quick example

    import vcf2fhir
    vcf_fhir_converter = vcf2fhir.Converter('sample.vcf', 'GRCh37')
    vcf_fhir_converter.convert()

More Example to instantiate Converter

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

Logging
---------------------
You can use python standard [logging](https://docs.python.org/3/library/logging.html) to enable logs. Two logger ('vcf2fhir.general') and ('vcf2fhir.invalidrecord') are avialble to configure.
* **vcf2fhir.general**: standard library logs. 
* **vcf2fhir.invalidrecord**: logs all the records from vcf file which are in conversion region but are not converted to fhir format.


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

