from Report import ReportGen
from Nvwa.BaseLib import Update, SetUpLib
from Nvwa.Config import SutConfig
from Nvwa.Config.PlatConfig import Msg


def update_debug_bios(branch):
    tc = ('001', '[TC001]Update Debug BIOS', 'Update Debug BIOS')
    result = ReportGen.LogHeaderResult(tc)
    img = Update.get_test_image(SutConfig.Env.LOG_DIR, branch, 'debug-build')
