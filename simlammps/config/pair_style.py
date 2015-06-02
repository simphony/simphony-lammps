import yaml

from simlammps.cuba_extension import CUBAExtension


# here is the info to create the different pair info handlers
# TODO add more pair styles for the different types
# TODO add optional pair params
_supported_pair_styles = {"lj": {"pair_style": "lj/cut",
                                 "required_global_params": ["global_cutoff"],
                                 "required_pair_params":
                                 ["epsilon", "sigma", "cutoff"]},
                          "coul": {"pair_style": "coul/cut",
                                   "required_global_params": ["global_cutoff"],
                                   "required_pair_params":
                                   ["cutoff"]},
                          }


class PairStyle(object):
    """ A PairStyle instance

    The PairStyle object interprets the configuration of the SP
    to determine the pairwise interaction of atoms in LAMMPS


    """

    def __init__(self, SP):
        """ Constructor.

         Parses the pair style information in the SP

        """
        self._global = ""
        self._pair_coefs = ""
        self._pair_infos = self._create_pair_infos(SP)

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
                return "pair_style {} {}\n".format(
                    pair_info.pair_style,
                    " ".join(map(str, pair_info.global_params)))
            else:
                # hybrid/overlay style
                result = "pair_style hybrid/overlay"
                for pair_info in self._pair_infos:
                    result += " {} {}".format(
                        pair_info.pair_style,
                        " ".join(map(str, pair_info.global_params)))
                result += "\n"
                return result
        else:
            return ""

    def get_pair_coeffs(self):
        """ Returns global configuration text

        """
        if self._pair_infos:
            coeffs = ""
            isOverlay = len(self._pair_infos) > 1
            for pair_info in self._pair_infos:
                for pair, params in pair_info.pair_params.iteritems():
                    coeffs += "pair_coeff "

                    # first add list pair info
                    coeffs += " ".join(map(str, pair)) + " "

                    if isOverlay:
                        # add additional info for overlay
                        coeffs += pair_info.pair_style + " "

                    # then add all params
                    coeffs += " ".join(map(str, params)) + "\n"
            coeffs += "\n"

            # work-around for not being able to change the number of types
            # (see issue #66), we set up a general wildcard pair coeffiencents
            # so that every type is covered (i.e. pair_coeff * * XXX XXX XXX)
            # and then what the user specifically sets overrides it for the
            # actual types that are in use.
            coeffs = self._extract_wildcard_coeffs() + coeffs
            return coeffs
        else:
            return ""

    # Private methods #######################################################

    def _extract_wildcard_coeffs(self):
        """ Get wildcard coefficients

            Get wildcard pair coefficients.  This is used due to issue #66.
            See comment in get_pair_coeffs method.
        """
        coeffs = ""
        isOverlay = len(self._pair_infos) > 1
        for pair_info in self._pair_infos:
            for pair, params in pair_info.pair_params.iteritems():
                # first add list pair info
                # pair_coeff * * x.xx x.xx x.xx
                coeffs += "pair_coeff * * "

                if isOverlay:
                    # add additional info for overlay
                    coeffs += pair_info.pair_style + " "

                # then add params all params
                coeffs += " ".join(map(str, params)) + "\n"

                # now we stop as we need only one wild card for each type
                break
        coeffs += "\n"

        return coeffs

    @staticmethod
    def _create_pair_infos(SP):
        """ Creates appropriate pair info handler(s) from information
            stored in the SP.

        """
        styles = []
        if (CUBAExtension.PAIR_POTENTIALS in SP and
                SP[CUBAExtension.PAIR_POTENTIALS]):
            keywords = yaml.safe_load(SP[CUBAExtension.PAIR_POTENTIALS])
            my_pair_style = SP[CUBAExtension.PAIR_POTENTIALS]

            for key in keywords:
                my_pair_style = key
                parameters = keywords[key]
                if parameters and my_pair_style in _supported_pair_styles:
                    handler_info = _supported_pair_styles[my_pair_style]
                    req_global = handler_info["required_global_params"]
                    req_params = handler_info["required_pair_params"]
                    global_params = PairStyle._get_global_params(
                        parameters, req_global)
                    pair_params = PairStyle._get_pair_params(parameters,
                                                             req_params)
                    styles.append(
                        PairStyleInfo(pair_style=handler_info["pair_style"],
                                      global_params=global_params,
                                      pair_params=pair_params))
                else:
                    raise RuntimeError(
                        "Unsupported pair style: {}".format(my_pair_style))
        return styles

    @staticmethod
    def _get_global_params(keywords, required_global_params):
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
            raise RuntimeError(msg)

        return global_params

    @staticmethod
    def _get_pair_params(keywords, required_pair_params):
        pair_params = {}

        parameter_keywords = keywords["parameters"]
        for params in parameter_keywords:
            pair = None
            if "pair" in params:
                pair = tuple((params["pair"]))
            else:
                raise RuntimeError("Pair information is missing")

            pair_dict = []
            missing_params = []
            for req in required_pair_params:
                if req in params:
                    pair_dict.append(params[req])
                else:
                    missing_params.append(req)

            if missing_params:
                msg = "The pair ({}) is missing the " \
                      + " following parameters: ".format(pair)
                msg += ', '.join(missing_params)
                raise RuntimeError(msg)

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
