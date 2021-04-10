import doctest
import unittest
import os
import vcf2fhir
import json
from os.path import join, dirname
import shutil
import logging
from vcf2fhir.common import ignore_warnings

suite = doctest.DocTestSuite(vcf2fhir)


def _get_uids_map(fhir_json):
    obv_ids = []
    result_ids = []
    for index, obv in enumerate(fhir_json['contained']):
        id = obv['id']
        obv_ids.append(f'#{id}')
        fhir_json['contained'][index]['id'] = ''

    for index, result in enumerate(fhir_json['result']):
        result_ids.append(result['reference'])
        fhir_json['result'][index]['reference'] = ''
    fhir_json['id'] = ''
    return {'obv_ids': obv_ids, 'result_ids': result_ids}


def _validate_phase_rel(fhir_json, map_variant_index):
    for index_seq, list_index_var in map_variant_index.items():
        for index, ref in enumerate(
                fhir_json['contained'][index_seq]['derivedFrom']):
            variant_id = fhir_json['contained'][list_index_var[index]]['id']
            if not ref['reference'] == f'#{variant_id}':
                return False
            s1 = 'contained'
            s2 = 'derivedFrom'
            s3 = 'reference'
            fhir_json[s1][index_seq][s2][index][s3] = ''
    return True


class TestVcf2FhirInputs(unittest.TestCase):

    @ignore_warnings
    def test_required_vcf_filename(self):
        with self.assertRaises(Exception) as context:
            vcf2fhir.Converter()
        self.assertTrue(
            'You must provide vcf_filename' in str(context.exception))

    @ignore_warnings
    def test_invalid_vcf_filename(self):
        self.assertRaises(FileNotFoundError,
                          vcf2fhir.Converter, *['Hello', 'GRCh38'])

    @ignore_warnings
    def test_required_ref_build(self):
        with self.assertRaises(Exception) as context:
            vcf2fhir.Converter(os.path.join(
                os.path.dirname(__file__), 'vcf_example1.vcf'))
        self.assertEqual(
            'You must provide build number ("GRCh37" or "GRCh38")', str(
                context.exception))

    @ignore_warnings
    def test_invalid_ref_build(self):
        with self.assertRaises(Exception) as context:
            vcf2fhir.Converter(os.path.join(
                os.path.dirname(__file__), 'vcf_example1.vcf'), 'b38')
        self.assertEqual(
            'You must provide build number ("GRCh37" or "GRCh38")', str(
                context.exception))

    @ignore_warnings
    def test_valid_ref_build_37(self):
        o_vcf_2_fhir = vcf2fhir.Converter(os.path.join(
            os.path.dirname(__file__), 'vcf_example1.vcf'), 'GRCh37')
        self.assertEqual(type(o_vcf_2_fhir), vcf2fhir.Converter)

    @ignore_warnings
    def test_valid_ref_build_38(self):
        o_vcf_2_fhir = vcf2fhir.Converter(os.path.join(
            os.path.dirname(__file__), 'vcf_example1.vcf'), 'GRCh38')
        self.assertEqual(type(o_vcf_2_fhir), vcf2fhir.Converter)

    @ignore_warnings
    def test_conv_region_only(self):
        conv_region_filename = os.path.join(os.path.dirname(
            __file__), 'RegionsToConvert_example3.bed')
        o_vcf_2_fhir = vcf2fhir.Converter(
            os.path.join(
                os.path.dirname(__file__),
                'vcf_example3.vcf'),
            'GRCh37',
            'abc',
            conv_region_filename=conv_region_filename)
        self.assertEqual(type(o_vcf_2_fhir), vcf2fhir.Converter)

    @ignore_warnings
    def test_conv_region_dict(self):
        conv_region_dict = {
            "Chromosome": ["X", "X", "M"],
            "Start": [50001, 55001, 50001],
            "End": [52001, 60601, 60026]
        }
        o_vcf_2_fhir = vcf2fhir.Converter(
            os.path.join(
                os.path.dirname(__file__),
                'vcf_example3.vcf'),
            'GRCh37',
            'abc',
            conv_region_dict=conv_region_dict)
        self.assertEqual(type(o_vcf_2_fhir), vcf2fhir.Converter)

    @ignore_warnings
    def test_conv_region_region_studied(self):
        region_studied_filename = os.path.join(
            os.path.dirname(__file__), 'RegionsStudied_example3.bed')
        conv_region_filename = os.path.join(os.path.dirname(
            __file__), 'RegionsToConvert_example3.bed')
        o_vcf_2_fhir = vcf2fhir.Converter(
            os.path.join(
                os.path.dirname(__file__),
                'vcf_example3.vcf'),
            'GRCh37',
            'abc',
            conv_region_filename=conv_region_filename,
            region_studied_filename=region_studied_filename)
        self.assertEqual(type(o_vcf_2_fhir), vcf2fhir.Converter)

    @ignore_warnings
    def test_conv_region_nocall(self):
        conv_region_filename = os.path.join(os.path.dirname(
            __file__), 'RegionsToConvert_example3.bed')
        nocall_filename = os.path.join(os.path.dirname(
            __file__), 'NoncallableRegions_example3.bed')
        with self.assertRaises(Exception) as context:
            vcf2fhir.Converter(
                os.path.join(
                    os.path.dirname(__file__),
                    'vcf_example3.vcf'),
                'GRCh37',
                'abc',
                conv_region_filename=conv_region_filename,
                nocall_filename=nocall_filename)
        self.assertEqual(
            ('Please also provide region_studied_filename ' +
             'when nocall_filename is provided'), str(
                context.exception))

    @ignore_warnings
    def test_no_conv_region_region_studied(self):
        region_studied_filename = os.path.join(
            os.path.dirname(__file__), 'RegionsStudied_example3.bed')
        o_vcf_2_fhir = vcf2fhir.Converter(
            os.path.join(
                os.path.dirname(__file__),
                'vcf_example3.vcf'),
            'GRCh37',
            'abc',
            region_studied_filename=region_studied_filename)
        self.assertEqual(type(o_vcf_2_fhir), vcf2fhir.Converter)

    @ignore_warnings
    def test_no_conv_region_nocall(self):
        nocall_filename = os.path.join(os.path.dirname(
            __file__), 'NoncallableRegions_example3.bed')
        with self.assertRaises(Exception) as context:
            vcf2fhir.Converter(
                os.path.join(
                    os.path.dirname(__file__),
                    'vcf_example3.vcf'),
                'GRCh37',
                'abc',
                nocall_filename=nocall_filename)
        self.assertEqual(
            ('Please also provide region_studied_filename ' +
             'when nocall_filename is provided'), str(
                context.exception))


