#!/bin/bash
set -euxo pipefail

enable() {
    cards="sklnau8825adi sklnau8825max"
    for card in $cards; do
	if [[ -e "/proc/asound/${card}" ]]; then
            pid=$(pidof pulseaudio)
            user=$(stat -c '%U' /proc/"${pid}")
            uid=$(stat -c '%u' /proc/"${pid}")
            export PULSE_RUNTIME_PATH="/run/user/${uid}/pulse"
            su --preserve-environment -c "pactl set-card-profile 0 $1" "${user}"
	fi
    done
}

if [[ "$1" == "jack/headphone HEADPHONE plug" ]]; then
    enable Headphone-Profile
elif [[ "$1" == "jack/microphone MICROPHONE plug" ]]; then
    # for a headphones+mic, we will get 1st: headphone plug, 2nd this event
    enable Headset-Profile
elif [[ "$1" == "jack/headphone HEADPHONE unplug" ]]; then
    enable HiFi
elif [[ "$1" == "jack/microphone MICROPHONE unplug" ]]; then
    enable HiFi
fi