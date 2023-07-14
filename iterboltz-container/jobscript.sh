#!/bin/bash
#SBATCH -p medium 
#SBATCH -c 8
#SBATCH -t 1-23:30:00
#SBATCH -o outfile-%J
#SBATCH --mail-type=ALL
#SBATCH --mail-user=tobias.weber01@stud.uni-goettingen.de
module load singularity

singularity run portable
