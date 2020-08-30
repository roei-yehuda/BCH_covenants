# this is the command line interface for our covenant generator
from covenant_generator import *
from termcolor import colored
import copy
import sys
import re


# print colors:
REG = 'white'
ERR = 'red'
IN = 'yellow'
HIGHLIGHT = 'blue'



class js_bridge():

    def __init__(self):
        self.args = {
            'NETWORK': 'testnet',
            'MAINNET_API': 'https://free-main.fullstack.cash/v3/',
            'TESTNET_API': '',  # (Chris) 'https://free-test.fullstack.cash/v3/'    # (ts) 'https://trest.bitcoin.com/v2/'
            'W_JSON': 'wallet.json',
            'MNEMONIC': '',
            'CHILD_I': 0,
            'CASH_F': 'cov.cash',
            'ARTIFACT_F': 'cov.json',
            'C_JSON': '_cov_info.json',
            'DO_COMPILE': 'true',
            'CONSTRUCTOR_ARGS': '',
            'TX_FUNC': '',
            'MAIN': ''
        }
        self.js_template_path = 'js_bridge_template'
        self.js_temp_code_path = '_temp_js_code.ts'

    def run(self):

        with open(self.js_template_path, mode='r') as f:
            js_code = f.read()

        for k in self.args.keys():
            js_code = js_code.replace('###{}###'.format(k), self.args[k])

        with open(self.js_temp_code_path, "w") as f:
            print(js_code, file=f)

        os.system("ts-node " + self.js_temp_code_path)



