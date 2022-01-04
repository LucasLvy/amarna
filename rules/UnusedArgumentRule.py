from lark import tree, Token
from typing import Set

from output_sarif import *
from rules.GenericRule import GenericRule


class UnusedArgumentRule(GenericRule):
    """
    Check for unused arguments inside a function
    """

    RULE_TEXT = "Unused arguments might indicate a misspelled variable use or unnecessary argument."
    RULE_NAME = "unused-arguments"

    # visit the code_element_function node of the AST
    def code_element_function(self, tree: tree.Tree):
        arguments = set()
        for child in tree.children:
            # get the function name
            if child.data == "identifier_def":
                function_name = child.children[0]

            # get the arguments names
            elif child.data == "arguments":
                for args in child.find_data("identifier_def"):
                    arguments.add(args.children[0])

            # get the function code ASTree
            elif child.data == "code_block":
                code_block = child

            # ignore if the function is a @storage_var
            elif child.data == "decorator_list":
                for decorator in child.find_data("identifier_def"):
                    # since this is a class attribute, there is no need to check argument usage because there is no code.
                    if decorator.children[0] == "storage_var":
                        return

        used_ids: Set[Token] = set()
        for code_child in code_block.find_data("identifier"):
            used_ids.add(code_child.children[0])

        unused_arguments = arguments - used_ids

        # find if this is part of a @contract_interface
        for struct in self.original_tree.find_data("code_element_struct"):
            for child in struct.find_data("decorator_list"):
                for decorator in child.find_data("identifier_def"):
                    if decorator.children[0] == "contract_interface":
                        if tree in struct.iter_subtrees():
                            return

        for arg in unused_arguments:
            positions = (arg.line, arg.column, arg.end_line, arg.end_column)
            sarif = generic_sarif(
                self.fname,
                self.RULE_NAME,
                self.RULE_TEXT,
                positions,
            )
            self.results.append(sarif)
