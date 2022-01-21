from amarna.output_sarif import *
from amarna.rules.gatherer_rules.FunctionsReturningErrorsGatherer import (
    FunctionsReturningErrorsGatherer,
)
from amarna.rules.gatherer_rules.RValueFunctionCallsGatherer import (
    RValueFunctionCallsGatherer,
)


class MustCheckOverflow:
    """
    Gather function calls and their return values.
    """

    RULE_TEXT = "This function returns a variable that indicates if an overflow occurred and must be properly checked."
    IGNORED_RULE_TEXT = "This function ignores the overflow indicator variable."

    RULE_NAME = "must-check-overflow"

    # dictionary with function_name : index of the returned overflow variable
    OVERFLOW_FUNCTIONS = {"uint256_add": 1}

    def run_rule(self, gathered_data):

        function_calls = gathered_data[RValueFunctionCallsGatherer.GATHERER_NAME]

        results = []
        for call in function_calls:
            file_name, function_name, returned_list = call

            # when the function is one of those returning errors
            if function_name in self.OVERFLOW_FUNCTIONS:
                overflow_idx = self.OVERFLOW_FUNCTIONS[function_name]

                must_check = returned_list[overflow_idx].children[0]

                if must_check == "_":
                    # the overflow return value is being ignored
                    rule = self.IGNORED_RULE_TEXT
                else:
                    # here we say that it must be checked
                    rule = self.RULE_TEXT

                sarif = generic_sarif_token(
                    file_name,
                    self.RULE_NAME,
                    rule,
                    must_check,
                )
                results.append(sarif)

        return results