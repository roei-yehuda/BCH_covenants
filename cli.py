# this is the command line interface for our covenant generator
from covenant_generator import cov_gen
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
    my_main()



"""
start
"""