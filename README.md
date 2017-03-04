Continuing the work of [Vanessa Sochat et. al.](https://github.com/vsoch/forward-modeling-cognitive-concepts)

------
# Forward Modeling of Cognitive Concepts

This is a quasi-reproducible repo to run the "thesis version" of semantic image comparison. I was planning on making a Singularity (or other) container, but Russ is trying to run this on TACC, so neither of those will work. The original pipeline was run on Sherlock with Python 2.7.6, and this uses a SLURM job submission framework. If you don't use that, you'll need to update those scripts. Please see [semantic-image-comparison-analysis](https://github.com/vsoch/semantic-image-comparison/blob/master/SUMMARY.md) for a complete history of this work. This final repo represents only a snapshot of the pulling and tugging on data that was done to arrive at this result.

## Instructions

### Installation

Download the repo to your cluster environment:

      git clone https://github.com/vsoch/forward-modeling-cognitive-concepts
      cd forward-modeling-cognitive-concepts
      pip install -r requirements.txt

### Data

You should first generate your data,meaning download images from the NeuroVault database with pyneurovault, filtering the data, and tranforming T-maps to Z-maps. The final Z-maps, resampled to 4mm space, will be output in the `data/resampled_z_4mm` folder. The tables with a log of data will be output to `results`. The equivalent files for Vanessa Sochat's thesis, reflective of the database in early 2016, is provided in the [hidden data](.data) and [hidden results](.results) folders. Note that when you run the script to generate the data, you will acquire many more maps (>400) than were included in the analysis for thesis (N=93). This is because we were limited to a small, hand annotated set for concepts in the Cognitive Atlas. While there are many more with cognitive concept labels, use at your own risk, as I've personally looked at some of these map annotations, and they are completely wrong.

For all scripts, you need to define a base directory as the single argument - this is the base folder for your project, and it's suggested you make a folder in `SCRATCH` as we will need to save data outputs here.

      mkdir /scratch/users/vsochat/forward-modeling-analysis
      
You then can run the first script to download neurovault images and prepare maps, and give it your scratch directory as the first argument.

      python 0.neurovault_images.py /scratch/users/vsochat/forward-modeling-analysis

If you are using IPYTHON, then you should define the base directory in your terminal first:

      base="/scratch/users/vsochat/forward-modeling-analysis"

Your resampled 4mm, Z-maps will be in `data/resampled_z_4mm`

The final preparation that you must do for your data is to generate lookup tables for cognitive concept annotations, applied to images. Retrieving these annotations (a set of labels for each statistical brain map) uses the Cognitive Atlas api, and so we should do this once, and save the results in a data frame for lookup to be most efficient. You can equivalently run the script [1.prep_semantic_comparison.py](1.prep_semantic_comparison.py) to do this:

      python 1.prep_semantic_comparison.py /scratch/users/vsochat/forward-modeling-analysis

The equivalent applies for the base directory if you are using IPython. This will produce a lookup table of images (rows) by cognitive concepts (columns) in your data directory, an example file generated at the time of the actual analysis is provided ([.results/concepts_binary_df.tsv](.results/concepts_binary_df.tsv)).

### Running the Analysis
We use a permutation approach that holds two images out, builds the forward model with the remaining data, and tests on the two images:

      Classification framework
      for image1 in all images:
         for image2 in allimages:
             if image1 != image2:
                 hold out image 1 and image 2, generate regression parameter matrix using other images
                 generate predicted image for image 1 [PR1]
                 generate predicted image for image 2 [PR2]
                 classify image 1 as fitting best to PR1 or PR2
                 classify image 2 as fitting best to PR1 or PR2

To run this, we used a SLURM cluster, with a submission script, [2.run_encoding_regression_performance.py](2.run_encoding_regression_performance.py), that dynamically generates and submits jobs with [2.encoding_regression_performance.py](2.encoding_regression_performance.py). You shouldn't need to edit the latter, however you should look over the first to check the submission variables and the commands best fit for your cluster. At the start of the script we've provided variables for you to specify runtime (for a single job), memory, and any other submission commands:

      # VARIABLES FOR SLURM
      max_runtime="2-00:00"                    # Two days. Each script needs ~10-15 minutes, 30 is recommended for buffer
      memory="32000"                           # 16000 might also work
      submission_command="sbatch"                  # Your cluster submission command, eg sbatch, qsub
      submission_args="-p russpold --qos russpold" # Does not need spaces to left and right

The runscript will produce two directories, `.out` and `.job` in your script directory (defined as the variable `here`). If you need to re-run something, you can find the jobfiles in `.job`. To debug, all output and error logs will be in `.out`. The results of the permutations, each a pickled file with the naming schema (image1)_(image2)_perform.pkl will be placed in `results/permutations`.

### Generating the Null Model

### Parsing Results

To be added/written when the above is tested!
