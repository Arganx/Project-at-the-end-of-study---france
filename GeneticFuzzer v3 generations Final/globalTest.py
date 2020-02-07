global globalVariable
globalVariable = 5

def fun():
    global globalVariable
    globalVariable = 7

print(globalVariable)
fun()
print(globalVariable)