import doctest
import unittest
import os
import vcf2fhir
import json
import jsonschema
from os.path import join, dirname
from jsonschema import validate

suite = doctest.DocTestSuite(vcf2fhir)

def _load_json_schema(filename):
    """ Loads the given schema file """

    relative_path = join('', filename)
    absolute_path = join(dirname(__file__), relative_path)
    with open(absolute_path) as schema_file:
        return json.loads(schema_file.read())

class TestVcfSpecs(unittest.TestCase):
    def test_wo_patient_id(self):
        oVcf2Fhir = vcf2fhir.Converter(os.path.join(os.path.dirname(__file__), 'HG00628.b37.UROD.M.vcf'), 'b37')
        bDone = oVcf2Fhir.convert(format='json', output_filename=os.path.join(os.path.dirname(__file__),'fhir1.json'))
        self.assertEqual(bDone, True)
    
    def test_with_patient_id(self):
        oVcf2Fhir = vcf2fhir.Converter(os.path.join(os.path.dirname(__file__), 'HG00628.b37.UROD.M.vcf'), 'b37', 'HG00628')
        bDone = oVcf2Fhir.convert(format='json', output_filename=os.path.join(os.path.dirname(__file__),'fhir2.json'))
        self.assertEqual(bDone, True)

    def test_anotherfile(self):
        oVcf2Fhir = vcf2fhir.Converter(os.path.join(os.path.dirname(__file__), 'HG00628.b37.CYP2C19.M.vcf'), 'b37', 'HG00628')
        bDone = oVcf2Fhir.convert(format='json', output_filename=os.path.join(os.path.dirname(__file__),'fhir_new.json'))
        self.assertEqual(bDone, True)

suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVcfSpecs))