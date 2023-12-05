from concurrent.futures import ProcessPoolExecutor
from os import getpid as pid
from time import sleep

L = [1,2,3,4,5]

#单进程,要用至少25秒
for i in L:
    sleep(5)
    print(pid(),"已过5秒",i)

#多进程并发，5秒
def SleepPrint (in_value) :
    sleep(5)
    print(pid(),"已过5秒",in_value)
pool = ProcessPoolExecutor(2)
for i in L :
    pool.submit(SleepPrint,i)