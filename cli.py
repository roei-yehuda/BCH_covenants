# this is the command line interface for our covenant generator
from covenant_generator import *
from termcolor import colored
import copy
import sys


# print colors:
REG = 'white'
ERR = 'red'
IN = 'yellow'
HIGHLIGHT = 'green'



class cov_gen_CLI():

    intro = "Welcome to the BCH covenant app!" \
            "vds" \
            ""


    def __init__(self):

        # variables for the generation of cov_gen
        self.cov_init_args = copy.deepcopy(cov_gen.cov_init_kwargs_d)   # {'contract_name':'cov', 'cashScript_pragma':'0.4.0', 'miner_fee':1000, 'intro_comment':''}
        self.funcs_list = []

        # global commands - the user may input these commands at any point
        self.globals = ['-i', '-h', '-exit', '-clear']

        self.run()

    # def print_comment(self, comment: str):
    #     print(colored(comment, 'yellow'))
    #
    # def print_error(self, err: str):
    #     print(colored(err, 'red'))

    def print(self, s: str, c: str=None):
        if c is not None:
            print(colored(s, c))
        else:
            print(colored(s, REG))

    def run(self):
        # print intro:
        # Rs = ['-o- operators', '-r- recipients', '-a- amount', '-t- time']
        options = ['operators - could key participants ',
                   'recipients - hot key participants',
                   'amount - the max amount that can be drawn at any transaction',
                   'time - waiting period in which the transaction can be evoked']
        intro = 'Hello, \n' \
                'what restrictions would you like to put on your money in BCH? \n' \
                'your options are: \n\n{}\n\nlets start!\n'.format('\n'.join(options))
        self.print(intro)
        # set init
        self.set_init()
        # in_between_fns
        self.in_between_fns()
        # generate cov
        self.generate_cov()

    def set_init(self):
        # {'contract_name':'cov', 'cashScript_pragma':'0.4.0', 'miner_fee':1000, 'intro_comment':''}
        self.print('name your contract:', IN)
        self.cov_init_args['contract_name'] = self.parse_input(name='contract name with no spaces', tp=str,
                                                               default='cov', choices=None,
                                                               i_msg='pick a contract name with no spaces')
        self.print('which cashScript_pragma would you like to use?', IN)
        self.cov_init_args['cashScript_pragma'] = self.parse_input(name='cashScript pragma', tp=str,
                                                                   default='0.4.0', choices=None,
                                                                   i_msg='from which pragma would you like to run')
        self.print('miner fee for deployment, a two low fee results in your contract not being excepted', IN)
        self.cov_init_args['miner_fee'] = self.parse_input(name='miner fee', tp=str,
                                                           default=1000, choices=None,
                                                           i_msg='miner fee for deploying the contract')
        self.print("if you'd like to enter a comment do so now, otherwise just press enter", IN)
        self.cov_init_args['intro_comment'] = self.parse_input(name='intro comment', tp=str, default='', choices=None,
                                                               i_msg='what comment would you like to enter?')
        return

    def in_between_fns(self):
        # add functions in a while loop
        create_f = self._y_n_question('would you like to add a function?') == 'y'
        while create_f:
            self.add_fn()
            create_f = self._y_n_question('would you like to add another function?') == 'y'

    def parse_input(self, name='', tp=str, default=None, choices=None,
                    i_msg='Sorry, no more information is provided. You can always try -h'):

        print('enter {}{}: '.format(name, '' if default is None else ' [{}]'.format(str(default))))
        my_input = input()

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
            self.parse_input(name, tp, default, choices, i_msg)

        # no input entry
        if my_input == '':
            if default is not None:
                return default
            else:
                self.parse_input(name, tp, default, choices, i_msg)

        # wrong input
        try:
            my_input_in_tp = tp(my_input)
            if choices is not None:
                if my_input_in_tp in choices:
                    return my_input_in_tp
                else:
                    self.print('Oops! wrong input, your options are {}:'.format(str(choices)), ERR)
                    self.parse_input(name, tp, default, choices, i_msg)
            return my_input_in_tp
        except ValueError:
            self.print('Oops! {} is not of type {}, try again:'.format(str(my_input), str(tp)), ERR)
            self.parse_input(name, tp, default, choices, i_msg)

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
        self.print(question, IN)
        return self.parse_input(name='y or n', tp=str, default=None, choices=['y', 'n'],
                                i_msg='{}? type y or n and then enter)'.format(question))

    def fn_rs_operators(self):
        """ restrict operators """
        r_d = copy.deepcopy(cov_fn.restrict_operators_kwargs_d)
        r_d['n'] = self.parse_input(name='number of desired operators', tp=int, default=1,
                                    i_msg='type the number of desired operators and then click enter:')
        return r_d

    def fn_rs_recipients(self):
        """ restrict recipients """
        r_d = copy.deepcopy(cov_fn.restrict_recipients_kwargs_d)
        r_d['n_PKH'] = self.parse_input(name='number of desired recipients (P2PKH)', tp=int, default=1,
                                        i_msg='type the number of desired recipients and then click enter:')

        r_d['n_SH'] = self.parse_input(name='number of desired contract recipients (P2SH)', tp=int, default=0,
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
            r_d['max_amount_per_tx'] = self.parse_input(name='amount limit per transaction', tp=int, default=None,
                                                        i_msg='pic a transaction limit, must be an integer')
        if limit_amount_y_n('recipient') == 'y':
            r_d['max_amount_per_recipient'] = self.parse_input(name='amount limit per recipient', tp=int, default=None,
                                                               i_msg='pic a limit per recipient, must be an integer')
        return r_d

    def fn_rs_time(self):
        """ create a time window for cancellation """
        r_d = copy.deepcopy(cov_fn.restrict_time_kwargs_d)
        # todo: fix
        r_d_min_max = self.parse_input(name='min or max time window', tp=str, default=None, choices=['min', 'max'],
                                       i_msg='pick a time limitation, before a certain time passes (min), or after (max)')
        r_d[r_d_min_max] = self.parse_input(name='time limitation [number][time stamp]', tp=str, default=None,
                                            i_msg='pick a time limitation a number and then a time stamp, for example "30 days"')
        self.print('which type of time limit would you like to use? time or age?', IN)
        r_d_typ_lim = self.parse_input(name='type of time limit', tp=str, default=None, choices=['time', 'age'],
                                       i_msg='pick a type of time limitation, time - absolute, age - relative')
        r_d['{}_limit'.format(r_d_typ_lim)] = True
        return r_d

    def add_fn(self):
        self.print('pick function name - No spaces', IN)
        fn_name = self.parse_input(name='function name', tp=str, default=None,
                                   i_msg='write a name for your function and then click enter:')
        self.print('enter function description', IN)
        fn_desc = self.parse_input(name='function description', tp=str, default=None,
                                   i_msg='write a description for your function and then click enter:')

        fn_restrictions = []

        def add_restriction():
            Rs = ['-o- operators', '-r- recipients', '-a- amount', '-t- time']
            restrict_txt = 'which restriction(s) would you like to apply?\n' \
                           'your options are:\n{}' \
                           '\ntype the first letter of one option and then click enter'.format('\n'.join(Rs))
            self.print(restrict_txt, IN)
            r = self.parse_input(name='restriction', tp=str, default=None, choices=['o', 'r', 'a', 't'],
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
        create_f = self._y_n_question('would you like to add a restriction?') == 'y'
        while create_f:
            add_restriction()
            create_f = self._y_n_question('would you like to add a restriction?') == 'y'

        self.funcs_list.append((fn_name, fn_desc, fn_restrictions))

    def generate_cov(self):
        cg = cov_gen(**self.cov_init_args)
        cg.build_from_fn_list(self.funcs_list)
        print(cg.get_script())
        return cg


"""
Avigail's tasks:
- tx.time vs tx.age
- add an option to remove fn
"""


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
    intro_comment = enter_param(name='intro comment', tp=str, has_default=True, default='')
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


if __name__ == '__main__':
    # my_main()

    cov_gen_CLI()

"""
start
"""
