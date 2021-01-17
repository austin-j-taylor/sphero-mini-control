#!/bin/sh


rfkill unblock bluetooth
# Turn on bluetooth
sudo bluetoothctl power on
sudo bluetoothctl agent on
sudo bluetoothctl default-agent
sudo bluetoothctl discoverable on
sudo bluetoothctl pairable on
#echo "bluetooth activated."

#sudo bluetoothctl remove 74:F9:CA:4B:21:6C
#sudo bluetoothctl scan on > /dev/null &
#echo "scanning"
# connect to the switch pro controller by its MAC address

#until sudo bluetoothctl pair 74:F9:CA:4B:21:6C
#do
#	sleep 1
#	echo "not found... still scanning..."
#done

#echo "done scanning"
#sudo bluetoothctl trust 74:F9:CA:4B:21:6C
#sudo bluetoothctl scan off
#sudo bluetoothctl quit

#until sudo bluetoothctl connect 74:F9:CA:4B:21:6C
#do
#	sleep 1
#	echo "not yet connected..."
#done
#echo "connected"
#whoami
#sleep 1
python3 ~/Desktop/spheroControl/spheroSwitchProController.py
until python3 ~/Desktop/spheroControl/spheroSwitchProController.py
do
	echo "Running the script again."
	sleep 1
	until sudo bluetoothctl connect 74:F9:CA:4B:21:6C
	do
		sleep 1
		echo "not yet connected..."
	done
	echo "connected"
done

echo "Script has finally ended. Shutting down the pi."
sudo shutdown -P now
