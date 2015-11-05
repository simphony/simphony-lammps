from enum import Enum


class AtomStyle(Enum):
    """ Supported atom styles

    """
    ATOMIC = 0
    GRANULAR = 1
    SPHERE = 1  # same as GRANULAR in LIGGGHTS

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


def get_lammps_string(atom_style):
    """ Return atom style from string

        Parameters
        ----------
        atom_style : AtomStyle
            atom style

        Returns
        -------
        string
            lammps string describing the atom style

        Raises
        ------
        RunTimeError

    """
    for lammps_style, corresponding_atom_style in LAMMPS_STYLE.iteritems():
        if atom_style == corresponding_atom_style:
            return lammps_style

    return RuntimeError(
        "Could not find lammps atom style for '{}'".format(atom_style))
