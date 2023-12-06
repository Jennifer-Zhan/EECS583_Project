import sys

file_path, p_thread_indicator = sys.argv[1], sys.argv[2]
with open(file_path, 'r') as file:
    if p_thread_indicator == '1': file.readline()
    Aw = list(map(int, file.readline().split()))
    Ar = list(map(int, file.readline().split()))
    Anx = list(map(int, file.readline().split()))
    Anp = list(map(int, file.readline().split()))

    write_counter = int(file.readline())
    distinct_write_counter = int(file.readline())

def lrpd_test():
    for i in range(len(Aw)):
        if Ar[i] == Aw[i]: return True
    
    if write_counter == distinct_write_counter: return True

    for i in range(len(Aw)):
        if Aw[i] == Anp[i] == Anx[i]: return False
    
    return True

print('LRPD Test passed, loop is DOALL') if lrpd_test() else print('LRPD test failed, loop is NOT DOALL')