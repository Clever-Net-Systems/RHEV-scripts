#!/usr/bin/python
# -*- coding: utf-8 -*-

# This script automatically creates a VM by calling the oVirt Python API
# To use, first download your oVirt certificate:
# curl -o rhevm.cer http://<your.rhev.url>/ca.crt

from ovirtsdk.xml import params
from ovirtsdk.api import API
import argparse,sys,re,getpass
from time import sleep
from vmcreateconfig import credentials
from vmcreateconfig import domains_clusters
from vmcreateconfig import domains_hosts
from vmcreateconfig import defaults

MB = 1024*1024
GB = 1024*MB

# From http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input
def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def NICOption(s):
	try:
		return re.match("^(.+:.+:.+)$", s).group(0)
	except:
		raise argparse.ArgumentTypeError("String '%s' does not match required format (nic:network:driver e.g. \"eth0:ovirtmgmt:virtio\") " % (s,))

def DiskOption(s):
	try:
		return re.match("^(.+:.+:(sparse|raw):[01])$", s).group(0)
	except:
		raise argparse.ArgumentTypeError("String '%s' does not match required format (domain:sizeGB:type:bootable e.g. \"Domain1:10:sparse|raw:0|1\") " % (s,))

# This is where we validate that the storage domain / cluster configurations are coherent
def validateClusterConfig(cluster, domain):
	for disk in args.disk:
		vals = re.match("^(.+):(.+):(sparse|raw):([01])$", disk).group(1,2,3,4)
		if not vals[0] in domains_clusters[cluster]:
			return "Domain " + vals[0] + " can not be used by a VM running in cluster " + cluster
	return True

# This is where we validate that the storage domain / cluster configurations are coherent
def validateHostConfig(host, domain):
	if host is None:
		return True
	for disk in args.disk:
		vals = re.match("^(.+):(.+):(sparse|raw):([01])$", disk).group(1,2,3,4)
		if not vals[0] in domains_hosts[host]:
			return "Domain " + vals[0] + " can not be used by a VM running on host " + host
	return True

if credentials['password'] is None:
	sys.stdout.write("Please enter password for user %s: " % credentials['username'])
	password = getpass.getpass()
else:
	password = credentials['password']

# Connect to API - we need to do that before parsing command line arguments because argparse calls the API
api = API(url=credentials['url'], username=credentials['username'], password=password, insecure=False, ca_file=credentials['ca_file'])

# Parse command line arguments
parser = argparse.ArgumentParser(prog = "vmcreate", description = "Create a RHEV VM")
subparsers = parser.add_subparsers(help="sub-command help")
parser_create = subparsers.add_parser('create', help="Create a VM")
parser_export = subparsers.add_parser('export', help="Export a VM")
parser_import = subparsers.add_parser('import', help="Import a VM")

parser_create.set_defaults(which='create')
parser_create.add_argument("name", help="the name of the VM")
parser_create.add_argument("cluster", help="the cluster in which to run the VM", choices = map(lambda x: x.name, api.clusters.list()))
parser_create.add_argument("mem", help="amount of memory in MB", type=int)
parser_create.add_argument("vcpus", help="number of VCPUs", type=int)
parser_create.add_argument("--host", help='Specify host to start on (Any host in Cluster if unspecified)', choices = map(lambda x: x.name, api.hosts.list()), default=None)
parser_create.add_argument("--affinity", help='Specify host affinity: migratable|user_migratable|pinned (corresponds to GUI options Allow manual and automatic migration, Allow manual migration only, and Do not allow migration)', choices = ['migratable', 'user_migratable', 'pinned'], default='migratable')
parser_create.add_argument("--nic", help='add a NIC to the VM (nic:network:driver e.g. "eth0:ovirtmgmt:virtio")', action='append', type = NICOption)
parser_create.add_argument("--disk", help='add a virtual disk to the VM (domain:sizeGB:type:bootable e.g. "Domain1:10:sparse|raw:0|1")', action='append', type = DiskOption)
parser_create.add_argument("-d", "--description", help="VM description", default="")
parser_create.add_argument("-c", "--comment", help="VM description", default="")
parser_create.add_argument("-b", "--boot", help="Boot VM after creation", action='store_true')

parser_import.set_defaults(which='import')
parser_import.add_argument("name", help="the name of the VM")
parser_import.add_argument("expdomain", help="the name of the export domain", choices = map(lambda x: x.name, api.storagedomains.list(type_='export')))
parser_import.add_argument("storage", help="the name of the storage domain for the imported VM", choices = map(lambda x: x.name, api.storagedomains.list(type_='data')))
parser_import.add_argument("cluster", help="the cluster in which to run the VM", choices = map(lambda x: x.name, api.clusters.list()))

parser_export.set_defaults(which='export')
parser_export.add_argument("name", help="the name of the VM", choices = map(lambda x: x.name, api.vms.list()))
parser_export.add_argument("domain", help="the name of the export domain", choices = map(lambda x: x.name, api.storagedomains.list(type_='export')))

args = parser.parse_args()

if args.which == "export":
	if api.vms.get(args.name).status.state != 'down':
		if query_yes_no("VM " + args.name + " is not down. Do you wish to power it off ?", default = "no"):
			api.vms.get(args.name).stop()
			print 'Waiting for VM to reach Down status'
			while api.vms.get(args.name).status.state != 'down':
				sleep(1)
		else:
			sys.exit(0)
	try:
		api.vms.get(args.name).export(params.Action(storage_domain = api.storagedomains.get(args.domain)))
		print 'VM was exported successfully'
		print 'Waiting for VM to reach Down status'
		while api.vms.get(args.name).status.state != 'down':
			sleep(1)
	except Exception as e:
		print 'Failed to export VM ' + args.name + ': %s' % str(e)

