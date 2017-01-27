from simphony.core import CUBA


def create_material_to_atom_type_map(state_data):
    """ Creates a map from material type ui to atom type

    create a mapping from material-uids to atom_type based
    on the materials given in SD.  which goes from 1 to N in lammps

    Parameters:
    -----------
    state_data : StateData
        state data with information on materials

    """
    material_to_atom = {}
    number_atom_types = 1
    for material in state_data.iter(item_type=CUBA.MATERIAL):
        material_to_atom[material.uid] = number_atom_types
        number_atom_types += 1
    return material_to_atom
