import pandas as pd


def _getAllelicState(record, gender):
    allelicState = ''
    allelicCode = ''
    # Using  the first sample
    sampleVal = record.samples[0].data.GT
    allele = sampleVal.split('/')
    allelePipe = sampleVal.split('|')
    if len(allelePipe) == 2:
        x = allelePipe[0]
        y = allelePipe[1]
    if len(allele) == 2:
        x = allele[0]
        y = allele[1]
    else:
        if gender == 'M' and record.CHROM == 'MT':
            allelicState = 'Homoplasmic'
            allelicCode = 'LA6704-6'

    if gender == 'F':
        if record.CHROM != 'Y' and record.CHROM != 'MT':
            if x != y:
                allelicState = 'heterozygous'
                allelicCode = 'LA6706-1'
            else:
                allelicState = 'homozygous'
                allelicCode = 'LA6705-3'
    elif gender == 'M':
        if record.CHROM == 'Y' or record.CHROM == 'X':
            allelicState = 'hemizygous'
            allelicCode = 'LA6707-9'
        elif record.CHROM == 'MT':
            if x != y:
                allelicState = 'heteroplasmic'
                allelicCode = 'LA6703-8'
            else:
                allelicState = 'homoplasmic'
                allelicCode = 'LA6704-6'
        else:
            if x != y:
                allelicState = 'heterozygous'
                allelicCode = 'LA6706-1'
            else:
                allelicState = 'homozygous'
                allelicCode = 'LA6705-3'    
    return {'ALLELE': allelicState, 'CODE' : allelicCode}

