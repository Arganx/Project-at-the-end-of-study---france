def uniqnessDeterminationFunction(newSet, arrayOfSets, allSetsCombined): #1 - not unique, 3 - unique, 2 - partialy unique
    if(not type(newSet)==type(set()) or not type(arrayOfSets) == type(list()) or not type(allSetsCombined) == type(set())):
        return -1
    if(len(newSet.difference(allSetsCombined))):
        return 3
    for x in arrayOfSets:
        if newSet.issubset(x):
            return 1
    return 2

def calcFitness(newSet,coverage_sets):
    coverage_sets.append(newSet)
    newFitnesses = reevaluate(coverage_sets)
    fitSum = 0.0
    for x in newFitnesses:
        fitSum = fitSum + float(x)
    print(fitSum)
    newFitnesses = [x/fitSum for x in newFitnesses]
    return newFitnesses
        

def createMainSet(coverageSet):
    mainSet = set()
    for x in coverageSet:
        mainSet.update(x)
    return mainSet

#reevaluation
def reevaluate(coverageSets):
    copyOfSets = coverageSets[:]
    fitnessList = []
    print(copyOfSets)
    for i in range(len(copyOfSets)):
        x = copyOfSets.pop(0)
        print(x)
        tmpMainSet = createMainSet(copyOfSets)
        uniqness = uniqnessDeterminationFunction(x,copyOfSets,tmpMainSet)
        copyOfSets.append(x)
        fitnessList.append(len(x)*uniqness)
    return fitnessList

set1 = set()
set2 = set()
set3 = set()
set4 = set()
set5 = set()

set1.update([1,2,3])
set2.update([7,8,9,10])
set3.update([3,4,5])
set4.update([1,2])
set5.update([7,8,9,10,11])

arrayOfSets = []
arrayOfSets.append(set1)
arrayOfSets.append(set2)
arrayOfSets.append(set3)
arrayOfSets.append(set4)

#print(reevaluate(arrayOfSets))

print(calcFitness(set5,arrayOfSets))

#implement it in the main program with 