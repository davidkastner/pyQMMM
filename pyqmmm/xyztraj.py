class xyztraj3D:
  '''
  Holds information about a molecular trajectory, used to do maniplualtions.
  Reads informaiton from structural xyz file.
  
  Example instantiation of a molecular scan from an XYZ trajectory:
  
  >>> mol_scan = traj3D()
  >>> mol_scan.get_xyz('tc_scan.xyz')
  '''
  
  def __init__(self, pdbCode=''):
    
