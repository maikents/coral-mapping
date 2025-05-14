#!/bin/sh
#SBATCH --partition=CPUQ
#SBATCH --account=ie-itk
#SBATCH --time=0-1:00:00     # 0 days and 15 minutes limit
#SBATCH --nodes=1             # 1 compute nodes
#SBATCH --cpus-per-task=20     # 2 CPU cores
#SBATCH --mem=64G              # 5 gigabytes memory
#SBATCH --output=./logs/create-bottom-features-log.txt    # Log file

python ""../create-SINMOD-bottom-features.py