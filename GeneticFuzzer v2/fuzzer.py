import struct
import subprocess
import random
import os
import sys
from glob import glob
import shutil

global main_coverage #union of all coverages
main_coverage = set()

def load_file(fname):
    with open(fname, "rb") as f:
        result = bytearray(f.read())
        #returns bytearray
        return result

def save_file(fname,data):
    if isinstance(data, str) == False:
        with open(fname,"wb") as f:
            f.write(bytearray(data))
    else:
        with open(fname,"w") as f:
            f.write(data)

def mutate_bits(data):
    #print("bits")
    count = int((len(data) * 8) * 0.01)
    if count == 0:
        count=1
    for _ in range(count):
        bit = random.randint(0,len(data)*8-1)
        idx_bit = bit%8
        idx_byte = int(bit/8)
        data[idx_byte] ^= 1 << idx_bit
    return data

def mutate_bytes(data):
    #print("bytes")
    count = int(len(data) * 0.01)
    if count == 0:
        count=1
    for _ in range(count):
        data[random.randint(0,len(data)-1)] = random.randint(ord('a'),ord('z'))
    return data

def mutate_magic(data):
    #print("magic")
    numbers = [
        (1,struct.pack("B",0xff)),
        (1,struct.pack("B",0)),
        (1,struct.pack("B",0x7f)),
        (2,struct.pack("H",0xffff)),
        (2,struct.pack("H",0)),
        (4,struct.pack("I",0xffffffff)),
        (4,struct.pack("I",0)),
        (4,struct.pack("I",0x80000000)),
        (4,struct.pack("I",0x40000000)),
        (4,struct.pack("I",0x7fffffff)),
    ]

    count = int(len(data) * 0.01)
    if count == 0:
        count=1
    for _ in range(count):
        n_size, n=random.choice(numbers)
        sz = len(data) -n_size
        if(sz < 0):
            continue
        idx = random.randint(0,sz)
        data[idx:idx+n_size] = bytearray(n)
    return data

    pass

def mutate(data):
    return random.choice([
        #mutate_bits,
        mutate_bytes,
        #mutate_magic
    ])(data[::])

def selectIndexFromListOfProbabilities(probabilityList):
    chosenValue=random.uniform(0, 1)
    sumDistribution=0
    for i in range(len(probabilityList)):
        sumDistribution = sumDistribution + probabilityList[i]
        if(chosenValue<sumDistribution):
            return i

def uniqnessDeterminationFunction(newSet, arrayOfSets, allSetsCombined): #1 - not unique, 3 - unique, 2 - partialy unique
    if(not type(newSet)==type(set()) or not type(arrayOfSets) == type(list()) or not type(allSetsCombined) == type(set())):
        return -1
    if(len(newSet.difference(allSetsCombined))):
        return 3
    for x in arrayOfSets:
        if newSet.issubset(x):
            return 1
    return 2

def createMainSet(coverageSet): #function  used to create main set for a list of sets. Used when calculationg main set for a list with an element removed
    mainSet = set()
    for x in coverageSet:
        mainSet.update(x)
    return mainSet

def reevaluateCoverage(coverageSets):
    copyOfSets = coverageSets[:]
    fitnessList = []
    for i in range(len(copyOfSets)):
        x = copyOfSets.pop(0)
        tmpMainSet = createMainSet(copyOfSets)
        uniqness = uniqnessDeterminationFunction(x,copyOfSets,tmpMainSet)
        copyOfSets.append(x)
        fitnessList.append(len(x)*uniqness)
    return fitnessList

def chose_input(input_samples):
    if(len(input_samples) != len(coverage_sets)):
        print("Wrong size of coverage set or inputs set")
        print("Input sample: %i" %len(input_samples))
        print("Coverage sample: %i" %len(coverage_sets))
        return -1
    print(coverage_sets)
    inputProbability = reevaluateCoverage(coverage_sets)
    fitSum = 0.0
    for x in inputProbability:
        fitSum = fitSum + float(x)
    print(fitSum)
    inputProbability = [x/fitSum for x in inputProbability]
    return inputProbability
    '''
    #amount of blocks in coverage + uniqness + gdb crashSS
    print(coverage_sets)
    fullnumberofcoverages = fullsum(coverage_sets)
    for x in coverage_sets:
        print(float(calculate_fitness(x)/fullnumberofcoverages))
    return len(coverage_sets)#type(coverage_sets).__name__
    #for every new important input reevaluation of all other inputs
    '''

