#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ViPNet HW1000 Cluster Emulator — FULL v4
Изменения:
  - Команда 'place sticker' для физического обслуживания
  - Auto-enable при логине под admin (после мастера)
"""

import time, sys, os

USER_PASSWORD = "user"
ADMIN_PASSWORD = "admin"
ENABLE_PASSWORD = "admin"

def clear(): os.system('cls' if os.name == 'nt' else 'clear')
def pause(s): time.sleep(s)

BANNER = r"""
╔══════════════════════════════════════════════════════════════╗
║   ViPNet HW1000 Cluster Emulator — FULL v4                    ║
║   'version' — версия, 'help' — команды, 'exit' — выход.       ║
╚══════════════════════════════════════════════════════════════╝
"""

class Node:
    def __init__(self, name):
        self.name = name
        self.state = "passive"
        self.version = "5.4.1"
        self.services = {"mftp": True, "ipdr": True, "failover": True}
        self.enabled = False
        self.usb = False
        self.token = False
        self.eth2 = True
        self.vbe = False
        self.upgraded = False
        self.backup = False
        self.config = False
        self.vpn_saved = False
        self.login_user = "user"
        self.login_password = USER_PASSWORD
        self.powered = True
        self.phase = "normal"
        self.wiz = 0
        self.sticker_placed = False      # наклейка наклеена
        self.cables_marked = False       # кабели промаркированы
        self.photo_committed = False     # фото коммутации

    def prompt(self):
        if self.phase == "wizard": return "Ctrl+C>"
        role = "admin" if self.enabled else "user"
        suf = "#" if self.enabled else ">"
        return f"{role}@{self.name}{suf}"


class Emulator:
    def __init__(self):
        self.n1 = Node("hw1000-node1")
        self.n2 = Node("hw1000-node2")
        self.n2.state = "active"
        self.current = self.n1
        self.photo_n = 0
        self.relogin = False
        self.remote = {self.n1.name: "unknown", self.n2.name: "unknown"}

    def other(self): return self.n2 if self.current is self.n1 else self.n1

    def photo(self, label=None):
        self.photo_n += 1
        print()
        print(f"  📸 [ФОТО #{self.photo_n}] {label or '(ручной скриншот)'}")
        print("     → отправить руководителю работ.")
        print()

    def run(self):
        clear(); print(BANNER)
        self.login(); self.loop()

    def login(self):
        n = self.current
        if not n.powered:
            print(f"{n.name} выключена. Включите её: 'machine start'.")
            return
        if n.phase == "wizard": return
        print(f"Подключение монитора и клавиатуры к {n.name}...")
        pause(0.3); print()
        print(f"{n.name} login: ", end="")
        while True:
            u = input().strip()
            if u == n.login_user: break
            print(f"Login incorrect. Введите '{n.login_user}': ", end="")
        print("Password: ", end="")
        while True:
            p = input().strip()
            if p == n.login_password: break
            print(f"Password incorrect. Введите '{n.login_password}': ", end="")
        print("\nLast login: today on ttyS0\n")
        # Auto-enable при логине под admin
        if n.login_user == "admin":
            n.enabled = True
            print(f"{n.name}: режим администратора включён (#) автоматически.")
        else:
            n.enabled = False

    def loop(self):
        while True:
            if self.relogin:
                self.login(); self.relogin = False
            n = self.current
            if n.phase == "wizard":
                self.wizard(); continue
            if not n.powered:
                print(f"── {n.name} (выключена) ──")
            else:
                print(f"── {n.name} | {n.state} | version {n.version} ──")
            try:
                cmd = input(f"{n.prompt()} ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nВыход."); return
            if not cmd: continue
            if cmd == "exit": print("logout"); return
            self.dispatch(cmd)

    def find_node(self, text):
        t = text.lower()
        if "hw1000-node1" in t or "node1" in t or "node 1" in t:
            return self.n1
        if "hw1000-node2" in t or "node2" in t or "node 2" in t:
            return self.n2
        return None

    def dispatch(self, cmd):
        low = cmd.lower()

        # --- служебные ---
        if low == "help": self.help(); return
        if low == "version": print("FULL v4"); return
        if low == "clear": clear(); return
        if low == "photo": self.photo(); return
        if low == "check": self.check(); return
        if low == "debug":
            n = self.current
            print(f"current={n.name} relogin={self.relogin} phase={n.phase} "
                  f"powered={n.powered} enabled={n.enabled} "
                  f"sticker={n.sticker_placed} cables_marked={n.cables_marked}")
            return

        # --- физические действия ---
        if "connect" in low and ("monitor" in low or "keyboard" in low or "node" in low):
            target = self.find_node(low)
            if target:
                self.current = target
                print(f"  ➡  Монитор/клавиатура подключены к {self.current.name}")
                self.relogin = True
            else:
                print("Укажите ноду: connect node1  или  connect node2")
            return

        if low == "switch":
            self.current = self.other()
            print(f"\n  ➡  Монитор/клавиатура переключены на {self.current.name}")
            self.relogin = True
            pause(0.4); return

        if low == "disconnect eth2":
            self.current.eth2 = False
            print("  🔌 Кабель eth2 отключён."); return
        if low == "connect eth2":
            self.current.eth2 = True
            print("  🔌 Кабель eth2 подключён."); return
        if low == "insert usb":
            self.current.usb = True
            print("USB-накопитель обнаружен: /dev/sdb1 (vfat)"); return
        if low == "remove usb":
            self.current.usb = False
            print("USB-накопитель извлечён."); return
        if low == "insert token":
            self.current.token = True
            print("Токен обнаружен."); return
        if low == "remove token":
            self.current.token = False
            print("Токен извлечён."); return

        if low == "machine halt":
            n = self.current
            n.powered = False
            n.enabled = False
            n.cables_marked = False
            n.sticker_placed = False
            print(f"{n.name}: система остановлена (halt).")
            print("⚠  Нода выключена. Можно маркировать кабели и наклеивать стикер.")
            return

        if low == "machine start":
            n = self.current
            n.powered = True
            print(f"{n.name}: питание подано, загрузка...")
            pause(1.5); self.relogin = True; return

        if low == "reboot":
            print(f"{self.current.name}: перезагрузка...")
            pause(1.5); self.relogin = True; return

        # --- физическое обслуживание (только при выключенной ноде) ---
        if low == "mark cables":
            n = self.current
            if n.powered:
                print("Сначала выключите ноду: 'machine halt'.")
                return
            n.cables_marked = True
            print("  ✅ Кабели промаркированы бирками:")
            print("       PSU, eth0, eth1, eth2 (cluster)")
            self.photo("Маркировка кабелей")
            return

        if low == "place sticker":
            n = self.current
            if n.powered:
                print("Сначала выключите ноду: 'machine halt'.")
                return
            if n.sticker_placed:
                print("Наклейка уже наклеена.")
                return
            print("  🔖 Наклеиваю новую инвентарную наклейку ниже старой...")
            pause(0.5)
            n.sticker_placed = True
            print("  ✅ Наклейка наклеена.")
            self.photo("Новая наклейка с данными ПАК")
            return

        # --- системные ---
        if low == "enable":
            self.cmd_enable(); return
        if low in ("failover show info",
                   "failover show info and version",
                   "failover show active-mac-address"):
            self.cmd_show(low); return
        if low == "failover start passive":
            self.cmd_switch(); return
        if low in ("mftp stop","mftp start","ipdr stop","ipdr start",
                   "failover stop","failover start"):
            self.cmd_service(low); return
        if low == "admin export keys binary-encrypted usb":
            self.cmd_export_keys(); return
        if low == "admin upgrade software usb":
            self.cmd_upgrade(); return
        if low == "vpn config save after_upgrade":
            self.cmd_vpn_save(); return
        if low == "machine backup export usb":
            self.cmd_backup("backup"); return
        if low == "machine config export usb":
            self.cmd_backup("config"); return

        print(f"-sh: {cmd}: command not found")

    # ---------------- system commands ----------------
    def cmd_enable(self):
        n = self.current
        if not n.powered: print("Нода выключена."); return
        if n.enabled: print("Уже в режиме администратора."); return
        print("Type the administrator password:")
        p = input("Password: ").strip()
        if p != ENABLE_PASSWORD:
            print("Admin login failed due to wrong password."); return
        n.enabled = True
        print(f"{n.name}: режим администратора включён (#).")

    def cmd_show(self, low):
        n = self.current
        print(); print(low); print("-" * 55)
        print(f"  Node name      : {n.name}")
        print(f"  Current state  : {n.state}")
        print(f"  Software ver.  : {n.version}")
        print("  Services       :")
        for s, up in n.services.items():
            print(f"     {s:10s} : {'running' if up else 'stopped'}")
        if low == "failover show info":
            o = self.other()
            if not n.eth2: self.remote[o.name] = "unknown"
            else: self.remote[o.name] = o.state
            print(f"  remote         : {self.remote[o.name]}")
        if low == "failover show active-mac-address":
            print(f"  active-mac     : 00:1B:44:11:3A:B7")
        print("-" * 55)

    def cmd_service(self, low):
        n = self.current
        svc, action = low.split()
        if not n.enabled:
            print("Требуется режим администратора ('enable')."); return
        if action == "stop":
            if not n.services[svc]: print(f"{svc} уже остановлена."); return
            n.services[svc] = False
            print(f"Stopping {svc}... OK")
        else:
            if n.services[svc]: print(f"{svc} уже запущена."); return
            n.services[svc] = True
            print(f"Starting {svc}... OK")

    def cmd_switch(self):
        n = self.current; o = self.other()
        if n.state == "active":
            print("Эта нода уже активна."); return
        if n.services["failover"]:
            print("Сначала остановите службу failover: `failover stop`."); return
        if not n.upgraded:
            print("ВНИМАНИЕ: нода ещё не обновлена.")
        n.state = "active"; o.state = "passive"
        print(f"\n  ⚡ Переключение: {n.name} -> ACTIVE, {o.name} -> PASSIVE\n")
        print("  ⚠  Не забудьте: failover start   (на активной ноде)\n")

    def cmd_export_keys(self):
        n = self.current
        if not n.enabled: print("Требуется 'enable'."); return
        if n.vbe: print("Ключи VBE уже выгружены."); return
        if not n.usb:
            print("Insert USB drive with at least 100 MB free space and press Enter")
            print("(вставьте USB командой 'insert usb')"); return
        if not n.token:
            print("⚠  Вставьте токен администратора ('insert token').")
        print("\nExporting VBE keys to USB ...")
        pause(1.2)
        print("Select target partition [1-3] or [q] to abort:")
        ans = input("[1]: ").strip()
        if ans not in ("1", ""):
            print("Aborted."); return
        n.vbe = True
        print("Export completed successfully.")
        print("File: /mnt/sdb1/keys_vbe.bin")
        self.photo("Экспорт ключей VBE")

    def cmd_upgrade(self):
        n = self.current
        if not n.enabled: print("Требуется 'enable'."); return
        if n.upgraded: print("Нода уже обновлена."); return
        if not n.usb:
            print("Insert USB flash drive into empty USB slot and press Enter")
            print("(вставьте USB командой 'insert usb')"); return
        print("\nInsert USB flash drive into empty USB slot and press Enter")
        input("Press Enter ... ")
        print()
        print("Select file for software upgrade:")
        print("  1 — /mnt/tmp/sdb1/hw1000_vip-net_base_x86_64_drv_5.4.2-13381.izh")
        print("  q — cancel")
        c = input("Enter file number [1-x] or [q]: ").strip()
        if c.lower() == "q": print("Upgrade cancelled."); return
        if c != "1": print("Invalid choice."); return

        print("\nStarting local upgrade... upgrade - Melled : 000")
        pause(0.5)
        print("331 Starting sanity check before upgrade ...")
        pause(0.4)
        print("Stopping VPN services...")
        pause(0.3); print("Shutting down failover daemon...")
        pause(0.3); print("Shutting down ViPNet Web GUI service...")
        pause(0.3); print("Shutting down MFTP daemon...")
        pause(0.3); print("Shutting down IpLir...")
        pause(0.3); print("Checking integrity of the upgrade file...")
        for i in range(0, 101, 10):
            sys.stdout.write(f"\r  {i:3d}%"); sys.stdout.flush(); time.sleep(0.1)
        print()
        print("\nThis is hw1000 platform WARNING! You are going to upgrade software to the version 5.")
        print("Downgrade to previous versions is not supported. The saved software configurations will")
        print("be deleted. We strongly recommend to create VBE-backup before proceeding.")
        print()
        ans = input("Do you want to proceed? [Yes/No]: ").strip().lower()
        if ans not in ("yes","y","да"):
            print("Upgrade cancelled."); return
        print("\nInstallation complete. Rebooting...")
        pause(2.0)

        n.version = "5.4.2"
        n.upgraded = True
        n.enabled = False
        n.phase = "wizard"
        n.wiz = 0
        self.relogin = False
        print(f"\n  ✅ {n.name} перезагружена. Запускается мастер настройки.\n")

    def cmd_vpn_save(self):
        n = self.current
        if not n.enabled: print("Требуется 'enable'."); return
        print("Saving VPN configuration after upgrade ...")
        pause(0.7); n.vpn_saved = True
        print("VPN config saved: /etc/vipnet/vpn.cfg")

    def cmd_backup(self, kind):
        n = self.current
        if not n.enabled: print("Требуется 'enable'."); return
        if not n.usb:
            print("Insert USB drive ...")
            print("(вставьте USB командой 'insert usb')"); return
        if kind == "backup":
            if n.backup: print("Backup уже сделан."); return
            print("Exporting machine backup ...")
            pause(0.9); n.backup = True
            print(f"Backup written: /mnt/sdb1/backup_{n.name}.tar.gz")
            self.photo(f"Бэкап машины {n.name}")
        else:
            if n.config: print("Config уже выгружен."); return
            print("Exporting machine config ...")
            pause(0.9); n.config = True
            print(f"Config written: /mnt/sdb1/config_{n.name}.tar.gz")
            self.photo(f"Экспорт конфигурации {n.name}")

    def wizard(self):
        n = self.current
        step = n.wiz
        print()
        if step == 0:
            print("Please select setup wizard operating mode:")
            print("  1 — Restore configuration from backup")
            print("  2 — Manual configuration")
            a = input("[1]: ").strip()
            if a not in ("1",""): print("Выберите 1."); return
            n.wiz = 1
        elif step == 1:
            print("Now you need to install keys or restore configuration from backup.")
            a = input("Do you want to begin? [Yes/no]: ").strip().lower()
            if a not in ("yes","y","да",""): print("Введите y."); return
            n.wiz = 2
        elif step == 2:
            print("Would you like to start installing configuration? [Yes/no]")
            a = input().strip().lower()
            if a not in ("yes","y","да",""): print("Введите y."); return
            n.wiz = 3
        elif step == 3:
            print("Insert USB storage device with DST or VBE file and press Enter.")
            print("Are you using USB or CD storage device? [Yes]")
            a = input().strip()
            if a.lower() == "insert usb":
                n.usb = True
                print("USB-накопитель обнаружен: /dev/sdb1 (vfat)")
                return
            if a.lower() not in ("yes", "y", "да", ""):
                print("Введите 'insert usb' или 'y'.")
                return
            if not n.usb:
                print("⚠  USB не вставлен. Введите 'insert usb'.")
                return
            n.wiz = 4
        elif step == 4:
            print("Mode ID in the appliance initialization file does not match current Node ID.")
            a = input("Change Node ID? [Yes/no]: ").strip().lower()
            if a not in ("yes","y","да",""): print("Введите y."); return
            n.wiz = 5
        elif step == 5:
            print("Restart password setup.")
            p1 = input("Enter new password: ").strip()
            if len(p1) < 4:
                print("Пароль слишком короткий."); return
            p2 = input("Confirm password: ").strip()
            if p1 != p2:
                print("Пароли не совпадают. Повторите.")
                n.wiz = 5; return
            n.login_user = "admin"
            n.login_password = p1
            print("User password successfully checked.")
            n.wiz = 6
        elif step == 6:
            print(f"  ✅ Мастер настройки завершён на {n.name}.")
            print(f"     Логин: admin   Пароль: {n.login_password}")
            print("  ⚠  Не забудьте сделать бэкап:")
            print("       vpn config save after_upgrade")
            print("       machine backup export usb")
            print("       machine config export usb")
            n.phase = "normal"
            n.wiz = 0
            self.relogin = True

    def check(self):
        print(); print("=" * 60)
        print("  СОСТОЯНИЕ КЛАСТЕРА"); print("=" * 60)
        for n in (self.n1, self.n2):
            print(f"\n[{n.name}]  state={n.state}  version={n.version}  "
                  f"eth2={'on' if n.eth2 else 'OFF'}")
            print(f"  vbe={n.vbe}  upgraded={n.upgraded}  "
                  f"vpn_saved={n.vpn_saved}  backup={n.backup}  config={n.config}")
            print(f"  sticker={n.sticker_placed}  cables_marked={n.cables_marked}")
            print("  services: " + ", ".join(
                f"{k}={'up' if v else 'DOWN'}" for k, v in n.services.items()))
        active = [x for x in (self.n1, self.n2) if x.state == "active"]
        if len(active) != 1:
            print("\n⚠  Должна быть РОВНО ОДНА активная нода!")
        else:
            a = active[0]
            if not a.services["failover"]:
                print(f"\n⚠  На активной ноде {a.name} failover ОСТАНОВЛЕН.")
        print()

    def help(self):
        print("""
=== ЭМУЛЯТОР ===
  version                           — версия эмулятора
  connect node1 / connect node2     — подключить монитор к ноде
  connect monitor keyboard <node>   — то же самое (длинная форма)
  switch                            — переключить на другую ноду
  disconnect eth2 / connect eth2    — кабель кластерной синхронизации
  insert usb / remove usb           — USB
  insert token / remove token       — токен администратора
  machine halt / machine start      — выключить/включить ноду
  reboot                            — перезагрузить ноду
  mark cables                       — промаркировать кабели (при выключенной ноде)
  place sticker                     — наклеить новую наклейку (при выключенной ноде)
  photo                             — скриншот
  check                             — состояние кластера
  debug                             — отладка
  clear / exit

=== СИСТЕМА ===
  enable
  failover show info
  failover show info and version
  failover show active-mac-address
  mftp stop / mftp start
  ipdr stop / ipdr start
  failover stop / failover start / failover start passive
  admin export keys binary-encrypted usb
  admin upgrade software usb
  vpn config save after_upgrade
  machine backup export usb
  machine config export usb
""")

if __name__ == "__main__":
    Emulator().run()