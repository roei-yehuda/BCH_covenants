##  This file is part of the covGen project which can be found at https://github.com/roei-yehuda/BCH_covenants
##  This project was a created for a university course, and then made publicly available.
##  Introduction to Cryptocurrencies, course #67513, Hebrew University Jerusalem Israel, Aug 2020.
##  Avigail Suna; avigail.suna@mail.huji.ac.il
##  Roei Yehuda; roei.yehuda@mail.huji.ac.il


"""

The class js_bridge amends the js_bridge_template to create a temporary .js file (well, .ts to be exact) with the
relevant script to connect and operate on the blockchain.

"""

import os


class js_bridge():

    def __init__(self):
        self.args = {}
        self.reset_args()
        self.js_template_path = 'js_bridge_template'
        self.js_temp_code_path = '_temp_js_code.ts'

    def reset_args(self):
        self.args = {
            'DEBUG': 'false',
            'NETWORK': 'testnet',
            'MAINNET_API': 'https://free-main.fullstack.cash/v3/',
            'TESTNET_API': 'https://free-test.fullstack.cash/v3/', # (Chris) 'https://free-test.fullstack.cash/v3/'    # (ts) 'https://trest.bitcoin.com/v2/'
            'W_JSON': 'wallet.json',
            'MNEMONIC': '',
            'CHILD_I': '0',
            'CASH_F': 'cov.cash',
            'ARTIFACT_F': 'cov.json',
            'C_JSON': '_cov_info.json',
            'DO_COMPILE': 'true',
            'NET_PROVIDER': 'new BitboxNetworkProvider(NETWORK, bitbox)', # new ElectrumNetworkProvider(NETWORK)   # new BitboxNetworkProvider(NETWORK, bitbox)
            'CONSTRUCTOR_ARGS': '',
            'TX_FUNC': "''", # the entire right hand side for "const txDetails = " , should start with "await con.functions. ..."
            'MAIN': "console.log('Hello BCH world!');"
        }

    def run(self):
        with open(self.js_template_path, mode='r') as f:
            js_code = f.read()

        for k in self.args.keys():
            js_code = js_code.replace('###{}###'.format(k), self.args[k])

        with open(self.js_temp_code_path, "w") as f:
            print(js_code, file=f)

        os.system("ts-node " + self.js_temp_code_path)
