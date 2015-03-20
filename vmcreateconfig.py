# Define the credentials
credentials = {
	'username': 'admin@internal',
	'password': None,		# password or None if it is to be input by the user
	'url': 'https://<your.rhev.url>/api',
        'ca_file': 'rhevm.cer'
}

# Define the domains that can be used by VMs depending on the cluster on which they are created
domains_clusters = {
	'Cluster1': [ 'StorageDomain1', 'StorageDomain2', 'StorageDomain3' ],
	'Cluster2': [ 'StorageDomain1', 'StorageDomain2' ]
}

# Define the domains that can be used by VMs depending on the host on which they are created
domains_hosts = {
	'hypervisor1': 	[ 'StorageDomain1', 'StorageDomain2' ],
	'hypervisor2': 	[ 'StorageDomain1', 'StorageDomain2' ],
	'hypervisor3':	[ 'StorageDomain1', 'StorageDomain2' ],
	'hypervisor4':	[ 'StorageDomain1', 'StorageDomain2' ],
	'hypervisor5':	[ 'StorageDomain1', 'StorageDomain3' ],
	'hypervisor6':	[ 'StorageDomain1', 'StorageDomain3' ],
	'hypervisor7':	[ 'StorageDomain1', 'StorageDomain3' ],
	'hypervisor8':	[ 'StorageDomain1', 'StorageDomain3' ]
}

# Define defaults
defaults = {
	'operating_system': "rhel_6x64",
	'optimized_for': 'server',
	# https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Virtualization/3.0/html-single/REST_API_Guide/#appe-REST_API_Guide-Timezones
	'timezone': 'Europe/Warsaw' # (GMT+01:00) Central European Standard Time
}
