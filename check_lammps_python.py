import lammps
l = lammps.lammps(cmdargs=["-log", "none"])
l.command("print \"Python-LAMMPS interface is working\"")
