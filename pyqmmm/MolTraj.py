# @file MolTraj.py
#  Defines MolTraj class and trajectory manipulation methods.
#
#  Written by David W. Kastner
#
#  Department of Chemical Engineering, MIT

class MolTraj:
  '''
  Stores a molecular trajectory and facilitates manipulations.
  Reads information from an multiframe xyz file.
  
  Example instantiation of a molecular scan from an molecular trajectory:
  
  >>> mol_scan = MolTraj()
  >>> mol_scan.get_xyz('tc_scan.xyz')
  '''
  
  def __init__(self, name=''):
    # The number of frames
    self.frames = []
    # The number of atoms in the structure
    self.natoms = 0
    # The multiplicty of the structure
    self.multiplicty = 0
    # Thecharge of the structure
    self.charge = 0
    
  def get_traj(self, filename):
    '''
    Turns an xyz trajectory file into a list of lists where each element is a frame.
    Parameters
    ----------
    xyz_filename : string
      The file name of a trajectory

    Returns
    -------
    trajectory_list :list
      List of lists containing the trajectory with each frame saved as an element
    '''
    # Variables that measure our progress in parsing the optim.xyz file
    xyz_as_list = []  # List of lists containing all frames
    frame_contents = ''
    line_count = 0
    frame_count = 0
    first_line = True  # Marks if we've looked at the atom count yet

    # Loop through optim.xyz and collect distances, energies and frame contents
    with open(xyz_filename, 'r') as trajectory:
        for line in trajectory:
            # We determine the section length using the atom count in first line
            if first_line == True:
                section_length = int(line.strip()) + 2
                first_line = False
            # At the end of the section reset the frame-specific variables
            if line_count == section_length:
                line_count = 0
                xyz_as_list.append(frame_contents)
                frame_contents = ''
                frame_count += 1
            frame_contents += line
            line_count += 1

        xyz_as_list.append(frame_contents)
    