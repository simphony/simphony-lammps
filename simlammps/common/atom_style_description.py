from simphony.core.cuba import CUBA

from simlammps.common.atom_style import AtomStyle


class ValueInfo(object):
    """  Class describes cuba value and how to convert between LAMMPS/SIMPHONY

    Attributes
    ----------
    cuba_key : CUBA
        CUBA key
    convertToCuba : function (optional)
        method to convert from LAMMPS value to SimPhoNy CUBA
    convertFromCuba : function (optional)
        method to convert from SimPhoNy CUBA to LAMMPS value

    """
    def __init__(self,
                 cuba_key,
                 convert_to_cuba=None,
                 convert_from_cuba=None):
        self.cuba_key = cuba_key
        self.convert_to_cuba = convert_to_cuba
        self.convert_from_cuba = convert_from_cuba


ATOM_STYLE_DESCRIPTIONS = {
    AtomStyle.ATOMIC: [],  # just default (i.e. coordinates, velocity..)
    AtomStyle.GRANULAR:
        [ValueInfo(cuba_key=CUBA.RADIUS,
                   convert_to_cuba=lambda x: x / 2,  # diameter to radius
                   convert_from_cuba=lambda x: x * 2),  # radius to diameter
         ValueInfo(cuba_key=CUBA.DENSITY)]}
