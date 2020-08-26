# todo - check for any "???" left...
# todo - add a clear desclaimer that this is a 'school' project.. no taking responsibility here :)

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
        if indices is not None, tabs will only be added to lines with the relevant indices
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

    def __init__(self, contract_name='cov', cashScript_pragma='0.4.0', miner_fee=1000, intro_comment=''):
        """
        Initializing a cov_gen.
        :param contract_name: string
        :param cashScript_pragma: string - cashScript version
        :param miner_fee: int - an estimation of a reasonable miner_fee, according to the contract's size.
        :param intro_comment: string - the user might want to add a free comment. It is unlimited in size (as it
                appears only in the cash file, not in the bytecode) and appears at the very beginning of the file.
        """

        self.contract_name = contract_name
        self.pragma = cashScript_pragma
        self.miner_fee = miner_fee
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
        # we record the order of arrival with len(self.constructor_args.keys())
        self.constructor_args[name] = (type, name, len(self.constructor_args.keys()), description)

    def _get_constructor_text(self):
        """
        calculate the final string for the constructor
        :return: string
        """
        sorted_args_tuples = list(self.constructor_args.values())
        sorted_args_tuples.sort(key=lambda t: t[2])     # '2' since the index of the constructor_arg is the third argument in each tuple
        return ', '.join([sorted_args_tuples[i][0] + ' ' + sorted_args_tuples[i][1] for i in range(len(sorted_args_tuples))])

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
        # we strip the input fn_text, then add one indentation ('\t') to its entirety and then another indentation
        # to its inner scope
        return '\n\n'.join([utils().indent(utils().indent_inside(fn_tup[0].strip())) for fn_tup in self.functions.values()])

    def _get_intro_comment_text(self):
        """
        calculate the final string for the intro comment
        """
        if self.intro_comment == '':
            return ''
        return '/*\n' + self.intro_comment + '\n*/\n\n'

    def get_script(self):
        """
        Calculate the (current) final script
        :return: string
        """
        full_script = \
            self._get_intro_comment_text() + \
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
        :param cash_file_path: (optional) string. if None, no cashScript file (.cash) is saved to file.
        :param json_file_path: (optional) string. if None, no compiled artifact (.json) is saved to file.
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
                       n_recipients=1,
                       p2sh_recipients_indices=[],
                       include_any=True):

        # todo - maybe we need to check that the input is valid

        fn_name = 'spend'

        p2pkh_recipients_indices = [i for i in list(range(n_recipients)) if i not in p2sh_recipients_indices]

        # todo - note that if this function has been called once, then we need to change the format of its constructor args: otherwise it'll just use ""recepient_{}_pkh"" again and it'll collide with the args created on the first run... they have to have a new unique name!
        #

        for i in p2pkh_recipients_indices:
            self._add_to_constructor(type="bytes20",
                                     name="recepient_{}_pkh".format(i),
                                     description="allowed_recepient")

        """ OLDER VERSION (before transitioning to fn_lines we used a more explicit fn_text)

        fn_text =   "function " + fn_name + "(pubkey pk, sig s) {\n" \
                    "require(hash160(pk) == pkh);\n" \  # todo
                    "require(checkSig(s, pk));\n" \
                    "// Create and enforce outputs\n" \
                    "int minerFee = " + str(self.miner_fee) + "; // hardcoded fee\n" \
                    "bytes8 amount = bytes8(int(bytes(tx.value)) - minerFee);\n" \
                    ""

        for i in range(n_recipients):
            fn_text += "bytes34 out_{} = new OutputP2PKH(amount, recepient_{}_pkh);\n".format(i,i)


        fn_text += "require("
        for i in range(n_recipients):
            fn_text += "tx.hashOutputs == hash256(out_{}) || ".format(i)
        fn_text = fn_text[:-4] + ");\n"

        fn_text += "}"

        self._add_to_functions(fn_name, fn_text, description='basic_covenant')
        
        """

        fn_lines = []
        fn_lines.append("function " + fn_name + "(pubkey pk, sig s) {")

        # # this is commented out because it is not necessary to check *who* the signer is. But useful so don't delete yet :)
        # req_pkh_cond = ' || '.join(["hash160(pk) == recepient_{}_pkh".format(i) for i in p2pkh_recipients_indices])
        # fn_lines.append("require(" + req_pkh_cond + ");")

        fn_lines.append("require(checkSig(s, pk));")
        fn_lines.append("// Create and enforce outputs")
        fn_lines.append("int minerFee = " + str(self.miner_fee) + "; // hardcoded fee")
        amount = "int(bytes(tx.value)) - minerFee" if include_any else "int((int(bytes(tx.value)) - minerFee) / {})".format(n_recipients)
        fn_lines.append("bytes8 amount = bytes8(" + amount + ");")

        for i in range(n_recipients):
            if i in p2pkh_recipients_indices:
                fn_lines.append("bytes34 out_{} = new OutputP2PKH(amount, recepient_{}_pkh);".format(i,i))
            else:   # this means i is in p2sh_recipients_indices
                fn_lines.append("bytes32 out_{} = new OutputP2SH(amount, recepient_{}_pkh);".format(i,i))   # todo

        if include_any:
            hashOutputs_cond = ' || '.join(["tx.hashOutputs == hash256(out_{})".format(i) for i in range(n_recipients)])
        else:
            hashOutputs_cond = 'tx.hashOutputs == hash256(' + ' + '.join(['out_{}'.format(i) for i in range(n_recipients)]) + ')'
        fn_lines.append("require(" + hashOutputs_cond + ");")

        fn_lines.append('}')

        fn_text = '\n'.join(fn_lines)
        self._add_to_functions(fn_name, fn_text, description='basic_covenant')


    def allow_cold(self, n=1):
        """
        This method basically allows easy and unlimited access to the funds in the contract for n people defined
        in the constructor.
        :param n: int
        """

        fn_name = 'cold'

        for i in range(n):
            self._add_to_constructor(type="bytes20",
                                     name="cold_{}_pkh".format(i),
                                     description="cold_{}".format(i))

        fn_lines = []
        fn_lines.append("function " + fn_name + "(pubkey pk, sig s) {")
        req_pkh_cond = ' || '.join(["hash160(pk) == cold_{}_pkh".format(i) for i in range(n)])
        fn_lines.append("require(" + req_pkh_cond + ");")
        fn_lines.append("require(checkSig(s, pk));")
        fn_lines.append('}')

        fn_text = '\n'.join(fn_lines)
        self._add_to_functions(fn_name, fn_text, description='cold')



cg = cov_gen(intro_comment='gannan gidel dagan bagan')
cg.basic_covenant(n_recipients=2, include_any=True)
cg.allow_cold(2)
print(cg.get_script())
print()
# print(cg.compile_script(cash_file_path='cov.cash', json_file_path='arti.json'))




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
