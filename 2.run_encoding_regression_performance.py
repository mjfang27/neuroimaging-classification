"""
permutation (third) step in forward modeling analysis - building a forward model, testing with 2 images held out. This is the submission script to run the analysis, submitting to a SLURM cluster. You MUST edit the last line of this script for your particular submission command. If you do not use this kind of cluster, you should edit the end of the script (where submission occurs) to fit your format.

  Classification framework
  for image1 in all images:
     for image2 in allimages:
         if image1 != image2:
             hold out image 1 and image 2, generate regression parameter matrix using other images
             generate predicted image for image 1 [PR1]
             generate predicted image for image 2 [PR2]
             classify image 1 as fitting best to PR1 or PR2
             classify image 2 as fitting best to PR1 or PR2
"""

import os
import pandas
import sys

from utils import (
   get_base, get_pwd, make_dirs
)

# VARIABLES FOR SLURM
max_runtime="2-00:00"                    # Two days. Each script needs ~10-15 minutes, 30 is recommended for buffer
memory="32000"                           # 16000 might also work
submission_command="sbatch"                  # Your cluster submission command, eg sbatch, qsub
submission_args="-p russpold --qos russpold" # Does not need spaces to left and right


# Get the base and present working directory
base = get_base()
here = get_pwd()

data = os.path.abspath("%s/data" %(base))
results = os.path.abspath("%s/results" %(base))
output_folder = "%s/permutations" %results  

# Make the output directory
make_dirs(output_folder,reason="for permutation results.")

# Images by Concepts data frame
labels_tsv = "%s/concepts_binary_df.tsv" %results
images = pandas.read_csv(labels_tsv,sep="\t",index_col=0)
image_lookup = "%s/image_nii_lookup.pkl" %results

# We will need these folders to exist for job and output files
log_folders = ["%s/.out" %here,"%s/.job" %here]
make_dirs(log_folders)    

# Image metadata with number of subjects included
contrast_file = "%s/filtered_contrast_images.tsv" %results

for image1_holdout in images.index.tolist():
    print "Parsing %s" %(image1_holdout)
    for image2_holdout in images.index.tolist():
        if (image1_holdout != image2_holdout) and (image1_holdout < image2_holdout):
            output_file = "%s/%s_%s_perform.pkl" %(output_folder,image1_holdout,image2_holdout)
            if not os.path.exists(output_file):
                job_id = "%s_%s" %(image1_holdout,image2_holdout)
                filey = "%s/.job/class_%s.job" %(here,job_id)
                filey = open(filey,"w")
                filey.writelines("#!/bin/bash\n")
                filey.writelines("#SBATCH --job-name=%s\n" %(job_id))
                filey.writelines("#SBATCH --output=%s/.out/%s.out\n" %(here,job_id))
                filey.writelines("#SBATCH --error=%s/.out/%s.err\n" %(here,job_id))
                filey.writelines("#SBATCH --time=%s\n" %(max_runtime))
                filey.writelines("#SBATCH --mem=%s\n" %(memory))
                filey.writelines("python %s/2.encoding_regression_performance.py %s %s %s %s %s %s" %(here, 
                                                                                                      image1_holdout, 
                                                                                                      image2_holdout, 
                                                                                                      output_file, 
                                                                                                      labels_tsv, 
                                                                                                      image_lookup, 
                                                                                                      contrast_file))
                filey.close()
                os.system("%s %s " + "%s/.job/class_%s.job" %(submission_command,
                                                              submission_args,
                                                              here,
                                                              job_id))
