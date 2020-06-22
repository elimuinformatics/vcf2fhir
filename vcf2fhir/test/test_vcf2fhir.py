import doctest
import unittest
import os
import vcf2fhir
import json
from os.path import join, dirname
import shutil

suite = doctest.DocTestSuite(vcf2fhir)

def _get_uids_map(fhir_json):
    obv_ids = []
    result_ids = []
    for index, obv in enumerate(fhir_json['contained']):
        id = obv['id']
        obv_ids.append(f"#{id}")
        fhir_json['contained'][index]['id'] = ""

    for index, result in enumerate(fhir_json['result']):
        result_ids.append(result['reference'])
        fhir_json['result'][index]['reference'] = ""
    fhir_json['id'] = ""
    return {'obv_ids' : obv_ids, 'result_ids' : result_ids}

def _validate_phase_rel(fhir_json, map_variant_index):
    for index_seq, list_index_var in map_variant_index.items():
        for index, ref in enumerate(fhir_json['contained'][index_seq]['derivedFrom']):
            variant_id = fhir_json['contained'][list_index_var[index]]['id']
            if not ref['reference'] == f"#{variant_id}":
                return False
            fhir_json['contained'][index_seq]['derivedFrom'][index]['reference'] = ''
    return True

    
class TestVcf2FhirInputs(unittest.TestCase):  
    
    def test_required_vcf_filename(self):
        with self.assertRaises(Exception) as context:
            vcf2fhir.Converter()
        self.assertTrue('You must provide vcf_filename' in str(context.exception))

    def test_invalid_vcf_filename(self):
        self.assertRaises(FileNotFoundError, vcf2fhir.Converter, *['Hello', 'GRCh38'])

    def test_required_ref_build(self):
        with self.assertRaises(Exception) as context:
            vcf2fhir.Converter(os.path.join(os.path.dirname(__file__), 'vcf_example1.vcf'))
        self.assertTrue('You must provide build number ("GRCh37" or "GRCh38)' in str(context.exception))

    def test_invalid_ref_build(self):
        with self.assertRaises(Exception) as context:
            vcf2fhir.Converter(os.path.join(os.path.dirname(__file__), 'vcf_example1.vcf'), 'b38')
        self.assertTrue('You must provide build number ("GRCh37" or "GRCh38)' in str(context.exception))
    
    def test_valid_ref_build_37(self):
        oVcf2Fhir = vcf2fhir.Converter(os.path.join(os.path.dirname(__file__), 'vcf_example1.vcf'), 'GRCh37')
        self.assertEqual(type(oVcf2Fhir), vcf2fhir.Converter)

    def test_valid_ref_build_38(self):
        oVcf2Fhir = vcf2fhir.Converter(os.path.join(os.path.dirname(__file__), 'vcf_example1.vcf'), 'GRCh38')
        self.assertEqual(type(oVcf2Fhir), vcf2fhir.Converter)

class TestTranslation(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.TEST_RESULT_DIR = os.path.join(os.path.dirname(__file__),'output')
        os.mkdir(self.TEST_RESULT_DIR)

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.TEST_RESULT_DIR)

    def test_wo_patient_id(self):
        self.maxDiff = None
        oVcf2Fhir = vcf2fhir.Converter(os.path.join(os.path.dirname(__file__),'vcf_example1.vcf'), 'GRCh37')
        outfult_filename = os.path.join(os.path.dirname(__file__), self.TEST_RESULT_DIR,'fhir1_wo_patient.json')
        expected_outfult_filename = os.path.join(os.path.dirname(__file__),'fhir1_wo_patient_expected.json')
        print(outfult_filename)
        bDone = oVcf2Fhir.convert(outfult_filename)
        # check if translation was completed
        self.assertEqual(bDone, True)
        actual_fhir_json = json.load(open(outfult_filename))
        # Validate the pased sequence relationship
        self.assertEqual(_validate_phase_rel(actual_fhir_json, {8 : [5, 6]}), True)
        # Validate: list of observation uids and list of result uids same.
        # Also set the uids to '' to avoid guid comparison in next step
        map_ids = _get_uids_map(actual_fhir_json)
        self.assertEqual(map_ids['obv_ids'], map_ids['result_ids'])
        actual_fhir_json['issued'] = ''
        # Finally, check if the acutal json after removing all uids is same as exppected json
        expected_fhir_json = json.load(open(expected_outfult_filename))
        self.assertEqual(actual_fhir_json, expected_fhir_json)
    
    def test_with_patient_id(self):
        self.maxDiff = None
        oVcf2Fhir = vcf2fhir.Converter(os.path.join(os.path.dirname(__file__), 'vcf_example1.vcf'), 'GRCh37', 'HG00628')        
        outfult_filename = os.path.join(os.path.dirname(__file__), self.TEST_RESULT_DIR, 'fhir1_with_patient.json')
        expected_outfult_filename = os.path.join(os.path.dirname(__file__),'fhir1_with_patient_expected.json')
        bDone = oVcf2Fhir.convert(outfult_filename)
        # check if translation was completed
        self.assertEqual(bDone, True)
        actual_fhir_json = json.load(open(outfult_filename))
        # Validate the pased sequence relationship
        self.assertEqual(_validate_phase_rel(actual_fhir_json, {8 : [5, 6]}), True)
        # Validate: list of observation uids and list of result uids same.
        # Also set the uids to '' to avoid guid comparison in next step
        map_ids = _get_uids_map(actual_fhir_json)
        self.assertEqual(map_ids['obv_ids'], map_ids['result_ids'])
        actual_fhir_json['issued'] = ''
        # Finally, check if the acutal json after removing all uids is same as exppected json        
        expected_fhir_json = json.load(open(expected_outfult_filename))
        self.assertEqual(actual_fhir_json, expected_fhir_json)

    #FIXME: just a temporary test, later change it to a test that test particular variant
    def test_anotherfile(self):
        oVcf2Fhir = vcf2fhir.Converter(os.path.join(os.path.dirname(__file__), 'vcf_example2.vcf'), 'GRCh37', 'HG00628')
        bDone = oVcf2Fhir.convert(output_filename=os.path.join(os.path.dirname(__file__), self.TEST_RESULT_DIR,'fhir2.json'))
        self.assertEqual(bDone, True)

suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVcf2FhirInputs))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTranslation))

if __name__ == '__main__':
    unittest.main()