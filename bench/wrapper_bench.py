from collections import namedtuple

from simphony.engine import lammps
from simphony.bench.util import bench
from simphony.core.cuds_item import CUDSItem

from simlammps.bench.util import get_particles
from simlammps.testing.md_example_configurator import MDExampleConfigurator

_Tests = namedtuple(
    '_Tests', ['method', 'name'])


def configure_wrapper(wrapper, state_data, particles, number_time_steps):
    """  Configure wrapper

    Parameters:
    -----------
    wrapper : ABCModelingEngine
        wrapper to be configured
    state_data : StateData
        state data (materials)
    particles :  ABCParticles
        particles to use
    number_time_steps : int
        number of time steps to run

    """
    materials = [material for material in state_data.iter_materials()]

    configurator = MDExampleConfigurator(materials=materials,
                                         number_time_steps=number_time_steps)
    configurator.set_configuration(wrapper)

    wrapper.add_dataset(particles)


def run(wrapper):
    wrapper.run()


def run_iterate(wrapper):
    wrapper.run()
    for particles_dataset in wrapper.iter_datasets():
        for _ in particles_dataset.iter_particles():
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
            particles, state_data = get_particles(y_range)
            number_particles = particles.count_of(CUDSItem.PARTICLE)
            number_time_steps = 10

            SD = "DUMMY - TODO"
            for test in run_wrapper_tests:
                lammps_wrapper = lammps.LammpsWrapper(
                    use_internal_interface=is_internal)
                configure_wrapper(lammps_wrapper,
                                  state_data,
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
                                                      state_data,
                                                      particles,
                                                      number_time_steps),
                            repeat=1,
                            adjust_runs=False)

            print(describe("configure_wrapper",
                  number_particles,
                  number_time_steps,
                  is_internal), results)
