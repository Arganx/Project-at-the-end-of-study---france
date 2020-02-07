set1 = set()
set2 = set()
set3 = set()
set4 = set()
mainSet = set()

newSet = set()

set1.update([1,2,3])
set2.update([3,4])
set3.update([3,4,5,6,7,8])
set4.update([9,10])
print("Input your desired new set")
x = input()

#newSet.update(int(input()))#[1,2,5,6])
newSet.update(map(int, x.split()))
#each unique value 3 times as important as a normal value
#complete uniqness - The block of code not executed previously even once
#partial uniqness - The block of code was never executed in the configuration with outher blocks
mainSet.update(set1,set2,set3,set4)

arrayOfSets = []
arrayOfSets.append(set1)
arrayOfSets.append(set2)
arrayOfSets.append(set3)
arrayOfSets.append(set4)

'''
print(set1)
print(set2)
print(set3)
print(set4)


print("Main Set: " , mainSet)

print("Is it a new block of code: 0- no,", len(newSet.difference(mainSet)))


subsetFlag = 0 #To be delated later in a function
for x in arrayOfSets:
    if newSet.issubset(x):
        print("Superset of " , x)
        subsetFlag = 1
        break
if(not subsetFlag):
    print("Partial uniqness")
'''
#The more generations the slower the algorithm will become, in exchange the randomness will decrease

def uniqnessDeterminationFunction(newSet, arrayOfSets, allSetsCombined): #0 - not unique, 1 - unique, 2 - partialy unique
    print(type(allSetsCombined))
    if(not type(newSet)==type(set()) or not type(arrayOfSets) == type(list()) or not type(allSetsCombined) == type(set())):
        return -1
    #print("newSet: ", newSet)
    #print("allsetsCombined: ", allSetsCombined)
    #print(newSet.difference(allSetsCombined))
    
    if(len(newSet.difference(allSetsCombined))):
        return 1
    for x in arrayOfSets:
        if newSet.issubset(x):
            print("Subset of: ", x)
            return 0
    return 2

print(uniqnessDeterminationFunction(newSet,arrayOfSets,mainSet))
#What about 1 2 vs 123