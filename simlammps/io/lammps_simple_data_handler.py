class LammpsSimpleDataHandler(object):
    """  Class to handle what is parsed by LammpsDataFileParser

        Class just stores the parsed data and provides methods to
        retrieve this data
    """
    def __init__(self):
        self.begin()

    def begin(self):
        """ Handle begin of file parsing

        """
        # Clear/prepare cache of data
        self._number_types = None
        self._atoms = {}
        self._masses = {}
        self._velocities = {}
        self._box_origin = None
        self._box_vectors = None
        self._atom_type = None

    def end(self):
        """ Handle end of file parsing

        """
        pass

    def process_number_atom_types(self, number_types):
        self._number_types = number_types

    def get_number_atom_types(self):
        return self._number_types

    def process_atoms(self, id, values):
        self._atoms[id] = values

    def get_atoms(self):
        return self._atoms

    def process_masses(self, id, value):
        self._masses[id] = value

    def get_masses(self):
        return self._masses

    def process_velocities(self, id, values):
        self._velocities[id] = values

    def get_velocities(self):
        return self._velocities

    def process_box_origin(self, values):
        self._box_origin = values

    def get_box_origin(self):
        return self._box_origin

    def process_box_vectors(self, values):
        self._box_vectors = values

    def get_box_vectors(self):
        return self._box_vectors

    def process_atom_type(self, atom_type):
        self._atom_type = atom_type

    def get_atom_type(self):
        ''' Returns atom type

         Returns
         -------
         atom_type : string
            Atom type.  None if atom type is not known
        '''
        return self._atom_type
