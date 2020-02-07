import struct
import subprocess
import random
import os
import sys
from glob import glob
import shutil
import uuid

global main_coverage #union of all coverages
main_coverage = set()
global inputProbability #Array of probabilities of each input being selected to be run through tested program
inputProbability=[1.0]
global parents
global parents_cov
global children
global children_cov
safetybarrier = 5000
fullFuzzing = False
sessionId = uuid.uuid4()

numberOfEpochs=1000 #Number of tries in one generation to get new coverages

def cleanFiles(path):
    for file in glob(path):
        os.unlink(file)

def load_file(fname):
    with open(fname, "rb") as f:
        result = bytearray(f.read())
        return result

def save_file(fname,data):
    if isinstance(data, str) == False:
        with open(fname,"wb") as f:
            f.write(bytearray(data))
    else:
        with open(fname,"w") as f:
            f.write(data)

def mutate_bits(data):
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
    count = int(len(data) * 0.01)
    if count == 0:
        count=1
    for _ in range(count):
        data[random.randint(0,len(data)-1)] = random.randint(ord('a'),ord('z'))
    return data

def mutate_magic(data):
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

def chose_input_probabilities(input_samples):
    if(len(input_samples) != len(parents_cov)):
        print("Wrong size of coverage set or inputs set")
        print("Input sample: %i" %len(input_samples))
        print("Coverage sample: %i" %len(parents_cov))
        return -1

    #set input probability
    insideInputProbability = reevaluateCoverage(parents_cov)
    fitSum = 0.0
    for x in insideInputProbability:
        fitSum = fitSum + float(x)
    insideInputProbability = [x/fitSum for x in insideInputProbability]

    return insideInputProbability
    #amount of blocks in coverage + uniqness + gdb crashSS

def calculate_fitness(coverage_set):
    return float(len(coverage_set)) #+ uniqueness(coverage_set) + gdb_report(coverage_set)

def fullsum(coverages):
    sum = 0
    for x in coverages:
        sum = sum + len(x)
    return float(sum)

def parentsToChildren(children,children_cov,parents,parents_cov):
    uniqueSet = set()
    while(len(children) + len(uniqueSet) < len(parents)):
        position = random.choice(range(len(parents)))
        uniqueSet.add(position)
    for x in uniqueSet:
        children.append(parents[x])
        children_cov.append(parents_cov[x])
    return children, children_cov

def run_gdb(exename):
    #subprocess.check_call([exename,"test.sample"],timeout=2)
    p = subprocess.Popen(["gdb","--batch","-x","detect.gdb",exename],
                         stdout=subprocess.PIPE,
                         stderr = None)
    output, _ = p.communicate()

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

def run_cov(exename,input_name,iteration,sessionId):
    global errorcode
    global inputProbability
    global children
    global children_cov
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
            shutil.copyfile("test.sample","./inputs/input.{}.session:{},unique:{}.sample".format(iteration,sessionId,uuid.uuid4()))

            children.append(load_file(input_name))
            #Add new coverage to coverages
            coverage_file  = open("./cov/coverage.{}.session:{},unique:{}.txt".format(iteration,sessionId,uuid.uuid4()),"w")

            for data in c:
                coverage_file.write(str(data)+"\n")
            coverage_file.close()
            children_cov.append(c)

            #Bound them together - same text
            main_coverage.update(c)
            fname = "input_%u.sample" % len(main_coverage)
            print "Found new block.", len(main_coverage), fname
            
            shutil.copyfile("test.sample",fname)
    return None

