import subprocess

from charms.reactive import when, when_not, set_state
from charmhelpers.core.hookenv import status_set
from charmhelpers.core.unitdata import kv
from charmhelpers.core.host import mkdir, symlink, chownr

@when_not('openvim-compute.installed')
def prepare_for_openvim_compute():
    status_set("maintenance", "preparing compute node")
    subprocess.check_call("usermod -aG libvirtd ubuntu".split())
    status_set("active", "openvim compute is prepared - needs manual connection")
    mkdir('/opt/VNF', owner='ubuntu', group='ubuntu', perms=0o777, force=False)
    symlink('/var/lib/libvirt/images', '/opt/VNF/images')
    chownr('/opt/VNF', owner='ubuntu', group='ubuntu', follow_links=False, chowntopdir=True)
    chownr('/var/lib/libvirt/images', owner='root', group='ubuntu', follow_links=False, chowntopdir=True)
    subprocess.check_call('chmod g+rwx /var/lib/libvirt/images', shell=True)
    subprocess.check_call('wget https://cloud-images.ubuntu.com/releases/16.04/release/ubuntu-16.04-server-cloudimg-amd64-disk1.img -O /opt/VNF/images/ubuntu-16.04-server-cloudimg-amd64-disk1.img', shell=True)
    subprocess.check_call('virsh net-start default', shell=True)
    set_state('openvim-compute.installed')
    
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
    
    