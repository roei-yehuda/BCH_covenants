# this is the command line interface for our covenant generator
from covenant_generator import *

from termcolor import colored

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
        self.cov_init_args = copy.deepcopy(cov_gen.cov_init_kwargs_d)   # {'contract_name':'cov', 'cashScript_pragma':'0.4.0', 'miner_fee':1000, 'intro_comment':''}
        self.funcs_list = []

        # global commands - these are commands that the user may input at any point
        self.globals = ['-i', '-h', '-exit', '-clear']

        self.run()


    def run(self):
        # print intro:
        intro = "intro msg"
        print(colored(intro, 'yellow'))
        # set init
        # in_between_fns

    def in_between_fns(self):
        pass

    def set_init(self):
        pass

    def parse_input(self, name='', tp=str, default=None, i_msg='Sorry, no more information is provided. You can always try -h'):

        print('enter {}{}: '.format(name, '' if default is None else ' [{}]'.format(str(default))))
        my_input = input()

        if my_input in self.globals:
            if my_input == '-i':
                print(i_msg)
            # if ... # todo

        if default is not None and my_input == '':
            return default

        try:
            return tp(my_input)
        except ValueError:
            print(colored('Oops! {} is not of type {}, try again:'.format(str(my_input), str(tp)), 'red'))
            self.parse_input(name, tp, default)

    def _h(self):
        pass

    def _exit(self):
        pass

    def _clear(self):
        pass

    def add_fn(self):

        fn_name = ''
        fn_desc = ''
        fn_restrictions = []

        def add_restriction():
            Rs = ['operators', 'recipients', 'amount', 'time']
            Rs_args = [copy.deepcopy(cov_fn.restrict_operators_kwargs_d),
                       copy.deepcopy(cov_fn.restrict_recipients_kwargs_d),
                       copy.deepcopy(cov_fn.restrict_amount_kwargs_d),
                       copy.deepcopy(cov_fn.restrict_time_kwargs_d)]

            r = ''
            # r_args_d = Rs_args[?]

            # set r, r_args_d   # todo

            fn_restrictions.append((r, r_d))

        # add restrictions in a while loop # todo

        self.funcs_list.append((fn_name, fn_desc, fn_restrictions))


    def generate_cov(self):
        pass


"""
Avigail's tasks:
- tx.time vs tx.age
- how to print IN COLOR in the cmd
- add an option to remove fn
"""






def enter_param(name='', tp=str, has_default=True, default=None):
    print('enter ' + name + (' ['+str(default)+']: ') if has_default else ':')
    my_input = input()
    if has_default and my_input=='':
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