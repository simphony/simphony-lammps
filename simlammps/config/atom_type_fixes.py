from simphony.core.cuba import CUBA

from simlammps.common.atom_style import AtomStyle


_ATOM_TYPE_PROPERTIES = {AtomStyle.GRANULAR: [CUBA.YOUNG_MODULUS,
                                              CUBA.POISSON_RATIO],
                         AtomStyle.ATOMIC: []}

_CUBA_TO_LAMMPS = {CUBA.YOUNG_MODULUS: "youngsModulus",
                   CUBA.POISSON_RATIO: "poissonsRatio"}


def get_per_atom_type_fixes(atom_style, materials):
    """ Get per-atom-type fixes

    This method returns all required per-atom-type fixes for
    a certain atom style.

    Parameter
    ---------
    atom_style : AtomStyle
        atom style
    materials : list of Material
        materials containing required parameters

    Raises
    ------
    ValueError:
        if the materials are missing the required variables

    """
    fixes = ''
    for cuba in _ATOM_TYPE_PROPERTIES[atom_style]:
        values = []
        if not materials:
            raise ValueError("No materials were defined.")
        for material in materials:
            try:
                values.append(material.data[cuba])
            except KeyError:
                raise ValueError(
                    "Material is missing ".format(cuba.name))
        # use always the same name
        fix_name = "{}_1".format(_CUBA_TO_LAMMPS[cuba])

        command = "fix {} all property/global {} peratomtype".format(
            fix_name,
            _CUBA_TO_LAMMPS[cuba])
        command += " {}\n".format(' '.join(map(str, values)))
        fixes += command
    return fixes
