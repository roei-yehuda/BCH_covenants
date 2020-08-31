##  This file is part of the covGen project which can be found at https://github.com/roei-yehuda/BCH_covenants
##  This project was a created for a university course, and then made publicly available.
##  Introduction to Cryptocurrencies, course #67513, Hebrew University Jerusalem Israel, Aug 2020.
##  Avigail Suna; avigail.suna@mail.huji.ac.il
##  Roei Yehuda; roei.yehuda@mail.huji.ac.il


"""

The code in this file holds the command-line interface (CLI) for the covGen.

The classes cov_gen_CLI and create_contract_CLI utilize the cov_gen class to create and compile a new contract.
cov_gen_CLI and use_contract_CLI use the js_bridge class for deployment, management of and interaction with smart
contracts on the blockchain through the JavaScript SDK.

"""

from covenant_generator import *
from js_bridge import *

import copy
import os
import sys
import re

# allow to print in color on the shell:
from termcolor import colored
import platform
if platform.platform().startswith('Windows'):
    import colorama
    colorama.init()
REG = 'white'
ERR = 'red'
IN = 'yellow'
HIGHLIGHT = 'cyan'


debug = False


class cov_gen_CLI():

    def __init__(self):
        # global commands - the user may input these commands at any point
        self.globals = ['-i', '-h', '-exit']

    def print(self, s: str, c: str = None, end="\n"):
        if c is not None:
            print(colored(s, c), end=end)
        else:
            print(colored(s, REG), end=end)

    def run(self):

        def print_intro():
            self.print('\n\n{}'.format('*' * 50), HIGHLIGHT)
            self.print("Welcome to the BCH Covenant Generator!", HIGHLIGHT)
            self.print('{}\n'.format('*' * 50), HIGHLIGHT)

            intro_msg = "This program facilitates the creation, deployment and use of\n" \
                        "smart contracts and covenants in BCH.\n" \
                        "\n" \
                        "Quick usage info and tips:\n" \
                        "* This command line interface (CLI) asks you questions and waits for your input.\n" \
                        "  Default answers are shown in square brackets (leave the input empty to go with the default).\n" \
                        "  Limited choice options are shown in curly brackets.\n" \
                        "* At any given moment you can type '-i' for more information about the specific point you are at,\n" \
                        "  as well as '-h' to get general instructions for usage of this command line interface (CLI).\n" \
                        "  If this is your first time here, you are encouraged to try both now.\n" \
                        "\n"

            # use color on -i and -h
            a, b, c = re.split('-i|-h', intro_msg)
            print(colored(a, REG), end='')
            print(colored('-i', 'yellow'), end='')
            print(colored(b, REG), end='')
            print(colored('-h', 'yellow'), end='')
            print(colored(c, REG))

        print_intro()

        q = "First things first, what are you here for?\n" \
            "1) Create and compile a new smart contract\n" \
            "2) Initialize or use an existing contract\n"
        intro_msg_i = "The covGen has two modes - \n" \
                      "mode 1: creation (+compilation) of a new smart contract\n" \
                      "mode 2: instantiating and operation of a compiled contract"
        do_create_contract = '1' == self.parse_input(desc_line=q,
                                                     default=None,
                                                     choices=["1", "2"],
                                                     i_msg=intro_msg_i,
                                                     show_choice=False)

        return do_create_contract


    def parse_input(self,
                    desc_line='', tp=str, default=None, choices=None,
                    i_msg='Sorry, no more information is provided. You can always try -h',
                    end='', show_choice=True):

        self.print("{q}{deft}{choice}{sep}".format(q=desc_line,
                                                   deft='' if default is None else ' [{}]'.format(str(default)),
                                                   choice='' if (choices is None or not show_choice) else " {" + ', '.join(choices) + "}",
                                                   sep=' ' if desc_line == '' or desc_line.endswith(("?", "\n", "-", "=")) else ': '), IN, end)
        my_input = input().strip()

        # help and global functions
        if my_input in self.globals:
            if my_input == '-i':
                self.print(i_msg)
            if my_input == '-h':
                self._h()
            if my_input == '-exit':
                self._exit()
            my_input = self.parse_input(desc_line, tp, default, choices, i_msg, end, show_choice)

        # no input entry
        if my_input == '':
            if default is not None:
                return default
            else:
                my_input = self.parse_input(desc_line, tp, default, choices, i_msg, end, show_choice)

        # check if input is valid
        try:
            my_input_in_tp = tp(my_input)
            if choices is not None:
                if my_input_in_tp in choices:
                    return my_input_in_tp
                else:
                    self.print('Oops! wrong input, your options are {}:'.format(str(choices)), ERR)
                    return self.parse_input(desc_line, tp, default, choices, i_msg, end, show_choice)
            return my_input_in_tp
        except ValueError:
            self.print('Oops! {} is not of type {}, try again:'.format(str(my_input), str(tp)), ERR)
            return self.parse_input(desc_line, tp, default, choices, i_msg, end, show_choice)


    def _h(self):
        """ help information global """
        h_msg = "The following commands can be typed in at any time:\n" \
                "-h: help (this message)\n" \
                "-i: information for cuurent position\n" \
                "-exit: terminate the program"
        self.print(h_msg)


    def _exit(self):
        """ exit the program """
        self.print("Exiting. Goodbye", HIGHLIGHT)
        sys.exit(0)


    def _y_n_question(self, question: str, i_msg=None):
        if i_msg is None:
            i_msg = '{}? type y or n and then enter)'.format(question)
        return self.parse_input(desc_line=question, tp=str, default=None, choices=['y', 'n'],
                                i_msg=i_msg)




