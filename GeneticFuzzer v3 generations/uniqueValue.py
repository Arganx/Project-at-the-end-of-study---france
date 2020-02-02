import uuid
uniqueList =set()
for x in range(1000000):
    uniqueList.add(uuid.uuid4())

print(len(uniqueList))
uniqueList =[]