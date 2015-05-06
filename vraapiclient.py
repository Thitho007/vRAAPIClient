#!/usr/bin/python
__author__ = 'https://github.com/chelnak'
import requests
import json
import sys
from prettytable import PrettyTable

#disable this in production
requests.packages.urllib3.disable_warnings()

def checkResponse(r):
	"""
	Quick logic to check the http response code.
	
	Parameters:
		r = http response object.
	"""

	acceptedResponses = [200,201]
	if not r.status_code in acceptedResponses:
		print "STATUS: {status} ".format(status=r.status_code)
		print "ERROR: " + r.text
		sys.exit(r.status_code)

def authenticate(host, user, password, tenant):
	"""
	Function that will authenticate a user and build.

	Parameters:
		host = vRA Appliance fqdn.
		user = user account with access to the vRA portal.
		passowrd = valid password for above user.
		tenant = tenant for the user.
	"""

	headers = {'Content-Type' : 'application/json', 'Accept' : 'application/json'}
	payload = {"username": user, "password": password, "tenant": tenant}
	url = 'https://'+ host + '/identity/api/tokens'
	r = requests.post(url = url, data = json.dumps(payload), headers = headers, verify = False)
	checkResponse(r)
	response =  r.json() 

	usr_token = 'Bearer ' + response['id']

	return usr_token

class vRAAPIConsumerClient(object):
	def __init__(self, host, username, password, tenant=None):
		"""
		Creates a connection to the vRA REST API using the provided
		username and password.

		Parameters:
	                host = vRA Appliance fqdn
        	        user = user account with access to the vRA portal
                	passowrd = valid password for above user
	                tenant = tenant for user. if this is NONE it will default to "vsphere.local"
		"""

		if tenant is None:
			tenant = "vsphere.local"

		self.host = host
		self.username = username
		self.password = password
		self.tenant = tenant
		self.token = authenticate(host, username, password, tenant)

	def getToken(self):
		"""
		Function that prints the bearer token for the session.
		This is only for troubleshooting.
		"""

		print self.token

	def getResource(self, id):
		"""
		Function that will get a vRA resource by id.

		Parameters:
			id = id of the vRA resource.
		"""

		host = self.host
		token = self.token
		
		url = 'https://' + host + '/catalog-service/api/consumer/resources/' + id
		headers = {'Content-Type' : 'application/json', 'Accept' : 'application/json', 'Authorization' : token}
		r = requests.get(url = url, headers = headers, verify = False)
		checkResponse(r)
		resource = r.json()
	
		return resource

	def getResourceId(self, id):
		"""
		Function that will search for a resource with a matching requestId.

		Parameters:
			id = request id of the vRA resource.
		"""

		host = self.host
                token = self.token

                url = 'https://' + host + '/catalog-service/api/consumer/resources?$filter=request eq \'' + id +'\'' 
                headers = {'Content-Type' : 'application/json', 'Accept' : 'application/json', 'Authorization' : token}
                r = requests.get(url = url, headers = headers, verify = False)
                checkResponse(r)
                resource = r.json()
		resourceId = resource['content'][0]['id']

                return resourceId
	

	def getAllResources(self):
		"""
		Function that will return all resources that are available to the current user.
		"""

		host = self.host
		token = self.token

		url = 'https://' + host + '/catalog-service/api/consumer/resources'
		headers = {'Content-Type' : 'application/json', 'Accept' : 'application/json', 'Authorization' : token}
		r = requests.get(url = url, headers = headers, verify = False)
		checkResponse(r)
		resources = r.json()

		return resources['content']
	
	def getResourceNetworking(self, id):
		"""
		Function that will return networking information for a given resource.

		Parameters:
			id = id of the vRA resource. 
		"""

                host = self.host
                token = self.token
	
		resource = self.getResource(id)
		resourceData = resource['resourceData']['entries']
	
		for i in resourceData:
			if i['key'] == 'NETWORK_LIST':
				networkList = i['value']['items']
				for j in networkList:
					entries = j['values']['entries']
		return entries
	
	def getRequest(self, id):
		"""
		Function that will return request information for a given request.

		Parameters:
			id = the id of the vRA request.
		"""

	        host = self.host
                token = self.token

                url = 'https://' + host + '/catalog-service/api/consumer/requests/' + id
                headers = {'Content-Type' : 'application/json', 'Accept' : 'application/json', 'Authorization' : token}
                r = requests.get(url = url, headers = headers, verify = False)
		checkResponse(r)

		return r.json()

	def requestResource(self, payload):
		"""
		Function that will submit a request based on payload.
		payload = json body (example in request.json)

		Parameters:
			payload = JSON request body.
		"""
	
                host = self.host
                token = self.token
		
                url = 'https://' + host + '/catalog-service/api/consumer/requests'
                headers = {'Content-Type' : 'application/json', 'Accept' : 'application/json', 'Authorization' : token}
	        r = requests.post(url = url, data = json.dumps(payload), headers = headers, verify = False)
		checkResponse(r)

		id = r.headers['location'].split('/')[7]
		
		return id

