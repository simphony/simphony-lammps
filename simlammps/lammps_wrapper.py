"""LAMMPS SimPhoNy Wrapper.

This module provides a wrapper for LAMMPS-md
"""
import os
import contextlib
import shutil
import tempfile

from simphony.api import CUDS, CUBA
from simphony.core.data_container import DataContainer
from simphony.cuds.abc_modeling_engine import ABCModelingEngine
from simphony.cuds.abc_particles import ABCParticles
from simphony.cuds.meta import api
import simphony.cuds.particles as scp

from simlammps.common.atom_style import AtomStyle
from simlammps.config.script_writer import ScriptWriter
from simlammps.internal.lammps_internal_data_manager import LammpsInternalDataManager

from simlammps.io.lammps_fileio_data_manager import LammpsFileIoDataManager
from simlammps.io.lammps_process import LammpsProcess


def _temp_directory():
    """Provide a temp directory.

    The name of the created temp directory is returned when context is entered
    and this directory is deleted when context is exited
    """
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

_TEMP_DIRECTORY = contextlib.contextmanager(_temp_directory)


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
        self.boundary_condition = DataContainer()
        self.BC = self.boundary_condition
        self.computational_model = DataContainer()
        self.CM = self.computational_model
        self.solver_parameters = DataContainer()
        self.SP = self.solver_parameters
        self.cuds_sd = kwargs.get('cuds', CUDS())
        self.SD = self.cuds_sd

        self._use_internal_interface = use_internal_interface
        self._script_writer = ScriptWriter(AtomStyle.ATOMIC)

        if self._use_internal_interface:
            import lammps
            self._lammps = lammps.lammps(cmdargs=["-log", "none"])
            self._data_manager = LammpsInternalDataManager(self._lammps,
                                                           self.cuds_sd,
                                                           AtomStyle.ATOMIC)
        else:
            self._data_manager = LammpsFileIoDataManager(self.cuds_sd, AtomStyle.ATOMIC)

        # Number of runs
        self._run_count = 0

        # Dataset uids which are added.
        self._dataset_uids = []

        # Call the base class in order to load CUDS
        super(LammpsWrapper, self).__init__(**kwargs)

    def _count_of(self, cuds, item_type):
        """Workaround for broken CUDS counter."""
        count = 0
        for item in cuds.iter():
            if isinstance(item, item_type):
                count += 1
        return count

    def _check_cuds(self, cuds):
        """Check the given cuds for consistency."""
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

        if cuds.count_of(CUBA.MOLECULAR_DYNAMICS) != 1:
            raise Exception('simlammps supports only MD')

        if cuds.count_of(CUBA.BOX) != 1:
            raise Exception('simlammps needs one box')

        if cuds.count_of(CUBA.INTERATOMIC_POTENTIAL) != 1:
            raise Exception('Lammps needs one interatomic potention')

        if cuds.count_of(CUBA.CONDITION) != 1:
            raise Exception('Sorry only one condition is accepted, not %s' %
                            cuds.count_of(CUBA.CONDITION))

        if not cuds.count_of(CUBA.INTEGRATION_TIME):
            raise Exception('Only one integration time setup is accepted')

    def _load_cuds(self):
        """Load CUDS data into lammps engine."""
        cuds = self.get_cuds()
        if not cuds:
            return

        # Move checks to a separate method
        self._check_cuds(cuds)

        material_to_atom = {}
        number_atom_types = 0
        materials = []
        for mat in cuds.iter(item_type=CUBA.MATERIAL):
            if CUBA.MASS not in mat.data:
                raise Exception('Material needs mass property!')
            number_atom_types += 1
            material_to_atom[mat.uid] = number_atom_types
            materials.append(mat)

        if len(materials) != 1:
            raise Exception('Invalid number of materials provided: %d' % len(materials))

        box = self._get_box(cuds)
        particle_sum = 0

        for particle_container in cuds.iter(item_type=CUBA.PARTICLES):
            particle_sum += len(particle_container)
            self._assign_material_to_particles(particle_container, materials[0])
            data = materials[0].data
            data.update({CUBA.VECTOR: box.vector})
            particle_container.data = data
            # Add dataset when it is not already there. Rely on uid.
            if particle_container.uid not in self._dataset_uids:
                self.add_dataset(particle_container)
                self._dataset_uids.append(particle_container.uid)

        if particle_sum == 0:
            raise Exception('simlammps needs some particles')

        # TODO: add thermo check. else?
        for thermo in cuds.iter(item_type=CUBA.THERMOSTAT):
            if isinstance(thermo, api.TemperatureRescaling):
                self.computational_model[CUBA.THERMODYNAMIC_ENSEMBLE] = 'NVE'

        for integration_time in cuds.iter(item_type=CUBA.INTEGRATION_TIME):
            self.computational_model[CUBA.TIME_STEP] = integration_time.step
            self.computational_model[CUBA.NUMBER_OF_TIME_STEPS] =\
                int(integration_time.final / integration_time.step)

        for condition in cuds.iter(item_type=CUBA.CONDITION):
            if isinstance(condition, api.Periodic):
                self.boundary_condition[CUBA.FACE] = [
                    'periodic',
                    'periodic',
                    'periodic']
                continue
            raise Exception('Sorry, I am confused!')

        interatomic_potential = self._get_interatomic_potential(cuds)

        self.solver_parameters[CUBA.PAIR_POTENTIAL] =\
            'lj:\n  global_cutoff: {global_cutoff}\n'\
            '  parameters:\n  - pair: [{mat1}, {mat2}]\n'\
            '    epsilon: {energy_well_depth}\n'\
            '    sigma: {vanderwaals_radious}\n'\
            '    cutoff: {cutoff}\n'\
            .format(global_cutoff=1.12246,
                    mat1=material_to_atom[interatomic_potential.material[0].uid],
                    mat2=material_to_atom[interatomic_potential.material[1].uid],
                    energy_well_depth=interatomic_potential.energy_well_depth,
                    vanderwaals_radious=interatomic_potential.van_der_waals_radius,
                    cutoff=interatomic_potential.cutoff_distance)

    def _assign_material_to_particles(self, particle_container, material):
        update_list = []
        for particle in particle_container.iter():
            particle.data[CUBA.MATERIAL_TYPE] = material.uid
            update_list.append(particle)
        particle_container.update(update_list)


    def _get_box(self, cuds):
        boxes = []
        for box in cuds.iter(item_type=CUBA.BOX):
            boxes.append(box)

        if len(boxes) != 1:
            raise Exception('Invalid number of boxes provided: %d' % len(boxes))
        return boxes[0]

    def _get_interatomic_potential(self, cuds):
        ips = []
        for interatomic_potential in cuds.iter(item_type=CUBA.INTERATOMIC_POTENTIAL):
            ips.append(interatomic_potential)

        if len(ips) != 1:
            raise Exception('Wrong number of interatomic potentials: %d' % len(ips))

        return ips[0]

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
        """Run lammps-engine based on configuration and data."""
        if self._run_count > 0:
            self._load_cuds()

        if self._use_internal_interface:
            self._data_manager.flush()
            commands = ''
            commands += ScriptWriter.get_pair_style(self.solver_parameters)
            commands += ScriptWriter.get_fix(CM=self.computational_model)
            commands += ScriptWriter.get_pair_coeff(self.solver_parameters)
            commands += ScriptWriter.get_boundary(self.boundary_condition, change_existing_boundary=True)
            commands += ScriptWriter.get_run(CM=self.computational_model)
            for command in commands.splitlines():
                self._lammps.command(command)
            # after running, we read any changes from lammps
            self._data_manager.read()
        else:
            with _TEMP_DIRECTORY() as temp_dir:
                input_data_filename = os.path.join(temp_dir, 'data_in.lammps')
                output_data_filename = os.path.join(temp_dir,
                                                    'data_out.lammps')
                self._data_manager.flush(input_data_filename)

                commands = self._script_writer.get_configuration(
                    input_data_file=input_data_filename,
                    output_data_file=output_data_filename,
                    BC=self.boundary_condition,
                    CM=self.computational_model,
                    SP=self.solver_parameters,
                    materials=[mat for mat in self.cuds_sd.iter(item_type=CUBA.MATERIAL)])

                process = LammpsProcess(lammps_name=os.environ.get('SIM_LAMMPS_BIN', 'lammps'),
                                        log_directory=temp_dir)

                process.run(commands)
                self._data_manager.read(output_data_filename)
        # A naive flag for the next run.
        self._run_count += 1

        if self.get_cuds():
            # Replace datasets in CUDS with proxy ones.
            for ds_name in self._data_manager:
                proxy_dataset = self.get_dataset(ds_name)
                cuds_dataset = self.get_cuds().get_by_name(ds_name)
                # FIXME: don't touch internal state of proxy_dataset. Add a param.
                proxy_dataset._uid = cuds_dataset.uid
                self.get_cuds().update([self.get_dataset(ds_name)])
