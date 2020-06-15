import vcf
from .jsonGenerator import getFhirJSON
from .geneRefSeq import getRefSeqByGene,getChrombyGene
class Converter(object):
    def __init__(self, vcf_filename, patient_id, ref_build, sex='M', conv_region_filename=None,variant_types=()):
        if not (vcf_filename):
            raise Exception('You must provide vcf_filename')
        self.vcf_filename = vcf_filename
        self._vcf_reader = vcf.Reader(open(vcf_filename, 'r'))
        self.variant_types = variant_types
        self.patient_id = patient_id
        self.sex = sex
        self.ref_build = ref_build
        self.refSeq = getRefSeqByGene(self.ref_build, 'UROD')
    def convert(self, format='json', output_filename='fhir.json'):
        getFhirJSON(self._vcf_reader,self.patient_id, self.refSeq,  noCall=False, gender=self.sex, output_filename=output_filename)