class create_contract_CLI(cov_gen_CLI):
    """
    CLI for the first mode - creation (+compilation) of a new smart contract
    """
    # restrictions info massages:
    rs_operators_i_msg = "Operator of a function is someone who is allowed to use (call) it.\n" \
                         "Their public key and signature will be checked upon calling the function.\n" \
                         "- Note that if a function is composed solely of an operators restriction, then\n" \
                         "  these operators may create a transaction that calls this function and spend the\n" \
                         "  contract's funds freely."
    rs_recipients_i_msg = "Recipient of a function is someone that appears on the transaction's output.\n" \
                          "Recipients may be public keys (P2PKH) or contract addresses (P2SH).\n" \
                          "- If the recipients are required for a signature as well (relevant for PKH recipients),\n" \
                          "  this means they have to be of the signers of the transaction, i.e. only one of the \n" \
                          "  recipients can call this function.\n" \
                          "- Any or all: It is possible to allow any (one) of the recipients to get the funds, or \n" \
                          "  demand that all of them get an equal share every time this function is called.\n" \
                          "- Note that if a function is composed solely of a recipients restriction, and\n" \
                          "  without requiring their signatures, then anyone can create any transaction given\n" \
                          "  that the output is (either one of, or all of) the pre-defined recipients."
    rs_amount_i_msg = "The amount of money in the transaction (in satoshis) can be restricted per the \n" \
                      "transaction, per a recipient i.e. output, or both."
    rs_time_i_msg = "The time of the transaction can be restricted to be within a certain period.\n" \
                    "- 'time' vs 'age': \n" \
                    "  It is possible to use either a relative time restriction (using tx.age), or\n" \
                    "  an absolute one (using tx.time). Note that due to limitations in the Bitcoin \n" \
                    "  Script time can only be used with MIN, age can be used with MIN or MAX.\n" \
                    "- 'time' and 'age' can be either a block number or a time stamp\n" \
                    "- 'min' vs 'max':\n" \
                    "  If min is defined, then the funds must be pulled after the TIME specified.\n" \
                    "  If max is defined, the funds must be pulled before the TIME specified."
    rs_i_msg = "Operators restriction:\n" + utils().indent(rs_operators_i_msg) + "\n" \
               + "Recipients restriction:\n" + utils().indent(rs_recipients_i_msg) + "\n" \
               + "Amount restriction:\n" + utils().indent(rs_amount_i_msg) + "\n" \
               + "Time restriction:\n" + utils().indent(rs_time_i_msg)
    add_fn_i_msg = "A contract consists of functions. Each function consists of restrictions,\n" \
                   " i.e. requirements. In order to access the funds stored in the contract, a\n" \
                   "(single) function is called and all of its restrictions must be met."
    add_rs_i_msg = add_fn_i_msg + "\n" + rs_i_msg
    update_i_msg = "A deployed instance of a smart contract cannot be changed. The only way to update\n" \
                   "your contract is by transferring its funds to a new contract, with the new constructor\n" \
                   "parameters. An editor may choose to do so by simply providing the new contract address"

    def __init__(self):
        super().__init__()

    def run(self):
        """
        initiate the creation of a new contract - defining name and functions and restrictions
        """

        # variables for the generation of cov_gen
        self.cov_init_args = copy.deepcopy(cov_gen.cov_init_kwargs_d)  # {'contract_name':'cov', 'cashScript_pragma':'0.5.0', 'miner_fee':1000, 'intro_comment':''}
        self.cov_funcs_list = []

        self.set_init()

        self.print("\nGood, now that we have the basics, let's write the functions.\n" +
                   "\tIn a nutshell, a smart contract is composed of functions.\n" +
                   '\tEach function includes at least one restriction (requirement).\n' +
                   '\tIn order to use a contract (e.g. spend money from it), one interacts\n' +
                   '\twith one of its functions and has to meet all of its restrictions.')
        while self._y_n_question('would you like to add a new function?', i_msg=self.add_fn_i_msg) == 'y':
            self.add_fn()

        # updatability
        make_updatabile = self._y_n_question('would you like to make this contract updatable?', i_msg=self.update_i_msg) == 'y'
        if make_updatabile:
            self.add_updatability()

        # generate contract and exit
        self.print('\n', REG)
        self.generate_cov()
        self._exit()

    def set_init(self):
        """
        Setting some basic initial parameters for the contract, before going down the rabbit hole with the functions
        """

        self.print('Upon creating a new contract, set some basic parameters first:')
        self.cov_init_args['contract_name'] = self.parse_input(desc_line='contract name (wo spaces)',
                                                               tp=str,
                                                               default=self.cov_init_args['contract_name'],
                                                               choices=None,
                                                               i_msg='Choose a name for your contract. Do not use spaces or tabs etc.')
        self.cov_init_args['cashScript_pragma'] = self.parse_input(desc_line='cashScript pragma',
                                                                   tp=str,
                                                                   default=self.cov_init_args['cashScript_pragma'],
                                                                   choices=None,
                                                                   i_msg='cashScript version with which the contract will be written and compiled.')
        self.cov_init_args['miner_fee'] = self.parse_input(desc_line='miner fee',
                                                           tp=str,
                                                           default=self.cov_init_args['miner_fee'],
                                                           choices=None,
                                                           i_msg='miner fee (in satoshis) for deployment of the contract on the blockchain and \n'
                                                                 'for transactions interacting with it - this will be hardcoded to the script in some cases.\n'
                                                                 'Too low of a fee might result in your contract not being accepted')
        self.cov_init_args['intro_comment'] = self.parse_input(desc_line='description comment (optional)',
                                                               tp=str,
                                                               default='',
                                                               choices=None,
                                                               i_msg='This comment will appear at the very start of the .cash script,\n'
                                                                     'so it is best used for a general description of the contract or some important notes.\n')
        return

    def fn_rs_operators(self):
        """
        restrict operators
        """

        r_d = copy.deepcopy(cov_fn.restrict_operators_kwargs_d)
        r_d['n'] = self.parse_input(desc_line='number of desired operators', tp=int, default=1,
                                    i_msg=self.rs_operators_i_msg)
        return r_d

    def fn_rs_recipients(self):
        """
        restrict recipients
        """

        r_d = copy.deepcopy(cov_fn.restrict_recipients_kwargs_d)

        r_d['n_PKH'] = self.parse_input(desc_line='number of desired P2PKH recipients (P2PKH)', tp=int, default=1,
                                        i_msg=self.rs_recipients_i_msg)

        r_d['n_SH'] = self.parse_input(desc_line='number of desired P2SH recipients (P2SH)', tp=int, default=0,
                                       i_msg=self.rs_recipients_i_msg)

        r_d['require_recipient_sig'] = 'y' == self._y_n_question(
            'would you like to require a signature from the recipient(s)?',
            i_msg=self.rs_recipients_i_msg)
        r_d['include_all'] = 'all' == self.parse_input(
            desc_line="Would you like the tx's output to include any of the recipients or all of them?",
            tp=str, default='any', choices=['any', 'all'],
            i_msg=self.rs_recipients_i_msg)

        return r_d

    def fn_rs_amount(self):
        """
        restrict the amount that can be pulled in a transaction
        """

        r_d = copy.deepcopy(cov_fn.restrict_amount_kwargs_d)
        _tx = "It is possible to restrict the amount per transaction or per recipient or both"
        self.print(_tx, REG)

        def limit_amount_y_n(whom: str):
            return self._y_n_question('would you like to limit the amount per {}?'.format(whom),
                                      i_msg=self.rs_amount_i_msg)

        if limit_amount_y_n('transaction') == 'y':
            r_d['max_amount_per_tx'] = self.parse_input(
                desc_line='amount limit per transaction (positive natural number, in satoshis)', tp=int, default=None,
                i_msg=self.rs_amount_i_msg)
        if limit_amount_y_n('recipient') == 'y':
            r_d['max_amount_per_recipient'] = self.parse_input(
                desc_line='amount limit per recipient (positive natural number, in satoshis)', tp=int, default=None,
                i_msg=self.rs_amount_i_msg)
        return r_d

    def fn_rs_time(self):
        """
        create a time window for cancellation
        """

        r_d = copy.deepcopy(cov_fn.restrict_time_kwargs_d)
        _tx = "A time restriction defines the time window in which the funds can be pulled, and can\n" \
              "either be used with a relative or absolute time lock."
        self.print(_tx, REG)

        def pick_min_max():
            _min = self._y_n_question('would you like to add a minimum time limitation?',
                                      i_msg=self.rs_time_i_msg) == 'y'
            _max = self._y_n_question('would you like to add a maximum time limitation?',
                                      i_msg=self.rs_time_i_msg) == 'y'
            return _min, _max

        _min, _max = pick_min_max()
        while not (_min) and not (_max):
            self.print('You must pick at least one min or max option', ERR)
            _min, _max = pick_min_max()

        def insert_to_rd_min_mex(min_max: str):
            time_stamp = self.parse_input(desc_line='pick a unit of time for {} time limit'.format(min_max), tp=str,
                                          default=None,
                                          choices=['seconds', 'minutes', 'hours', 'days', 'weeks'],
                                          i_msg='write down one of the choices for a {} time reference.\nFurther info:\n{}'.format(
                                              min_max, self.rs_time_i_msg))
            time_num = self.parse_input(desc_line='how many {} would you like?'.format(time_stamp), tp=int,
                                        default=None,
                                        i_msg='enter a number of {} for {} time limit, must be an integer.\nFurther info:\n{}'.format(
                                            time_stamp, min_max, self.rs_time_i_msg))
            return "{} {}".format(time_stamp, str(time_num))

        if _min:
            r_d['min'] = insert_to_rd_min_mex(min_max='min')
        if _max:
            r_d['max'] = insert_to_rd_min_mex(min_max='max')

        r_d_typ_lim = self.parse_input(desc_line='time limit type', tp=str, default=None, choices=['time', 'age'],
                                       i_msg='pick a type of time limitation, time - absolute, age - relative.\nFurther info:\n{}'.format(
                                           self.rs_time_i_msg))
        r_d['{}_limit'.format(r_d_typ_lim)] = True
        return r_d

    def add_fn(self):
        """
        add a new function to the contract
        """

        fn_name = self.parse_input(desc_line='function name', tp=str, default=None,
                                   i_msg='write a name for your function (again - wo spaces)) and then click enter')
        self.print("{} new function: {}".format('-' * 20, fn_name), HIGHLIGHT)
        fn_desc = self.parse_input(desc_line='function description (optional)', tp=str, default='',
                                   i_msg="write a description for your function.\n" +
                                         "This will appear right after the function's signature line")

        fn_restrictions = []

        def add_restriction():
            self.print('Possible restrictions are: operators | recipients | amount | time')
            r = self.parse_input(desc_line='which restriction would you like to apply?', tp=str, default=None,
                                 choices=['o', 'r', 'a', 't'],
                                 i_msg=self.rs_i_msg)
            if r == 'o':
                r = 'operators'
                r_args_d = self.fn_rs_operators()
            elif r == 'r':
                r = 'recipients'
                r_args_d = self.fn_rs_recipients()
            elif r == 'a':
                r = 'amount'
                r_args_d = self.fn_rs_amount()
            else:  # r == 't':
                r = 'time'
                r_args_d = self.fn_rs_time()

            fn_restrictions.append((r, r_args_d))

        # add restrictions in a while loop
        while self._y_n_question('would you like to add a new restriction?', i_msg=self.add_rs_i_msg) == 'y':
            add_restriction()

        self.cov_funcs_list.append((fn_name, fn_desc, fn_restrictions))

        self.print("{} end of function: {}".format('-' * 20, fn_name), HIGHLIGHT)


    def add_updatability(self):
        """
        create a function with a single restriction for operator(s) to allow them
        to transfer the funds to a new contract
        """

        fn_name = 'editContract'
        fn_desc = 'allows an editor to transfer the funds in this contract to a new one'
        fn_restrictions = []

        self.print("{} new function: {}".format('-' * 20, fn_name), HIGHLIGHT)

        r = 'operators'
        r_d = copy.deepcopy(cov_fn.restrict_operators_kwargs_d)
        r_d['n'] = self.parse_input(desc_line='number of desired editors', tp=int, default=1,
                                    i_msg=self.update_i_msg)
        fn_restrictions.append((r, r_d))

        self.cov_funcs_list.append((fn_name, fn_desc, fn_restrictions))

        self.print("{} end of function: {}".format('-' * 20, fn_name), HIGHLIGHT)

    def generate_cov(self):
        """
        use cov_gen to generate the source code and artifact for the contract
        """

        cg = cov_gen(**self.cov_init_args)
        cg.build_from_fn_list(self.cov_funcs_list)
        self.print("{} final script: {}".format('-' * 20, '-' * 20), HIGHLIGHT)
        self.print(cg.get_script())
        self.print("{} end of script {}\n".format('-' * 20, '-' * 20), HIGHLIGHT)

        save_i_msg = "A cashScript smart contract is saved as a '.cash' file. A descriptive artifact\n" \
                     "file, which includes the compiled code, is saved as a '.json' file."

        if self._y_n_question('would you like compile and save it?', i_msg=save_i_msg) == 'y':
            cash_f_def = os.path.join(os.getcwd(), 'contract.cash')
            json_f_def = os.path.join(os.getcwd(), 'contract.json')
            cash_f = self.parse_input(desc_line='choose location for the smart contract file',
                                      default=cash_f_def,
                                      i_msg=save_i_msg)
            json_f = self.parse_input(desc_line='choose location for the artifact file',
                                      default=json_f_def,
                                      i_msg=save_i_msg)

            byte_code = cg.compile_script(cash_f, json_f)
            self.print("{}\nThe compiled code: \n".format('-' * 20), HIGHLIGHT)
            self.print(byte_code)
            self.print(
                "{}\nFiles for the smart contract were successfully saved at:\n{}\n{}\nGoodbye :)".format('-' * 20,
                                                                                                          cash_f,
                                                                                                          json_f), HIGHLIGHT)
        return cg


