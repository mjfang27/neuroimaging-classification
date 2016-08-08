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

Your resampled 4mm, Z-maps will be in `data/resampled_z_4mm`

### Running the Analysis

**will write after above tested on TACC**
