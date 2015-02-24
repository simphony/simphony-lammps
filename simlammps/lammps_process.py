""" LAMMPS Process

This module provides a way to run the lammps process
"""

import subprocess


class LammpsProcess(object):
    """ Class runs the lammps programm

    Parameters
    ----------
    lammps_name :
        name of lammps executable

    Raises
    ------
    RuntimeError
        if Lammps did not run correctly
    """
    def __init__(self, lammps_name="lammps"):
        self._lammps_name = lammps_name
        self._returncode = 0
        self._stderr = ""
        self._stdout = ""

        # see if lammps can be started
        try:
            self.run(" ")
        except Exception:
            msg = "Lammps could not be started."
            if self._returncode == 127:
                msg += " Lammps executable was not found."
            else:
                msg += " stdout/err: " + self._stdout + " " + self._stderr
            raise RuntimeError(msg)

    def run(self, commands):
        """Run lammps with a set of commands

        Parameters
        ----------
        commands : str
            set of commands to run

        Raises
        ------
        RuntimeError
            if Lammps did not run correctly
        """

        proc = subprocess.Popen(
            self._lammps_name, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self._stdout, self._stderr = proc.communicate(commands)
        self._returncode = proc.returncode

        if self._returncode != 0 or self._stderr:
            msg = "Lammps did not run correctly. "
            msg += "Error code: {} ".format(proc.returncode)
            if self._stderr:
                msg += "stderr: \'{}\n\' ".format(self._stderr)
            if self._stdout:
                msg += "stdout: \'{}\n\'".format(self._stdout)
            raise RuntimeError(msg)
