#!/bin/bash

cd "$(dirname "$0")"

if [ -z "$TMUX" ]; then
    echo "No TMUX session found. Exit."
    exit 1
fi

REBOOT_FLAG="./reboot_flag"
UPDATE_FLAG="./update_flag"

rm -f "$REBOOT_FLAG"

if [[ -f "./afterreboot_flag" ]]; then
    echo "Afterreboot state. No need of playit.gg"

    rm -f "./afterreboot_flag"
else
    echo "Starting playit.gg tunnel in a new window..."
    tmux new-window -n "Playit" "playit; echo 'Tunnel stopped. Press enter...'; read"

    echo $! > "./playit.pid"

fi


echo "Starting Minecraft Server..."
tmux new-window -n "Minecraft" "java -Xms2048M -Xmx2048M -XX:+AlwaysPreTouch -XX:+DisableExplicitGC -XX:+ParallelRefProcEnabled -XX:+PerfDisableSharedMem -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1HeapRegionSize=8M -XX:G1HeapWastePercent=5 -XX:G1MaxNewSizePercent=40 -XX:G1MixedGCCountTarget=4 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1NewSizePercent=30 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:G1ReservePercent=20 -XX:InitiatingHeapOccupancyPercent=15 -XX:MaxGCPauseMillis=200 -XX:MaxTenuringThreshold=1 -XX:SurvivorRatio=32 -Dusing.aikars.flags=https://mcflags.emc.gs -Daikars.new.flags=true -jar ../server.jar --nogui"

JAVA_PID=$!

source .venv/bin/activate

sleep 8

echo "Starting ControlRoom..."

python main.py

sleep 2


if [ -f "$REBOOT_FLAG" ]; then
    echo "Restart flag detected."

    if [ -f "$UPDATE_FLAG" ]; then
        rm "$UPDATE_FLAG"

        echo "Update flag detected."

        git pull origin main
    fi

    touch "./afterreboot_flag"

    rm "$REBOOT_FLAG"
    sleep 5
    exec "$0" "$@"
else
    if [ -f "./playit.pid" ]; then
        OLD_PID=$(cat "./playit.pid")
        if ps -p $OLD_PID > /dev/null; then
            echo "Killing playit process..."
            pkill playit
        fi
        rm "./playit.pid"
    fi
fi


echo "Done. Press any key to exit."
read -n 1