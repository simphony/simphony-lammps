from simphony.engine import lammps
from simphony.bench.util import bench
from simphony.core.cuba import CUBA
from simphony.core.cuds_item import CUDSItem

from simlammps.bench.util import get_particles
from simlammps.testing.md_example_configurator import MDExampleConfigurator


def configure_wrapper(wrapper, particles):
    """  Configure wrapper

    Parameters:
    -----------
    wrapper : ABCModelingEngine
        wrapper to be configured
    particles : iterable of ABCParticles
        particles to use

    Returns
    --------
    steps : int
        number of steps which were run
    number of particles : int
        number of point configured

    """
    material_types = []
    number_particles = 0
    for dataset in particles:
        material_types.append(dataset.data[CUBA.MATERIAL_TYPE])
        wrapper.add_dataset(dataset)
        number_particles += dataset.count_of(CUDSItem.PARTICLE)

    MDExampleConfigurator.set_configuration(wrapper, material_types)

    return wrapper.CM[CUBA.NUMBER_OF_TIME_STEPS], number_particles


def run(wrapper):
    wrapper.run()


def run_iterate(wrapper):
    wrapper.run()
    for particles_dataset in wrapper.iter_datasets():
        for particle in particles_dataset.iter_particles():
            pass


def run_update_run(wrapper):
    wrapper.run()
    for particles_dataset in wrapper.iter_datasets():
        for particle in particles_dataset.iter_particles():
            particles_dataset.update_particles([particle])
    wrapper.run()


def describe(name, number_particles, number_steps, is_internal):
    wrapper_type = "INTERNAL" if is_internal else "FILE-IO"
    result = "{}__{}_particles_{}_steps_{}:".format(name,
                                                    number_particles,
                                                    number_steps,
                                                    wrapper_type)
    return result


if __name__ == '__main__':

    for y_range in [3000, 8000]:
        for is_internal in [True, False]:

            lammps_wrapper = lammps.LammpsWrapper(
                use_internal_interface=is_internal)
            particles = get_particles(y_range)
            number_steps, number_particles = configure_wrapper(lammps_wrapper,
                                                               particles)

            results = bench(lambda: run(lammps_wrapper),
                            repeat=1,
                            adjust_runs=False)
            print(describe("run",
                           number_particles,
                           number_steps,
                           is_internal),
                  results)

            results = bench(lambda: run(lammps_wrapper),
                            repeat=1,
                            adjust_runs=False)
            print(describe("run",
                           number_particles,
                           number_steps,
                           is_internal),
                  results)

            results = bench(lambda: run_iterate(lammps_wrapper),
                            repeat=1,
                            adjust_runs=False)
            print(describe("run_iterate",
                           number_particles,
                           number_steps,
                           is_internal),
                  results)

            results = bench(lambda: run_update_run(lammps_wrapper),
                            repeat=1,
                            adjust_runs=False)
            print(describe("run_update_run",
                           number_particles,
                           number_steps,
                           is_internal),
                  results)
