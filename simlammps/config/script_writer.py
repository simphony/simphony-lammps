from simphony.core.cuba import CUBA

from simlammps.config.pair_style import PairStyle


class ConfigurationError(RuntimeError):
    pass


class ScriptWriter(object):
    """ Writer of a LAMMPS-commands script

    The ScriptWriter generates a series of LAMMPS commands
    (that make up a LAMMPS-input script).

    The command script generated by this class can be passed to
    a LAMMPS executable as a file or string. Alternately, this
    script can be passed to the library interface of LAMMPS or
    individual commands generated by this script can be passed
    "one by one" to the library interface of LAMMPS

    """

    @staticmethod
    def get_configuration(input_data_file, output_data_file, BC, CM, SP):
        """ Return configuration command-script

        Parameters
        ----------
        input_data_file: string
            name of data file to be read at beginning of run (input)
        output_data_file: string
            name of data file to be written after run (output)
        BC : DataContainer
            container of attributes related to the boundary conditions
        CM : DataContainer
            container of attributes related to the computational method
        SP : DataContainer
            container of attributes related to the system parameters/conditions

        Returns
        -------
        command script - string
            lines of a LAMMPS command script

        """

        _check_configuration(CM)

        number_steps = CM[CUBA.NUMBER_OF_TIME_STEPS]
        time_step = CM[CUBA.TIME_STEP]

        pair_style = PairStyle(SP)
        pair_style_input = pair_style.get_global_config()
        pair_coeff_input = pair_style.get_pair_coeffs()

        # TODO
        boundary = _get_boundary(BC)

        # TODO
        fixes = _get_thermodynamic_ensemble(CM)

        return CONFIGURATION.format(BOUNDARY=boundary,
                                    INPUT_DATAFILE=input_data_file,
                                    OUTPUT_DATAFILE=output_data_file,
                                    FIXES=fixes,
                                    NUMBER_STEPS=number_steps,
                                    TIME_STEP=time_step,
                                    PAIR_STYLE=pair_style_input,
                                    PAIR_COEFF=pair_coeff_input)


def _check_configuration(CM):
    """ Check if everything is configured correctly

    Raises
    ------
    ConfigurationError
        if anything is wrong with the configuration
    """
    cm_requirements = [CUBA.NUMBER_OF_TIME_STEPS,
                       CUBA.TIME_STEP,
                       CUBA.THERMODYNAMIC_ENSEMBLE]

    missing = [str(req) for req in cm_requirements
               if req not in CM.keys()]

    msg = ""
    if missing:
        msg = "Problem with CM component. "
        msg += "Missing: " + ', '.join(missing)

    # TODO check SP, BC

    if msg:
        # TODO throw unique exception that
        # users can catch and then try to fix
        # their configuration
        raise ConfigurationError(msg)

CONFIGURATION = """
# Control file generated by SimPhoNy

dimension 3
{BOUNDARY}

atom_style  atomic
neighbor    0.3 bin
neigh_modify    delay 5

{PAIR_STYLE}

# read from SimPhoNy-generated file
read_data {INPUT_DATAFILE}

{PAIR_COEFF}

{FIXES}

# Run

timestep {TIME_STEP}

run {NUMBER_STEPS}

# write reults to simphony-generated file
write_data {OUTPUT_DATAFILE}
"""


def _get_thermodynamic_ensemble(CM):
    esemble = CM[CUBA.THERMODYNAMIC_ENSEMBLE]
    if esemble == "NVE":
        return "fix 1 all nve"
    else:
        message = ("Unsupported ensemble was provided "
                   "CM[CUBA.THERMODYNAMIC_ENSEMBLE] = {}")
        ConfigurationError(message.format(esemble))


def _get_boundary(BC):
    """ get lammps boundary command from BC

    The boundary command can be either fixed or periodic.

    >> BC[CUBA.BOX_FACES] = ("periodic", "fixed", "periodic"]

    """

    errorMessage = ""
    boundaryCommand = "boundary"

    # mapping of cuds-value to lammps string
    mappings = {'periodic': 'p', 'fixed': 'f'}

    if len(BC[CUBA.BOX_FACES]) != 3:
        errorMessage += "3 dimensions need to be given.\n"
    for b in BC[CUBA.BOX_FACES]:
        if b in mappings:
            boundaryCommand += " {}".format(mappings[b])
        else:
            errorMessage += "'{}' is not supported\n"
    if errorMessage:
        message = ("Unsupported boundary was provided "
                   "BC[CUBA.CUBA.BOX_FACES] = {}\n"
                   "{}")
        ConfigurationError(message.format(
            BC[CUBA.CUBA.BOX_FACES], errorMessage))
    return boundaryCommand
