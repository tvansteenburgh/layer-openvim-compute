from os import chmod
from charms.reactive import when, when_not, set_state
from charmhelpers.core.hookenv import status_set
from charmhelpers.core.unitdata import kv
from charmhelpers.core.host import mkdir, symlink, chownr, add_user_to_group
from charmhelpers.fetch.archiveurl import ArchiveUrlFetchHandler

def add_user_to_libvirt_group():
    status_set("maintenance", "adding user to libvirtd group")
    add_user_to_group("ubuntu", "libvirtd")

def setup_qemu_binary():
    status_set("maintenance", "setting up qemu-kvm binary")
    mkdir('/usr/libexec', owner='root', group='root', perms=0o775, force=False)
    symlink('/usr/bin/kvm', '/usr/libexec/qemu-kvm')

def setup_images_folder():
    status_set("maintenance", "setting up VM images folder")
    mkdir('/opt/VNF', owner='ubuntu', group='ubuntu', perms=0o775, force=False)
    symlink('/var/lib/libvirt/images', '/opt/VNF/images')
    chownr('/opt/VNF', owner='ubuntu', group='ubuntu', follow_links=False, chowntopdir=True)
    chownr('/var/lib/libvirt/images', owner='root', group='ubuntu', follow_links=False, chowntopdir=True)
    chmod('/var/lib/libvirt/images', 0o775)

def download_default_image():
    status_set("maintenance", "downloading default image")
    fetcher = ArchiveUrlFetchHandler()
    fetcher.download(
        source="https://cloud-images.ubuntu.com/releases/16.04/release/ubuntu-16.04-server-cloudimg-amd64-disk1.img",
        dest="/opt/VNF/images/ubuntu-16.04-server-cloudimg-amd64-disk1.img"
        # TODO: add checksum
    )

@when_not('openvim-compute.installed')
def prepare_for_openvim_compute():
    add_user_to_libvirt_group()
    setup_qemu_binary()
    setup_images_folder()
    download_default_image()
    status_set("active", "ready")
    set_state('openvim-compute.installed')

@when('compute.available', 'openvim-compute.installed')
def install_ssh_key(compute):
    cache = kv()
    if cache.get("ssh_key:" + compute.ssh_key()):
        return
    with open("/home/ubuntu/.ssh/authorized_keys", 'a') as f:
        f.write(compute.ssh_key() + '\n')
    compute.ssh_key_installed()
    cache.set("ssh_key:" + compute.ssh_key(), True)

@when('compute.connected')
def send_user(compute):
    compute.send_user('ubuntu')
