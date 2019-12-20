import struct
import subprocess
import random

def load_file(fname):
    with open(fname, "rb") as f:
        return bytearray(f.read())

def save_file(fname,data):
    if isinstance(data, str) == False:
        with open(fname,"wb") as f:
            f.write(bytearray(data))
    else:
        with open(fname,"w") as f:
            f.write(data)

def mutate_bits(data):
    print("bits")
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
    print("bytes")
    count = int(len(data) * 0.01)
    if count == 0:
        count=1
    for _ in range(count):
        data[random.randint(0,len(data)-1)] = random.randint(0,255)
    return data

def mutate_magic(data):
    print("magic")
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
        mutate_bits,
        mutate_bytes,
        mutate_magic
    ])(data[::])

input_samples = [
    load_file("input.sample")
]

def run(exename):
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
i=0
while True:
    print(i)
    i=i+1
    mutated_sample = mutate(random.choice(input_samples))
    save_file("test.sample", mutated_sample)
    #try:
    output = run("VulnerableProgram.exe")
    if output != None:
        print("CRASH")
        save_file("crash.sample.%i" % i, mutated_sample)
        save_file("crash.sample.%i.txt" % i, output)
        break
    #except subprocess.TimeoutExpired:
    #    print("Expired")
    #    continue
    #except subprocess.CalledProcessError:
