"""LAMMPS SimPhoNy Wrapper.

This module provides a wrapper for LAMMPS-md
"""
import contextlib
import os
import shutil
import tempfile

from io.lammps_fileio_data_manager import LammpsFileIoDataManager
from io.lammps_process import LammpsProcess

from common.atom_style import AtomStyle

from config.script_writer import ScriptWriter

from cuba_extension import CUBAExtension

from internal.lammps_internal_data_manager import LammpsInternalDataManager

from simphony.core import CUBA
from simphony.core.data_container import DataContainer
from simphony.cuds import CUDS
from simphony.cuds.abc_modeling_engine import ABCModelingEngine
from simphony.cuds.abc_particles import ABCParticles
from simphony.cuds.meta import api
import simphony.cuds.particles as scp


def _temp_directory():
    """Provide a temp directory.

    The name of the created temp directory is returned when context is entered
    and this directory is deleted when context is exited
    """
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

_temp_directory = contextlib.contextmanager(_temp_directory)


class LammpsWrapper(ABCModelingEngine):
    """Wrapper to LAMMPS-md."""

    def __init__(self, use_internal_interface=False, **kwargs):
        """Constructor.

        Parameters
        ----------
        engine_type : EngineType
            type of engine

        use_internal_interface : bool, optional
            If true, then the internal interface (library) is used when
            communicating with LAMMPS, if false, then file-io interface is
            used where input/output files are used to communicate with LAMMPS
        """
        self.BC = DataContainer()
        self.CM = DataContainer()
        self.SP = DataContainer()
        self.CM_extension = {}
        self.SP_extension = {}
        self.BC_extension = {}
        self.SD = kwargs.get('cuds', CUDS())

        self._use_internal_interface = use_internal_interface
        atom_style = AtomStyle.ATOMIC
        self._executable_name = 'lammps'
        self._script_writer = ScriptWriter(atom_style)

        if self._use_internal_interface:
            import lammps
            # lammps.lammps(cmdargs=["-screen", "none", "-log", "none"])
            self._lammps = lammps.lammps()
            self._data_manager = LammpsInternalDataManager(self._lammps,
                                                           self.SD,
                                                           atom_style)
        else:
            self._data_manager = LammpsFileIoDataManager(self.SD, atom_style)

        # Call the base class in order to load CUDS
        super(LammpsWrapper, self).__init__(**kwargs)

    def _count_of(self, cuds, item_type):
        """Workaround for broken CUDS counter."""
        count = 0
        for c in cuds.iter():
            if isinstance(c, item_type):
                count += 1
        return count

    def _load_cuds(self):
        '''Load CUDS data into lammps engine.'''
        cuds = self.get_cuds()
        if not cuds:
            return

        # FIXME: `count_of` is broken for non-meta classes,
        # e.g. Particles, Particle, Mesh, etc.
        # if cuds.count_of(CUBA.PARTICLES) != 1:
        if self._count_of(cuds, scp.Particles) != 1:
            raise Exception('This version of simlammps'
                            ' needs only one particle dataset, not %s' %
                            self._count_of(cuds, scp.Particles))
        if cuds.count_of(CUBA.MATERIAL) != 1:
            raise Exception('This version of simlammps needs'
                            ' only one material not %s' %
                            cuds.count_of(CUBA.MATERIAL))

        material_to_atom = {}
        number_atom_types = 0
        for mat in cuds.iter(item_type=CUBA.MATERIAL):
            if CUBA.MASS not in mat.data:
                raise Exception('Material needs mass property!')
            number_atom_types += 1
            material_to_atom[mat.uid] = number_atom_types

        for particles in cuds.iter(item_type=CUBA.PARTICLES):
            update_list = []
            for single_particle in particles.iter():
                single_particle.data[CUBA.MATERIAL_TYPE] = mat.uid
                update_list.append(single_particle)
            particles.update(update_list)

        for b in cuds.iter(item_type=CUBA.BOX):
            pass

        particle_sum = 0
        for ds in cuds.iter(item_type=CUBA.PARTICLES):
            particle_sum += len(ds)
            ds.data = mat.data
            ds.data_extension = {
                CUBAExtension.BOX_VECTORS: b.vector}
            self.add_dataset(ds)

        if particle_sum == 0:
            raise Exception('simlammps needs some particles')

        if cuds.count_of(CUBA.MOLECULAR_DYNAMICS) != 1:
            raise Exception('simlammps supports only MD')

        if cuds.count_of(CUBA.BOX) != 1:
            raise Exception('simlammps needs one box')

        for termo in cuds.iter(item_type=CUBA.THERMOSTAT):
            if isinstance(termo, api.TemperatureRescaling):
                self.CM_extension[CUBA.THERMODYNAMIC_ENSEMBLE] = 'NVE'
                continue

        if not cuds.count_of(CUBA.INTEGRATION_TIME):
            raise Exception('Only one integration time setup is accepted')

        for i in cuds.iter(item_type=CUBA.INTEGRATION_TIME):
            self.CM[CUBA.TIME_STEP] = i.step
            self.CM[CUBA.NUMBER_OF_TIME_STEPS] = int(i.final / i.step)

        if cuds.count_of(CUBA.CONDITION) != 1:
            raise Exception('Sorry only one condition is accepted, not %s' %
                            cuds.count_of(CUBA.CONDITION))

        for c in cuds.iter(item_type=CUBA.CONDITION):
            if isinstance(c, api.Periodic):
                self.BC_extension[CUBAExtension.BOX_FACES] = [
                    'periodic',
                    'periodic',
                    'periodic']
                continue
            raise Exception('Sorry, I am confused!')

        if cuds.count_of(CUBA.INTERATOMIC_POTENTIAL) != 1:
            raise Exception('Lammps needs one interatomic potention')

        for ip in cuds.iter(item_type=CUBA.INTERATOMIC_POTENTIAL):
            pass

        self.SP_extension[CUBAExtension.PAIR_POTENTIALS] =\
            'lj:\n  global_cutoff: {global_cutoff}\n'\
            '  parameters:\n  - pair: [{mat1}, {mat2}]\n'\
            '    epsilon: {energy_well_depth}\n'\
            '    sigma: {vanderwaals_radious}\n'\
            '    cutoff: {cutoff}\n'\
            .format(global_cutoff=1.12246,
                    mat1=material_to_atom[ip.material[0].uid],
                    mat2=material_to_atom[ip.material[1].uid],
                    energy_well_depth=ip.energy_well_depth,
                    vanderwaals_radious=ip.van_der_waals_radius,
                    cutoff=ip.cutoff_distance)

    def add_dataset(self, container):
        """Add a CUDS container.

        Parameters
        ----------
        container : {ABCParticles}
            The CUDS container to add to the engine.

        Raises
        ------
        TypeError:
            If the container type is not supported (i.e. ABCLattice, ABCMesh).
        ValueError:
            If there is already a dataset with the given name.

        """
        if not isinstance(container, ABCParticles):
            raise TypeError(
                'The type of the dataset container is not supported')
        if container.name in self._data_manager:
            raise ValueError("Particle container '{}' already exists"
                             .format(container.name))
        self._data_manager.new_particles(container)

    def get_dataset(self, name):
        """Get the dataset.

        The returned particle container can be used to query
        and change the related data inside LAMMPS.

        Parameters
        ----------
        name: str
            name of CUDS container to be retrieved.

        Returns
        -------
        container :
            A proxy of the dataset named ``name`` that is stored
            internally in the Engine.

        Raises
        ------
        ValueError:
            If there is no dataset with the given name

        """
        if name in self._data_manager:
            return self._data_manager[name]

        raise ValueError("Particle container '{}` does not exist"
                         .format(name))

    def get_dataset_names(self):
        """Return the names of all the datasets."""
        return [name for name in self._data_manager]

    def remove_dataset(self, name):
        """Remove a dataset.

        Parameters
        ----------
        name: str
            name of CUDS container to be deleted

        Raises
        ------
        ValueError:
            If there is no dataset with the given name

        """
        if name in self._data_manager:
            del self._data_manager[name]
        else:
            raise ValueError("Particles '{}\\' does not exist".format(name))

    def iter_datasets(self, names=None):
        """Return an iterator over a subset or all of the containers.

        Parameters
        ----------
        names : sequence of str, optional
            names of specific containers to be iterated over. If names is not
            given, then all containers will be iterated over.

        """
        if not names:
            for name in self._data_manager:
                yield self._data_manager[name]
        else:
            for name in names:
                if name in self._data_manager:
                    yield self._data_manager[name]
                    continue
                raise ValueError("Particle container '{}\\` does not exist"
                                 .format(name))

    def run(self):
        ''' Run lammps-engine based on configuration and data

        '''
        if self._use_internal_interface:
            self._data_manager.flush()
            commands = ''
            commands += ScriptWriter.get_pair_style(
                _combine(self.SP, self.SP_extension))
            commands += ScriptWriter.get_fix(CM=_combine(self.CM,
                                                         self.CM_extension))
            commands += ScriptWriter.get_pair_coeff(_combine(
                self.SP, self.SP_extension))
            commands += ScriptWriter.get_boundary(_combine(
                self.BC, self.BC_extension), change_existing_boundary=True)
            commands += ScriptWriter.get_run(CM=_combine(
                self.CM, self.CM_extension))
            for command in commands.splitlines():
                self._lammps.command(command)
            # after running, we read any changes from lammps
            self._data_manager.read()
        else:
            with _temp_directory() as temp_dir:
                input_data_filename = os.path.join(temp_dir, 'data_in.lammps')
                output_data_filename = os.path.join(temp_dir,
                                                    'data_out.lammps')
                self._data_manager.flush(input_data_filename)

                commands = self._script_writer.get_configuration(
                    input_data_file=input_data_filename,
                    output_data_file=output_data_filename,
                    BC=_combine(self.BC, self.BC_extension),
                    CM=_combine(self.CM, self.CM_extension),
                    SP=_combine(self.SP, self.SP_extension),
                    materials=[
                        material for material in
                        self.SD.iter(item_type=CUBA.MATERIAL)])

                process = LammpsProcess(lammps_name=self._executable_name,
                                        log_directory=temp_dir)

                process.run(commands)
                self._data_manager.read(output_data_filename)


def _combine(data_container, data_container_extension):
    ''' Combine a the approved CUBA with non-approved CUBA key-values

    Parameters
    ----------
    data_container : DataContainer
        data container with CUBA attributes
    data_container_extension : dict
        data container with non-approved CUBA attributes

    Returns
    ----------
    dict
        dictionary containing the approved adn non-approved
        CUBA key-values

    """
    result = dict(data_container_extension)
    result.update(data_container)
    return result
