Using a wifi dongle to create a bridge/hotspot.

sudo apt-get install hostapd dnsmasq

sudo systemctl stop systemd-resolved
sudo systemctl disable systemd-resolved
sudo systemctl mask systemd-resolved