class cov_gen_CLI():


    def __init__(self):
        # global commands - the user may input these commands at any point
        self.globals = ['-i', '-h', '-exit', '-clear']
        self.run()

    def print(self, s: str, c: str=None, end="\n"):
        if c is not None:
            print(colored(s, c), end=end)
        else:
            print(colored(s, REG), end=end)

    def run(self):

        # variables for the generation of cov_gen
        self.cov_init_args = copy.deepcopy(cov_gen.cov_init_kwargs_d)  # {'contract_name':'cov', 'cashScript_pragma':'0.4.0', 'miner_fee':1000, 'intro_comment':''}
        self.cov_funcs_list = []

        def print_intro():

            self.print('\n\n{}'.format('*'*50), HIGHLIGHT)
            self.print("Welcome to the BCH Covenant Generator!", HIGHLIGHT)
            self.print('{}\n'.format('*'*50), HIGHLIGHT)

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
                        "\n" \

            # use color on -i and -h
            a, b, c  = re.split('-i|-h', intro_msg)
            print(colored(a, REG), end='')
            print(colored('-i', 'yellow'), end='')
            print(colored(b, REG), end='')
            print(colored('-h', 'yellow'), end='')
            print(colored(c, REG))

            desc_line = "First things first, what are you here for?\n" \
                        "1) Create and compile a new smart contract\n" \
                        "2) Initialize or use an existing contract\n"
            intro_msg_i = "intro_msg_i"

            createContract = '1' == self.parse_input(desc_line=desc_line,
                                                     default=None,
                                                     choices=["1","2"],
                                                     i_msg=intro_msg_i,
                                                     show_choice= False)

            return createContract




        # # print intro_msg:
        # # Rs = ['-o- operators', '-r- recipients', '-a- amount', '-t- time']
        # options = ['operators - could key participants ',
        #            'recipients - hot key participants',
        #            'amount - the max amount that can be drawn at any transaction',
        #            'time - waiting period in which the transaction can be evoked']
        # intro_msg = 'Hello, \n' \
        #         'what restrictions would you like to put on your money in BCH? \n' \
        #         'your options are: \n\n{}\n\nlets start!\n'.format('\n'.join(options))
        # self.print(self.intro_msg)

        # print intro msg and ask if the user wants to create a new contract or use an existing one
        create_contract = print_intro()

        if create_contract:
            self.run_create_contract()
        else:
            self.run_use_contract()

    def run_create_contract(self):

        self.set_init()

        self.print("\nGood, now that we have the basic, let's write the functions.\n" +
                   "\tIn a nutshell, a smart contract is composed of functions.\n" +
                   '\tEach function includes at least one restriction (requirement).\n' +
                   '\tIn order to use a contract (e.g. spend money from it), one interacts\n' +
                   '\twith one of its functions and has to meet all of its restrictions.')

        while self._y_n_question('would you like to add another function?') == 'y':
            self.add_fn()

        self.generate_cov()

    def run_use_contract(self):
        pass

    def set_init(self):
        self.print('Upon creating a new contract, set some basic variables first:')
        # {'contract_name':'cov', 'cashScript_pragma':'0.4.0', 'miner_fee':1000, 'intro_comment':''}
        self.cov_init_args['contract_name'] = self.parse_input(desc_line='contract name (wo spaces)',
                                                               tp=str,
                                                               default='cov',
                                                               choices=None,
                                                               i_msg='Choose a name for your contract. Do not use spaces or tabs etc.')
        self.cov_init_args['cashScript_pragma'] = self.parse_input(desc_line='cashScript pragma',
                                                                   tp=str,
                                                                   default='0.4.0',
                                                                   choices=None,
                                                                   i_msg='cashScript version with which the contract will be written and compiled.')
        self.cov_init_args['miner_fee'] = self.parse_input(desc_line='miner fee',
                                                           tp=str,
                                                           default=1000,
                                                           choices=None,
                                                           i_msg='miner fee (in satoshis) for deployment of the contract on the blockchain and \n'
                                                                 'for transactions interacting with it - this will be hardcoded to the script in some cases.\n'
                                                                 'Too low of a fee might result in your contract not being accepted')
        self.cov_init_args['intro_comment'] = self.parse_input(desc_line='description comment (optional)',
                                                               tp=str,
                                                               default='',
                                                               choices=None,
                                                               i_msg='This comment will appear at the very start of the .cash script,\n'
                                                                     'so it is best used for a general description of the contract or some important notes.\n'
                                                                     'if multi')
        return

    def parse_input(self,
                    desc_line='', tp=str, default=None, choices=None,
                    i_msg='Sorry, no more information is provided. You can always try -h',
                    end='', show_choice=True):

        self.print("{q}{deft}{choice}{sep}".format(q=desc_line,
                                                   deft = '' if default is None else ' [{}]'.format(str(default)),
                                                   choice = '' if (choices is None or not show_choice) else " {" + ', '.join(choices) + "}",
                                                   sep = ' ' if desc_line=='' or desc_line.endswith(("?", "\n", "-")) else ': '), IN, end)
        my_input = input().strip()

        # help and global functions
        if my_input in self.globals:
            if my_input == '-i':
                self.print(i_msg)
            if my_input == '-h':
                self._h()
            if my_input == '-exit':
                self._exit()
            if my_input == '-clear':
                self._clear()
            self.parse_input(desc_line, tp, default, choices, i_msg, end, show_choice)

        # no input entry
        if my_input == '':
            if default is not None:
                return default
            else:
                self.parse_input(desc_line, tp, default, choices, i_msg, end, show_choice)

        # check if input is valid
        try:
            my_input_in_tp = tp(my_input)
            if choices is not None:
                if my_input_in_tp in choices:
                    return my_input_in_tp
                else:
                    self.print('Oops! wrong input, your options are {}:'.format(str(choices)), ERR)
                    self.parse_input(desc_line, tp, default, choices, i_msg, end, show_choice)
            return my_input_in_tp
        except ValueError:
            self.print('Oops! {} is not of type {}, try again:'.format(str(my_input), str(tp)), ERR)
            self.parse_input(desc_line, tp, default, choices, i_msg, end, show_choice)

    def _h(self):
        """ help information global """
        self.print(' -h: help\n-exit: exit and close\n-clear: clear all the functions without exiting\n'
                           '-i information about this specific function')

    def _exit(self):
        """ exit the program """
        sys.exit(0)

    def _clear(self):
        """ restart, clear all """
        # todo
        pass

    def _y_n_question(self, question: str):
        return self.parse_input(desc_line=question, tp=str, default=None, choices=['y', 'n'],
                                i_msg='{}? type y or n and then enter)'.format(question))

    def fn_rs_operators(self):
        """ restrict operators """
        r_d = copy.deepcopy(cov_fn.restrict_operators_kwargs_d)
        r_d['n'] = self.parse_input(desc_line='number of desired operators', tp=int, default=1,
                                    i_msg='type the number of desired operators and then click enter:')
        return r_d

    def fn_rs_recipients(self):
        """ restrict recipients """
        r_d = copy.deepcopy(cov_fn.restrict_recipients_kwargs_d)
        r_d['n_PKH'] = self.parse_input(desc_line='number of desired recipients (P2PKH)', tp=int, default=1,
                                        i_msg='type the number of desired recipients and then click enter:')

        r_d['n_SH'] = self.parse_input(desc_line='number of desired contract recipients (P2SH)', tp=int, default=0,
                                       i_msg='type the number of desired contract recipients and then click enter:')

        r_d['require_recipient_sig'] = self._y_n_question('would you like the tx to only be signed by one of the pkh recipients?') == 'y'
        r_d['include_all'] = self._y_n_question('would you like the funds to be distributed to all?') == 'y'

        return r_d

    def fn_rs_amount(self):
        """ restrict the amount that can be pulled in a transaction """
        r_d = copy.deepcopy(cov_fn.restrict_amount_kwargs_d)

        def limit_amount_y_n(whom:str):
            self._y_n_question('would you like to limit the amount per {}? (y/n)'.format(whom))

        if limit_amount_y_n('transaction') == 'y':
            r_d['max_amount_per_tx'] = self.parse_input(desc_line='amount limit per transaction', tp=int, default=None,
                                                        i_msg='pic a transaction limit, must be an integer')
        if limit_amount_y_n('recipient') == 'y':
            r_d['max_amount_per_recipient'] = self.parse_input(desc_line='amount limit per recipient', tp=int, default=None,
                                                               i_msg='pic a limit per recipient, must be an integer')
        return r_d

    def fn_rs_time(self):
        """ create a time window for cancellation """
        r_d = copy.deepcopy(cov_fn.restrict_time_kwargs_d)
        # todo: fix
        r_d_min_max = self.parse_input(desc_line='min or max time window', tp=str, default=None, choices=['min', 'max'],
                                       i_msg='pick a time limitation, before a certain time passes (min), or after (max)')
        r_d[r_d_min_max] = self.parse_input(desc_line='time limitation [number][time stamp]', tp=str, default=None,
                                            i_msg='pick a time limitation a number and then a time stamp, for example "30 days"')
        self.print('which type of time limit would you like to use? time or age?', IN)
        r_d_typ_lim = self.parse_input(desc_line='type of time limit', tp=str, default=None, choices=['time', 'age'],
                                       i_msg='pick a type of time limitation, time - absolute, age - relative')
        r_d['{}_limit'.format(r_d_typ_lim)] = True
        return r_d

    def add_fn(self):
        fn_name = self.parse_input(desc_line='function name', tp=str, default=None,
                                   i_msg='write a name for your function (again - wo spaces)) and then click enter')
        self.print("{} new function: {} {} ".format('-'*20, fn_name, '-'*20), HIGHLIGHT)
        fn_desc = self.parse_input(desc_line='function description (optional)', tp=str, default='',
                                   i_msg="write a description for your function.\n" +
                                         "This will appear right after the function's signature line.\n" +
                                         "If you want it to be a multi line answer, type in MULTI and then enter")

        fn_restrictions = []

        def add_restriction():
            Rs = ['-o- operators', '-r- recipients', '-a- amount', '-t- time']
            restrict_txt = 'which restriction(s) would you like to apply?\n' \
                           'your options are:\n{}' \
                           '\ntype the first letter of one option and then click enter'.format('\n'.join(Rs))
            self.print(restrict_txt, IN)
            r = self.parse_input(desc_line='restriction', tp=str, default=None, choices=['o', 'r', 'a', 't'],
                                 i_msg='type the first letter of one option and then click enter:\n{}'.format('\n'.join(Rs)))
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
        while self._y_n_question('would you like to add another restriction?') == 'y':
            add_restriction()

        self.cov_funcs_list.append((fn_name, fn_desc, fn_restrictions))

        self.print("{} end of function: {} {} ".format('-' * 20, fn_name, '-' * 20), HIGHLIGHT)

    def generate_cov(self):
        cg = cov_gen(**self.cov_init_args)
        cg.build_from_fn_list(self.cov_funcs_list)
        print(cg.get_script())
        return cg





