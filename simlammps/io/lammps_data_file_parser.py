import re
import string
from enum import Enum
from collections import OrderedDict


class LammpsDataFileParser(object):
    """  Class parses Lammps data file (produced by lammps command
    write_data) and calls a handler which processes the parsed
    information.

    A handler class is given the parsed information. This handler class can
    then determine what it is does with it.  For, example it could just store
    the data in memory (see LammpsSimpleDataHandler) or write it some other
    data file (e.g. a CUDS-file).

    Handler classes have the following methods:
        def process_number_atom_types(self, number_types):
        def process_atoms(self, id, values):
        def process_masses(self, id, value):
        def process_velocities(self, id, values):
        def process_box_origin(self, values):
        def process_box_vectors(self, values):
        def process_atom_type(self, atom_type)


    Parameters
    ----------
    handler :
       handler will handle the parsed information provided by this class

    """
    def __init__(self, handler):
        self._handler = handler
        self._simulation_box = SimulationBoxParser(self._handler)

    def parse(self, file_name):
        """ Read in data file containing current state of simulation

        """
        self._handler.begin()
        state = _ReadState.UNKNOWN

        with open(file_name, 'r') as f:
            line_number = 0
            try:
                for line in f:
                    line_number += 1

                    # skip blank lines
                    if not line.strip():
                        continue

                    state = _ReadState.get_state(state, line)
                    if state is _ReadState.ATOM_TYPES:
                        number_types = int(string.split(line, " ", 1)[0])
                        self._handler.process_number_atom_types(
                            number_types)
                    elif state is _ReadState.MASSES:
                        values = line.split()
                        self._handler.process_masses(
                            int(values[0]),
                            int(values[1]))
                    elif state is _ReadState.ATOMS:
                        values = line.split()
                        id = int(values[0])
                        type_coord_etc = [int(values[1])]
                        for v in map(float, values[2:]):
                            type_coord_etc.append(v)
                        self._handler.process_atoms(id, type_coord_etc)
                    elif state is _ReadState.ATOMS_BEGIN:
                        # atom-type is listed after '#', e.g: "Atom # sphere"
                        values = line.split('#', 1)
                        if len(values) > 1:
                            atom_type = values[1].strip()
                            if atom_type:
                                self._handler.process_atom_type(atom_type)
                    elif state is _ReadState.VELOCITIES:
                        values = line.split()
                        self._handler.process_velocities(
                            int(values[0]),
                            map(float, values[1:]))
                    elif state is _ReadState.SIMULATION_BOX_BOUNDARIES:
                        self._simulation_box.parse(line)
                    else:
                        continue
            except Exception:
                print("problem with line number=", line_number)
                raise
        self._handler.end()


class _ReadState(Enum):
    UNKNOWN, UNSUPPORTED, \
        SIMULATION_BOX_BOUNDARIES, \
        MASSES_BEGIN, MASSES, \
        VELOCITIES_BEGIN, VELOCITIES, \
        ATOM_TYPES, \
        ATOMS, \
        ATOMS_BEGIN = range(10)

    @staticmethod
    def get_state(current_state, line):
        """ Reads line and returns state

        """

        # TODO how the state is determined and how
        # we transition to other states needs to be
        # rewritten.
        if (current_state is _ReadState.ATOMS_BEGIN or
                current_state is _ReadState.ATOMS):
            new_state = _ReadState.ATOMS
        elif (current_state is _ReadState.MASSES_BEGIN or
                current_state is _ReadState.MASSES):
            new_state = _ReadState.MASSES
        elif (current_state is _ReadState.VELOCITIES_BEGIN or
                current_state is _ReadState.VELOCITIES):
            new_state = _ReadState.VELOCITIES
        else:
            new_state = _ReadState.UNKNOWN

        box_re = '\\bxlo\\b\s*\\bxhi|\\bylo\\b\s*\\byhi|\\bzlo\\b\s*\\bzhi'
        if re.findall(box_re, line):
            new_state = _ReadState.SIMULATION_BOX_BOUNDARIES
        elif "atom types" in line:
            new_state = _ReadState.ATOM_TYPES
        elif "Masses" in line:
            new_state = _ReadState.MASSES_BEGIN
        elif "Velocities" in line:
            new_state = _ReadState.VELOCITIES_BEGIN
        elif "Atoms" in line:
            new_state = _ReadState.ATOMS_BEGIN
        elif "Pair Coeffs" in line:
            new_state = _ReadState.UNSUPPORTED

        return new_state


class SimulationBoxParser(object):
    """ Classes parses lines related to simulation box

    parses lines related to simulation box and then calls the
    related handler methods when enough information is read
    (i.e. all related lines in file have been read)

    The relevant lines have the form:
        0.0000000000000000e+00 2.5687134504920127e+01 xlo xhi
        -2.2245711031688635e-03 2.2247935602791809e+01 ylo yhi
        -3.2108918131150160e-01 3.2108918131150160e-01 zlo zhi

    Once all needed information is parsed, then the "handler"'s
    process_box_vectors is called.

    Parameters
    ----------
    handler :
        handler's 'process_box_vectors' and 'process_box_origin' methods
        will be called once the required information has been parsed

    """
    _components = ['x', 'y', 'z']

    def __init__(self, handler):
        self._handler = handler
        self._stored = OrderedDict()

    def parse(self, line):
        values = map(float, line.split()[:2])

        for component in SimulationBoxParser._components:
            if component in line:
                self._stored[component] = values
                break

        if SimulationBoxParser._components == self._stored.keys():
            origin = tuple(
                value[0] for value in self._stored.values())  # xlo, ylo, zlo
            self._handler.process_box_origin(origin)

            diffs = [value[1] - value[0] for value in self._stored.values()]
            vectors = [(diffs[0], 0.0, 0.0),
                       (0.0, diffs[1], 0.0),
                       (0.0, 0.0, diffs[2])]
            self._handler.process_box_vectors(vectors)
