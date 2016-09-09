import itertools

from simphony.core.cuba import CUBA

from .atom_style import AtomStyle


class AtomStyleDescription(object):
    """  Class describes atom style

    Each atom style has a particular set of attributes that it supports
    (or provides). This class contains a list of what  attributes it
    contains. Note that the order of items in 'attributes' corresponds to
    the order they appear in lammps-data file.

    Attributes
    ----------
    attributes : list of ValueInfo
         ordered list of what attributes each particle/atom contains
    velocity_attributes : list of ValueInfo
         ordered list of what velocity related attributes each atom contains
         (CUBA.VELOCITY is always included)
    has_mass_per_type : bool (optional)
        True if this style requires a mass (specifically mass-per-atom_type)

    """
    def __init__(self,
                 attributes=None,
                 velocity_attributes=None,
                 has_mass_per_type=False):
        if attributes is None:
            self.attributes = []
        else:
            self.attributes = attributes

        self.velocity_attributes = [ValueInfo(cuba_key=CUBA.VELOCITY,
                                              lammps_key="v")]
        if velocity_attributes:
            self.velocity_attributes.extend(velocity_attributes)

        self.has_mass_per_type = has_mass_per_type


class ValueInfo(object):
    """  Class describes cuba value

    Class information on cuba value and provides conversion
    between LAMMPS/SIMPHONY

    Attributes
    ----------
    cuba_key : CUBA
        CUBA key
    lammps_key : str
        lammps keyword
    convert_to_cuba : function (optional)
        method to convert from LAMMPS value to SimPhoNy-CUBA
    convert_from_cuba : function (optional)
        method to convert from SimPhoNy-CUBA to LAMMPS value

    """
    def __init__(self,
                 cuba_key,
                 lammps_key,
                 convert_to_cuba=None,
                 convert_from_cuba=None):
        self.cuba_key = cuba_key
        self.lammps_key = lammps_key
        self.convert_to_cuba = convert_to_cuba
        self.convert_from_cuba = convert_from_cuba

# description of each atom-style
ATOM_STYLE_DESCRIPTIONS = {
    AtomStyle.ATOMIC:
        AtomStyleDescription(
            # attributes has default (i.e. coordinates)
            # , velocity..)
            has_mass_per_type=True),  # but with mass
    AtomStyle.GRANULAR:
        AtomStyleDescription(
            attributes=[
                ValueInfo(cuba_key=CUBA.RADIUS,  # but diameter in LAMMPS
                          lammps_key="diameter",  # TODO check!!!!
                          convert_to_cuba=lambda x: x / 2,  # d to radius
                          convert_from_cuba=lambda x: x * 2),  # radius to d
                ValueInfo(cuba_key=CUBA.MASS,
                          lammps_key="mass")],
            velocity_attributes=[ValueInfo(cuba_key=CUBA.ANGULAR_VELOCITY,
                                           lammps_key="omega")],  # TODO check
            has_mass_per_type=False)
}

MATERIAL_TYPE_VALUE_INFO = ValueInfo(cuba_key=CUBA.MATERIAL_TYPE,
                                     lammps_key="type")

# all particles will have a material type
_default_attributes = [MATERIAL_TYPE_VALUE_INFO]


def get_all_attributes(atom_style):
    """ Return list of value info describing attributes expected on particle

    Parameters:
    -----------
    atom_style : AtomStyle
        style of atom

    """
    atom_style_description = ATOM_STYLE_DESCRIPTIONS[atom_style]
    return [attribute for attribute in
            itertools.chain(
                atom_style_description.attributes,
                atom_style_description.velocity_attributes,
                _default_attributes)]


def get_all_cuba_attributes(atom_style):
    """ Return list of all CUBA-key expected on particle

    Parameters:
    -----------
    atom_style : AtomStyle
        style of atom


    """
    return [attribute.cuba_key for attribute in get_all_attributes(atom_style)]
