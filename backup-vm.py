#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# This scripts performs a cold-backup of the argument-specified VM, to an export domain
# Usage : backup-vm.py <vm_name>
# You need to modify the RHEV_URL, RHEV_USERNAME, RHEV_PASSWORD and
# EXPORT_DOMAIN_NAME variables below before use
###

from ovirtsdk.api import API
from ovirtsdk.xml import params
from time import sleep, gmtime, strftime
import sys

RHEV_URL = "https://127.0.0.1"
RHEV_USERNAME = "admin@internal"
RHEV_PASSWORD = "mypassword"

EXPORT_DOMAIN_NAME = "My-export-domain-name"


try:

	################################################################################ Check parameters
	if len(sys.argv) < 2:
		print "Usage : backup-vm.py <vm_name>"
		exit(2)


	################################################################################ Connection to RHEV
	print strftime("%a, %d %b %Y %H:%M:%S", gmtime())+" : Connecting to RHEV"
	api = API ( url=RHEV_URL,
				username=RHEV_USERNAME,
				password=RHEV_PASSWORD,
				ca_file="/etc/pki/ovirt-engine/ca.pem")
	print "Connected to %s successfully!" % api.get_product_info().name
	
	
	################################################################################ Display information about the VM
	print "\n"+strftime("%a, %d %b %Y %H:%M:%S", gmtime())+" : Gathering information about the virtual machine %s" % (sys.argv[1])
	vm = api.vms.get(name=sys.argv[1])
	print "VM name : %s" % (vm.name)
	initial_status = vm.status.state
	print "Status : %s" % (initial_status)
	vm_cluster = api.clusters.get(id=vm.cluster.id)
	print "Cluster : %s" % (vm_cluster.get_name())
	vm_dc = api.datacenters.get(id=vm_cluster.data_center.id)
	print "Datacenter : %s" % (vm_dc.get_name())
	
	
	################################################################################ Check export domain availability
	print "\n"+strftime("%a, %d %b %Y %H:%M:%S", gmtime())+" : Ensuring that the export domain %s is not already attached and activated on a datacenter" % (EXPORT_DOMAIN_NAME)
	dc_list = api.datacenters.list()
	for dc in dc_list:
		dc_export_list = dc.storagedomains.list()
		for dc_export in dc_export_list:
			if dc_export.name == EXPORT_DOMAIN_NAME:
				print "Datacenter %s, Export %s : KO"  % (dc.get_name(), dc_export.name)
				print "> Deactivating the export domain from the Datacenter %s" % (dc.get_name())
				dc_export.deactivate()
				print "> OK : Deactivated data storage domain '%s' to data center '%s' (Status:%s)." %(dc_export.get_name(), dc.get_name(), dc_export.get_status().get_state())
				print "> Unattaching export domain from the Datacenter %s" % (dc.get_name())
				dc_export.delete()
				print "> OK : Detached data storage domain '%s' to data center '%s' (Status:%s)." %(dc_export.get_name(), dc.get_name(), dc_export.get_status().get_state())
			else:
				print "Datacenter %s, Export %s : OK"  % (dc.get_name(), dc_export.name)
	
	
	################################################################################ Activate export domain
	print "\n"+strftime("%a, %d %b %Y %H:%M:%S", gmtime())+" : Activating export domain %s on the datacenter %s" % (EXPORT_DOMAIN_NAME, vm_dc.get_name())	
	sd_export = api.storagedomains.get(name=EXPORT_DOMAIN_NAME)
	dc_export = vm_dc.storagedomains.add(sd_export)
	
	
	################################################################################ Shutdown the VM
	if api.vms.get(name=sys.argv[1]).status.state != 'down':
		print '\n"+strftime("%a, %d %b %Y %H:%M:%S", gmtime())+" : Shutdown VM'
		api.vms.get(name=sys.argv[1]).shutdown()
		print 'Waiting for VM to reach Down status'
		while api.vms.get(name=sys.argv[1]).status.state != 'down':
			sys.stdout.write('.')
			sleep(1)
		print '\nOK'
	else:
		print "\n"+strftime("%a, %d %b %Y %H:%M:%S", gmtime())+" : VM already down"
	
	################################################################################ Export the VM
	print "\n"+strftime("%a, %d %b %Y %H:%M:%S", gmtime())+" : Export of the virtual machine"
	api.vms.get(sys.argv[1]).export(params.Action(storage_domain=api.storagedomains.get(EXPORT_DOMAIN_NAME), exclusive=1, discard_snapshots=1))
	print 'Waiting '
	while api.vms.get(sys.argv[1]).status.state != 'down':
		print "Export in progress : %s" %(api.vms.get(sys.argv[1]).status.state)
		sleep(1)
	print "\n"+strftime("%a, %d %b %Y %H:%M:%S", gmtime())+" OK"
	
	
	################################################################################ Restart of the VM
	if initial_status == 'up':
		print "\n"+strftime("%a, %d %b %Y %H:%M:%S", gmtime())+" : Virtual machine was up before the backup. Restoring state to up."
		if api.vms.get(name=sys.argv[1]).status.state != 'up':
			print 'Starting VM'
			api.vms.get(name=sys.argv[1]).start()
			print 'Waiting for VM to reach Up status'
			while api.vms.get(name=sys.argv[1]).status.state != 'up':
				sleep(1)
				sys.stdout.write('.')
			print '\nOK'
		else:
			print 'VM is already up'
	else:
		print "\n"+strftime("%a, %d %b %Y %H:%M:%S", gmtime())+" : Virtual machine was down before the backup. Keeping it down."
	

	################################################################################ Deactivation of the export domain
	dc_export = vm_dc.storagedomains.get(name=EXPORT_DOMAIN_NAME)
	print "\n"+strftime("%a, %d %b %Y %H:%M:%S", gmtime())+" : Deactivating the export domain"
	dc_export.deactivate()
	print "OK : Deactivated data storage domain '%s' to data center '%s' (Status:%s)." %(dc_export.get_name(), vm_dc.get_name(), dc_export.get_status().get_state())
	print "\n"+strftime("%a, %d %b %Y %H:%M:%S", gmtime())+" : Unattaching export domain from the Datacenter %s" % (vm_dc.get_name())
	dc_export.delete()
	print "OK : Detached data storage domain '%s' to data center '%s' (Status:%s)." %(dc_export.get_name(), vm_dc.get_name(), dc_export.get_status().get_state())


	################################################################################ End	
	api.disconnect()	
	print "\n"+strftime("%a, %d %b %Y %H:%M:%S", gmtime())+" : BACKUP OK"
	exit(0)


except Exception as ex:
	print "\n"+strftime("%a, %d %b %Y %H:%M:%S", gmtime())+" : Unexpected error: %s" % ex
	exit(1)
