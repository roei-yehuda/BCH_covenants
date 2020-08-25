# todo - check for any "???" left...

"""
This file is part of the ??? project which can be found at ???github...???
This project was a created for a university course, and then made publicly available.
Introduction to Cryptocurrencies, course #67513, Hebrew University Jerusalem Israel, Aug 2020.
Avigail Suna; email ???
Roei Yehuda; email ???

The purpose of the code here is to implement a cashScript (https://cashscript.org/) covenants generator for BCH smart contracts.
The class cashScript_cov_gen outputs a .cash file with the generated covenant smart contract.
"""

import os
# import os.path
# import os.system
# import glob
# import datetime
# import sys
# from datetime import datetime
# import re
# import numpy as np
# import pandas as pd
# import subprocess



class utils():

    def __init__(self):
        pass

    def indent(self, s, tab='\t', indices=None):
        """
        This method adds a tab in the beginning of every line.
        if indices is not None, tabs will only be added to lines with relevant indices
        :param s: string
        :param tab: string
        :param indices: list of integers, or range
        :return: string
        """
        lines_to_indent = list(range(s.count('\n') + 1)) if indices is None else list(indices)
        lines = s.split('\n')
        for i in lines_to_indent:
            lines[i] = tab + lines[i]
        return '\n'.join(lines)

    def indent_inside(self, s, tab='\t'):
        """
        indent all lines except the first and last lines
        """
        return self.indent(s, tab, indices=list(range(s.count('\n') + 1))[1:-1])

    def get_byte_code_from_artifact(self, json_path):
        """
        read an artifact json file, an output of cashc compilation, and return the bytecode
        :param json_path: string
        :return: string - if no bytecode is found, this methods returns an empty string
        """
        with open(json_path, "r") as f:
            for line in f:
                if line.split(':')[0].strip(' \t\",') == 'bytecode':
                    return line.split(':')[1].strip(' \t\",\n')
        return ''


