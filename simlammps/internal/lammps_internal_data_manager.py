import uuid

from simphony.cuds.meta.api import Material
from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer
from simphony.cuds.particles import Particle

from .particle_data_cache import ParticleDataCache
from ..abc_data_manager import ABCDataManager
from ..common import globals
from ..common.atom_style_description import ATOM_STYLE_DESCRIPTIONS
from ..config.domain import get_box
from ..config.script_writer import ScriptWriter
from ..cuba_extension import CUBAExtension


class MaterialAtomTypeManager(object):
    """ Class keeps track of materials and their repsective atom-types

        In Simphony, we have materials which each have a UID while in
        lammps there is atom-type (that goes from 1 to N).  The relationship
        between these two things is managed by this class.

        Parameters:
        -----------
        materials : list of Material
            materials in our system
    """
    def __init__(self, materials):
        self._materials = materials

        # map from material-ui to atom_type
        self._material_to_atom = {}

        # inverse of _material_to_atom
        self._atom_to_material = {}

        self.update_materials(materials)

    def update_materials(self, materials):
        """ Update with new list of materials

        Any materials already known by this manager will be ignored.  New
        materials will be given the next available atom_type.

        """
        for material in materials:
            if material.uid not in self._material_to_atom:
                atom_type = len(self._material_to_atom) + 1
                self._material_to_atom[material.uid] = atom_type

        # get inverse
        if len(self._atom_to_material) != len(self._material_to_atom):
            self._atom_to_material = {
                v: k for k, v in self._material_to_atom.iteritems()}

    def get_material_uid(self, atom_type):
        """ Return material uid

        Raises
        ------
        KeyError
            if atom_type is unknown.


        """
        return self._atom_to_material[atom_type]

    def get_atom_type(self, material_uid):
        """ Return atom type

        If we are not yet aware of 'material_uid', we will add it to our
        list and assign it a lammps_atom.

        """
        if material_uid not in self._material_to_atom:
            self.update_materials([material_uid])
        return self._material_to_atom[material_uid]

    def has_atom_type(self, atom_type):
        return atom_type in self._atom_to_material

    def iter_material_uids(self):
        for material_ui in self._material_to_atom.iterkeys():
            yield material_ui


