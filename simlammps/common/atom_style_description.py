from simphony.core.cuba import CUBA

from simlammps.common.atom_style import AtomStyle


class AtomStyleDescription(object):
    """  Class describes atom style

    Each atom style has a particular set of attributes that it supports
    (or provides). This class contains a list of what  attributes it
    contains. Note that the order of items in 'attributes' corresponds
    to the order they appear in lammps-data file.

    Attributes
    ----------
    attributes : list of ValueInfo
         a list of what attributes it contains is listed
    has_mass : bool (optional)
        True if this style requires a mass

    """
    def __init__(self, attributes=None, has_mass=False):
        if attributes is None:
            self.attributes = []
        else:
            self.attributes = attributes
        self.has_mass = has_mass


class ValueInfo(object):
    """  Class describes cuba value

    Class information on cuba value and provides conversion
    between LAMMPS/SIMPHONY

    Attributes
    ----------
    cuba_key : CUBA
        CUBA key
    convert_to_cuba : function (optional)
        method to convert from LAMMPS value to SimPhoNy-CUBA
    convert_from_cuba : function (optional)
        method to convert from SimPhoNy-CUBA to LAMMPS value

    """
    def __init__(self,
                 cuba_key,
                 convert_to_cuba=None,
                 convert_from_cuba=None):
        self.cuba_key = cuba_key
        self.convert_to_cuba = convert_to_cuba
        self.convert_from_cuba = convert_from_cuba

# description of each atom-style
ATOM_STYLE_DESCRIPTIONS = {
    AtomStyle.ATOMIC:
        AtomStyleDescription(  # default (i.e. coordinates, velocity..)
            has_mass=True),  # but with mass
    AtomStyle.GRANULAR:
        AtomStyleDescription(
            attributes=[
                ValueInfo(cuba_key=CUBA.RADIUS,  # but diameter in LAMMPS
                          convert_to_cuba=lambda x: x / 2,  # d to radius
                          convert_from_cuba=lambda x: x * 2),  # radius to d
                ValueInfo(cuba_key=CUBA.DENSITY)],
            has_mass=False)
}
