import os, psutil

def getMemoryUsedMB():
    proc = psutil.Process(os.getpid())
    return proc.memory_info()[0] / float(2**20)

    