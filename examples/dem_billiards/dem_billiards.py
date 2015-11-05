from __future__ import print_function

import click

from simphony.engine import lammps

from simlammps import EngineType
from simphony.core.cuba import CUBA


@click.command()
@click.option('--show/--no-show', default=False)
def billiards_example(show):
    particles_list = lammps.read_data_file("billiards_init.data")

    # configure dem-wrapper
    dem = lammps.LammpsWrapper(engine_type=EngineType.DEM)

    dem.CM_extension[lammps.CUBAExtension.THERMODYNAMIC_ENSEMBLE] = "NVE"
    dem.CM[CUBA.NUMBER_OF_TIME_STEPS] = 1000
    dem.CM[CUBA.TIME_STEP] = 0.001
    total_steps = 35000

    # Define the BC component of the SimPhoNy application model:
    dem.BC_extension[lammps.CUBAExtension.BOX_FACES] = ["fixed",
                                                        "fixed",
                                                        "fixed"]
    dem.add_dataset(particles_list[0])
    particles_in_wrapper = dem.get_dataset(particles_list[0].name)

    if show:
        from simphony.visualisation import aviz

        #  set the proper view parameters for the snapshot
        aviz.show(particles_in_wrapper)

    step = 0
    for run_number in range(0, total_steps/dem.CM[CUBA.NUMBER_OF_TIME_STEPS]):
        step = step + dem.CM[CUBA.NUMBER_OF_TIME_STEPS]
        print ("running step {} of {}".format(step, total_steps))
        dem.run()

        if show:
            aviz.snapshot(particles_in_wrapper,
                          "billiards{:0>5}.png".format(step))

if __name__ == '__main__':
    billiards_example()
