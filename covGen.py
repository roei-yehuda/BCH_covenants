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
