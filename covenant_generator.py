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
import copy


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




class cov_fn():

    def __init__(self, fn_name, desc_comment=None, miner_fee=1000):

        self.fn_name = fn_name
        self.miner_fee = miner_fee

        self.fn_args = {}
        self.fn_vars = {}
        self.constructor_args = {}
        self.fn_lines = []

        # start by adding the desc_comment right at the start:
        if desc_comment is not None and desc_comment != '':
            self.fn_lines.append('/*')
            for l in desc_comment.split('\n'):
                self.fn_lines.append(l)
            self.fn_lines.append('*/')

    def _add_to_fn_args(self, type, name, description=''):
        """
        Adding a single argument to the function's arguments.
        :param type: string
        :param name: string
        :param description: (optional) string - this is used for inner purposes, and will not be written to the output contract
        """
        # we record the order of arrival with len(self.constructor_args.keys())
        self.fn_args[name] = (type, name, len(self.fn_args.keys()), description)

    def _add_to_fn_vars(self, type, name):
        """
        Adding a single argument to the function's arguments.
        :param type: string
        :param name: string
        :param v: string
        """
        self.fn_vars[name] = (type, name)

    def _append_line_if_new(self, line):
        """
        append to sel.fn_lines only if this line did not appear beforehand
        :param line: string
        """
        do_append = True
        for l in self.fn_lines:
            if l==line:
                do_append = False
        if do_append:
            self.fn_lines.append(line)

    def _count_fn_vars(self, prefix=''):
        """
        Count how many variables are already stored in self.fn_vars
        :param prefix: string - count only variables with this prefix
        :return: int
        """
        return len([k for k in self.fn_vars.keys() if k.startswith(prefix)])

    def _get_fn_args_text(self):
        return ', '.join([self.fn_args[k][0] + ' ' + self.fn_args[k][1] for k in self.fn_args.keys()])

    def _add_to_constructor(self, type, name, description=''):
        """
        Adding a single argument to the contract's constructor.
        :param type: string
        :param name: string
        :param description: (optional) string - this is used for inner purposes, and will not be written to the output contract
        """
        # we record the order of arrival with len(self.constructor_args.keys())
        self.constructor_args[name] = (type, name, len(self.constructor_args.keys()), description)

    def _get_fn_text(self):
        """
        unindented
        :return:
        """
        fn_text = "function " + self.fn_name + "(" + self._get_fn_args_text() + ") {\n"
        fn_text += '\n'.join(self.fn_lines)
        fn_text += '\n}'
        return fn_text

    def get_fn_info(self):
        return self._get_fn_text(), self.constructor_args


    restrict_operators_kwargs_d = {'n':1}
    def restrict_operators(self, n=1):

        if n < 1:
            return

        self.fn_lines.append("// *** restrict operators")

        for i in range(n):
            self._add_to_constructor(type="bytes20",
                                     name="operator_{}_pkh_{}".format(i, self.fn_name),
                                     description="operator".format(i))

        self._add_to_fn_args('pubkey', 'pk')
        self._add_to_fn_args('sig', 's')

        req_pkh_cond = ' || '.join(["hash160(pk) == operator_{}_pkh_{}".format(i, self.fn_name) for i in range(n)])
        self.fn_lines.append("require(" + req_pkh_cond + ");")
        self._append_line_if_new("require(checkSig(s, pk));")

    restrict_recipients_kwargs_d = {'n_PKH':1, 'n_SH':0, 'require_recipient_sig':False, 'include_all':False}
    def restrict_recipients(self,
                            n_PKH=1,
                            n_SH=0,
                            require_recipient_sig=False,
                            include_all=False
                            ):
        n = n_PKH + n_SH
        if n == 0:
            return

        self.fn_lines.append("// *** restrict recipients")

        for i in range(n_PKH):
            self._add_to_constructor(type="bytes20",
                                     name="recepient_{}_pkh_{}".format(i, self.fn_name),
                                     description="recepient_pkh")

        for i in range(n_SH):
            self._add_to_constructor(type="bytes20",
                                     name="recepient_{}_sh_{}".format(i, self.fn_name),
                                     description="recepient_sh")

        self._add_to_fn_args('pubkey', 'pk')
        self._add_to_fn_args('sig', 's')

        if require_recipient_sig:
            self.fn_lines.append("// the tx can only be signed by one of the pkh recipients")
            req_pkh_cond = ' || '.join(["hash160(pk) == recepient_{}_pkh_{}".format(i, self.fn_name) for i in range(n_PKH)])
            self.fn_lines.append("require(" + req_pkh_cond + ");")
        else:
            self.fn_lines.append("// the tx can be signed by anyone (after all, money can only be sent to the correct address)")
        self._append_line_if_new("require(checkSig(s, pk));")

        self.fn_lines.append("// Create and enforce outputs")

        if self._count_fn_vars('minerFee') == 0:
            self.fn_lines.append("int minerFee = " + str(self.miner_fee) + "; // hardcoded fee")
            self._add_to_fn_vars('int', 'minerFee')
        if self._count_fn_vars('intTxVal') == 0:
            self.fn_lines.append("int intTxVal = int(bytes(tx.value));")
            self._add_to_fn_vars('int', 'intTxVal')

        j = self._count_fn_vars('intAmount_')
        if include_all and n > 1:
            # we assume all recipients get an equal share
            self.fn_lines.append("int intAmount_{} = int((intTxVal - minerFee) / {})".format(j, n)) # todo maybe we need to do -1 ?
        else:
            self.fn_lines.append("int intAmount_{} = intTxVal - minerFee".format(j))
        self._add_to_fn_vars('int', 'intAmount_{}'.format(j))
        self.fn_lines.append("bytes8 amount = bytes8(intAmount_{});".format(j))

        for i in range(n_PKH):
            self.fn_lines.append("bytes34 outPKH_{} = new OutputP2PKH(amount, recepient_{}_pkh_{});".format(i, i, self.fn_name))
        for i in range(n_SH):
            self.fn_lines.append("bytes32 outSH_{} = new OutputP2SH(amount, recepient_{}_sh_{});".format(i, i, self.fn_name))
        # todo - when the user is typing SH recipients adresses, allow him to type THIS_CONTRACT, in which case we need to write "hash160(tx.bytecode)"

        if include_all:
            sep = ' + '
            all_outs = ['outPKH_{}'.format(i) for i in range(n_PKH)] + ['outSH_{}'.format(i) for i in range(n_SH)]
            hashOutputs_cond = 'tx.hashOutputs == hash256(' + sep.join(all_outs) + ')'
        else:
            sep = ' || '
            all_outs = ["tx.hashOutputs == hash256(outPKH_{})".format(i) for i in range(n_PKH)] + ["tx.hashOutputs == hash256(outSH_{})".format(i) for i in range(n_SH)]
            hashOutputs_cond = sep.join(all_outs)
        self.fn_lines.append("require(" + hashOutputs_cond + ");")

    restrict_amount_kwargs_d = {'max_amount_per_tx': None, 'max_amount_per_recipient': None}
    def restrict_amount(self, max_amount_per_tx=None, max_amount_per_recipient=None):

        if max_amount_per_tx is None and max_amount_per_recipient is None:
            return

        self.fn_lines.append("// *** restrict amount")

        self._add_to_fn_args('pubkey', 'pk')
        self._add_to_fn_args('sig', 's')
        self._append_line_if_new("require(checkSig(s, pk));")

        if self._count_fn_vars('minerFee') == 0:
            self.fn_lines.append("int minerFee = " + str(self.miner_fee) + "; // hardcoded fee")
            self._add_to_fn_vars('int', 'minerFee')
        if self._count_fn_vars('intTxVal') == 0:
            self.fn_lines.append("int intTxVal = int(bytes(tx.value));")
            self._add_to_fn_vars('int', 'intTxVal')

        if max_amount_per_tx is not None:
            self.fn_lines.append("// restrict amount per tx")
            self.fn_lines.append("require(intTxVal <= " + str(max_amount_per_tx) + " + minerFee);")

        if max_amount_per_recipient is not None:
            self.fn_lines.append("// restrict amount per recipient")
            saved_intAmounts = [k for k in self.fn_vars.keys() if k.startswith('intAmount_')]
            self.fn_lines.append("require(" + ' && '.join(["{} <= {}".format(k, str(max_amount_per_recipient)) for k in saved_intAmounts]) + ");")

    restrict_time_kwargs_d = {'min':None, 'max':None, 'time_limit':None, 'age_limit':None}
    def restrict_time(self, min=None, max=None, time_limit=None, age_limit=None):   # todo - understand what the difference is...

        if (min is None and max is None) or (time_limit is None and age_limit is None):
            return

        self.fn_lines.append("// *** restrict time of tx")

        self._add_to_fn_args('pubkey', 'pk')
        self._add_to_fn_args('sig', 's')
        self._append_line_if_new("require(checkSig(s, pk));")

        txT = "tx.time" if time_limit is not None else "tx.age"
        if min is not None:
            self.fn_lines.append("require({} <= {});".format(str(min), txT))
        if max is not None:
            self.fn_lines.append("require({} <= {});".format(txT, str(max)))


    # def restrict_P2PKH_recipients(self,
    #                               n=1,
    #                               require_recipient_sig=False,
    #                               include_all=False
    #                               ):
    #
    #     if n < 1:
    #         return
    #
    #     self.fn_lines.append("// *** restrict P2PKH recipients")
    #
    #     for i in range(n):
    #         self._add_to_constructor(type="bytes20",
    #                                  name="recepient_{}_pkh_{}".format(i, self.fn_name),
    #                                  description="recepient")
    #
    #     self._add_to_fn_args('pubkey', 'pk')
    #     self._add_to_fn_args('sig', 's')
    #
    #     if require_recipient_sig:
    #         self.fn_lines.append("// the tx can only be signed by one of the recipients")
    #         req_pkh_cond = ' || '.join(["hash160(pk) == recepient_{}_pkh_{}".format(i, self.fn_name) for i in range(n)])
    #         self.fn_lines.append("require(" + req_pkh_cond + ");")
    #     else:
    #         self.fn_lines.append("// the tx can be signed by anyone (after all, money can only be sent to the correct address)")
    #     self._append_line_if_new("require(checkSig(s, pk));")
    #
    #     self.fn_lines.append("// Create and enforce outputs")
    #
    #     if self._count_fn_vars('minerFee') == 0:
    #         self.fn_lines.append("int minerFee = " + str(self.miner_fee) + "; // hardcoded fee")
    #         self._add_to_fn_vars('int', 'minerFee')
    #     if self._count_fn_vars('intTxVal') == 0:
    #         self.fn_lines.append("int intTxVal = int(bytes(tx.value));")
    #         self._add_to_fn_vars('int', 'intTxVal')
    #
    #     j = self._count_fn_vars('intAmount_')
    #     if include_all:
    #         # we assume all recipients get an equal amount
    #         self.fn_lines.append("int intAmount_{} = int((intTxVal - minerFee) / {})".format(j, n))
    #         # amount_str = "int((intTxVal - minerFee) / {})".format(n)    # todo maybe we need to do -1 ?
    #     else:
    #         # amount = "int(bytes(tx.value)) - minerFee"
    #         # amount_str = "intTxVal - minerFee"
    #         self.fn_lines.append("int intAmount_{} = intTxVal - minerFee".format(j))
    #     self._add_to_fn_vars('int', 'intAmount_{}'.format(j))
    #     self.fn_lines.append("bytes8 amount = bytes8(intAmount_{});".format(j))
    #
    #     for i in range(n):
    #         self.fn_lines.append("bytes34 out_{} = new OutputP2PKH(amount, recepient_{}_pkh_{});".format(i, i, self.fn_name))
    #
    #     if include_all:
    #         hashOutputs_cond = 'tx.hashOutputs == hash256(' + ' + '.join(['out_{}'.format(i) for i in range(n)]) + ')'
    #     else:
    #         hashOutputs_cond = ' || '.join(["tx.hashOutputs == hash256(out_{})".format(i) for i in range(n)])
    #     self.fn_lines.append("require(" + hashOutputs_cond + ");")

