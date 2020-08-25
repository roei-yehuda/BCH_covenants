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

import os.path
import glob
import datetime
import sys
from datetime import datetime
import re
import numpy as np
import pandas as pd


class cov_gen():

    def __init__(self, contract_name='cov', cashScript_pragma='0.4.0'):
        self.contract_name = contract_name
        self.pragma = cashScript_pragma
        self.constructor_text = ""
        self.body_text = ""

    def _write_to_constructor(self, text):
        self.constructor_text += text + ", "

        # cons = [("bytes20", "recepient_0"), ("bytes20", "recepient_1")]

    def _write_to_body(self, fn_text):
        # we strip the input fn_text, then add indentation to its inner scope

        def add_indentation(text):
            text = "\t" + text.strip()[:-1]
            text = text.replace('\n', '\n\t\t')
            text = text[:text.rfind('\n')+1] + "\t}"
            return text

        self.body_text += add_indentation(fn_text) + "\n"


    def output_script(self, return_as_string=False, output_file_path=None):

        full_script = \
            "pragma cashscript ^" + self.pragma + ";\n\n" \
            "contract " + self.contract_name + "(" + self.constructor_text[:-2] + "){\n" \
            "\n" + self.body_text + "\n" \
            "}"

        if output_file_path is not None:
            with open(output_file_path, "w") as f:
                print(full_script, file=f)

        if return_as_string:
            return full_script

    def basic_covenant(self,
                       number_of_receipients=1):
                       #
                       # allowed_output_pkh=[], use_all_pkh=False,
                       # allowed_output_sh=[], use_all_sh=False):

        # todo - maybe we need to check input is valid


        # for pkh in allowed_output_pkh:
        for i in range(number_of_receipients):
            self._write_to_constructor("bytes20 recepient_{}".format(i))

        fn_text =   "function spend(pubkey pk, sig s) {\n" \
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

        self._write_to_body(fn_text)


# if __name__ == 'main':

cg = cov_gen()
cg.basic_covenant(number_of_receipients=3)
print(cg.output_script(return_as_string=True))




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
