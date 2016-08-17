"""
second step in forward modeling analysis - generating data structures to look up associated Cognitive Atlas terms
    with the images downloaded in 0.neurovault_images.py

"""

from cognitiveatlas.api import get_concept

from glob import glob

import numpy
import os
import pandas
import pickle
import re
import sys

from utils import (
   get_base, get_pwd, make_dirs
)


# Get the base and present working directory
base = get_base()
here = get_pwd()

data = os.path.abspath("%s/data" %(base))
results = os.path.abspath("%s/results" %(base))

# Read in images metadata
images = pandas.read_csv("%s/filtered_contrast_images.tsv" %results,sep="\t",index_col=0)

unique_concepts = dict()
for row in images.iterrows():
    idx = row[1].image_id
    # There is a bug with getting contrasts for these two images - these I manually looked up (@vsoch):
    if idx == 109:
        unique_concepts[idx] = ["trm_567982752ff4a","trm_4a3fd79d0afcf","trm_5534111a8bc96",
                                "trm_557b48a224b95","trm_557b4a81a4a17","trm_4a3fd79d0b64e","trm_4a3fd79d0a33b",
                                "trm_557b4a7315f1b","trm_4a3fd79d0af71","trm_557b4b56de455","trm_557b4add1837e"]
    elif idx == 118:
        unique_concepts[idx] = ["trm_4a3fd79d0b642","trm_4a3fd79d0a33b","trm_557b4a7315f1b","trm_4a3fd79d0af71",
                                "trm_557b4b56de455"]
    else:
        contrast = row[1].cognitive_contrast_cogatlas_id
        concepts = get_concept(contrast_id=contrast)
        concepts = numpy.unique(concepts.pandas.id).tolist() 
        unique_concepts[idx] = concepts
    
all_concepts = []
for image_id,concepts in unique_concepts.items():
    for concept in concepts:
        if concept not in all_concepts:
            all_concepts.append(concept)


res = {"all_concepts":all_concepts,"unique_concepts":unique_concepts,"images":images}

## STEP 1: GENERATE IMAGE BY CONCEPT DATA FRAME
concept_df = pandas.DataFrame(0,columns=all_concepts,index=images.image_id.unique().tolist())
for image_id,concepts in unique_concepts.items():
    concept_df.loc[image_id,concepts] = 1   

res["concept_df"] = concept_df
pickle.dump(res,open("%s/concepts.pkl" %results,"wb"))
concept_df.to_csv("%s/concepts_binary_df.tsv" %results,sep="\t")

## STEP 2: Generate image lookup
image_folder = "%s/resampled_z_4mm" %(data)
files = glob("%s/*.nii.gz" %image_folder)

if len(files) == 0:
    print(("Error, did not find image files in %s. Did you generate them with 0.neurovault_images.py?" %(image_folder)))
else:
    lookup = dict()
    for f in files:
        image_id = int(os.path.basename(f).strip(".nii.gz"))
        if image_id in concept_df.index:
            lookup[image_id] = f
        else:
            print(("Cannot find image %s in concept data frame" %(image_id)))

    pickle.dump(lookup,open("%s/image_nii_lookup.pkl" %results,"wb"))
