import cpuinfo
import os
print('Getting CPU Info...')
os.chdir(os.path.dirname(__file__))

cpuinfog = cpuinfo.get_cpu_info()
with open('../README.md', 'a') as f:
    f.write('## CPU Info\n')
    for key, value in cpuinfog.items():
        f.write(f'{key}: {value}  \n')
    f.write('\n')
print('Done!')