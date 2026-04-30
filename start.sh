#!/bin/bash

cd "$(dirname "$0")"

FLAG="./ControlRoom/reboot_flag"

rm -f "$FLAG"

if [[ -f "./ControlRoom/afterreboot_flag" ]]; then
    echo "Afterreboot state. No need of playit.gg"

    rm -f "./ControlRoom/afterreboot_flag"
else
    echo "Starting playit.gg tunnel in a new window..."
    setsid kitty --title "Playit Tunnel" bash -c "playit; echo 'Tunnel stopped. Press enter...'; read" &

    echo $! > "./ControlRoom/playit.pid"

fi


echo "Starting Minecraft Server..."
setsid kitty --title "Java 1.21.11 | Bedrock 1.21.130" bash -c "java -Xms6656M -Xmx6656M -XX:+AlwaysPreTouch -XX:+DisableExplicitGC -XX:+ParallelRefProcEnabled -XX:+PerfDisableSharedMem -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1HeapRegionSize=8M -XX:G1HeapWastePercent=5 -XX:G1MaxNewSizePercent=40 -XX:G1MixedGCCountTarget=4 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1NewSizePercent=30 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:G1ReservePercent=20 -XX:InitiatingHeapOccupancyPercent=15 -XX:MaxGCPauseMillis=200 -XX:MaxTenuringThreshold=1 -XX:SurvivorRatio=32 -Dusing.aikars.flags=https://mcflags.emc.gs -Daikars.new.flags=true -jar server.jar --nogui" &

JAVA_PID=$!

source .venv/bin/activate

sleep 8

cd ControlRoom

echo "Starting ControlRoom..."

python main.py

sleep 2

cd ..


if [ -f "$FLAG" ]; then
    echo "Restart flag detected."

    touch "./ControlRoom/afterreboot_flag"

    rm "$FLAG"
    sleep 5
    exec "$0" "$@"
else
    if [ -f "./ControlRoom/playit.pid" ]; then
        OLD_PID=$(cat "./ControlRoom/playit.pid")
        if ps -p $OLD_PID > /dev/null; then
            echo "Killing playit process ($OLD_PID)..."
            kill $OLD_PID
        fi
        rm "./ControlRoom/playit.pid"
    fi
fi


echo "Done. Press any key to exit."
read -n 1