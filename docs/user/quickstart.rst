.. _quickstart:

Quickstart
==========

.. module:: vcf2fhir

Eager to get started? This page gives a good introduction in how to get started
with vcf2fhir.

First, make sure that:

* vcf2fhir is :ref:`installed <install>`
* vcf2fhir is :ref:`up-to-date <updates>`


Let's get started with some simple examples.


Convert a vcf file to Fhir Response
--------------

Making a request with Requests is very simple.

Begin by importing the Requests module::

    >>> import vcf2fhir
    >>> oVcf2Fhir = vcf2fhir.Converter('sample.vcf', 'GRCh37')
    >>> oVcf2Fhir.convert()

Logging
---------------------
You can use python standard [logging](https://docs.python.org/3/library/logging.html) to enable logs. Two logger ('vcf2fhir.general') and ('vcf2fhir.invalidrecord') are avialble to configure.
* **vcf2fhir.general**: standard library logs. 
* **vcf2fhir.invalidrecord**: logs all the records from vcf file which are in conversion region but are not converted to fhir format.

```python
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
'''

Errors and Exceptions
---------------------

In the event of a network problem (e.g. DNS failure, refused connection, etc),
vcf2fhir will raise a :exc:`~vcf2fhir.exceptions.ConnectionError` exception.

-----------------------
