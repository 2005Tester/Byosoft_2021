import sys
from Core import TcExecutor

cli = TcExecutor.CliParse()

if cli.get_project() == "ICX2P":
    from ICX2P import SutConfig as cfg
    from ICX2P import Main as script
elif cli.get_project() == "Pangea":
    from Pangea import SutConfig as cfg
    from Pangea import Main as script
else:
    print("Invalid project name.")
    sys.exit()


def run_test():
    type = cli.get_execution_type()
    post_result = cli.get_post()
    test = TcExecutor.RunTest(cfg, script, type, post_result)
    test.run()


if __name__ == '__main__':
    run_test()