class use_contract_CLI(cov_gen_CLI):
    """
    CLI for the second mode - instantiating and operation of a compiled contract
    """

    def __init__(self):
        super().__init__()
        self.js_args = copy.deepcopy(js_bridge().args)

    def run(self):
        """
        initiate the instantiation of a contract - defining general parameters (e.g. network) and constructor arguments
        """

        self.js_args = copy.deepcopy(js_bridge().args)

        self.set_init()

        self.set_constructor()

        self.print("Finaly we can get down to business.", HIGHLIGHT)
        self.print("\tFrom this point on the CLI will ask you to choose an action, if you wish\n"
                   "\tto finish up just type '-exit'")

        action = self.parse_input(
            desc_line="would you like to instantiate a contract (init), or operate an \ninstantiated one (use)?",
            default=None,
            choices=['init', 'use'],
            i_msg='Choose an action. You can always type in -h for general instructions.')

        while action is not None:
            if action == 'init':
                self.init_contract()
            else:
                self.use_contract()
            action = self.parse_input(
                desc_line="would you like to instantiate a contract (init), or operate an \ninstantiated one (use)?",
                default=None,
                choices=['init', 'use'],
                i_msg='Choose an action. You can always type in -h for general instructions.')

    def set_init(self):
        """
        Set basic parameters for the deployment of a contract. this is a long method with ~10 parameters to set,
        but the majority have default values
        """

        self.print('Before we start interacting with the contract, we need to set some basics first.')
        self.print("Currently, all your parameters are set to default:", IN)
        self.print(utils().indent("\n".join(["{} = {}".format(k, self.js_args[k]) for k in self.js_args.keys()])))

        if 'n' == self._y_n_question('would you like to change any of them?'):
            return

        # self.args = {
        ##     'DEBUG': 'false',
        ##     'NETWORK': 'testnet',
        ##     'MAINNET_API': 'https://free-main.fullstack.cash/v3/',
        ##     'TESTNET_API': 'https://free-test.fullstack.cash/v3/',
        ##     # (Chris) 'https://free-test.fullstack.cash/v3/'    # (ts) 'https://trest.bitcoin.com/v2/'
        ##     'W_JSON': 'wallet.json',
        ##     'MNEMONIC': '',
        ##     'CHILD_I': '0',
        ##     'CASH_F': 'cov.cash',
        ##     'ARTIFACT_F': 'cov.json',
        ##     'C_JSON': '_cov_info.json',
        ##     'DO_COMPILE': 'true',
        ##     'NET_PROVIDER': 'new BitboxNetworkProvider(NETWORK, bitbox)',
        ##     # new ElectrumNetworkProvider(NETWORK)   # new BitboxNetworkProvider(NETWORK, bitbox)
        #     'CONSTRUCTOR_ARGS': '',
        #     'TX_FUNC': "''",
        #     # the entire right hand side for "const txDetails = " , should start with "await con.functions. ..."
        #     'MAIN': "console.log('Hello BCH world!');"
        # }

        self.js_args['DEBUG'] = 'true' if debug else 'false'

        self.js_args['NETWORK'] = self.parse_input(desc_line='choose BCH network',
                                                   default=self.js_args['NETWORK'],
                                                   choices=['testnet', 'mainnet'],
                                                   i_msg='Basically, mainnet uses real BCH and testnet is a simulation')

        if self.js_args['NETWORK'] == 'mainnet':
            self.js_args['MAINNET_API'] = self.parse_input(desc_line='set rest url for the network',
                                                           default=self.js_args['MAINNET_API'],
                                                           choices=None,
                                                           i_msg='')
        else:
            self.js_args['TESTNET_API'] = self.parse_input(desc_line='set rest url for the network',
                                                           default=self.js_args['TESTNET_API'],
                                                           choices=None,
                                                           i_msg='')

        cash_f_i_msg = "a BCH smart contract written in cashScript is saved in source code in a cash file.\n" \
                       "After being compiled by cashc, an artifact file is saved in a json file. \n" \
                       "The artifact file features useful info about the contract, including its bytecode."
        self.print("Set the paths to the contract's source code (cash file) and artifact (json file).")
        self.js_args['CASH_F'] = self.parse_input(desc_line="location of contract's source code:",
                                                  default=self.js_args['CASH_F'],
                                                  choices=None,
                                                  i_msg=cash_f_i_msg)
        self.js_args['DO_COMPILE'] = 'true' if self.js_args['CASH_F'] != '' else 'false'
        self.js_args['ARTIFACT_F'] = self.parse_input(desc_line="location of contract's artifact",
                                                      default=self.js_args['ARTIFACT_F'],
                                                      choices=None,
                                                      i_msg=cash_f_i_msg)

        c_json_i_msg = "After instantiation and deployment to the BCH blockchain, we save a json file\n" \
                       "with the contract's info, such as its address and constructor arguments."
        self.js_args['C_JSON'] = self.parse_input(desc_line="set location for the deployed contract's info json file",
                                                  default=self.js_args['C_JSON'],
                                                  choices=None,
                                                  i_msg=c_json_i_msg)

        w_json_i_msg = "The wallet's json file defines the user, i.e. creator of the transaction,\n" \
                       "operator of the contract calling a function.\n" \
                       "This json file has to include the following fields:\n" \
                       "- childPK\n" \
                       "- childPKH\n" \
                       "- cashAddress\n" \
                       "Or, alternatively i.e. instead of all of the above, the json file has to include:\n" \
                       "- mnemonic (12 words string)"
        self.js_args['W_JSON'] = self.parse_input(desc_line="set location for the wallet's json file",
                                                  default=self.js_args['W_JSON'],
                                                  choices=None,
                                                  i_msg=w_json_i_msg)

        ### more advanced parameters
        mnemonic_i_msg = "The wallet's mnemonic - a (private!) 12 words string"
        child_i_i_msg = "The wallet's (HDnode) child_i - its derived path index associated with the cashAddress"
        net_provider_i_msg = "The network's (mainnet/testnet) provider, syntax should be according to https://cashscript.org/docs/sdk/instantiation"
        if 'y' == self._y_n_question(
                'would you like to set the following items as well (more advanced):\n- mnemonic\n- childNode indexi\n- network provider',
                i_msg="{}\n{}\n{}".format(mnemonic_i_msg, child_i_i_msg, net_provider_i_msg)):
            self.js_args['MNEMONIC'] = self.parse_input(desc_line="wallet's mnemonic (optional)",
                                                        default=self.js_args['MNEMONIC'],
                                                        choices=None,
                                                        i_msg=mnemonic_i_msg)
            self.js_args['CHILD_I'] = self.parse_input(desc_line="wallet's childNode index",
                                                       default=self.js_args['CHILD_I'],
                                                       choices=None,
                                                       i_msg=child_i_i_msg + '\nThis should be an index (int from 0 to 9 is preferable)')
            self.js_args['NET_PROVIDER'] = self.parse_input(desc_line="The network's (mainnet/testnet) provider",
                                                            default=self.js_args['NET_PROVIDER'],
                                                            choices=None,
                                                            i_msg=net_provider_i_msg)

        return

    def set_constructor(self):
        """
        define the arguments the constructor of the contract instance should get
        """

        # first, trying to find current known cons_args

        cons_args = {}
        constructorInputs, constructorValues = None, None

        if os.path.exists(self.js_args['ARTIFACT_F']):
            with open(self.js_args['ARTIFACT_F']) as f:
                artifact_data = json.load(f)
            constructorInputs = artifact_data['constructorInputs']

        if os.path.exists(self.js_args['C_JSON']):
            with open(self.js_args['C_JSON']) as f:
                c_data = json.load(f)
            constructorValues = c_data['constructor_args']

        if constructorInputs is not None:
            if constructorValues is not None:
                for i in range(len(constructorInputs)):
                    cons_args[constructorInputs[i]["name"]] = (constructorInputs[i]["type"],
                                                               constructorInputs[i]["name"],
                                                               constructorValues[i])
            else:
                cons_args = {a["name"]: (a["type"], a["name"], '') for a in constructorInputs}

        cons_args_in_str = lambda: '\n'.join(
            ["{} {} = {}".format(cons_args[k][0], cons_args[k][1], cons_args[k][2]) for k in cons_args.keys()])

        self.print("check constructor parameters:\n"
                   "\tIn order to work with a smart contract on the blockchain, we need to have\n"
                   "\tits constructor parameters. These can be imported from a valid contract's\n"
                   "\tinfo json file, if such exists, or be given here manually (necessary for\n"
                   "\tthe first instantiation of the contract).\n\n"
                   "currently known contract's info json file: {}\n"
                   "currently known constructor parameters:\n{}\n".format('\t' + self.js_args['C_JSON'],
                                                                          utils().indent(cons_args_in_str())))
        if 'y' == self._y_n_question('would you like to update any of the above?'):
            c_json_i_msg = "After instantiation and deployment to the BCH blockchain, we save a json file\n" \
                           "with the contract's info, such as its address and constructor arguments."
            self.js_args['C_JSON'] = self.parse_input(
                desc_line="set location for the deployed contract's info json file",
                default=self.js_args['C_JSON'],
                choices=None,
                i_msg=c_json_i_msg)
            if 'y' == self._y_n_question('would you like to manually set the constructor arguments?'):
                for k in cons_args.keys():
                    v = self.parse_input(desc_line="{} {}".format(cons_args[k][0], cons_args[k][1]),
                                         default=cons_args[k][2],
                                         choices=None)
                    cons_args[k] = (cons_args[k][0], cons_args[k][1], v)

        # now we assume we are up to date
        self.cons_args = cons_args
        self.js_args['CONSTRUCTOR_ARGS'] = ', '.join(
            [cons_args[k][2] for k in [constructorInputs[i]["name"] for i in range(len(constructorInputs))]])

    def init_contract(self):
        """
        call js_bridge with the main function of init_contract()
        """

        self.js_args['MAIN'] = "init_contract();\nprint_contract_info();"
        self.js_run()

    def use_contract(self):
        """
        Define a transaction that uses a deployed contract
        """

        abi = None
        if os.path.exists(self.js_args['ARTIFACT_F']):
            with open(self.js_args['ARTIFACT_F']) as f:
                artifact_data = json.load(f)
            abi = artifact_data['abi']

        if abi is None or len(abi) == 0:
            self.print("Err: not able to get abi from the artifact, or abi is empty", ERR)
            return

        self.print("We will now create the transaction which interacts with the contract.")

        minerFee = self.parse_input(desc_line="set miner fee (in satoshis)",
                                    default='1000',
                                    choices=None,
                                    i_msg="The miner fee is hardcoded to the transaction.")

        func = self.parse_input(desc_line="Which function would you like to call?",
                                default=None,
                                choices=[func_d["name"] for func_d in abi],
                                i_msg='Choose a function to call with the current transaction.')

        ### get function arguments

        self.print("Set the arguments to be passed to the chosen function.\n"
                   "** Note! type 'SIG' when the signature of the tx creator is required.\n"
                   "   more information st '-i'")
        args_i_msg = "Set the arguments to be passed to the chosen function: {}\n" \
                     "** Note! if the signature of the tx creator is required (mostly, this argument\n" \
                     "is named 'sig s' or something similar), then it cannot be explicitly provided\n" \
                     "by you since it has to sign the entire transaction, which is not ready yet.. \n" \
                     "so in this case, just type in 'SIG'".format(func)
        funcInputs = None
        for func_d in abi:
            if func_d["name"] == func:
                funcInputs = func_d["inputs"]

        funcArgs = []
        for item in funcInputs:
            v = self.parse_input(desc_line="{} {} = ".format(item["type"], item["name"]),
                                 default=None,
                                 choices=None,
                                 i_msg=args_i_msg)
            if v == 'SIG':
                v = "new SignatureTemplate(walletInfo.childKeyPair)"
            funcArgs.append(v)

        def short_parse(a):
            return "{}".format(a) if a.isdigit() else "'{}'".format(a)
        funcArgs_str = ', '.join([short_parse(arg) for arg in funcArgs])

        ### tx output
        outputs = []
        amounts = []
        self.print("Type in the outputs of the transaction. Note that order matters.")
        output_i_msg = "Define the output(s) of the tx. Both the cashAdresses and amounts (satoshis).\n" \
                       "If the function being called has a restriction over its recipients, these must\n" \
                       "be given here in the exact same order as mentioned in the contract source code."
        output_count = 0
        while 'y' == self._y_n_question('would you like to add a new output?', i_msg=output_i_msg):
            out = self.parse_input(desc_line="output_{} (cashAdress)= ".format(output_count),
                                   default=None,
                                   choices=None,
                                   i_msg=output_i_msg)
            amount = self.parse_input(desc_line="amount_{} (satoshis)= ".format(output_count),
                                      default=None,
                                      choices=None,
                                      i_msg=output_i_msg)
            outputs.append(out)
            amounts.append(amount)
            output_count += 1
        to_str = ''.join([".to('{}', {})".format(t[0], t[1]) for t in zip(outputs,amounts)])

        self.js_args['TX_FUNC'] = "await con.functions.{}({}){}.withHardcodedFee({});".format(func,
                                                                                              funcArgs_str,
                                                                                              to_str,
                                                                                              minerFee)

        self.js_args['MAIN'] = "use_contract();"
        self.js_run()


    def js_run(self):
        """
        Use the self.js_args as set by now to create a temporary js script and run it
        """

        js = js_bridge()
        js.args = copy.deepcopy(self.js_args)
        js.run()


