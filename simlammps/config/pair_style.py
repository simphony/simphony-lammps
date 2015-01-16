import yaml

from simphony.core.cuba import CUBA

# here is the info to create the different handlers
# TODO add more handlers for the different types
_pair_style_handlers = {"lj": {"pair_style": "lj/cut",
                               "required_global_params": ["global_cutoff"],
                               "required_pair_params":
                               ["epsilon", "sigma", "cutoff"]}}


class PairStyle(object):
    """ A PairStyle instance

    The PairStyle object interprets the configuration of the CM
    to determine the pairwise interaction of atoms in LAMMPS


    """

    def __init__(self, CM):
        """ Constructor.

         Parses the pair style information in the CM

        """
        self._global = ""
        self._pair_coefs = ""
        self._handler = self._create_handler(CM)

    def get_global_config(self):
        """ Returns global configuration text

        For example, for lj-cut, it returns:

        "pair_style lj/cut 1.2334"

        An empty string is returned if there is no pair style
        information
        """
        if self._handler:
            return "pair_style {} {}".format(
                self._handler.pair_style,
                " ".join(map(str, self._handler.get_global_parameters())))
        else:
            return ""

    def get_pair_coeffs(self):
        """ Returns global configuration text

        """
        if self._handler:
            coeffs = ""
            for pair_params in self._handler.iter_pair_params():
                coeffs = coeffs + "pair_coeff " + \
                    " ".join(map(str, pair_params)) + "\n"
            coeffs = coeffs + "\n"
            return coeffs
        else:
            return ""

    # Private methods #######################################################

    def _create_handler(self, CM):
        """ Creates appropriate handler(s) from information stored in the
            CM.

        """
        if CUBA.PAIR_STYLE in CM and CM[CUBA.PAIR_STYLE]:
            my_pair_style = CM[CUBA.PAIR_STYLE]
            if my_pair_style in _pair_style_handlers:
                handler_info = _pair_style_handlers[my_pair_style]
                req_global = handler_info["required_global_params"]
                req_params = handler_info["required_pair_params"]
                return PairStyleHandler(CM,
                                        pair_style=handler_info["pair_style"],
                                        required_global_params=req_global,
                                        required_pair_params=req_params)
            else:
                raise Exception(
                    "Unsupported pair style: {}".format(my_pair_style))
        return None


class PairStyleHandler(object):
    """ A pair style handler which knows its required global and pair-specific
    parameters

    """

    def __init__(self,
                 CM, pair_style,
                 required_global_params, required_pair_params):
        self._required_global_params = required_global_params
        self._required_pair_params = required_pair_params
        self.pair_style = pair_style
        self._global_params = None
        self._pair_params = None
        if CUBA.PAIR_STYLE in CM:
            if CUBA.PAIR_STYLE_PARAMETERS in CM:
                keywords = yaml.safe_load(CM[CUBA.PAIR_STYLE_PARAMETERS])
                self._global_params = self._get_global_params(keywords)
                self._pair_params = self._get_pair_params(keywords)
            else:
                raise Exception(
                    "CUBA.PAIR_STYLE_PARAMETERS was not set in the CM")

    def _get_global_params(self, keywords):
        global_params = {}
        for params in keywords:
            for req in self._required_global_params:
                if req in params:
                    global_params[req] = params[req]

        missing_reqs = list(self._required_global_params)
        for key in global_params:
            while key in missing_reqs:
                missing_reqs.remove(key)
        if missing_reqs:
            msg = ("Missing the following required "
                   "pair style parameters: {}").format(missing_reqs)
            raise Exception(msg)
        return global_params

    def _get_pair_params(self, keywords):
        pair_params = {}
        for params in keywords:
            if "pair" in params:
                pair = tuple((params["pair"]))
                pair_dict = {}
                for req in self._required_pair_params:
                    if req in params:
                        pair_dict[req] = params[req]
                    else:
                        msg = "The pair ({}) is missing {}".format(pair, req)
                        raise Exception(msg)
                pair_params[pair] = pair_dict
        return pair_params

    def get_global_parameters(self):
        """Returns list of values of all the required global parameters

        """

        params = []
        for req in self._required_global_params:
            params.append(self._global_params[req])
        return params

    def iter_pair_params(self):
        """Returns list of global parameters

        """
        for pair in self._pair_params:
            result = list(map(int, pair))
            for req in self._required_pair_params:
                result.append(self._pair_params[pair][req])
            yield result
