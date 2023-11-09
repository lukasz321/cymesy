#!/bin/sh

/bin/mkdir -p /var/lib/misc
/bin/touch /var/lib/misc/dnsmasq.leases
/sbin/ifconfig wlp0s20f3 down
/usr/sbin/ip addr flush dev wlp0s20f3
/sbin/ifconfig wlp0s20f3 up
/usr/sbin/ip addr add 172.16.1.1/24 dev wlp0s20f3

/sbin/dnsmasq