# f1 = cov_fn('f1')
# f_fn = cov_fn.restrict_time
# f2 = cov_fn('f2')
# f2.f_fn()


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
        sorted_args_tuples.sort(
            key=lambda t: t[2])  # '2' since the index of the constructor_arg is the third argument in each tuple
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
        def indent_fn(fn_text):
            # main indentation:
            output = utils().indent_inside(fn_text.strip()) # we strip the input fn_text, then add indentation ('\t') to its inner scope
            output = utils().indent(output)     # another indentation for the entire thing
            # now check for "if" statements and add an additional tab. (We don't account for nested "if"s...)
            lines = fn_text.split('\n')
            lines_to_indent = []
            for i in range(len(lines)):
                l, l_is_an_if_line = lines[i].strip(), False
                for if_prefix in []:
                    if l.startswith(if_prefix):
                        l_is_an_if_line = True
                if l_is_an_if_line:
                    lines_to_indent.append(i+1)
            output = utils().indent(output, indices=lines_to_indent)
            return output

        return '\n\n'.join([indent_fn(fn_tup[0]) for fn_tup in self.functions.values()])

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
            "\n\n" \
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



    def new_fn(self, fn_name, desc_comment=None, restrictions=[]):
        """
        add a new function to current contract
        :param fn_name: string
        :param desc_comment: string
        :param restrictions: list of tuples (r, kwargs_dict) where r is a string describing one of the restrict
                              functions in cov_fn and kwargs_dict is a dictionary with the required kwargs
        """
        fn = cov_fn(fn_name, desc_comment, miner_fee=self.miner_fee)

        for r_tup in restrictions:
            restriction, kwargs_dict = r_tup
            if restriction == 'operators':
                fn.restrict_operators(**kwargs_dict)
            if restriction == 'recipients':
                fn.restrict_recipients(**kwargs_dict)
            if restriction == 'amount':
                fn.restrict_amount(**kwargs_dict)
            if restriction == 'time':
                fn.restrict_time(**kwargs_dict)

        # get the function's text, and the dictionary with Args 4 Constructor
        fn_text, fn_a4c_dict = fn.get_fn_info()

        for k in fn_a4c_dict.keys():
            self._add_to_constructor(type= fn_a4c_dict[k][0],
                                     name= fn_a4c_dict[k][1],
                                     description= fn_a4c_dict[k][3])

        self._add_to_functions(fn_name, fn_text)

    def build_from_fn_list(self, l):
        """
        build the contract's body from a list of functions info
        :param l: list of tuples (fn_name, fn_desc, fn_restrictions) where:
                    fn_name: string
                    fn_desc: string
                    fn_restrictions: list of restrictions as described in self.new_fn
        :return:
        """
        for fn_tup in l:
            self.new_fn(fn_tup[0], fn_tup[1], fn_tup[2])


    # def basic_covenant(self,
    #                    n_recipients=1,
    #                    p2sh_recipients_indices=[],
    #                    include_any=True):
    #
    #     # todo - maybe we need to check that the input is valid
    #
    #     fn_name = 'spend'
    #
    #     p2pkh_recipients_indices = [i for i in list(range(n_recipients)) if i not in p2sh_recipients_indices]
    #
    #     # todo - note that if this function has been called once, then we need to change the format of its constructor args: otherwise it'll just use ""recepient_{}_pkh"" again and it'll collide with the args created on the first run... they have to have a new unique name!
    #     #
    #
    #     for i in p2pkh_recipients_indices:
    #         self._add_to_constructor(type="bytes20",
    #                                  name="recepient_{}_pkh".format(i),
    #                                  description="allowed_recepient")
    #
    #     fn_lines = []
    #     fn_lines.append("function " + fn_name + "(pubkey pk, sig s) {")
    #
    #     # # this is commented out because it is not necessary to check *who* the signer is. But useful so don't delete yet :)
    #     # req_pkh_cond = ' || '.join(["hash160(pk) == recepient_{}_pkh".format(i) for i in p2pkh_recipients_indices])
    #     # fn_lines.append("require(" + req_pkh_cond + ");")
    #
    #     fn_lines.append("require(checkSig(s, pk));")
    #     fn_lines.append("// Create and enforce outputs")
    #     fn_lines.append("int minerFee = " + str(self.miner_fee) + "; // hardcoded fee")
    #     amount = "int(bytes(tx.value)) - minerFee" if include_any else "int((int(bytes(tx.value)) - minerFee) / {})".format(
    #         n_recipients)
    #     fn_lines.append("bytes8 amount = bytes8(" + amount + ");")
    #
    #     for i in range(n_recipients):
    #         if i in p2pkh_recipients_indices:
    #             fn_lines.append("bytes34 out_{} = new OutputP2PKH(amount, recepient_{}_pkh);".format(i, i))
    #         else:  # this means i is in p2sh_recipients_indices
    #             fn_lines.append("bytes32 out_{} = new OutputP2SH(amount, recepient_{}_pkh);".format(i, i))  # todo
    #
    #     if include_any:
    #         hashOutputs_cond = ' || '.join(["tx.hashOutputs == hash256(out_{})".format(i) for i in range(n_recipients)])
    #     else:
    #         hashOutputs_cond = 'tx.hashOutputs == hash256(' + ' + '.join(
    #             ['out_{}'.format(i) for i in range(n_recipients)]) + ')'
    #     fn_lines.append("require(" + hashOutputs_cond + ");")
    #
    #     fn_lines.append('}')
    #
    #     fn_text = '\n'.join(fn_lines)
    #     self._add_to_functions(fn_name, fn_text, description='basic_covenant')
    #
    # def allow_cold(self, n=1):
    #     """
    #     This method basically allows easy and unlimited access to the funds in the contract for n people defined
    #     in the constructor.
    #     :param n: int
    #     """
    #
    #     fn_name = 'cold'
    #
    #     for i in range(n):
    #         self._add_to_constructor(type="bytes20",
    #                                  name="cold_{}_pkh".format(i),
    #                                  description="cold_{}".format(i))
    #
    #     fn_lines = []
    #     fn_lines.append("function " + fn_name + "(pubkey pk, sig s) {")
    #     req_pkh_cond = ' || '.join(["hash160(pk) == cold_{}_pkh".format(i) for i in range(n)])
    #     fn_lines.append("require(" + req_pkh_cond + ");")
    #     fn_lines.append("require(checkSig(s, pk));")
    #     fn_lines.append('}')
    #
    #     fn_text = '\n'.join(fn_lines)
    #     self._add_to_functions(fn_name, fn_text, description='cold')






