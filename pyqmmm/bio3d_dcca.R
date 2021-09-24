# Load the Bio3D library
library(bio3d)

# Save file locations as variables
dcdfile <- "6edh_all.dcd"
pdbfile <- "6edh_dry.pdb"

# Read in your protein and DCD files
pdb <- read.pdb(pdbfile)
dcd <- read.dcd(dcdfile)

# Align each from based on its backbone
ca.inds <- atom.select(pdb, elety="CA")
xyz <- fit.xyz(fixed=pdb$xyz, mobile=dcd,
               fixed.inds=ca.inds$xyz,
               mobile.inds=ca.inds$xyz)

# Calculate the RMSD and write it to a file
#rmsd <- rmsd(xyz[1,ca.inds$xyz], xyz[,ca.inds$xyz])
#write.csv(rmsd, "rmsd.csv")

# Perform DCCA and get data for DCCM
cij<-dccm(xyz[,ca.inds$xyz])
pymol.dccm(cij, pdb, type="launch")