'''
See more here: https://github.com/davidkastner/pdb-utilities/blob/main/README.md
DESCRIPTION
   Reunubers waters that restart after reaching 9999
   Author: David Kastner
   Massachusetts Institute of Technology
   kastner (at) mit . edu
SEE ALSO
   renumerate.py
'''

#Introduce user to the function
print('WELCOME TO RENUMBER WATERS')
print('--------------------------\n')
print('So you have a CPPTRAJ PDB with more than 9999 residues? ')
pdb_name = input('Which PDB in this directory needs to be renumbered? ')
print('--------------------------\n')

change_start = 0
new_pdb = '{}_corrected.pdb'.format(pdb_name[:-4])
with open(new_pdb, 'w') as correct_waters:
  with open(pdb_name, 'r') as original:
    red_flag = False
    for i,line in enumerate(original):
      #We don't want to number the last line so we will watch for END
      if line[:3] == 'END':
        correct_waters.write(line)
        break

      #Check if we are on the last line of residue 9999
      if line[:3] == 'TER' and line[22:26] == '9999':
        red_flag = True
        correct_waters.write(line)
        continue

      #Throws a flag if we have passed the last row of 9999
      if red_flag == False:
        correct_waters.write(line)
        continue

      #Adds the original residue number to 10,000
      if change_start == 0: #Records first line changed to return to user
        change_start = i + 1
      count = int(line[22:26]) #Original residue number
      incorrect_waters_count = count #Output statistic for user
      start = 10000 + count

      #Replace residue number
      line_list = list(line)
      start_list = list(str(start))
      line_list[21:26] = start_list
      change_end = i + 1 #Tracks number of lines for user output
      correct_waters.write(''.join(line_list))

print('Renumbered lines {} to {}.'.format(change_start, change_end))
print('There were {} misnumbered waters.'.format(incorrect_waters_count))
print('Your new file is named {}.'.format(new_pdb))
print('Done.')