cg = cov_gen()
funcs_list = []

f1 = 'cold'
f1_desc = 'this is a cold func'
f1_restrictions = []
r, r_d = 'operators', copy.deepcopy(cov_fn.restrict_operators_kwargs_d) # {'n':1}
r_d['n'] = 1
f1_restrictions.append((r, r_d))
# r, r_d = 'time', copy.deepcopy(cov_fn.restrict_time_kwargs_d) # {'min':None, 'max':None, 'time_limit':None, 'age_limit':None}
# r_d['min'] = '30 days'
# r_d['age_limit'] = True
# f1_restrictions.append((r, r_d))
funcs_list.append((f1, f1_desc, f1_restrictions))

f2 = 'spend'
f2_desc = ''
f2_restrictions = []
r, r_d = 'recipients', copy.deepcopy(cov_fn.restrict_recipients_kwargs_d) # {'n_PKH':1, 'n_SH':0, 'require_recipient_sig':False, 'include_all':False}
r_d['n_PKH']=2
f2_restrictions.append((r, r_d))
funcs_list.append((f2, f2_desc, f2_restrictions))

cg.build_from_fn_list(funcs_list)
print(cg.get_script())

# print(cg.compile_script(cash_file_path='shared_cold_cov.cash', json_file_path='shared_cold_cov.json'))


