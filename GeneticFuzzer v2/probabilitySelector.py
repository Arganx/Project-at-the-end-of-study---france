import random

def selectIndexFromListOfProbabilities(probabilityList):
    chosenValue=random.uniform(0, 1)
    sumDistribution=0
    for i in range(len(probabilityList)):
        sumDistribution = sumDistribution + probabilityList[i]
        if(chosenValue<sumDistribution):
            return i

probabilityList = [0.1, 0.5, 0.1,0.3]
amountOfHits = []
for i in probabilityList:
    amountOfHits.append(0.0)
rang = 1000000

for i in range(rang):
    index = selectIndexFromListOfProbabilities(probabilityList)
    amountOfHits[index] = amountOfHits[index] +1.0

print(amountOfHits)
amountOfHits = [x / rang for x in amountOfHits]
print(amountOfHits)