if args.which == "import":
	try:
		api.storagedomains.get(args.expdomain).vms.get(args.name).import_vm(params.Action(storage_domain = api.storagedomains.get(args.storage), cluster=api.clusters.get(name=args.cluster)))
		print 'VM was imported successfully'
		print 'Waiting for VM to reach Down status'
		while api.vms.get(args.name).status.state != 'down':
			sleep(1)
	except Exception as e:
		print 'Failed to import VM:\n%s' % str(e)

if args.which == "create":
	print "This script will create a VM with the following parameters:"
	print "Cluster: " + args.cluster
	print "VM name: " + args.name
	print "VM memory: " + str(args.mem) + "MB"
	print "VM CPUs: " + str(args.vcpus) + " cores (1 virtual socket)"
	print "Start Running On: " + ("Any Host in Cluster" if args.host is None else str(args.host)) + " (" + args.affinity + ")"
	print "VM description: " + args.description
	print "VM comment: " + args.comment
	print "VM timezone: " + defaults['timezone']
	print "OS type: " + defaults['operating_system']
	print "Optimized for: " + defaults['optimized_for']
	print "Boot after creation: " + ("yes" if args.boot else "no")
	for nic in args.nic:
		vals = re.match("^(.+):(.+):(.+)$", nic).group(1,2,3)
		print "NIC: device = " + vals[0] + ", bridge = " + vals[1] + ", driver = " + vals[2]
	for disk in args.disk:
		vals = re.match("^(.+):(.+):(sparse|raw):([01])$", disk).group(1,2,3,4)
		print "Disk: domain = " + vals[0] + ", size = " + vals[1] + "GB, type " + vals[2] + " (" + ("bootable" if vals[3] == "1" else "not bootable") + ")"
	# Check correct association between storage domain and cluster
	reason =  validateClusterConfig(args.cluster, args.disk)
	if reason != True:
		print "Sorry, this configuration was not validated because " + reason
		sys.exit(1)
	# Check correct association between storage domain and host
	reason =  validateHostConfig(args.host, args.disk)
	if reason != True:
		print "Sorry, this configuration was not validated because " + reason
		sys.exit(1)
	if not query_yes_no("Please confirm creation of this VM", default = "no"):
		sys.exit(0)
	# Create VM
	try:
		vmcreated = False
		cpuparams = params.CPU(topology = params.CpuTopology(cores = args.vcpus, sockets = 1))
		osparams = params.OperatingSystem()
		osparams.set_type(defaults['operating_system'])
		vmplacement = params.VmPlacementPolicy(host = None if args.host == None else api.hosts.get(args.host), affinity = args.affinity)
		vmparams = params.VM(name = args.name, memory = args.mem * MB, cluster = api.clusters.get(args.cluster), template = api.templates.get('Blank'), cpu = cpuparams, timezone = defaults['timezone'], os = osparams, placement_policy = vmplacement, description = args.description, comment = args.comment, initialization = None)
		vmparams.set_type(defaults['optimized_for'])
		api.vms.add(vmparams)
		# Bug https://bugzilla.redhat.com/show_bug.cgi?id=1039009
		api.vms.get(args.name).set_initialization(None)
		vmcreated = True
		print 'VM ' + args.name + ' created'
		# Add NICs
		for nic in args.nic:
			vals = re.match("^(.+):(.+):(.+)$", nic).group(1,2,3)
			api.vms.get(args.name).nics.add(params.NIC(name = vals[0], network = params.Network(name = vals[1]), interface = vals[2]))
			print 'NIC ' + vals[0] + ' added to VM'
		# Add virtual disks
		for disk in args.disk:
			vals = re.match("^(.+):(.+):(sparse|raw):([01])$", disk).group(1,2,3,4)
			sparse = True if vals[2] == "sparse" else False
			format = 'cow' if vals[2] == "sparse" else 'raw'
			api.vms.get(args.name).disks.add(params.Disk(storage_domains = params.StorageDomains(storage_domain = [api.storagedomains.get(vals[0])]), size=int(vals[1])*GB, status=None, interface='virtio', format=format, sparse=sparse, bootable=(vals[3] == "1")))
			print 'Disk ' + vals[0] + ':' + vals[1] + 'GB added to VM'
		print 'Waiting for VM to reach Down status'
		while api.vms.get(args.name).status.state != 'down':
			sleep(1)
		print "MAC addresses:"
		for nic in api.vms.get(args.name).nics.list():
			print "\t" + nic.name + ": " + nic.mac.address + " (" + nic.interface + ")"
	except Exception as e:
		print 'Failed to create VM: %s' % str(e)
		if vmcreated and api.vms.get(args.name) and query_yes_no("Would you like to delete VM " + args.name + " ?", default = "no"):
			api.vms.get(args.name).delete()
		sys.exit(2)
	if args.boot:
		# Wait for disks to be unlocked
		print 'Waiting for VM disks to unlock'
		locked = True
		while locked:
			locked = False
			for disk in api.vms.get(args.name).disks.list():
				if disk.status.state != "ok":
					locked = True
			sleep(1)
		# Try to start newly created VM
		try:
			if api.vms.get(args.name).status.state != 'up':
				print 'Starting VM ' + args.name
				api.vms.get(args.name).start()
				print 'Waiting for VM to reach Up status'
				while api.vms.get(args.name).status.state != 'up':
					sleep(1)
			else:
				print 'VM already up'
		except Exception as e:
			print 'Failed to Start VM:\n%s' % str(e)
