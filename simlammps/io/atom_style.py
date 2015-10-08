from enum import Enum


class AtomStyle(Enum):
    ATOMIC = 0
    GRANULAR = 1
    SPHERE = 1  # same as GRANULAR in LIGGHTS

# mapping from lammps style to AtomStyle
LAMMPS_STYLE = {
    'atomic': AtomStyle.ATOMIC,
    'granular': AtomStyle.GRANULAR,
    'sphere': AtomStyle.SPHERE}


def get_atom_style(lammps_atom_style):
    """ Return atom style from string

        Parameters
        ----------
        lammps_atom_style : string
            string of lammps style (i.e. from lammps data file)

        Returns
        -------
        AtomStyle

        Raises
        ------
        RunTimeError
            If 'lammps_style' is not recognized

    """
    try:
        return LAMMPS_STYLE[lammps_atom_style]
    except KeyError:
        return RuntimeError(
            "Unsupported lammps atom style: '{}'".format(lammps_atom_style))
