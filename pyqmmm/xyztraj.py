# @file XYZTraj.py
#  Defines xyztraj class and manipulation methods.
#
#  Written by David Kastner
#
#  Department of Chemical Engineering, MIT

class XYZTraj:
  '''
  Holds information about a molecular trajectory, used to do maniplualtions.
  Reads informaiton from structural xyz file.
  
  Example instantiation of a molecular scan from an XYZ trajectory:
  
  >>> mol_scan = traj3D()
  >>> mol_scan.get_xyz('tc_scan.xyz')
  '''
  
  def __init__(self, file_name=''):
    # The number of frames
    self.frames = []
  
  
    
