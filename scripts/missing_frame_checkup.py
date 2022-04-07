'''
Docs: https://github.com/davidkastner/pyQMMM/blob/main/pyqmmm/README.md
DESCRIPTION
    If the scratch dir fills up some frames may not be written to the mdcrd.
    This script checks to see if any frames were not written to the mdcrd.
    Author: David Kastner
    Massachusetts Institute of Technology
    kastner (at) mit . edu
'''

################################ DEPENDENCIES ##################################
import re

################################## FUNCTIONS ###################################

def missing_frame_checkup(): 
    print('\n.-----------------------.')
    print('| MISSING FRAME CHECKUP |')
    print('.-----------------------.\n')
    print('Checks a production file for missing frames.')

    # Open the production run MD file
    print('Analyzing production output file ...\n')
    with open('constP_prod.out', 'r') as prod_file:
        nsteps = []
        nstep = 0
        nstlim = '' # The total number of frames
        ntpr = '' # The increment that frame data is written out
        # Identify the nstlim and ntpr variables
        for line in prod_file:
            if not nstlim or not ntpr:
                if line[1:7] ==  'nstlim':
                    line = line.strip()
                    nstlim = int(re.split('[=,]', line)[1])
                if line[1:5] == 'ntpr':
                    line = line.strip()
                    ntpr = int(re.split('[=,]', line)[1])
                continue
            
            # Save the value of nstep to a list
            if line[1:6] == 'NSTEP':
                nstep = int(line[8:].split()[0])
                nsteps.append(nstep)
            if nstep == nstlim:
                break
    
    # Calculate the number of missing nstep progress prints
    total = int(nstlim / ntpr)
    missing = int(nstlim / ntpr - len(nsteps))
    print(f'Out of {total} progress prints, {missing} were missing.')

if __name__ == "__main__":
    missing_frame_checkup()
