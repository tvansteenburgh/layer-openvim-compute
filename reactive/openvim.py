import subprocess

from charms.reactive import when, when_not, set_state
from charmhelpers.core.hookenv import status_set
from charmhelpers.core.unitdata import kv

@when_not('openvim-compute.installed')
def prepare_for_openvim_compute():
    status_set("maintenance", "preparing compute node")
    subprocess.check_call("usermod -aG libvirtd ubuntu".split())
    set_state('openvim-compute.installed')
    status_set("active", "openvim compute is prepared - needs manual connection")

@when('compute.available', 'openvim-compute.installed')
def install_ssh_key(compute):
    cache = kv()
    if cache.get('ssh_key_installed'):
        return
    with open("/home/ubuntu/.ssh/authorized_keys", 'a') as f:
        f.write(compute.ssh_key() + '\n')
    compute.ssh_key_installed()
    cache.set('ssh_key_installed', True)
        
@when('compute.connected')
def send_user(compute):
    compute.send_user('ubuntu')
    
    