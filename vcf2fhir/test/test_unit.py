import doctest
import unittest
import vcf2fhir
from vcf2fhir.common import *

suite = doctest.DocTestSuite(vcf2fhir)


class TestChromIdentifier(unittest.TestCase):

    def test_chrom_1_22(self):
        actual_chrom = ['chr1', '1', 'CHR1', '22', 'CHR22', 'chr22']
        expected_chrom = ['1', '1', '1', '22', '22', '22']
        i = 0
        for chrom in actual_chrom:
            self.assertEqual(extract_chrom_identifier(
                chrom), expected_chrom[i])
            i += 1

    def test_chrom_X_Y(self):
        actual_chrom = ['chrX', 'X', 'x', 'CHRX', 'chrY', 'Y', 'Y', 'CHRY']
        expected_chrom = ['X', 'X', 'X', 'X', 'Y', 'Y', 'Y', 'Y']
        i = 0
        for chrom in actual_chrom:
            self.assertEqual(extract_chrom_identifier(
                chrom), expected_chrom[i])
            i += 1

    def test_chrom_M(self):
        actual_chrom = ['MT', 'm', 'M', 'mt', 'chrm', 'chrM', 'chrmt', 'chrMT']
        expected_chrom = ['M', 'M', 'M', 'M', 'M', 'M', 'M', 'M']
        i = 0
        for chrom in actual_chrom:
            self.assertEqual(extract_chrom_identifier(
                chrom), expected_chrom[i])
            i += 1

    def test_chrom_validation(self):
        actual_chrom = [
            'chrX', 'R', 'mt', 'chrR', 'chrM', 'chrMT',
            'chr30', 'P', 'Z', '45', 'o', 'CHRX', '1', '22', 'CHR21', 'x']
        recognized = [
            True, False, True, False, True, True,
            False, False, False, False, False, True, True, True, True, True]
        i = 0
        for chrom in actual_chrom:
            self.assertEqual(validate_chrom_identifier(
                chrom), recognized[i])
            i += 1


class TestDataType(unittest.TestCase):

    def test_validate_ratio_ad_dp(self):
        ratio_ad_dp = [0.2, 0.65, 0.99, 1.3, -0.7, "Chr", False, True]
        valid = [True, True, True, False, False, False, False, False]
        i = 0
        for value in ratio_ad_dp:
            self.assertEqual(validate_ratio_ad_dp(
                value), valid[i])
            i += 1

    def test_validate_has_tabix(self):
        has_tabix = [True, False, 1, 23.4, 'C', "CHROM"]
        valid = [True, True, False, False, False, False]
        i = 0
        for value in has_tabix:
            self.assertEqual(validate_has_tabix(
                value), valid[i])
            i += 1


suite.addTests(unittest.TestLoader(
).loadTestsFromTestCase(TestChromIdentifier))
suite.addTests(unittest.TestLoader(
).loadTestsFromTestCase(TestDataType))

if __name__ == '__main__':
    unittest.main()
