#!/usr/bin/env python2

from pybraincompare.mr.datasets import get_standard_brain
from cognitiveatlas.api import get_task, get_concept
from pybraincompare.compare.maths import TtoZ
from nilearn.image import resample_img
from pyneurovault import api
from glob import glob
import shutil
import numpy
import pandas
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) < 2:
    print("You must specify a base project directory as your first argument.")
    sys.exit()

base=sys.argv[1]
print("BASE project directory is defined as %s" %(base))

data_directory = os.path.abspath("%s/data" %(base))
results_directory = os.path.abspath("%s/results" %(base))

folders = [data_directory,results_directory]
for folder in folders:
    if not os.path.exists(folder):
        os.mkdir(folder)

# Get all collections
collections = api.get_collections()

# Filter images to those that have a DOI
collections = collections[collections.DOI.isnull()==False]

# Useless, but might as well save it
collections.to_csv("%s/collections_with_dois.tsv" %(results_directory),encoding="utf-8",sep="\t")

# Get image meta data for collections
images = api.get_images(collection_pks=collections.collection_id.tolist())

# Get rid of any not in MNI
images = images[images.not_mni == False]

# Get rid of thresholded images
images = images[images.is_thresholded == False]

# Remove single subject maps
images = images[images.analysis_level!='single-subject']
images = images[images.number_of_subjects!=1]

# Remove non fmri-BOLD
images = images[images.modality=='fMRI-BOLD']

# We can't use Rest or other/none
images = images[images.cognitive_paradigm_cogatlas_id.isnull()==False]
images = images[images.cognitive_paradigm_cogatlas.isin(["None / Other","rest eyes closed","rest eyes open"])==False]

# Limit to Z and T maps (all are Z and T)
z = images[images.map_type == "Z map"]
t = images[images.map_type == "T map"]

# Remove tmaps that do not have # subjects defined
t = t[t.number_of_subjects.isnull()==False]
images = z.append(t)

# Download images
standard = os.path.abspath("%s/mr/MNI152_T1_2mm_brain.nii.gz" %(here))
api.download_images(dest_dir=data_directory,images_df=images,target=standard)

# For T images, convert to Z. NeuroVault outputs two folders - original and resampled
resampled_dir = "%s/resampled" %(data_directory)

# We need to select a subset of the images, just the T Maps from the set
tmaps = [ "%s/%06d.nii.gz" %(resampled_dir,x) for x in t.image_id.tolist()]

# We need degrees of freedom to convert properly to Zstat maps. 
dofs = []
for row in t.iterrows():
    dof = row[1].number_of_subjects -2
    dofs.append(dof)

# We will move converted Z maps, and as is Z maps, to a common folder
outfolder_z = "%s/resampled_z" %(data_directory)
if not os.path.exists(outfolder_z):
    os.mkdir(outfolder_z)

for tt in range(0,len(tmaps)):
    tmap = tmaps[tt]
    dof = dofs[tt]
    zmap_new = "%s/%s" %(outfolder_z,os.path.split(tmap)[-1])
    TtoZ(tmap,output_nii=zmap_new,dof=dof)

# Copy all (already) Z maps to the folder
zmaps = [ "%s/%06d.nii.gz" %(resampled_dir,x) for x in z.image_id.tolist()]
for zmap in zmaps:
    zmap_new = "%s/%s" %(outfolder_z,os.path.split(zmap)[-1])
    shutil.copyfile(zmap,zmap_new)

if len(glob("%s/*.nii.gz" %(outfolder_z))) != images.shape[0]:
    raise ValueError("ERROR: not all images were found in final folder %s" %(outfolder_z))

# We will actually need this one.
images.to_csv("%s/filtered_contrast_images.tsv" %(results_directory),encoding="utf-8",sep="\t")

# Finally, resample images to 4mm voxel for classification analysis
outfolder_z4mm = "%s/resampled_z_4mm" %(data_directory)
if not os.path.exists(outfolder_z4mm):
    os.mkdir(outfolder_z4mm)

maps = glob("%s/*.nii.gz" %(outfolder_z))
for mr in maps:
    image_name = os.path.basename(mr)
    print "Resampling %s to 4mm..." %(image_name)
    nii = nibabel.load(mr)
    nii_resamp = resample_img(nii,target_affine=numpy.diag([4,4,4]))
    nibabel.save(nii_resamp,"%s/%s" %(outfolder_z4mm,image_name))
