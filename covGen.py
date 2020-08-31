##  This file is part of the covGen project which can be found at https://github.com/roei-yehuda/BCH_covenants
##  This project was a created for a university course, and then made publicly available.
##  Introduction to Cryptocurrencies, course #67513, Hebrew University Jerusalem Israel, Aug 2020.
##  Avigail Suna; avigail.suna@mail.huji.ac.il
##  Roei Yehuda; roei.yehuda@mail.huji.ac.il


"""
This is the main file to use the covGen CLI
"""

from cli import *

if __name__ == '__main__':

    cli = cov_gen_CLI()
    do_create_contract = cli.run()
    if do_create_contract:
        create_cli = create_contract_CLI()
        create_cli.run()
    else:
        use_cli = use_contract_CLI()
        use_cli.run()
