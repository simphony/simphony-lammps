from enum import Enum, unique


@unique
class CUBAExtension(Enum):
    """ Provisional CUBA keywords specific for Lammps-Md

    These are additional CUBA-Keywords that are not included
    in simphony-common yet. The proposed description for
    these new CUBA keywords is:

    - description: Simulation box faces
    domain: [MD]
    key: BOX_FACES
    name: BoxFaces
    number: 100
    shape: [1]
    type: double
    - description: Simulation box vectors
    domain: [MD]
    key: BOX_VECTORS
    name: BoxVectors
    number: 101
    shape: [3,3]
    type: double
    - description: Simulation box origin
    domain: [MD]
    key: BOX_ORIGIN
    name: BoxOrigin
    number: 102
    shape: [3]
    type: double
    - description: Thermodynamic ensemble
    domain: [MD]
    key: THERMODYNAMIC_ENSEMBLE
    name: ThermodynamicEnsemble
    number: 103
    shape: [20]
    type: string
    - description: Pair potentials
    domain: [MD]
    key: PAIR_POTENTIALS
    name: PairPotentials
    number: 104
    shape: [20]
    type: string

"""

    BOX_FACES = "BOX_FACES"
    BOX_VECTORS = "BOX_VECTORS"
    BOX_ORIGIN = "BOX_ORIGIN"
    THERMODYNAMIC_ENSEMBLE = "THERMODYNAMIC_ENSEMBLE"
    PAIR_POTENTIALS = "PAIR_POTENTIALS"
