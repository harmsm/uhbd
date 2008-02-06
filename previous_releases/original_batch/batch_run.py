path = './'
input_path = 'SS_withH/'
output_path = 'uhbd_calcs/'

import os

def setupInp():
    f = open('pkaSH.pdb','r')
    pdb = f.readlines()
    f.close()

    start_index = pdb[1].split()
    end_index = pdb[-2].split()

    f = open('pkaS-doinp.inp','r')
    inp = f.readlines()
    f.close()

    inp[7] = 2*"%s" % (start_index[4],'\n')
    inp[9] = 2*"%s" % (end_index[4],'\n')

    g = open('pkaS-doinp.inp','w')
    g.write("".join(inp))
    g.close()

dir_list = os.listdir(2*"%s" % (path,input_path))

for dir in dir_list:
    total_path = 4*"%s" % (path,input_path,dir,'/')
    os.system(4*"%s" % ('/bin/mkdir ',path,output_path,dir))

    file_list = os.listdir(total_path)
    file_list = [x for x in file_list if x[-4:] == '.pdb']

    for filename in file_list:
        print filename
        os.system(4*"%s" % ('/bin/cp ',total_path,filename,' pkaSH.pdb'))

        setupInp()
        os.system('./run.sh')

        total_output = 5*"%s" % (path,output_path,dir,'/',filename)
        os.system(2*"%s" % ('/bin/mkdir ',total_output[:-4]))
        os.system(2*"%s" % ('/bin/cp pkaS-potentials hybrid.out sitesinpr.pdb ',
                            total_output[:-4]))
        os.system('./cleanup.sh')
