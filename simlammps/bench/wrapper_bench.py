from collections import namedtuple

_Tests = namedtuple(
    '_Tests', ['method', 'name'])

from simphony.engine import lammps
from simphony.bench.util import bench
from simphony.core.cuba import CUBA
from simphony.core.cuds_item import CUDSItem

from simlammps.bench.util import get_particles
from simlammps.testing.md_example_configurator import MDExampleConfigurator


def configure_wrapper(wrapper, particles, number_time_steps):
    """  Configure wrapper

    Parameters:
    -----------
    wrapper : ABCModelingEngine
        wrapper to be configured
    particles : iterable of ABCParticles
        particles to use
    number_time_steps : int
        number of time steps to run
    """
    material_types = []
    for dataset in particles:
        material_types.append(dataset.data[CUBA.MATERIAL_TYPE])
        wrapper.add_dataset(dataset)

    MDExampleConfigurator.set_configuration(wrapper,
                                            material_types,
                                            number_time_steps)


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


def run_test(func, wrapper):
    func(wrapper)

if __name__ == '__main__':

    run_wrapper_tests = [_Tests(method=run,
                                name="run"),
                         _Tests(method=run_iterate,
                                name="run_iterate"),
                         _Tests(method=run_update_run,
                                name="run_update_run")]

    for is_internal in [True, False]:
        for y_range in [3000, 8000]:

            # test different run scenarios
            particles = get_particles(y_range)
            number_particles = sum(p.count_of(
                CUDSItem.PARTICLE) for p in particles)
            number_time_steps = 10

            for test in run_wrapper_tests:
                lammps_wrapper = lammps.LammpsWrapper(
                    use_internal_interface=is_internal)
                configure_wrapper(lammps_wrapper,
                                  particles,
                                  number_time_steps=number_time_steps)

                results = bench(lambda: run_test(test.method, lammps_wrapper),
                                repeat=1,
                                adjust_runs=False)

                print(describe(test.name,
                               number_particles,
                               number_time_steps,
                               is_internal), results)

            # test configuration
            lammps_wrapper = lammps.LammpsWrapper(
                use_internal_interface=is_internal)

            results = bench(lambda: configure_wrapper(lammps_wrapper,
                                                      particles,
                                                      number_time_steps),
                            repeat=1,
                            adjust_runs=False)

            print(describe("configure_wrapper",
                  number_particles,
                  number_time_steps,
                  is_internal), results)
