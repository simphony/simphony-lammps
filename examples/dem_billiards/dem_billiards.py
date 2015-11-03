from __future__ import print_function

from simphony.engine import lammps
from simphony.visualisation import aviz

from simlammps import EngineType
from simphony.core.cuba import CUBA


particles_list = lammps.read_data_file("billiards_init.data")

# The total number
number_NVE_cycles = 1000

# configure dem-wrapper
dem = lammps.LammpsWrapper(engine_type=EngineType.DEM)

dem.CM_extension[lammps.CUBAExtension.THERMODYNAMIC_ENSEMBLE] = "NVE"
dem.CM[CUBA.NUMBER_OF_TIME_STEPS] = 1000
dem.CM[CUBA.TIME_STEP] = 0.001
total_time_steps = 35000

# Define the BC component of the SimPhoNy application model:
dem.BC_extension[lammps.CUBAExtension.BOX_FACES] = ["fixed",
                                                    "fixed",
                                                    "fixed"]
dem.add_dataset(particles_list[0])
particles_in_wrapper = dem.get_dataset(particles_list[0].name)

#  set the proper view parameters for the snapshot
aviz.show(particles_in_wrapper)

step = 0
for run_number in range(0, total_time_steps/dem.CM[CUBA.NUMBER_OF_TIME_STEPS]):
    step = step + dem.CM[CUBA.NUMBER_OF_TIME_STEPS]
    print ("running step {} of {}".format(step, total_time_steps))
    dem.run()
    aviz.snapshot(particles_in_wrapper, "billiards{:0>5}.png".format(step))
