# this is the command line interface for our covenant generator
from .covenant_generator import cov_gen, cov_fn
from termcolor import colored
import copy


# import click

# @click.group()
# @click.version_option()
# def cli():
#     pass #Entry Point
#
# @cli.group()
# @click.pass_context
# def cloudflare(ctx):
#     pass
#
# @click.option('--contract_name', prompt=True, default='cov', show_default=True)
# @click.option('--cashscript_pragma', prompt=True, default='0.4.0', show_default=True)
# @click.option('--miner_fee', prompt=True, default=1000, show_default=True)
# @click.option('--intro_comment', prompt=True, default='', show_default=True)
#
# @click.command
# def create_cov_gen(contract_name, cashscript_pragma, miner_fee, intro_comment):
#     my_cov = cov_gen(contract_name, cashscript_pragma, miner_fee, intro_comment)
#     print(contract_name, cashscript_pragma, miner_fee, intro_comment, sep='\n')
#     print(my_cov.contract_name)
#
# @click.command
# def my_main():
#     options = 'could - could key participants \n' \
#               'hot - hot key participants'
#     init_str = 'Hello, \n' \
#                'what restrictions would you like to put on your money in BCH? \n' \
#                'your options are: \n\n' + options + '\n\nlets start!\n'
#
#     print(init_str)
#     create_cov_gen()


class cov_gen_CLI():

    def __init__(self):

        # creating covenant
        self.cov_init_args = copy.deepcopy(
            cov_gen.cov_init_kwargs_d)  # {'contract_name':'cov', 'cashScript_pragma':'0.4.0', 'miner_fee':1000, 'intro_comment':''}
        self.funcs_list = []

        # global commands - these are commands that the user may input at any point
        self.globals = ['-i', '-h', '-exit', '-clear']

        self.run()

    def print_comment(self, comment: str):
        print(colored(comment, 'yellow'))

    def print_error(self, err: str):
        print(colored(err, 'red'))

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
        self.print_comment(intro)
        # set init
        # in_between_fns

    def in_between_fns(self):
        pass

    def set_init(self):
        pass

    def parse_input(self, name='', tp=str, default=None, choices=None,
                    i_msg='Sorry, no more information is provided. You can always try -h'):

        print('enter {}{}: '.format(name, '' if default is None else ' [{}]'.format(str(default))))
        my_input = input()

        # help and global functions
        if my_input in self.globals:
            if my_input == '-i':
                self.print_comment(i_msg)
                my_input = input()
            # if ... # todo

        # no input entry
        if my_input == '':
            if default is not None:
                return default
            else:
                self.parse_input(name, tp, default)

        # wrong input
        try:
            my_input_in_tp = tp(my_input)
            if choices is not None:
                if my_input_in_tp in choices:
                    return my_input_in_tp
                else:
                    self.print_error('Oops! wrong input, your options are {}:'.format(str(choices)))
                    self.parse_input(name, tp, default)
            return my_input_in_tp
        except ValueError:
            self.print_error('Oops! {} is not of type {}, try again:'.format(str(my_input), str(tp)))
            self.parse_input(name, tp, default)

    def _h(self):
        """ help information global """
        pass

    def _exit(self):
        """ exit the program """
        pass

    def _clear(self):
        """ restart, clear all """
        pass

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

        def get_y_n(comment: str):
            self.print_comment(comment)
            return self.parse_input(name='y or n', tp=str, default=None, choices=['y', 'n'],
                                    i_msg='{}}? type y or n and then enter)'.format(comment))

        r_d['require_recipient_sig'] = get_y_n('would you like the tx to only be signed by one of the pkh recipients?') == 'y'
        r_d['include_all'] = get_y_n('would you like the funds to be distributed to all?') == 'y'

        return r_d

    def fn_rs_amount(self):
        """ restrict the amount that can be pulled in a transaction """
        r_d = copy.deepcopy(cov_fn.restrict_amount_kwargs_d)

        def limit_amount_y_n(whom:str):
            self.print_comment('would you like to limit the amount per {}}? (y/n)'.format(whom))
            return self.parse_input(name='y or n', tp=str, default=None, choices=['y', 'n'],
                                    i_msg='would you like to limit the amount per {}}? type y or n and then enter)'.format(whom))

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

        r_d_min_max = self.parse_input(name='min or max time window', tp=str, default=None, choices=['min', 'max'],
                                       i_msg='pick a time limitation, before a certain time passes (min), or after (max)')
        r_d[r_d_min_max] = self.parse_input(name='time limitation [number][time stamp]', tp=str, default=None,
                                            i_msg='pick a time limitation a number and then a time stamp, for example "30 days"')

        r_d_typ_lim = self.parse_input(name='type of time limit', tp=str, default=None, choices=['time', 'age'],
                                       i_msg='pick a type of time limitation, time - absolute, age - relative')
        r_d['{}_limit'.format(r_d_typ_lim)] = True
        return r_d

    def add_fn(self):
        self.print_comment('pick function name')
        fn_name = self.parse_input(name='function name', tp=str, default=None,
                                   i_msg='write a name for your function and then click enter:')
        fn_desc = ''
        fn_restrictions = []

        def add_restriction():
            Rs = ['-o- operators', '-r- recipients', '-a- amount', '-t- time']
            restrict_txt = 'which restriction(s) would you like to apply?\n' \
                           'your options are:\n{}' \
                           '\ntype the first letter of one option and then click enter'.format('\n'.join(Rs))
            self.print_comment(restrict_txt)
            r = self.parse_input(name='restriction', tp=str, default=None, choices=['o', 'r', 'a', 't'],
                                 i_msg='type the first letter of one option and then click enter:\n{}'.format('\n'.join(Rs)))
            if r == 'o':
                r_args_d = self.fn_rs_operators()
            elif r == 'r':
                r_args_d = self.fn_rs_recipients()
            elif r == 'a':
                r_args_d = self.fn_rs_amount()
            elif r == 't':
                r_args_d = self.fn_rs_time()

            # r = ''
            # r_args_d = Rs_args[?]

            # set r, r_args_d   # todo
            fn_restrictions.append((r, r_args_d))

        # add restrictions in a while loop # todo

        self.funcs_list.append((fn_name, fn_desc, fn_restrictions))

    def generate_cov(self):
        pass


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
