import os
import datetime
import pandas as pd
import random, string
import pytz

VCF_FILE = os.path.join(os.getcwd()  + '/downloads/','result.vcf')
NO_CALL_FILE = os.path.join(os.getcwd()  + '/downloads/','nocall.csv')
QUERY_RANGE_FILE = os.path.join(os.getcwd()  + '/downloads/','query.bed') 
XML_TO_JSON_JAR = os.path.join(os.getcwd() ,'xmltojson.jar')
FHIR_XML_RESULT = os.path.join(os.getcwd() ,'fhir.xml')
FHIR_JSON_RESULT = os.path.join(os. getcwd() +'/downloads/','json/')

class Utilities(object):

    """
     * generates current date into fhir format 
     * @return date
     */
    """
    def getFilename(fileUrl):
        return os.path.splitext(fileUrl)[0].split('/')[-1]

    def getBuild(filename):
        return filename.split('.')[1]    
        
    def validateHeaders(vcfDataframe):
        pass

    def randomString():
        x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(15))
        return x

    def getFhirDate(): 
        #x = datetime.datetime.now()
        z = datetime.datetime.now(pytz.timezone('UTC')).strftime("%Y-%m-%dT%H:%M:%S%z")
        return z[:-2]+':'+z[-2:]

    """
     * provides genotype position from the format field from vcf 
     * for phase swap sort algorithm
     * @param  string format
     * @return integer
     */
    """

    def getGenoTypePosition(formatted):
        formatSegment = formatted.split(':')
        for key, value in formatSegment:
            if str(value) == 'GT':
                return key
    """
     * provides phase set position from the format field from vcf 
     * for phase swap sort algorithm
     *
     * @param  string format
     * @return integer
     */
    """
    def getPhaseSetPosition(formatted):
        formatSegment = formatted.split(':')
        for key, value in formatSegment:
            if str(value) == 'GT':
                return key
    """
     * calculate phase set by genotype
     * @param  string gt 
     * @param  string ps
     * @return string
     */
    """
    def getPsByGt(gt,ps):
        formatSegment = gt.split(':')
        for key, value in formatSegment:
            if str(value) == 'GT':
                gtPosition =  key
        alleles = ps.split(":")
        return alleles[gtPosition]; 
    """
    /**
     * returns the mutation type Cis or Trans
     *
     * @param  string gt1
     * @param  string gt2
     * @return string
     */
    """
    def getMutation(gt1, gt2):
        if gt1 == gt2:
            return 'Cis'
        else:
            return 'Trans'
    
    def getPhaseSetPositionValue(phaseSet, position):
        alleles = phaseSet.split(':')
        return alleles[position]
    
    def checkForSlash(phaseSet, position):
        alleles = phaseSet.split(':')
        if "|" in alleles[position]:
            return True
        else:
            return False
        
    def skipHomo(data, position):
        alleles = data.split(':')
        genotype = alleles[position].split(':')
        if genotype[1] == '.':
            genotype[1] = 0
        if genotype[0] == '.':
            genotype[0] = 0
        if genotype[0] == genotype[1]:
            return False
        else:
            return True;
        
    def searchInVarients(index, value, array):
        key = array_search(value, array_column(array, index))
        return array