def run_original(exename,input_name,session_id):
    global errorcode
    global parents
    global parents_cov
    tmp_cov =[]
    for x in range(1):
        p = subprocess.Popen([exename,input_name],
                            env=os.environ,
                            stdout=subprocess.PIPE,
                            stderr = subprocess.PIPE)
        output, error = p.communicate()
        errorcode = p.returncode
        for cov in glob("./cov/*.sancov"):
            c = get_coverage(cov)
            os.unlink(cov)
            tmp_cov.append(c)   
    mini = tmp_cov[0]
    maxi = tmp_cov[0]
    for i in tmp_cov:
        if mini>i:
            mini=i
        if maxi < i:
            maxi=i
    parents_cov.append(mini)
    main_coverage.update(mini)
    coverage_file  = open("./cov/coverage.input.session:{}.txt".format(session_id),"w")
    for data in mini:
        coverage_file.write(str(data)+"\n")
    coverage_file.close()
    return None

cleanFiles("./cov/*.*")
cleanFiles("./inputs/*.*")

os.environ["ASAN_OPTIONS"]="coverage=1, coverage_dir=./cov"


for cov in glob("./cov/*.sancov"):
    os.unlink(cov)

parents =[]
inputFiles = ["input.txt","input2.txt"]
for x in inputFiles:
    parents.append(load_file(x))
#parents = [load_file("input.txt"),load_file("input2.txt")] #old generation inputs
parents_cov = [] #old generation coverages
children = [] #new generation inputs
children_cov =[] #new generation coverage

errorcode=0
i=1 #to prevent new generation on entry into fullFuzzing mode
#execution of a original input to generate coverage file for it
for x in inputFiles:
    print("Run with: ",x)
    output = run_original("./a.out",x,sessionId)
    if output != None:
        print("CRASH")
        save_file("crash.sample.%i" % i, mutated_sample)
        save_file("crash.sample.%i.txt" % i, output)
print("Coveraages: " , parents_cov)
print(main_coverage)
inputProbability = chose_input_probabilities(parents)
print("Probabilities:",inputProbability)
#first x iterations of the fuzzer to check if there is a possible error with address sanitizer
#get out of function on new coverage or a crush
for iteration in range(safetybarrier):
    sys.stdout.write("%i"%errorcode)
    sys.stdout.flush()
    mutated_sample = mutate(parents[selectIndexFromListOfProbabilities(inputProbability)])
    save_file("test.sample", mutated_sample)
    output = run_cov("./a.out","test.sample",i,sessionId)

    if output != None:
        #run with gdb
        print("CRASH")
        save_file("crash.sample.%i" % i, mutated_sample)
        save_file("crash.sample.%i.txt" % i, output)
        break
    if children_cov: #found new coverage
        print("New coverage - proceeding to full fuzzing mode")
        fullFuzzing = True
        break



#infinite loop of fuzzer
if fullFuzzing:
    while True:
        if i%numberOfEpochs==0 and children:
            if(len(children) < len(parents)):
                parentsToChildren(children,children_cov,parents,parents_cov)
            print("Old coverage: ", main_coverage)
            main_coverage =[]
            print("Children Inputs: ", children)
            print("Children Covs: ", children_cov)
            parents=children
            parents_cov=children_cov
            children=[]
            children_cov=[]
            print("Parents Inputs: ", parents)
            print("Parents Covs: ", parents_cov)
            print("Children Inputs: ", children)
            print("Children Covs: ", children_cov)
            inputProbability = chose_input_probabilities(parents)
            print("probabilities are: ", inputProbability)
            main_coverage = createMainSet(parents_cov)
            print("New coverage: ", main_coverage)
        i=i+1
        sys.stdout.write("%i"%errorcode)
        sys.stdout.flush()
        mutated_sample = mutate(parents[selectIndexFromListOfProbabilities(inputProbability)])
        save_file("test.sample", mutated_sample)
        output = run_cov("./a.out","test.sample",i,sessionId)
        if output != None:
            #run with gdb
            print("CRASH")
            save_file("crash.sample.%i" % i, mutated_sample)
            save_file("crash.sample.%i.txt" % i, output)
            break

## TODO:
# lot of temporary files
# optimalisation
#longer work more files
#change place of updating main coverage (Partial generation devision)
#make it work with more then 1 initial input
#solve the problem if unique identifiers for files (only crashes left)
#Test with full on crash