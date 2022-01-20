from ast import arg
from curses.ascii import isdigit
from fileinput import filename
from lark import tree
from typing import Set

from output_sarif import *
from rules.AllFunctionCallsGatherer import AllFunctionCallsGatherer
import re

UPPER_CASE_PATTERN = re.compile("^[A-Z_]{2,}$")


def is_constant_case(s):
    return bool(UPPER_CASE_PATTERN.match(s))


class UniformAssertsConstants:
    """
    Look for different asserts where the same constant is used differently.
    assert_.*[A-Z_0-9]{6,}.*\)
    """

    RULE_TEXT = "This assertion uses the same constant differently [here](0) and [here](1)."
    RULE_NAME = "inconsistent-assert-constant"

    def run_rule(self, gathered_data):
        function_calls = gathered_data[AllFunctionCallsGatherer.GATHERER_NAME]

        results = []
        constant_uses = {}

        for call in function_calls:
            file_name, function_name, arguments = call

            if "assert" in function_name:

                for arg_tree in arguments.children:
                    # get all tokens in the argument that are a constant
                    argument_tokens = sorted(
                        list(
                            arg_tree.scan_values(
                                lambda v: isinstance(v, Token)
                                and is_constant_case(v.value)
                            )
                        )
                    )

                    if not argument_tokens:
                        continue

                    # create a dictionary key with the used constants
                    constants_key = "$".join(argument_tokens)

                    if constants_key not in constant_uses:
                        # when we haven't seen these constants being used,
                        # add their argument tree and the current filename to the dictionary
                        constant_uses[constants_key] = (arg_tree, arguments, file_name)

                    else:
                        old_tree, old_args, old_filename = constant_uses[constants_key]
                        # otherwise, when the trees differ it means that they are being used differently
                        if old_tree != arg_tree:

                            sarif = generic_sarif_two_positions(
                                file_name,
                                old_filename,
                                self.RULE_NAME,
                                self.RULE_TEXT,
                                [getPosition(arguments), getPosition(old_args)],
                            )
                            results.append(sarif)

        return results