class vRAAPIReservationClient(object):
	#http://pubs.vmware.com/vra-62/index.jsp#com.vmware.vra.programming.doc/GUID-7697320D-F3BD-4A42-8721-FBC971B47195.html
        def __init__(self, host, username, password, tenant=None):
		"""
                Creates a connection to the vRA REST API using the provided
                username and password.

                Parameters:
                        host = vRA Appliance fqdn
                        user = user account with access to the vRA portal
                        passowrd = valid password for above user
                        tenant = tenant for user. if this is NONE it will default to "vsphere.local"
                """

                if tenant is None:
                        tenant = "vsphere.local"

                self.host = host
                self.username = username
                self.password = password
                self.tenant = tenant
                self.token = authenticate(host, username, password, tenant)
	
	def getToken(self):
		"""
		Function that prints the bearer token for the session.
		This is only for troubleshooting.
		"""

		print self.token

	def getReservationTypes(self):
		"""
		Display a list of supported reservation types:
		http://pubs.vmware.com/vra-62/index.jsp#com.vmware.vra.programming.doc/GUID-57F7623F-6740-49EC-A572-0525D56862F1.html
		"""

		host = self.host
                token = self.token
		
	        url = 'https://' + host + '/reservation-service/api/reservations/types'
	        headers = { 'Content-Type' : 'application/json', 'Accept' : 'application/json', 'Authorization' : token}
	        r = requests.get(url = url, headers = headers, verify = False)
	        checkResponse(r)
	        reservationTypes = r.json()

        	return reservationTypes[u'content']

	def gerReservationSchema(self, schemaclassid):
		"""
		Displaying a schema definition for a reservation
		http://pubs.vmware.com/vra-62/index.jsp#com.vmware.vra.programming.doc/GUID-E957942A-1CCC-4C16-8147-0F5D382CDCB5.html
		
		Parameters:
			schemaclassid = schemaClassId of supported reservation Type. E.g Infrastructure.Reservation.Virtual.vSphere
		
		"""
		
		host = self.host
		token = self.token


	        url = 'https://' + host + '/reservation-service/api/data-service/schema/' + schemaclassid + '/default'
        	headers = { 'Content-Type' : 'application/json', 'Accept' : 'application/json', 'Authorization' : token}
	        r = requests.get(url = url, headers = headers, verify = False)
	        checkResponse(r)
	        reservationSchema = r.json()

	        return reservationSchema[u'fields']

	def getBusinessGroupId(self,tenant=None,buisenessGroupName=None):
		"""
		Get the business group ID for a reservation
		http://pubs.vmware.com/vra-62/index.jsp#com.vmware.vra.programming.doc/GUID-588865AE-0134-4087-B090-C725790C052C.html

		Parameters:
			tenant = vRA tenant. if null then it will default to vsphere.local
			businessGroupName = For future use. Need to be able to fetch ID from business group name
		"""

		host = self.host
		token = self.token

                if tenant is None:
                        tenant = "vsphere.local"
		
	        url = 'https://' + host + '/identity/api/tenants/' + tenant + '/subtenants'
	        headers = { 'Content-Type' : 'application/json', 'Accept' : 'application/json', 'Authorization' : token}
	        r = requests.get(url = url, headers = headers, verify = False)
	        checkResponse(r)

	        businessGroupId = r.json()

        	return businessGroupId

        def getAllBusinessGroups(self,tenant=None,show='table'):
                """
                Get All business groups 
		List ID and name for each business group

                Parameters:
                        tenant = vRA tenant. if null then it will default to vsphere.local
                """

                host = self.host
                token = self.token

                if tenant is None:
                        tenant = "vsphere.local"

                url = 'https://' + host + '/identity/api/tenants/' + tenant + '/subtenants'
                headers = { 'Content-Type' : 'application/json', 'Accept' : 'application/json', 'Authorization' : token}
                r = requests.get(url = url, headers = headers, verify = False)
                checkResponse(r)

                businessGroups = r.json()

		if show == 'table':
			table = PrettyTable(['Id','Name'])

        	        for i in businessGroups['content']:
				table.add_row([i['id'], i['name']])

	       	        print table
		elif show == 'json':
			return businessGroups['content']

	def getComputeResourceForReservation(self, schemaclassid):
		"""
		Get a compute resource for the reservation
		http://pubs.vmware.com/vra-62/index.jsp#com.vmware.vra.programming.doc/GUID-AF6F177D-13C2-47AD-842D-1D341591D5F4.html

		Parameters:
			schemaclassid = schemaClassId of supported reservation Type. E.g Infrastructure.Reservation.Virtual.vSphere
		"""

		host = self.host
		token = self.token

		url = 'https://' + host + '/reservation-service/api/data-service/schema/' + schemaclassid + '/default/computeResource/values'
	        headers = { 'Content-Type' : 'application/json', 'Accept' : 'application/json', 'Authorization' : token}
	        payload = {}
	        r = requests.post(url = url, headers = headers, data = json.dumps(payload), verify = False)
	        checkResponse(r)

        	computeResource = r.json()

	        return computeResource

	def getResourceSchemaForReservation(self, schemaclassid,fieldid, computeresourceid):
        	"""
		Getting a resource schema by reservation type
		#http://pubs.vmware.com/vra-62/index.jsp#com.vmware.vra.programming.doc/GUID-C19E4316-603F-4497-86DB-C241ECE4EEB4.html
		vSphere reservation syntax: http://pubs.vmware.com/vra-62/index.jsp#com.vmware.vra.programming.doc/GUID-CAB141B4-E25F-42EC-B2C4-8516366CB43F.html

		Parameters:
			schemaclassid = schemaClassId of supported reservation Type. E.g Infrastructure.Reservation.Virtual.vSphere
			fieldid = Extension field supported in the reservation... E.g resourcePool
			computeresourceId = Id of the compute resource to query
		"""
		
		host = self.host
		token = self.token

	        url = 'https://' + host + '/reservation-service/api/data-service/schema/' + schemaclassid + '/default/' + fieldid + '/values'
	        headers = { 'Content-Type' : 'application/json', 'Accept' : 'application/json', 'Authorization' : token}
	        payload = {
        	        "text": "",
                	"dependencyValues": {
                        	"entries": [{
                                	"key": "computeResource",
	                                "value": {
        	                                "type": "entityRef",
                	                        "componentId": 'null',
                        	                "classId": "ComputeResource",
                                	        "id": "{computeResourceId}".format(computeResourceId =  computeresourceid)
	                                }
        	                }]
                	  }
	        }

	        r = requests.post(url = url, headers = headers, data = json.dumps(payload), verify = False)
	        checkResponse(r)
		resourceSchema = r.json()

	        return resourceSchema

	def createReservation(self, payload):
		"""
		Creating a reservation by type
		http://pubs.vmware.com/vra-62/index.jsp#com.vmware.vra.programming.doc/GUID-11510887-0F55-4EA4-858C-9881F94C718B.html

		Parameters:
			payload = JSON payload containing the reservation information
		"""

		host = self.host
		token = self.token	

	        url = 'https://' + host + '/reservation-service/api/reservations'
        	headers = { 'Content-Type' : 'application/json', 'Accept' : 'application/json', 'Authorization' : token}
	        r = requests.post(url = url, headers = headers, data = json.dumps(payload), verify = False)
        	checkResponse(r)

	        reservationId = r.headers['location'].split('/')[6]

	        return reservationId

	def getReservation(self, reservationid):
		"""
		Verify a reservation and get reservation details
		http://pubs.vmware.com/vra-62/index.jsp#com.vmware.vra.programming.doc/GUID-2A2D96DE-9BBE-414B-82AB-DD70B82D3E0C.html

		Parameters:
			reservationid = Id of a new or existing reservation
		"""
		
		host = self.host
		token = self.token

		url = 'https://' + host + '/reservation-service/api/reservations/' + reservationid
	        headers = { 'Content-Type' : 'application/json', 'Accept' : 'application/json', 'Authorization' : token}
	        r = requests.get(url = url, headers = headers, verify = False)
 	        checkResponse(r)

	        reservation = json.dumps(r.json())
	
		return reservation

	def getAllReservations(self, show='table'):
		"""
		Get all reservations

		Parameters:
			show = Output either table format or raw json
		"""

		host = self.host
		token = self.token

	        url = 'https://' + host + '/reservation-service/api/reservations'
	        headers = { 'Content-Type' : 'application/json', 'Accept' : 'application/json', 'Authorization' : token}
	        r = requests.get(url = url, headers = headers, verify = False)
	        checkResponse(r)

	        reservations = r.json()

		if show == 'table':		
			table = PrettyTable(['Id','Name'])

		        for i in reservations['content']:
				table.add_row([i['id'], i['name']])
		
			print table
		elif show == 'json':
			return reservations['content']