import time
import requests

"""
Fusion BMC Web Request Module
"""


requests.packages.urllib3.disable_warnings()


class BmcWeb:
    def __init__(self, ip, user, password):
        self.host = f"https://{ip}"
        self.user = user
        self.password = password
        self.session = None
        self.headers = None
        self.session_id = None

    def web_login(self):
        try:
            self.session = requests.Session()
            login_data = {"UserName": self.user, "Password": self.password, "Type": "Local", "Domain": "LocaliBMC"}
            _login_session = self.session.post(url=f"{self.host}/UI/Rest/Login", json=login_data, verify=False)
            self.session.post(url=f"{self.host}/UI/Rest/KeepAlive", json={"Mode": "Activate"})
            _access_check = self.session.get(url=f"{self.host}/UI/Rest/AccessMgnt/RightManagement").status_code
            token = _login_session.headers.get("Token")
            cookie = self.session.cookies.get("SessionId")
            self.session_id = _login_session.json()["Session"]["SessionID"]
            self.headers = {"Cookie": f"SessionId = {cookie}", "X-CSRF-Token": token}
            return _access_check == 200
        except Exception as e:
            print("## [Exception]", e)

    def web_logout(self):
        try:
            _del_url = f"{self.host}/UI/Rest/Sessions/{self.session_id}"
            _del_session = self.session.delete(url=_del_url, verify=False, headers=self.headers).status_code
            self.session = None
            self.headers = None
            self.session_id = None
            return _del_session == 200
        except Exception as e:
            print("## [Exception]", e)

    def web_post(self, url: str, data: dict):
        if self.web_login():
            _post_result = self.session.post(url=f"{self.host}{url}", json=data, headers=self.headers).status_code
            self.web_logout()
            return _post_result == 200

    def web_patch(self, url: str, data: dict):
        if self.web_login():
            _patch_result = self.session.patch(url=f"{self.host}{url}", json=data, headers=self.headers).status_code
            self.web_logout()
            return _patch_result == 200

    def web_get(self, url: str):
        if self.web_login():
            try:
                _get_result = self.session.get(url=f"{self.host}{url}", headers=self.headers).json()
            except Exception:
                _get_result = {}
            self.web_logout()
            return _get_result

    def blackbox_switch(self, enable=True):
        _blackbox_url = f"/UI/Rest/Maintenance/SystemDiagnostic"
        _status, _message = (True, "Enable") if enable else (False, "Disable")
        print(f"## Set Blackbox to \"{_message}\"")
        return self.web_patch(url=_blackbox_url, data={"BlackBoxEnabled": _status, "PCIeInterfaceEnabled": _status})

    def power_switch(self, button):
        power_state = { "power_off":"GracefulShutdown",
                        "force_off": "ForceOff",
                        "power_on": "On",
                        "reset": "ForceRestart",
                        "power_cycle": "ForcePowerCycle" }
        if button not in power_state.keys():
            raise AttributeError(f"## {button} not in {list(power_state.values())}")
        _power_switch_url = "/UI/Rest/System/PowerControl"
        print(f"## Press power button from web: [{button}]")
        return self.web_post(url=_power_switch_url, data={"OperateType":power_state[button]})

