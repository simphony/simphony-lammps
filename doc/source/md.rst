Molecular Dynamics Engine
=========================

The SimPhoNy engine for LAMMPS currently supports a simple bulk atomistic
molecular dynamics simulations with NVE thermodynamic ensemble.


Configuration of the engine (CM, SP, BC)
-----------------------------------------

The user can configure the engine by setting specific values using CUBA
keywords. The CUBA keywords supported for each model component are provided
below.  Additionally, there are non-CUBA keywords used for configuration which
are also currently being used for configuration.

CM
^^

* ``CUBA.NUMBER_OF_TIME_STEPS``
* ``CUBA.TIME_STEP``
* ``CUBAExtension.THERMODYNAMIC_ENSEMBLE``
    * supported values:
        * "NVE" - use constant NVE integration

SP
^^

* ``CUBAExtension.PAIR_POTENTIALS``

BC
^^
* ``CUBAExtension.BOX_FACES``


Example
^^^^^^^

Here is an example configuration::

        # CM
        engine.CM[CUBA.NUMBER_OF_TIME_STEPS] = 10000
        engine.CM[CUBA.TIME_STEP] = 0.003
        engine.CM_extension[CUBAExtension.THERMODYNAMIC_ENSEMBLE] = "NVE"

        # SP
        pair_potential = ("lj:\n"
                          "  global_cutoff: 1.12246\n"
                          "  parameters:\n"
                          "  - pair: [1, 1]\n"
                          "    epsilon: 1.0\n"
                          "    sigma: 1.0\n"
                          "    cutoff: 1.2246\n"
                          "  - pair: [1, 2]\n"
                          "    epsilon: 1.0\n"
                          "    sigma: 1.0\n"
                          "    cutoff: 1.2246\n"
                          "  - pair: [1, 3]\n"
                          "    epsilon: 1.0\n"
                          "    sigma: 1.0\n"
                          "    cutoff: 1.2246\n"
                          "  - pair: [2, 2]\n"
                          "    epsilon: 1.0\n"
                          "    sigma: 1.0\n"
                          "    cutoff: 1.2246\n"
                          "  - pair: [2, 3]\n"
                          "    epsilon: 1.0\n"
                          "    sigma: 1.0\n"
                          "    cutoff: 1.2246\n"
                          "  - pair: [3, 3]\n"
                          "    epsilon: 1.0\n"
                          "    sigma: 1.0\n"
                          "    cutoff: 1.0001\n")
        engine.SP_extension[CUBAExtension.PAIR_POTENTIALS] = pair_potential

        # BC
        engine.BC_extension[CUBAExtension.BOX_FACES] = (
            "periodic", "periodic", "periodic")


Configuring the engine's state
------------------------------

The MD engine only supports Particles.

Particles
^^^^^^^^^
The Particles container's ``data`` should have ``CUBA.MASS`` and
``CUBA.MATERIAL_TYPE`` defined.

Individual particles
^^^^^^^^^^^^^^^^^^^^
The individual particles should have ``CUBA.VELOCITY`` defined.


Example
^^^^^^^

Here is an example configuration::

        pc = ParticleContainer
        data = DataContainer()
        data[CUBA.MASS] = mass
        data[CUBA.MATERIAL_TYPE] = material_type

        pc.data = data

        pc_w = engine.add_particles(pc)

        vectors = [(25.0, 0.0, 0.0),
                   (0.0, 22.0, 0.0),
                   (0.0, 0.0, 1.0)]

        pc_w.data_extension = {CUBAExtension.BOX_VECTORS: vectors,
                               CUBAExtension.BOX_ORIGIN: (0.0, 0.0, 0.0)}

        random.seed(42)
        for _ in range(10):
            coord = (random.uniform(0.0, 25.0),
                     random.uniform(0.0, 22.0),
                     0.0)
            p = Particle(coordinates=coord)
            p.data[CUBA.VELOCITY] = (0.0, 0.0, 0.0)
            pc_w.add_particle(p)


Additional notes
----------------

* Units : all quantities are unitless.