class TestTranslation(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.TEST_RESULT_DIR = os.path.join(
            os.path.dirname(__file__), 'output')
        if os.path.exists(self.TEST_RESULT_DIR):
            shutil.rmtree(self.TEST_RESULT_DIR)
        os.mkdir(self.TEST_RESULT_DIR)

    @classmethod
    def tearDownClass(self):
        shutil.rmtree(self.TEST_RESULT_DIR)

    @ignore_warnings
    def test_wo_patient_id(self):
        self.maxDiff = None
        o_vcf_2_fhir = vcf2fhir.Converter(os.path.join(
            os.path.dirname(__file__), 'vcf_example1.vcf'), 'GRCh37')
        output_filename = os.path.join(os.path.dirname(
            __file__), self.TEST_RESULT_DIR, 'fhir_wo_patient_example1.json')
        expected_output_filename = os.path.join(
            os.path.dirname(__file__), 'expected_example1_wo_patient.json')
        o_vcf_2_fhir.convert(output_filename)
        with open(output_filename) as output_file,\
                open(expected_output_filename) as expected_output_file:
            actual_fhir_json = json.load(output_file)
            # Validate the passed sequence relationship
            self.assertEqual(_validate_phase_rel(
                actual_fhir_json, {8: [5, 6]}), True)
            # Validate: list of observation uids and list of result uids same.
            # Also set the uids to '' to avoid guid comparison in next step
            map_ids = _get_uids_map(actual_fhir_json)
            self.assertEqual(map_ids['obv_ids'], map_ids['result_ids'])
            actual_fhir_json['issued'] = ''
            # Finally, check if the acutal json after removing all uids is
            # same as expected json
            expected_fhir_json = json.load(expected_output_file)
            self.assertEqual(actual_fhir_json, expected_fhir_json)

    @ignore_warnings
    def test_with_patient_id(self):
        self.maxDiff = None
        o_vcf_2_fhir = vcf2fhir.Converter(os.path.join(os.path.dirname(
            __file__), 'vcf_example1.vcf'), 'GRCh37', 'HG00628')
        output_filename = os.path.join(os.path.dirname(
            __file__), self.TEST_RESULT_DIR, 'fhir_with_patient_example1.json')
        expected_output_filename = os.path.join(os.path.dirname(
            __file__), 'expected_example1_with_patient.json')
        o_vcf_2_fhir.convert(output_filename)
        with open(output_filename) as output_file,\
                open(expected_output_filename) as expected_output_file:
            actual_fhir_json = json.load(output_file)
            # Validate the passed sequence relationship
            self.assertEqual(_validate_phase_rel(
                actual_fhir_json, {8: [5, 6]}), True)
            # Validate: list of observation uids and list of result uids same.
            # Also set the uids to '' to avoid guid comparison in next step
            map_ids = _get_uids_map(actual_fhir_json)
            self.assertEqual(map_ids['obv_ids'], map_ids['result_ids'])
            actual_fhir_json['issued'] = ''
            # Finally, check if the acutal json after removing all uids is
            # same as expected json
            expected_fhir_json = json.load(expected_output_file)
            self.assertEqual(actual_fhir_json, expected_fhir_json)

    # FIXME: just a temporary test, later change it to a test that test
    # particular variant
    @ignore_warnings
    def test_anotherfile(self):
        o_vcf_2_fhir = vcf2fhir.Converter(os.path.join(os.path.dirname(
            __file__), 'vcf_example2.vcf'), 'GRCh37', 'HG00628')
        o_vcf_2_fhir.convert(output_filename=os.path.join(
            os.path.dirname(__file__), self.TEST_RESULT_DIR, 'fhir2.json'))

    @ignore_warnings
    def test_region_studied(self):
        self.maxDiff = None
        region_studied_filename = os.path.join(
            os.path.dirname(__file__), 'RegionsStudied_example3.bed')
        conv_region_filename = os.path.join(os.path.dirname(
            __file__), 'RegionsToConvert_example3.bed')
        nocall_filename = os.path.join(os.path.dirname(
            __file__), 'NoncallableRegions_example3.bed')
        output_filename = os.path.join(os.path.dirname(
            __file__), self.TEST_RESULT_DIR, 'fhir_example3.json')
        expected_output_filename = os.path.join(
            os.path.dirname(__file__), 'expected_example3.json')
        o_vcf_2_fhir = vcf2fhir.Converter(
            os.path.join(
                os.path.dirname(__file__),
                'vcf_example3.vcf'),
            'GRCh38',
            'HG00628',
            conv_region_filename=conv_region_filename,
            region_studied_filename=region_studied_filename,
            nocall_filename=nocall_filename)
        o_vcf_2_fhir.convert(output_filename)
        with open(output_filename) as output_file,\
                open(expected_output_filename) as expected_output_file:
            actual_fhir_json = json.load(output_file)
            # Validate the passed sequence relationship
            self.assertEqual(_validate_phase_rel(
                actual_fhir_json, {7: [2, 3], 8: [3, 4]}), True)
            # Validate: list of observation uids and list of result uids same.
            # Also set the uids to '' to avoid guid comparison in next step
            map_ids = _get_uids_map(actual_fhir_json)
            self.assertEqual(map_ids['obv_ids'], map_ids['result_ids'])
            actual_fhir_json['issued'] = ''
            # Finally, check if the acutal json after removing all uids is
            # same as expected json
            expected_fhir_json = json.load(expected_output_file)
            self.assertEqual(actual_fhir_json, expected_fhir_json)

    @ignore_warnings
    def test_region_studied_dict(self):
        conv_region_dict = {
            "Chromosome": ["X", "X", "M"],
            "Start": [50001, 55001, 50001],
            "End": [52001, 60601, 60026]
        }
        self.maxDiff = None
        region_studied_filename = os.path.join(
            os.path.dirname(__file__), 'RegionsStudied_example3.bed')
        nocall_filename = os.path.join(os.path.dirname(
            __file__), 'NoncallableRegions_example3.bed')
        output_filename = os.path.join(os.path.dirname(
            __file__), self.TEST_RESULT_DIR, 'fhir_example3_dict.json')
        expected_output_filename = os.path.join(
            os.path.dirname(__file__), 'expected_example3.json')
        o_vcf_2_fhir = vcf2fhir.Converter(
            os.path.join(
                os.path.dirname(__file__),
                'vcf_example3.vcf'),
            'GRCh38',
            'HG00628',
            conv_region_dict=conv_region_dict,
            region_studied_filename=region_studied_filename,
            nocall_filename=nocall_filename)
        o_vcf_2_fhir.convert(output_filename)
        with open(output_filename) as output_file,\
                open(expected_output_filename) as expected_output_file:
            actual_fhir_json = json.load(output_file)
            # Validate the passed sequence relationship
            self.assertEqual(_validate_phase_rel(
                actual_fhir_json, {7: [2, 3], 8: [3, 4]}), True)
            # Validate: list of observation uids and list of result uids same.
            # Also set the uids to '' to avoid guid comparison in next step
            map_ids = _get_uids_map(actual_fhir_json)
            self.assertEqual(map_ids['obv_ids'], map_ids['result_ids'])
            actual_fhir_json['issued'] = ''
            # Finally, check if the acutal json after removing all uids is
            # same as expected json
            expected_fhir_json = json.load(expected_output_file)
            self.assertEqual(actual_fhir_json, expected_fhir_json)

    # Check if region studied observation outside the vcf files are also
    # included in fhir report.
    @ignore_warnings
    def test_multiple_region_studied(self):
        self.maxDiff = None
        region_studied_filename = os.path.join(
            os.path.dirname(__file__), 'RegionsStudied_example4.bed')
        conv_region_filename = os.path.join(os.path.dirname(
            __file__), 'RegionsToConvert_example4.bed')
        nocall_filename = os.path.join(os.path.dirname(
            __file__), 'NoncallableRegions_example4.bed')
        output_filename = os.path.join(os.path.dirname(
            __file__), self.TEST_RESULT_DIR, 'fhir_example4.json')
        expected_output_filename = os.path.join(
            os.path.dirname(__file__), 'expected_example4.json')
        o_vcf_2_fhir = vcf2fhir.Converter(
            os.path.join(
                os.path.dirname(__file__),
                'vcf_example4.vcf'),
            'GRCh38',
            'HG00628',
            conv_region_filename=conv_region_filename,
            region_studied_filename=region_studied_filename,
            nocall_filename=nocall_filename)
        o_vcf_2_fhir.convert(output_filename)
        with open(output_filename) as output_file,\
                open(expected_output_filename) as expected_output_file:
            actual_fhir_json = json.load(output_file)
            # Validate the passed sequence relationship
            self.assertEqual(_validate_phase_rel(
                actual_fhir_json, {31: [24, 25], 32: [25, 26]}), True)
            # Validate: list of observation uids and list of result uids same.
            # Also set the uids to '' to avoid guid comparison in next step
            map_ids = _get_uids_map(actual_fhir_json)
            self.assertEqual(map_ids['obv_ids'], map_ids['result_ids'])
            actual_fhir_json['issued'] = ''
            # Finally, check if the acutal json after removing all uids is
            # same as expected json
            expected_fhir_json = json.load(expected_output_file)
            self.assertEqual(actual_fhir_json, expected_fhir_json)

    @ignore_warnings
    def test_region_studied_only(self):
        region_studied_filename = os.path.join(
            os.path.dirname(__file__), 'RegionsStudied_example4.bed')
        output_filename = os.path.join(os.path.dirname(
            __file__), self.TEST_RESULT_DIR, 'fhir_example4_test.json')
        o_vcf_2_fhir = vcf2fhir.Converter(
            os.path.join(
                os.path.dirname(__file__),
                'vcf_example4.vcf'),
            'GRCh38',
            'HG00628',
            region_studied_filename=region_studied_filename)
        o_vcf_2_fhir.convert(output_filename)

    @ignore_warnings
    def test_empty_fhir_json(self):
        conv_region_filename = os.path.join(os.path.dirname(
            __file__), 'RegionsToConvert_empty_example4.bed')
        output_filename = os.path.join(os.path.dirname(
            __file__), self.TEST_RESULT_DIR, 'fhir_example4_test.json')
        o_vcf_2_fhir = vcf2fhir.Converter(
            os.path.join(
                os.path.dirname(__file__),
                'vcf_example4.vcf'),
            'GRCh38',
            'HG00628',
            conv_region_filename=conv_region_filename)
        o_vcf_2_fhir.convert(output_filename)

    @ignore_warnings
    def test_tabix(self):
        self.maxDiff = None
        region_studied_filename = os.path.join(
            os.path.dirname(__file__), 'RegionsStudied_example4.bed')
        conv_region_filename = os.path.join(os.path.dirname(
            __file__), 'RegionsToConvert_example4.bed')
        nocall_filename = os.path.join(os.path.dirname(
            __file__), 'NoncallableRegions_example4.bed')
        output_filename = os.path.join(os.path.dirname(
            __file__), self.TEST_RESULT_DIR, 'fhir_example4_tabix.json')
        expected_output_filename = os.path.join(
            os.path.dirname(__file__), 'expected_example4.json')
        o_vcf_2_fhir = vcf2fhir.Converter(
            os.path.join(
                os.path.dirname(__file__),
                'vcf_example4.vcf.gz'),
            'GRCh38',
            'HG00628',
            has_tabix=True,
            conv_region_filename=conv_region_filename,
            region_studied_filename=region_studied_filename,
            nocall_filename=nocall_filename)
        o_vcf_2_fhir.convert(output_filename)
        with open(output_filename) as output_file,\
                open(expected_output_filename) as expected_output_file:
            actual_fhir_json = json.load(output_file)
            # Validate the passed sequence relationship
            self.assertEqual(_validate_phase_rel(
                actual_fhir_json, {31: [24, 25], 32: [25, 26]}), True)
            # Validate: list of observation uids and list of result uids same.
            # Also set the uids to '' to avoid guid comparison in next step
            map_ids = _get_uids_map(actual_fhir_json)
            self.assertEqual(map_ids['obv_ids'], map_ids['result_ids'])
            actual_fhir_json['issued'] = ''
            # Finally, check if the acutal json after removing all uids is
            # same as expected json
            expected_fhir_json = json.load(expected_output_file)
            self.assertEqual(actual_fhir_json, expected_fhir_json)


class TestLogger(unittest.TestCase):
    def setUp(self):
        # create file handler and set level to debug
        self.log_general_filename = os.path.join(
            os.path.dirname(__file__), self.LOG_DIR, 'general.log')
        self.log_invalid_record_filename = os.path.join(
            os.path.dirname(__file__), self.LOG_DIR, 'invalid_record.log')
        genearl_fh = logging.FileHandler(self.log_general_filename)
        invalid_record_fh = logging.FileHandler(
            self.log_invalid_record_filename)
        genearl_fh.setLevel(logging.DEBUG)
        invalid_record_fh.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # add formatter to fh
        genearl_fh.setFormatter(formatter)
        invalid_record_fh.setFormatter(formatter)
        # store as a class variable
        self.genearl_fh = genearl_fh
        self.invalid_record_fh = invalid_record_fh

    @classmethod
    def setUpClass(self):
        self.LOG_DIR = os.path.join(os.path.dirname(__file__), 'log')
        if os.path.exists(self.LOG_DIR):
            shutil.rmtree(self.LOG_DIR)
        os.mkdir(self.LOG_DIR)

    # TODO: Delete the log folder after running
    # all the tests, below method throws error becasue
    # log files are still in use.
    # @classmethod
    # def tearDownClass(self):
    #     shutil.rmtree(self.LOG_DIR)

    @ignore_warnings
    def test_logger_forks(self):
        region_studied_filename = os.path.join(
            os.path.dirname(__file__), 'RegionsStudied_example3.bed')
        conv_region_filename = os.path.join(os.path.dirname(
            __file__), 'RegionsToConvert_example3.bed')
        nocall_filename = os.path.join(os.path.dirname(
            __file__), 'NoncallableRegions_example3.bed')
        output_filename = os.path.join(os.path.dirname(
            __file__), self.LOG_DIR, 'logging_fhir.json')
        # create logger
        general_logger = logging.getLogger('vcf2fhir.general')
        invalid_record_logger = logging.getLogger('vcf2fhir.invalidrecord')
        general_logger.setLevel(logging.DEBUG)
        invalid_record_logger.setLevel(logging.DEBUG)
        # add ch to logger
        general_logger.addHandler(self.genearl_fh)
        invalid_record_logger.addHandler(self.invalid_record_fh)
        o_vcf_2_fhir = vcf2fhir.Converter(
            os.path.join(
                os.path.dirname(__file__),
                'vcf_example3.vcf'),
            'GRCh38',
            'HG00628',
            conv_region_filename=conv_region_filename,
            region_studied_filename=region_studied_filename,
            nocall_filename=nocall_filename)
        o_vcf_2_fhir.convert(output_filename)
        self.assertEqual(os.path.exists(self.log_general_filename), True)
        self.assertEqual(os.path.exists(
            self.log_invalid_record_filename), True)


suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVcf2FhirInputs))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTranslation))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLogger))


if __name__ == '__main__':
    unittest.main()
