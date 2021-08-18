from Core import SutInit
from Core import TcExecutor
from Core import var


def main():
    cli = TcExecutor.CliParse()
    prj_init = SutInit.ProjectInit(cli)
    cfg, script, resources = prj_init.load_project()
    type = cli.get_execution_type()
    post_result = cli.get_post()
    test = TcExecutor.RunTest(cfg, script, type, post_result)
    SutInit.SutInit(var.get('project'), resources)
    test.run()


if __name__ == '__main__':
    main()
