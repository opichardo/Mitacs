#!/bin/sh
#SBATCH --account=def-belandl1
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=4G
#SBATCH --time=0-00:15:00

# Load the modules:
module load StdEnv/2020 intel/2020.1.217 openmpi/4.0.3

export LD_LIBRARY_PATH=/home/oupc/mlip_2/mylammps/src:$LD_LIBRARY_PATH

echo "Starting run at: `date`"


#srun ${lmp_exec} -in ${lmp_input} > ${lmp_output}

#mpirun -np 40 ${lmp_exec} -p 10x4 -in ${lmp_input} > ${lmp_output}

srun /home/oupc/mlip_2/interface-lammps-mlip-2/lmp_mpi -in lammps.in > out.run


echo "Program finished with exit code $? at: `date`"
