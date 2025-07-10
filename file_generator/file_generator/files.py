def generate_job_sh(time, num_task, num_core, mem_per_cpu, file_name="script_job.sh"):
    """
    Generates a file .sh for SLURM with specific parameters.
    
    Args:
        time (str): Time for the job in this format "days-hours:minutes:seconds" (ex. "0-00:15:00")
        num_task (int): Number of tasks (--ntasks)
        num_core (int): Number of cores for mpirun (used in the command mpirun -np)
        mem_per_cpu (str): Memory per CPU (ej. "4G")
        file_name (str): Name of the ouput file (optional)
    """
    content = f"""#!/bin/sh
#SBATCH --account=def-belandl1
#SBATCH --ntasks={num_task}
#SBATCH --mem-per-cpu={mem_per_cpu}
#SBATCH --time={time}

# Load the modules:
module load StdEnv/2020 intel/2020.1.217 openmpi/4.0.3

export LD_LIBRARY_PATH=/home/oupc/mlip_2/mylammps/src:$LD_LIBRARY_PATH

echo "Starting run at: `date`"


#srun ${{lmp_exec}} -in ${{lmp_input}} > ${{lmp_output}}

#mpirun -np {num_core} ${{lmp_exec}} -p 10x4 -in ${{lmp_input}} > ${{lmp_output}}

srun /home/oupc/mlip_2/interface-lammps-mlip-2/lmp_mpi -in lammps.in > out.run


echo "Program finished with exit code $? at: `date`"
"""

    with open(file_name, 'w') as f:
        f.write(content)
    
    print(f"File {file_name} succesfully generated.")

# Example:
# generate_job_sh(time="0-01:30:00", num_task=4, num_core=40, mem_per_cpu="8G", file_name="mi_job.sh")

def generate_lammps_input(input_data_file, output_file="lammps.in"):
    """
    Genera un archivo de entrada para LAMMPS basado en el script proporcionado.
    
    Parámetros:
        input_data_file (str): Nombre del archivo de datos de entrada (para 'read_data').
        output_file (str): Nombre del archivo de salida (por defecto: 'lammps.in').
    """
    lammps_script = f"""# ---------- Initialize Simulation --------------------- 
clear 
units       metal 
dimension   3 
boundary    p p p 
atom_style  atomic 
atom_modify sort 0 1


# ---------- Create Atoms --------------------- 
read_data   {input_data_file}


# ---------- Define Interatomic Potential --------------------- 
pair_style  mlip mlip.ini
pair_coeff  * *

mass        1  28.0855

neighbor     2.0 bin 
neigh_modify delay 10 check yes 

# balance atoms per cpu
comm_style tiled
balance 1.1 rcb
 
# ---------- Define Settings --------------------- 
compute eng all pe/atom 
compute eatoms all reduce sum c_eng 


# ----------- OUTPUT
dump 10  all custom 1 config.dmp id type x y z fx fy fz

thermo 10 
thermo_style custom step pe fnorm lx ly lz press pxx pyy pzz c_eatoms 


# ----------- ARTn
plugin   load   /home/oupc/artn-plugin/Files_LAMMPS/libartn-lmp.so
plugin   list

fix             10 all artn alpha0 0.2 dmax 5.0
timestep 0.001


# ---------- Run Minimization --------------------- 
reset_timestep 0 

min_style fire 

minimize 1e-4 1e-5 2000 10000 


variable natoms equal "count(all)" 
variable teng equal "c_eatoms"
variable length equal "lx"
variable ecoh equal "v_teng/v_natoms"

print "Total energy (eV) = ${{teng}};"
print "Number of atoms = ${{natoms}};"
print "Lattice constant (Angstoms) = ${{length}};"
print "Cohesive energy (eV) = ${{ecoh}};"

print "All done!"
"""

    with open(output_file, 'w') as f:
        f.write(lammps_script)

    print(f"Archivo de entrada de LAMMPS generado: {output_file}")


# Example:
#generate_lammps_input(input_data_file="conf.sw", output_file="lammps.in")

import subprocess
import os

def submit_slurm_job(script_path, dependency=None):
    """
    Submits a .sh script to SLURM using sbatch.

    Args:
        script_path (str): Path to the .sh script
        dependency (str, optional): Previous job ID for dependency (e.g., "123456")

    Returns:
        str: Submitted job ID or None if error occurred
    """
    if not os.path.isfile(script_path):
        print(f"Error: File {script_path} does not exist")
        return None

    try:
        # Make script executable if it isn't already
        os.chmod(script_path, 0o755)

        # Build sbatch command
        command = ["sbatch"]

        # Add dependency if specified
        if dependency:
            command.extend(["--dependency=afterok", dependency])

        command.append(script_path)

        # Execute command
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Extract job ID from output (format: "Submitted batch job 123456")
        job_id = result.stdout.strip().split()[-1]
        print(f"Job submitted successfully. ID: {job_id}")
        return job_id

    except subprocess.CalledProcessError as e:
        print(f"Job submission error: {e.stderr}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

# Example usage:
# 1. First generate the script
# generate_slurm_script(runtime="0-01:00:00", num_tasks=4, num_cores=40,
#                      mem_per_cpu="8G", output_file="my_job.sh")
#
# 2. Then submit it
# job_id = submit_slurm_job("my_job.sh")
#
# 3. To chain jobs (run after previous one completes)
# next_job_id = submit_slurm_job("another_job.sh", dependency=job_id)