class LammpsInternalDataManager(ABCDataManager):
    """  Class managing LAMMPS data information using file-io

    The class performs communicating the data to and from LAMMPS using the
    internal interface (i.e. LAMMPS shared library).

    Parameters
    ----------
    lammps :
        lammps python wrapper
    state_data : StateData
        state data
    atom_style : AtomStyle
           atom_style
    """
    def __init__(self, lammps, state_data, atom_style):
        super(LammpsInternalDataManager, self).__init__()

        self._lammps = lammps
        self._state_data = state_data
        self._atom_style = atom_style

        materials = [m for m in state_data.iter(Material)]
        self._material_atom_type_manager = MaterialAtomTypeManager(materials)

        dummy_bc = {CUBAExtension.BOX_FACES: ("periodic",
                                              "periodic",
                                              "periodic")}
        commands = "dimension 3\n"
        script_writer = ScriptWriter(self._atom_style)
        commands = script_writer.get_initial_setup()

        commands += ScriptWriter.get_boundary(dummy_bc)
        for command in commands.splitlines():
            self._lammps.command(command)

        # create initial box with dummy values
        vectors = [(25.0, 0.0, 0.0),
                   (0.0, 22.0, 0.0),
                   (0.0, 0.0, 6.196)]
        dummy_box_data = {CUBAExtension.BOX_VECTORS: vectors,
                          CUBAExtension.BOX_ORIGIN: (0.0, 0.0, 0.0)}
        self._lammps.command(get_box([dummy_box_data], command_format=True))

        # due to not being able to alter the number of types (issue #66),
        # we set the number of supported types to a high number and then
        # give dummy values for the unused types
        self._lammps.command(
            "create_box {} box".format(globals.MAX_NUMBER_TYPES))

        # map from uname of Particles to Set of (particle) uids
        self._particles = {}

        # cache of coordinates and point data
        self._particle_data_cache = \
            ParticleDataCache(self._lammps,
                              self._atom_style,
                              self._material_atom_type_manager)

        # cache of data containers for each Particles-container
        self._pc_data = {}
        self._pc_data_extension = {}

    def get_data(self, uname):
        """Returns data container associated with particle container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """
        return DataContainer(self._pc_data[uname])

    def set_data(self, data, uname):
        """Sets data container associated with particle container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """
        self._pc_data[uname] = DataContainer(data)

    def get_data_extension(self, uname):
        """Returns data container extension associated with particle container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """
        return dict(self._pc_data_extension[uname])

    def set_data_extension(self, data, uname):
        """Sets data container extension associated with particle container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """
        self._pc_data_extension[uname] = dict(data)

    def _handle_delete_particles(self, uname):
        """Handle when a Particles is deleted

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """
        uids_to_be_deleted = [uid for uid in self._particles[uname]]

        for uid in uids_to_be_deleted:
            self.remove_particle(uid, uname)

        del self._pc_data[uname]
        del self._pc_data_extension[uname]
        del self._particles[uname]

    def _handle_new_particles(self, uname, particles):
        """Add new particle container to this manager.

        Parameters
        ----------
        uname : string
            non-changing unique name of particles
        particles : ABCParticles
            particle container to be added

        """

        self._particles[uname] = set()

        self._pc_data[uname] = DataContainer(particles.data)

        if hasattr(particles, 'data_extension'):
            self._pc_data_extension[uname] = dict(particles.data_extension)
        else:
            # create empty dc extension
            self._pc_data_extension[uname] = {}

        self._update_simulation_box()

        self._add_atoms(iterable=particles.iter_particles(),
                        uname=uname,
                        safe=True)

        # TODO bonds

    def _update_simulation_box(self):
        """Update simulation box

        """
        cmd = get_box([de for _, de in self._pc_data_extension.iteritems()],
                      command_format=True,
                      change_existing=True)
        self._lammps.command(cmd)

    def get_particle(self, uid, uname):
        """Get particle

        Parameters
        ----------
        uid :
            uid of particle
        uname : string
            name of particle container

        """
        if uid in self._particles[uname]:
            coordinates = self._particle_data_cache.get_coordinates(uid)
            data = self._particle_data_cache.get_particle_data(uid)

            p = Particle(uid=uid,
                         coordinates=coordinates,
                         data=data)
            return p
        else:
            raise KeyError("uid ({}) was not found".format(uid))

    def update_particles(self, iterable, uname):
        """Update particles

        """
        for particle in iterable:
            if particle.uid in self._particles[uname]:
                self._set_particle(particle, uname)
            else:
                raise ValueError(
                    "particle id ({}) was not found".format(particle.uid))

    def add_particles(self, iterable, uname):
        """Add particle

        """
        return self._add_atoms(iterable, uname, safe=False)

    def remove_particle(self, deleted_uid, uname):
        """Remove particle

        Parameters
        ----------
        uid :
            uid of particle
        uname : string
            non-changing unique name of particles

        """

        # remove the deleted id from our book keeping
        self._particles[uname].remove(deleted_uid)

        # Make a local copy of ALL the particles EXCEPT for the deleted one
        saved_particles = {}
        for uname in self._particles:
            saved_particles[uname] = {}
            for uid in self._particles[uname]:
                coordinates = self._particle_data_cache.get_coordinates(uid)
                data = self._particle_data_cache.get_particle_data(uid)

                p = Particle(uid=uid,
                             coordinates=coordinates,
                             data=data)
                saved_particles[uname][uid] = p

        self._lammps.command("delete_atoms group all compress yes")

        # Use the new cache
        self._particle_data_cache = \
            ParticleDataCache(self._lammps,
                              self._atom_style,
                              self._material_atom_type_manager)

        # re-add the saved atoms
        for uname in saved_particles:
            self._add_atoms(saved_particles[uname].values(), uname, safe=True)

    def has_particle(self, uid, uname):
        """Has particle

        Parameters
        ----------
        uid :
            uid of particle
        uname : string
            non-changing unique name of particles

        """
        return uid in self._particles[uname]

    def iter_particles(self, uname, uids=None):
        """Iterate over the particles of a certain type

        Parameters
        ----------
        uids : list of particle uids
            sequence of uids of particles that should be iterated over. If
            uids is None then all particles will be iterated over.
        uname : string
            non-changing unique name of particles

        """
        if uids:
            for uid in uids:
                yield self.get_particle(uid, uname)
        else:
            for uid in self._particles[uname]:
                yield self.get_particle(uid, uname)

    def number_of_particles(self, uname):
        """Get number of particles in a container

        Parameters
        ----------
        uname : string
            non-changing unique name of particles

        """
        return len(self._particles[uname])

    def read(self):
        """read latest state

        """
        self._update_from_lammps()

    def flush(self):
        """flush state

        """
        # TODO we should improve this as we are calling this although we
        # don't know if there were any changes to the materials
        self._update_material_atom_type_manager()

        if ATOM_STYLE_DESCRIPTIONS[self._atom_style].has_mass_per_type:
            # TODO set once and update only when mass has changed
            self._update_mass()

        if self._particles:
            # update the particle-data
            self._particle_data_cache.send()
        else:
            raise RuntimeError(
                "No particles.  Lammps cannot run without a particle")
        # TODO handle properly when there are no particle containers
        # or when some of them do not contain any particles
        # (i.e. someone has deleted all the particles)

    def _update_mass(self):
        mass = {}
        for material in self._state_data.iter(Material):
            atom_type = self._material_atom_type_manager.get_atom_type(
                material.uid)
            if CUBA.MASS not in material.data:
                raise RuntimeError(
                    "Material does not have the required mass")
            else:
                mass = material.data[CUBA.MASS]
                # TODO format mass correctly
                self._lammps.command("mass {} {}".format(atom_type,
                                                         mass))

        # set the mass of all unused types (see issue #66)
        for atom_type in range(1, globals.MAX_NUMBER_TYPES+1):
            if not self._material_atom_type_manager.has_atom_type(atom_type):
                self._lammps.command("mass {} {}".format(atom_type, 1.0))

    def _update_from_lammps(self):
        self._particle_data_cache.retrieve()

    def _set_particle(self, particle, uname):
        """ Set coordinates and data for a particle

        Parameters
        ----------
        particle : Particle
            particle to be set
        uname : string
            non-changing unique name of particle container

        """
        self._particle_data_cache.set_particle(particle.coordinates,
                                               particle.data,
                                               particle.uid)

    def _add_atoms(self, iterable, uname, safe=False):
        """ Add multiple particles as atoms to lammps

        The number of atoms to be added are randomly added somewhere
        in the simulation box by LAMMPS and then their positions (and
        other values will be corrected/updated..during next flush)

        Parameters
        ----------
        iterable : iterable of Particle objects
            particle with CUBA.MATERIAL_TYPE

        uname : str
            non-changing unique name of particle container

        safe : bool
            True if uids do not need to be to be checked (e.g.. in the
            case that all particles are being added to an empty particle
            container). False if uids need to be checked.

        Returns
        -------
        uuid : list of UUID4
            uids of added particles

        """

        # TODO we should improve this as we are calling this although we
        # don't know if there were any changes to the materials
        self._update_material_atom_type_manager()

        # keep track of how many particles we add per particle type
        number_added_per_material = {}
        for material_uid in \
                self._material_atom_type_manager.iter_material_uids():
            number_added_per_material[material_uid] = 0

        uids = []
        for particle in iterable:
            if particle.uid is None:
                particle.uid = uuid.uuid4()

            number_added_per_material[particle.data[CUBA.MATERIAL_TYPE]] += 1

            if not safe and particle.uid in self._particles[uname]:
                raise ValueError(
                    "particle with same uid ({}) already exists".format(
                        particle.uid))

            self._particles[uname].add(particle.uid)
            self._set_particle(particle, uname)

            uids.append(particle.uid)

        # create atoms in lammps
        for material, number in number_added_per_material.iteritems():
            if number > 0:
                atom_type = \
                    self._material_atom_type_manager.get_atom_type(material)
                self._lammps.command(
                    "create_atoms {} random {} 42 NULL".format(atom_type,
                                                               number))
        return uids

    def _update_material_atom_type_manager(self):
        """ Update materials from state data

        """
        materials = [m for m in self._state_data.iter(Material)]
        self._material_atom_type_manager.update_materials(materials)
