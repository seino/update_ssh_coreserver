import csv
import datetime
import requests
import pymsteams
from typing import List, Dict
from functools import lru_cache
from config import HOOK_URL, VALUESERVER_CSV, CORESERVER_CSV

# 定数
VALUE_SERVER_URL = "https://{}.valueserver.jp/cp/admin.cgi?telnet=1"
CORE_SERVER_URL = "https://api.coreserver.jp/v1/tool/ssh_ip_allow"
IP_CHECK_URL = "http://dyn.value-domain.com/cgi-bin/dyn.fcg?ip"
SSH_KEYWORD = "SSH登録"
ENCODING = "shift_jis"

class TeamsNotifier:
    def __init__(self, hook_url: str):
        self.hook_url = hook_url

    def send_notification(self, title: str, text: str) -> None:
        myTeamsMessage = pymsteams.connectorcard(self.hook_url)
        myTeamsMessage.title(title)
        myTeamsMessage.text(text)
        myTeamsMessage.send()

class SSHUpdater:
    def __init__(self, csv_file: str, server_type: str, teams_notifier: TeamsNotifier):
        self.csv_file = csv_file
        self.server_type = server_type
        self.teams_notifier = teams_notifier

    @lru_cache(maxsize=1)
    def get_ip(self) -> str:
        response = requests.get(IP_CHECK_URL)
        response.raise_for_status()
        return response.text.strip()

    def update_ssh_connections(self) -> None:
        rows = self._import_csv()
        for row in rows:
            if self.server_type == "coreserver":
                self._update_coreserver(*row)
            else:
                self._update_valueserver(*row)

        self._notify_update()

    def _import_csv(self) -> List[List[str]]:
        with open(self.csv_file, "r") as f:
            return list(csv.reader(f))

    def _update_valueserver(self, url: str, id: str, password: str) -> None:
        payload = {
            "id": id,
            "pass": password,
            "remote_host": self.get_ip(),
            "ssh2": SSH_KEYWORD.encode(ENCODING),
        }
        response = requests.post(VALUE_SERVER_URL.format(url), data=payload)
        response.raise_for_status()

    def _update_coreserver(self, url: str, id: str, api_key: str) -> None:
        payload = {
            "account": id,
            "server_name": f"{url}.coreserver.jp",
            "api_secret_key": api_key,
            "param[addr]": self.get_ip(),
        }
        response = requests.post(CORE_SERVER_URL, data=payload)
        response.raise_for_status()

    def _notify_update(self) -> None:
        title = f"{self.server_type} Update SSH connection"
        text = "SSH接続 IP許可登録を更新しました"
        self.teams_notifier.send_notification(title, text)
        date = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        print(f'{date}: {title}')

def main():
    teams_notifier = TeamsNotifier(hook_url=TEAMS_WEBHOOK_URL)

    valueserver_updater = SSHUpdater(VALUESERVER_CSV, "valueserver", teams_notifier)
    coreserver_updater = SSHUpdater(CORESERVER_CSV, "coreserver", teams_notifier)

    valueserver_updater.update_ssh_connections()
    coreserver_updater.update_ssh_connections()

if __name__ == "__main__":
    main()