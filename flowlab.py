
#!/usr/bin/env python3
"""CSC 6410 - Experiment 2: OpenFlow automation."""

import os
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.topo import SingleSwitchTopo
from mininet.log import setLogLevel


def main():
    # Use the datapath selected for the lab environment.
    switch_type = os.environ.get("MN_SWITCH", "ovsk")
    user_datapath = "datapath=user" in switch_type

    topo = SingleSwitchTopo(k=3)

    # No external controller: install the flow rules ourselves.
    net = Mininet(
        topo=topo,
        switch=OVSSwitch,
        controller=None,
        autoSetMacs=True,
        build=False,
    )

    net.build()
    s1 = net.get("s1")

    if user_datapath:
        s1.datapath = "user"

    try:
        net.start()

        # Secure mode prevents automatic standalone forwarding.
        s1.cmd("ovs-vsctl set-fail-mode s1 secure")
        s1.cmd("ovs-ofctl del-flows s1")

        print("\n=== Flow table BEFORE installing rules ===")
        print(s1.cmd("ovs-ofctl dump-flows s1"))

        # ARP flooding allows hosts to discover MAC addresses.
        rules = [
            "priority=100,arp,actions=flood",
            "priority=100,ip,nw_dst=10.0.0.1,actions=output:1",
            "priority=100,ip,nw_dst=10.0.0.2,actions=output:2",
            "priority=100,ip,nw_dst=10.0.0.3,actions=output:3",
        ]

        for rule in rules:
            print("Installing:", rule)
            print(s1.cmd("ovs-ofctl add-flow s1 '" + rule + "'"))

        print("\n=== Ping test ===")
        net.pingAll()

        print("\n=== Flow table AFTER ping test ===")
        print(s1.cmd("ovs-ofctl dump-flows s1"))

    finally:
        # Clean up emulated hosts and the switch.
        net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    main()
