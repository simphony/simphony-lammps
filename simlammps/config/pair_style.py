import yaml

from simphony.core.cuba import CUBA

# here is the info to create the different pair info handlers
# TODO add more pair styles for the different types
_supported_pair_styles = {"lj": {"pair_style": "lj/cut",
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
        self._pair_infos = self._create_pair_infos(CM)

    def get_global_config(self):
        """ Returns global configuration text

        For example, for lj-cut, it returns:

        "pair_style lj/cut 1.2334"

        An empty string is returned if there is no pair style
        information
        """
        if self._pair_infos:
            if len(self._pair_infos) == 1:
                pair_info = self._pair_infos[0]
                return "pair_style {} {}".format(
                    pair_info.pair_style,
                    " ".join(map(str, pair_info.global_params)))
            else:
                # TODO do hybrid/overlay style
                raise NotImplementedError
        else:
            return ""

    def get_pair_coeffs(self):
        """ Returns global configuration text

        """
        if self._pair_infos:
            coeffs = ""
            for pair_info in self._pair_infos:
                for pair, params in pair_info.pair_params.iteritems():
                    # first list pair info
                    result = list(map(int, pair))
                    # then all params
                    result += params
                    coeffs = coeffs + "pair_coeff " + \
                        " ".join(map(str, result)) + "\n"
            coeffs = coeffs + "\n"
            return coeffs
        else:
            return ""

    # Private methods #######################################################

    def _create_pair_infos(self, CM):
        """ Creates appropriate pair info handler(s) from information
            stored in the CM.

        """
        styles = []
        if CUBA.PAIR_STYLE in CM and CM[CUBA.PAIR_STYLE]:
            keywords = yaml.safe_load(CM[CUBA.PAIR_STYLE])
            my_pair_style = CM[CUBA.PAIR_STYLE]

            for key in keywords:
                my_pair_style = key
                parameters = keywords[key]
                if my_pair_style in _supported_pair_styles:
                    handler_info = _supported_pair_styles[my_pair_style]
                    req_global = handler_info["required_global_params"]
                    req_params = handler_info["required_pair_params"]
                    global_params = self._get_global_params(
                        parameters, req_global)
                    pair_params = self._get_pair_params(parameters, req_params)
                    styles.append(
                        PairStyleInfo(pair_style=handler_info["pair_style"],
                                      global_params=global_params,
                                      pair_params=pair_params))
                else:
                    raise Exception(
                        "Unsupported pair style: {}".format(my_pair_style))
        return styles

    def _get_global_params(self, keywords, required_global_params):
        global_params = []
        missing_params = []
        for req in required_global_params:
            if req in keywords:
                global_params.append(keywords[req])
            else:
                missing_params.append(req)

        if missing_params:
            msg = "The following global parameters are missing: "
            msg += ', '.join(missing_params)
            raise Exception(msg)

        return global_params

    def _get_pair_params(self, keywords, required_pair_params):
        pair_params = {}

        parameter_keywords = keywords["parameters"]
        for params in parameter_keywords:
            pair = None
            if "pair" in params:
                pair = tuple((params["pair"]))
            else:
                raise Exception("Pair information is missing")

            pair_dict = []
            missing_params = []
            for req in required_pair_params:
                if req in params:
                    pair_dict.append(params[req])
                else:
                    missing_params.append(req)
                    msg = "The pair ({}) is missing {}".format(pair, req)
                    raise Exception(msg)

            if missing_params:
                msg = "The pair ({}) is missing the following {}".format(
                    pair, req)
                msg += ', '.join(missing_params)
                raise Exception(msg)

            pair_params[pair] = pair_dict
        return pair_params


class PairStyleInfo(object):
    """ A pair style info which knows its all required global and pair-specific
    parameters

    """

    def __init__(self,
                 pair_style,
                 global_params,
                 pair_params):
        self.pair_style = pair_style
        self.global_params = global_params
        self.pair_params = pair_params
