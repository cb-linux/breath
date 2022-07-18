#!/bin/bash

case $1/$2 in
    post/*)
	for i in `seq 1 5`
	do
            rmmod iwlmvm iwlwifi mac80211 cfg80211
            modprobe iwlwifi
            sleep 1
            systemctl restart NetworkManager
            systemctl restart wpasupplicant
	    sleep 2
	    WIFI=`nmcli d | grep wifi`
	    if [ -n "$WIFI" ]
	    then
		break
	    fi
	done	
	;;
esac
exit 0
