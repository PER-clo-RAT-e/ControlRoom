import subprocess
from modules.instancer import manager

import threading
import modules.instancer as instancer

from mcrcon import MCRcon
import time
import os
import readline
from datetime import timedelta

assert instancer.log is not None
log = instancer.log
flags = instancer.flags

class ServerManager:
    @manager
    def __init__(self) -> None:
        self.run = True
        self.stop = False

        self.players = {}

        self.server_cmd = Cmd()

        self.uptime_str = ''

    readline.parse_and_bind("tab: complete")
    readline.set_history_length(100)

    def checkup(self):
        while self.run:
            if flags.get('POWEROFF') and flags.get('LETHALTEMP'):
                log.on_kill("CRITICAL: Got the POWEROFF flag! Emergency shutdown...")
                self._cmdline('stop mrg')

            elif flags.get('LETHALTEMP'):
                log.warn('Lethal temperature detected!')

            if self.stop:
                if not flags.get('HIGHTEMP'):
                    subprocess.run(["java", "-Xmx4G", "-Xms4G", "-jar", "server.jar", "nogui"])
                    self.stop = False

            
            start = time.time()
            uptime_seconds = int(time.time() - start)
            self.uptime_str = str(timedelta(seconds=uptime_seconds))

            time.sleep(0.3)

    def start(self):
        log.info("ServerManager: Console active. Type commands below.")

        threading.Thread(target=self.checkup).start()

        os.system('clear')

        print('Welcome to GenesisMC Control Room.')
        print('         Made by PER-clo-RAT-e for PER-clo-RAT-e')

        while self.run:
            if self.stop:
                time.sleep(0.3)
                continue
            uArg = input("> ")
            print('\033[J', end='')
            if uArg:
                self._cmdline(uArg)


    def _eval_things(self, things):
        tmp_arr = []
        lists = []
        leftover = []
        offset = 0
        for thing in things:
            match thing:
                case '[':
                    tmp_arr.append([])
                case ']':
                    offset += 1
                case _:
                    tmp_arr[offset].append(thing)

        for thing in tmp_arr:
            if isinstance(thing, list):
                lists.append(thing)
            else:
                leftover.append(thing)
        
        return lists, leftover

    def stop_server(self):
        self.server_cmd.title('@a', '[{"text":"По ","color":"red"},{"text":"какой-то ","color":"#f83a3a"},{"text":"причине ","color":"#f33535"}]', '[{"text":"сервер","color":"#e92b2b"},{"text":"закрывается.","color":"#e42626"}]')
        for speed in [20, 15, 10, 5, 2, 1]:
            self.server_cmd.set_tps(speed)
            time.sleep(1)


        self.server_cmd.sound('iron_door.close')
        self.server_cmd.kick('[PRCLRT]-EVERYONE', 'Ваш трудодень завершён. Возвращайтесь завтра.')
        time.sleep(1)
        self.server_cmd.stop()
        self.server_cmd.rcon_disconnect()
        self.run = False

    def _cmdline(self, cmd):
        cmd = cmd.split(' ')

        if len(cmd) == 1:
            match cmd[0]:
                case 'stop':
                    self.stop_server()
                case 'restart':
                    typo = input('?> ')
                    with open('/home/chlorik/projects/SERVERS/ALIVE/ctrl_room/reboot_flag', 'w', encoding='utf-8') as f:
                        f.write(typo if not None else 'full')

                    self.stop_server()

                case 'stats':
                    try:
                        import psutil

                        
                        fmt = {True: " YES ", False: " NO  "}

                        while self.run:
                        
                            INFO = f"""
╔══════════════════════════════════╗
║:      PER-clo-RAT-e Server      :║
╚══════════════════════════════════╝
{self.uptime_str:^36}
TEMPERATURE:    {psutil.sensors_temperatures()['coretemp'][0].current}
FREQ:           {psutil.cpu_freq().current / 1000:4.2f}GHz
LifePower:      {instancer.lp:4.2f}
FLAGS:          HIGHTEMP:   {fmt[flags["HIGHTEMP"]]}  |  HIGHTEMP++: {fmt[flags["HIGHTEMP++"]]}
                LETHALTEMP: {fmt[flags["LETHALTEMP"]]}  |  POWEROFF:   {fmt[flags["POWEROFF"]]}
""".strip()
                            print(INFO, end='\n\033[9A')
                            time.sleep(0.3)

                    except KeyboardInterrupt:
                        print('\033[J', end='')
                        return

                    except Exception as e:
                        log.error('CMDLine exception occured:', str(e))

                case 'clear':
                    os.system('clear')
                    
        
        else:
            match cmd[0]:
                case 'say':
                    self.server_cmd.say(f'Родина напоминает: `{" ".join(cmd[1:])}`')
                case 'kick':
                    self.server_cmd.kick(self._eval_things(cmd[1:]))
                case 'title':
                    self.server_cmd.title(*cmd[1:])
                case 'stop':
                    if cmd[1] == 'mrg':
                        self.server_cmd.say('Дабы вы смогли нас увидеть в следующий раз, мы вынуждены становить этот сервер.\nПричина: перегрев...\nкабум')
                        self.stop_server()
                    else:
                        if input('Emergency stop?').lower() in ['y', 'yes']:
                            self.server_cmd.say('Дабы вы смогли нас увидеть в следующий раз, мы вынуждены становить этот сервер.\nПричина: перегрев...\nкабум')

                            self.stop_server()





class Cmd:
    def __init__(self) -> None:
        self.rcon_adress = "127.0.0.1"
        self.rcon_port = 25575
        self.rcon_pass = "USERSS"

        self.server = MCRcon(self.rcon_adress, self.rcon_pass, port=self.rcon_port)
        self.connect(0)

    def connect(self, attempt):
        if attempt < 5:
            try:
                self.server.connect()

            except ConnectionRefusedError:
                time.sleep(5)
                self.connect(attempt + 1)

            except Exception as e:
                log.error('RCON.connect exception:', str(e))


    def rcon_disconnect(self):
        try:
            self.server.disconnect()

        except Exception as e:
            log.error('RCON.disconnect exception:', str(e))


    def say(self, text):
        result = self.server.command(f'say {"".join(text)}')
        print(result)
        log.info(f'RCON: `say {text}`', result)

    def set_tps(self, tps=20):
        result = self.server.command(f'tick rate {tps}')
        log.info(f'RCON: TPS set to {tps}', result)

    def stop(self):
        result = self.server.command('stop')
        print(result)
        log.info('RCON: `stop`', result)

    def title(self, player, title, subtitle):
        result = self.server.command(f'title {player} subtitle {subtitle}')
        print(result)
        log.info(f'RCON: `title {player} subtitle {subtitle}`', result)

        result = self.server.command(f'title {player} title {title}')
        print(result)
        log.info(f'RCON: `title {player} title {title}`', result)

    def sound(self, sound):
        result = self.server.command(f'playsound {sound}')
        print(result)
        log.info(f'RCON: `playsound {sound}`', result)

    def kick(self, player, desc="Наверное, Вы слишком много говорили, друг мой..."):
        match player:
            case '[PRCLRT]-EVERYONE':
                player = '@a'
            case _:
                if isinstance(player, (list, tuple)):
                    for pl in player:
                        self.kick(pl, desc)
                    return

        result = self.server.command(f'kick {player} {desc}')
        print(result)
        log.info(f'RCON: `kick {player} {desc}`', result)
