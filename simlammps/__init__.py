from simphony.engine import ABCEngineExtension
from simphony.engine import EngineInterface
from simphony.engine.decorators import register

from .lammps_wrapper import LammpsWrapper
from .io.file_utility import read_data_file

__all__ = ["LammpsWrapper", "read_data_file"]


@register
class SimlammpsExtension(ABCEngineExtension):
    """Simphony-lammps-md extension.

    This extension provides support for lammps and liggghts engines.
    """

    def get_supported_engines(self):
        """Get metadata about supported engines.

        Returns
        -------
        list: a list of EngineMetadata objects
        """
        # TODO: Add proper features as soon as the metadata classes are ready.
        # lammps_features =\
        #     self.create_engine_metadata_feature(MolecularDynamics(),
        #                                         [Verlet()])
        lammps_features = None
        lammps = self.create_engine_metadata('LAMMPS',
                                             lammps_features,
                                             [EngineInterface.Internal,
                                              EngineInterface.FileIO])

        return [lammps]

    def create_wrapper(self, cuds, engine_name, engine_interface):
        """Creates a wrapper to the requested engine.

        Parameters
        ----------
        cuds: CUDS
          CUDS computational model data
        engine_name: str
          name of the engine, must be supported by this extension
        engine_interface: EngineInterface
          the interface to interact with engine

        Returns
        -------
        ABCEngineExtension: A wrapper configured with cuds and ready to run
        """
        use_internal_interface = False
        if engine_interface == EngineInterface.Internal:
            use_internal_interface = True

        if engine_name != 'LAMMPS':
            raise Exception('Only LAMMPS engine is supported. '
                            'Unsupported eninge: %s', engine_name)

        return LammpsWrapper(cuds=cuds,
                             use_internal_interface=use_internal_interface)
