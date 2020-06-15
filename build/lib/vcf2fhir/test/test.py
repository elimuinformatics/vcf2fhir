import doctest
import unittest
import os
import vcf2fhir

suite = doctest.DocTestSuite(vcf2fhir)

class TestVcfSpecs(unittest.TestCase):
    def test_vcf_4_0(self):
        print(os.path.join(os.path.dirname(__file__), 'HG00628.b37.UROD.M.vcf'))
        oVcf2Fhir = vcf2fhir.Converter(os.path.join(os.path.dirname(__file__), 'HG00628.b37.UROD.M.vcf'), 'HG00628', 'b37', 'M')
        oVcf2Fhir.convert(format='json', output_filename='fhir1.json')
        print('hello')

suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVcfSpecs))