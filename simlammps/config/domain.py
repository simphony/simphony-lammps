from simphony.core.cuba import CUBA


def get_box(particle_containers):
    """ Get simulation box commands

    Using CUBA.BOX_VECTORS and CUBA.BOX_ORIGIN, return the
    string used by LAMMPS to define the simulation box in
    the LAMMPS data file

    Parameters:
    -----------
    particle_containers: list of particle containers
    """
    origin = None
    vectors = None

    for pc in particle_containers:
        # find box vectors (and origin) and ensure
        # that they are the same for each particle container
        if CUBA.BOX_VECTORS in pc.data:
            if vectors and vectors != pc.data[CUBA.BOX_VECTORS]:
                # TODO provide more info in exception message
                raise RuntimeError("Box vectors need to match")
            vectors = pc.data[CUBA.BOX_VECTORS]
        if CUBA.BOX_ORIGIN in pc.data:
            if origin and origin != pc.data[CUBA.BOX_ORIGIN]:
                # TODO provide more info in exception message
                raise RuntimeError("Box origin need to match")
            origin = pc.data[CUBA.BOX_ORIGIN]

    # origin is optional
    if not origin:
        origin = (0.0, 0.0, 0.0)

    # Note: For LAMMPS we can define a orthogonal simulation
    # or non-orthogonal simulation box. For the non-orthogonal
    # simulation box, the lammps doc states the following:
    # "a must lie on the positive x axis. b must lie in
    # the xy plane, with strictly positive y component. c may
    # have any orientation with strictly positive z component.
    # The requirement that a, b, and c have strictly positive
    # x, y, and z components, respectively, ensures that a, b,
    # and c form a complete right-handed basis."

    if not vectors:
        raise RuntimeError("CUBA.BOX_VECTORS was not set")
    else:
        _check_vectors(vectors)

    return _get_box_string(vectors, origin)


def _check_vectors(vectors):
    # TODO: currently only handling orthogonal simulation box
    # (where a must lie on positive x axis..) so only something
    # like the following is allowed: (x, 0, 0), (0, y, 0)
    # and (0, 0, z).
    for i, v in enumerate(vectors):
        for j, x in enumerate(v):
            if i != j and float(x) != 0.0:
                msg = ("Box vectors must have the form "
                       "(x, 0, 0), (0, y, 0) and (0, 0, z)")
                raise RuntimeError(msg)


def _get_box_string(vectors, origin):
    # TODO: see previous TODO
    x = vectors[0][0]
    y = vectors[1][1]
    z = vectors[2][2]
    box = "{:.16e} {:.16e} xlo xhi\n".format(
        origin[0], x-origin[0])
    box += "{0:.16e} {1:.16e} ylo yhi\n".format(
        origin[1], y-origin[1])
    box += "{0:.16e} {1:.16e} zlo zhi\n".format(
        origin[2], z-origin[2])
    return box
