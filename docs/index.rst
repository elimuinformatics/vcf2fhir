
Welcome to VCF to FHIR documentation!
=======================================

Release v 0.0.11


.. image:: https://img.shields.io/pypi/l/requests.svg
    :target: https://pypi.org/project/vcf2fhir/

.. image:: https://img.shields.io/pypi/wheel/requests.svg
    :target: https://pypi.org/project/vcf2fhir/


**vcf2fhir** is an elegant and simple library for Python, built for translating vcf files to FHIR diagnostic reports.

-------------------

**Quick Examples**::

    >>> import vcf2fhir
    >>> oVcf2Fhir = vcf2fhir.Converter('sample.vcf', 'GRCh37')
    >>> oVcf2Fhir.convert()


**vcf2fhir** 

Beloved Features
----------------

vcf2fhir is ready for today's web.

**Input:** 

*VCF file (required): Path to a text-based or bgzipped VCF file.*
*Tabix file (required if VCF file is bgzipped): Path to tabix index of VCF file.*
*Genome build (required): Must be one of 'GRCh37' or 'GRCh38'.*
*Patient ID (required): Supplied patient ID is inserted into generated FHIR output.*
*Conversion region (optional): VCF region(s) to convert.*
*Studied region (optional): Genomic regions that have been studied by the lab.*
*Noncallable region (optional): Subset of studied region(s) that are deemed uncallable by the lab.*

**Output:**

*FHIR Genomics Diagnostic Report (in JSON format) that contains converted variants.*

vcf2fhir officially supports Python 3.6+, and runs great on PyPI.


The User Guide
--------------

This part of the documentation, which is mostly prose, begins with some
background information about Requests, then focuses on step-by-step
instructions for getting the most out of Requests.

.. toctree::
   :maxdepth: 2

   user/install
   user/quickstart


The Community Guide
-------------------

This part of the documentation, which is mostly prose, details the
vcf2fhir ecosystem and community.

.. toctree::
   :maxdepth: 2

   community/support
   community/release-process

.. toctree::
   :maxdepth: 1

   community/updates

The API Documentation / Guide
-----------------------------

If you are looking for information on a specific function, class, or method,
this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   api


The Contributor Guide
---------------------

If you want to contribute to the project, this part of the documentation is for
you.

.. toctree::
   :maxdepth: 3

   dev/contributing
   dev/authors

There are no more guides. You are now guideless.
Good luck.