if __name__ == '__main__':
    cov_gen_CLI()



"""
# Avigail's tasks:
# - tx.time vs tx.age
# - add an option to remove fn


def enter_param(name='', tp=str, has_default=True, default=None):
    print('enter ' + name + (' [' + str(default) + ']: ') if has_default else ':')
    my_input = input()
    if has_default and my_input == '':
        return default
    try:
        return tp(my_input)
    except ValueError:
        print(str(my_input) + ' is not of type ' + str(tp) + ', try again')
        enter_param(name, tp, has_default, default)


def create_cov_gen():
    contract_name = enter_param(name='contract name', tp=str, has_default=True, default='cov')
    cashscript_pragma = enter_param(name='cashscript pragma', tp=str, has_default=True, default='0.4.0')
    miner_fee = enter_param(name='miner fee', tp=int, has_default=True, default=1000)
    intro_comment = enter_param(name='intro_msg comment', tp=str, has_default=True, default='')
    my_cov = cov_gen(contract_name, cashscript_pragma, miner_fee, intro_comment)
    # print(contract_name, cashscript_pragma, str(miner_fee), intro_comment, sep='\n')
    return my_cov


def limit_players():
    pass


def create_function():
    pass


def my_main():
    options = 'could - could key participants \n' \
              'hot - hot key participants'
    init_str = 'Hello, \n' \
               'what restrictions would you like to put on your money in BCH? \n' \
               'your options are: \n\n' + options + '\n\nlets start!\n'

    print(init_str)
    my_cov = create_cov_gen()
    print()

    pass


"""
