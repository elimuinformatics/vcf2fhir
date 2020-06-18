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

# class TestVcfSpecs(unittest.TestCase):

class TestVcf2FhirInputs(unittest.TestCase):
    def test_required_vcf_filename(self):
        with self.assertRaises(Exception) as context:
            vcf2fhir.Converter()
        self.assertTrue('You must provide vcf_filename' in str(context.exception))

    def test_invalid_vcf_filename(self):
        self.assertRaises(FileNotFoundError, vcf2fhir.Converter, *['Hello', 'GRCh38'])

    def test_required_ref_build(self):
        with self.assertRaises(Exception) as context:
            vcf2fhir.Converter(os.path.join(os.path.dirname(__file__), 'HG00628.b37.UROD.M.vcf'))
        self.assertTrue('You must provide build number ("GRCh37" or "GRCh38)' in str(context.exception))

    def test_invalid_ref_build(self):
        with self.assertRaises(Exception) as context:
            vcf2fhir.Converter(os.path.join(os.path.dirname(__file__), 'HG00628.b37.UROD.M.vcf'), 'b38')
        self.assertTrue('You must provide build number ("GRCh37" or "GRCh38)' in str(context.exception))
    
    def test_valid_ref_build_37(self):
        oVcf2Fhir = vcf2fhir.Converter(os.path.join(os.path.dirname(__file__), 'HG00628.b37.UROD.M.vcf'), 'GRCh37')
        self.assertEqual(type(oVcf2Fhir), vcf2fhir.Converter)

    def test_valid_ref_build_38(self):
        oVcf2Fhir = vcf2fhir.Converter(os.path.join(os.path.dirname(__file__), 'HG00628.b37.UROD.M.vcf'), 'GRCh38')
        self.assertEqual(type(oVcf2Fhir), vcf2fhir.Converter)

class TestConversion(unittest.TestCase):
    def test_wo_patient_id(self):
        oVcf2Fhir = vcf2fhir.Converter(os.path.join(os.path.dirname(__file__), 'HG00628.b37.UROD.M.vcf'), 'GRCh37')
        bDone = oVcf2Fhir.convert(output_filename=os.path.join(os.path.dirname(__file__),'fhir1.json'))
        self.assertEqual(bDone, True)
    
    def test_with_patient_id(self):
        oVcf2Fhir = vcf2fhir.Converter(os.path.join(os.path.dirname(__file__), 'HG00628.b37.UROD.M.vcf'), 'GRCh37', 'HG00628')
        bDone = oVcf2Fhir.convert(output_filename=os.path.join(os.path.dirname(__file__),'fhir2.json'))
        self.assertEqual(bDone, True)

    def test_anotherfile(self):
        oVcf2Fhir = vcf2fhir.Converter(os.path.join(os.path.dirname(__file__), 'HG00628.b37.CYP2C19.M.vcf'), 'GRCh37', 'HG00628')
        bDone = oVcf2Fhir.convert(output_filename=os.path.join(os.path.dirname(__file__),'fhir_new.json'))
        self.assertEqual(bDone, True)

suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVcf2FhirInputs))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestConversion))