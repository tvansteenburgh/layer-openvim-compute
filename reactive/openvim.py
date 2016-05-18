from charms.reactive import when, when_not, set_state
from charmhelpers.core.hookenv import status_set

import subprocess

@when_not('openvim-compute.installed')
def prepare_for_openvim_compute():
    status_set("maintenance", "preparing compute node")
    subprocess.check_call("usermod -aG libvirtd ubuntu".split())
    set_state('openvim-compute.installed')
    status_set("active", "openvim compute is prepared - needs manual connection")
