import sys
from Core import var
from Core import TcExecutor

cli = TcExecutor.CliParse()

if cli.get_project() == "icx2p":
    from ICX2P.Config import SutConfig as cfg
    from ICX2P import Main as script
    var.set('project', 'ICX2P')
    
elif cli.get_project() == "pangea":
    from Pangea import SutConfig as cfg
    from Pangea import Main as script

elif cli.get_project() == "moc25":
    from Moc25 import SutConfig as cfg
    from Moc25 import Main as script
    var.set('project', 'Moc25')

elif cli.get_project() == "hygon":
    from Hygon.Config import SutConfig as cfg
    from Hygon import Main as script
    var.set('project', 'Hygon')

elif cli.get_project() == "tce":
    from TCE.Config import SutConfig as cfg
    from TCE import Main as script

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