def calculate_fitness(coverage_set):
    return float(len(coverage_set)) #+ uniqueness(coverage_set) + gdb_report(coverage_set)

def fullsum(coverages):
    sum = 0
    for x in coverages:
        sum = sum + len(x)
    return float(sum)

def run_gdb(exename):
    #subprocess.check_call([exename,"test.sample"],timeout=2)
    p = subprocess.Popen(["gdb","--batch","-x","detect.gdb",exename],
                         stdout=subprocess.PIPE,
                         stderr = None)
    output, _ = p.communicate()
    #print("Output", output)

    if "Program received signal" in str(output):
        result = str(output)
        return result.split("kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")[1]
    return None

def get_coverage(covname):
    with open(covname,"rb") as f:
        cov=f.read()
    return set([
        struct.unpack("Q",cov[i:i+8])[0] for i in range(8,len(cov),8)
    ])

def run_cov(exename,input_name,iteration):
    global errorcode
    p = subprocess.Popen([exename,input_name],
                        env=os.environ,
                        stdout=subprocess.PIPE,
                        stderr = subprocess.PIPE)
    output, error = p.communicate()
    errorcode = p.returncode
    for cov in glob("./cov/*.sancov"):
        c = get_coverage(cov)
        os.unlink(cov)#The coverage file stops existing
        if not c.issubset(main_coverage):
            #Add new file to inputs.
            input_file = open("./inputs/input.%i.sample" %iteration,"w")
            shutil.copyfile("test.sample","./inputs/input.%i.sample" % iteration)
            input_file.close()
            #Add new coverage to coverages
            coverage_file  = open("./cov/coverage.%i.txt" % iteration,"w")

            for data in c:
                coverage_file.write(str(data)+"\n")
            coverage_file.close()
            #print("Coverage set before appending in run_cov: " , coverage_sets)
            coverage_sets.append(c)
            #OK
            #Bound them together - same text
            main_coverage.update(c) #NOT OK BUGGED LINE
            #print("Coverage set after appending in run_cov: " , coverage_sets)
            fname = "input_%u.sample" % len(main_coverage)
            print "Found new block.", len(main_coverage), fname
            
            shutil.copyfile("test.sample",fname)
            #input_samples.pop()
            input_samples.append(load_file(fname))
    return None

def run_original(exename,input_name):
    global errorcode
    p = subprocess.Popen([exename,input_name],
                        env=os.environ,
                        stdout=subprocess.PIPE,
                        stderr = subprocess.PIPE)
    output, error = p.communicate()
    errorcode = p.returncode
    for cov in glob("./cov/*.sancov"):
        c = get_coverage(cov)
        os.unlink(cov)
        coverage_sets.append(c)
        #print("Coverage set after run_original: ", coverage_sets)
        main_coverage.update(c)
        coverage_file  = open("./cov/coverage.input.txt","w")
        for data in c:
            coverage_file.write(str(data)+"\n")
        coverage_file.close()
    return None

os.environ["ASAN_OPTIONS"]="coverage=1, coverage_dir=./cov"

#declaration of variable  containing all of the interesting coverage sets
global coverage_sets
coverage_sets = [set()]
coverage_sets.pop()

for cov in glob("./cov/*.sancov"):
    os.unlink(cov)

input_samples = [
    load_file("input.txt")
]

errorcode=0
i=0
#add execution of a original input to generate coverage file for it
output = run_original("./a.out","test.sample")
if output != None:
    print("CRASH")
    save_file("crash.sample.%i" % i, mutated_sample)
    save_file("crash.sample.%i.txt" % i, output)

#infinite loop of fuzzer
while True:
    if i==1000:
        probabilityList = chose_input(input_samples)
        print(probabilityList)
        print("Chosen file: ", selectIndexFromListOfProbabilities(probabilityList))
        break
    i=i+1
    sys.stdout.write("%i"%errorcode)
    sys.stdout.flush()
    mutated_sample = mutate(random.choice(input_samples))
    save_file("test.sample", mutated_sample)
    output = run_cov("./a.out","test.sample",i)
    if output != None:
        #run with gdb
        #test on dumb example
        print("CRASH")
        save_file("crash.sample.%i" % i, mutated_sample)
        save_file("crash.sample.%i.txt" % i, output)
        break

## TODO:
# lot of temporary files
# optimalisation
#longer work more files
