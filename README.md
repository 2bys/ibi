# Iterative Boltzmann Inversion
Implementation of the Iterative Boltzmann Inversion for statistical analysis.

## How to run the code?
1) Create a config file (see example files).
2) Go to folder 'iterboltz-container' build singularity container by, e.g.,
		singularity build portable Singulartiy.def
3) Run all config files in config folder with 
		python3 manage_runs.py
