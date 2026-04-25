from os import stat_result
import threading
import modules.instancer as instancer

# Инициализация
from modules.logger import Logger
Logger()

from modules.managers.safety_manager import SafetyManager
safety = SafetyManager()

from modules.managers.server_manager import ServerManager
server = ServerManager()

#from modules.managers.graph_manager import GraphManager
#graph = GraphManager()

assert instancer.log is not None
log = instancer.log

safety_thread = threading.Thread(target=safety.cycle, daemon=True)
#stats_thread = threading.Thread(target=graph.run_dashboard, daemon=True)

def main():
    log.info("System: Starting ControlRoom...")
    
    safety_thread.start()
    #stats_thread.start()
    
    try:
        server.start()
    except KeyboardInterrupt:
        log.info("System: Manual stop requested.")
    finally:
        safety.restore_and_exit()
        log.info("System: Safety protocols finished. Bye.")

if __name__ == "__main__":
    main()
