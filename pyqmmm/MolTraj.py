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
      # The charge of the structure
      self.charge = 0
      # The frame corresponding to the reactants
      self.reactant = []
      # The frame corresponding to the transition state
      self.ts = []
      # The frame corresponding to the products
      self.product = []

    
    def get_traj(self, filename):
        '''
        Turns an xyz trajectory file into a list of lists where each element is a frame.
        
        Parameters
        ----------
        filename : string
            The file name of a trajectory
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
            
        print('We found {} frames in {}.'.format(len(xyz_as_list), xyz_filename))

def combine_xyz_files():
    # Find xyz trajectories in the current directory
    combined_filename = 'combined.xyz'
    xyz_filename_list = get_xyz_filenames()
    # For each xyz file convert to a list with only the requested frames
    combined_xyz_list = []
    for file in xyz_filename_list:
        requested_frames = request_frames(file)
        # The user can skip files by with enter which returns an empty string
        if requested_frames == '':
            continue
        # Convert the xyz files to a list
        xyz_list = multiframe_xyz_to_list(file)
        requested_xyz_list = [frame for index, frame in enumerate(
            xyz_list) if index + 1 in requested_frames]
        # Ask the user if they want the frames reversed for a given xyz file
        reverse = input('Any key to reverse {} else Return: '.format(file))
        if reverse:
            requested_xyz_list.reverse()
            reverse = False
        combined_xyz_list += requested_xyz_list
    # Write the combined trajectories out to a new file called combined.xyz
    with open(combined_filename, 'w') as combined_file:
        for entry in combined_xyz_list:
            combined_file.write(entry)
            
    print('Your combined xyz was written to {}\n'.format(combined_filename))
