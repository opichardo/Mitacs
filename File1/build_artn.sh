#!/bin/sh

module load StdEnv
module load python
module load scipy-stack
module load cmake

DIR=`pwd`

echo $DIR

cd $DIR
git clone https://gitlab.com/ashapeev/mlip-2.git
cd mlip-2/
mkdir build
cd build/
cmake ../ -DBUILD_SHARED_LIBS=yes -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build . -j16

cd $DIR
git clone https://gitlab.com/groupe_mousseau/artn_abinitio.git
cd artn_abinitio/
git checkout mlip
mkdir build
cd build

cmake ../ -DMLIP_ROOT=$DIR/mlip-2 -DMLIP_LIB=build/lib_mlip_interface.so -DWITH_LAMMPS=no -DWITH_MLIP=yes
cmake --build . --target artn.x -j16