class cov_gen():

    def __init__(self, contract_name='cov', cashScript_pragma='0.4.0', intro_comment=''):
        # todo doc

        self.contract_name = contract_name
        self.pragma = cashScript_pragma
        self.intro_comment = intro_comment

        # self.constructor_args is a dictionary with arguments names as keys and tuples like
        # (type, name, index, description) as values. Saved in a dictionary in order to avoid having two arguments with
        # the same name, while keeping track of order of arrival (index in constructor)
        self.constructor_args = {}

        # self.functions is a dictionary with function names as keys and tuples like (fn_text, fn_description) as values
        # saved in a dictionary in order to avoid having two functions with the same name
        self.functions = {}

    def _add_to_constructor(self, type, name, description=''):
        """
        Adding a single argument to the contract's constructor.
        :param type: string
        :param name: string
        :param description: (optional) string - this is used for inner purposes, and will not be written to the output contract
        """
        # we record the order of arrival simply with len(self.constructor_args.keys())
        self.constructor_args[name] = (type, name, len(self.constructor_args.keys()), description)

    def _get_constructor_text(self):
        """
        calculate the final string for the constructor
        :return: string
        """

        sorted_args_tuples = list(self.constructor_args.values())
        sorted_args_tuples.sort(key=lambda t: t[2])     # '2' since the index of the constructor_arg is the third argument in each tuple

        text = ''
        for arg_tup in sorted_args_tuples:
            text += arg_tup[0] + ' ' + arg_tup[1] + ', '
        return text[:-2]

    def _add_to_functions(self, fn_name, fn_text, description=''):
        """
        Adding a single function to the contract's body.
        :param fn_name: string
        :param fn_text: string
        :param description: (optional) string - this is used for inner purposes, and will not be written to the output contract
        """
        self.functions[fn_name] = (fn_text, description)

    def _get_functions_text(self):
        """
        calculate the final string for the contract body
        :return: string
        """
        text = ''
        for fn_tup in self.functions.values():
            # we strip the input fn_text, then add one indentation ('\t') to its entirety and then another indentation
            # to its inner scope
            text += utils().indent(utils().indent_inside(fn_tup[0].strip())) + '\n'
        return text

    def get_script(self):
        """
        Calculate the (current) final script
        :return: string
        """
        full_script = \
            self.intro_comment + "\n\n" \
            "pragma cashscript ^" + self.pragma + ";\n\n" \
            "contract " + self.contract_name + "(" + self._get_constructor_text() + "){\n" \
            "\n" + \
            self._get_functions_text() + \
            "\n" \
            "}"
        return full_script

    def save_script(self, cash_file_path='covenant.cash'):
        """
        Save to file the (current) final script
        :param cash_file_path: string
        """
        with open(cash_file_path, "w") as f:
                print(self.get_script(), file=f)

    def compile_script(self, cash_file_path=None, json_file_path=None):
        """
        Use cashScript compiler, cashc, to compile the (current) final script, and return the byte_code.
        :param cash_file_path: (optional) string. if None, no compiled artifact is saved to file.
        :return: string
        """

        delete_cash_file_later = cash_file_path is None
        delete_json_file_later = json_file_path is None
        cash_file_path = cash_file_path if cash_file_path is not None else 'to_be_deleted.cash'
        json_file_path = json_file_path if json_file_path is not None else 'to_be_deleted.json'

        self.save_script(cash_file_path)
        os.system("cashc " + cash_file_path + " -o " + json_file_path)
        # subprocess.run(["cashc ", cash_file_path, " -o ", json_file_path])

        byte_code = utils().get_byte_code_from_artifact(json_file_path)

        if delete_cash_file_later and os.path.exists(cash_file_path):
            os.remove(cash_file_path)

        if delete_json_file_later and os.path.exists(json_file_path):
            os.remove(json_file_path)

        return byte_code

    def basic_covenant(self,
                       number_of_receipients=1):
                       #
                       # allowed_output_pkh=[], use_all_pkh=False,
                       # allowed_output_sh=[], use_all_sh=False):

        # todo - maybe we need to check input is valid

        for i in range(number_of_receipients):
            self._add_to_constructor(type="bytes20",
                                     name="recepient_{}".format(i),
                                     description="allowed_recepient")

        fn_name = 'spend'

        fn_text =   "function " + fn_name + "(pubkey pk, sig s) {\n" \
                    "require(checkSig(s, pk));\n" \
                    "// Create and enforce outputs\n" \
                    "int minerFee = 1000; // hardcoded fee\n" \
                    "bytes8 amount = bytes8(int(bytes(tx.value)) - minerFee);\n" \
                    ""

        for i in range(number_of_receipients):
            fn_text += "bytes34 out_{} = new OutputP2PKH(amount, recepient_{});\n".format(i,i)


        fn_text += "require("
        for i in range(number_of_receipients):
            fn_text += "tx.hashOutputs == hash256(out_{}) || ".format(i)
        fn_text = fn_text[:-4] + ");\n"

        fn_text += "}"

        self._add_to_functions(fn_name, fn_text, description='basic_covenant')


# if __name__ == 'main':

cg = cov_gen()
cg.basic_covenant(number_of_receipients=2)
print(cg.get_script())
print()
print(cg.compile_script())




"""

Output instantiation - enforcing transaction outputs 

    bytes34 out1 = new OutputP2PKH(bytes8(10000), pkh);
    bytes32 out2 = new OutputP2SH(bytes8(10000), hash160(tx.bytecode));
    require(hash256(out1 + out2) == tx.hashOutputs);



covenants - Restricting P2PKH recipients

contract Escrow(bytes20 arbiter, bytes20 buyer, bytes20 seller) {
    function spend(pubkey pk, sig s) {
        require(hash160(pk) == arbiter);
        require(checkSig(s, pk));

        // Create and enforce outputs
        int minerFee = 1000; // hardcoded fee
        bytes8 amount = bytes8(int(bytes(tx.value)) - minerFee);
        bytes34 buyerOutput = new OutputP2PKH(amount, buyer);
        bytes34 sellerOutput = new OutputP2PKH(amount, seller);
        require(tx.hashOutputs == hash256(buyerOutput) || tx.hashOutputs == hash256(sellerOutput);
    }
}


contract Basic('for i in aaa print bytes20 i, ') {
    
    function spend(pubkey pk, sig s) {
        require(hash160(pk) == arbiter);
        require(checkSig(s, pk));

        // Create and enforce outputs
        int minerFee = 1000; // hardcoded fee
        bytes8 amount = bytes8(int(bytes(tx.value)) - minerFee);
        bytes34 buyerOutput = new OutputP2PKH(amount, buyer);
        bytes34 sellerOutput = new OutputP2PKH(amount, seller);
        require(tx.hashOutputs == hash256(buyerOutput) || tx.hashOutputs == hash256(sellerOutput);
    }
}




"""
