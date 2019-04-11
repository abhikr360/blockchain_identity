import rsa
import yaml
from merkletools import *
from hashlib import sha256
import globalVs
import json

class Issuer:
	def __init__(self, name = None, keypair = None, schema = None):
		self.name = name
		if keypair == None:
			self.keypair = rsa.newkeys(1024)
		else:
			self.keypair = keypair
		globalVs.public_keys[self.name] = self.keypair[0]

		self.schema = yaml.load(open(schema))

	def verify_field(self, key, value, signature, root, proof, pkey):
		mt = MerkleTools()
		root_verified = mt.validate_proof(proof, sha256(str(key)+':'+str(value)).hexdigest(), root)
		if not root_verified:
			print("Incorrect Merkle Root")
			return False

		if not rsa.verify(root, signature, pkey):
			print("Signature mismatch")
			return False
		return True

	#proofs : dictionary of field and proof
	#values : dictionary of field and values

	def construct_cert_str(name, receiver, attr, address):
		return json.dumps(
			{
				'Name':name,
				'Issuer': self.name,
				'Receiver': receiver,
				'Attributes': attr,
				'Address': address
			}
		)

	def issue(self, proofs, values, receiver):
		
		for attr in self.schema['Proof_Request']:
			if attr not in values:
				print("Value not provided: "+attr)
				return False

		for attr in self.schema['Verifiable'].keys():
			if attr not in proofs:
				print("Proof not provided: "+attr)
				return False

			if(!self.verify_field(key = attr, 
								value = values[attr], 
								signature = globalVs.merkle_signatures[int(proofs[attr]['address'])], 
								root = proofs[attr]['root'], 
								proof = proofs[attr]['proof']
								pkey = globalVs.public_keys[self.schema['Verifiable'][attr]]
								)
			):
				print("Proof Verification Failed: "+attr)
				return False

		fields = {}
		for attr in self.certificate['Attributes']:
			if attr in values:
				fields[attr]=values[attr]
			else:
				fields[attr]=str(1)#raw_input(attr+': ') #Will be replaced with random quantity


		newCertificate = Certificate(name=globalVs.CertiName[self.name], issuer = self.name, receiver=receiver, fields = fields)
		# Insert into bloackchain, return the address

		newCertificate.makeMerkleTree()
		address = newCertificate.uploadMerkleSignature()

		return construct_cert_str(name = newCertificate.name, receiver = receiver, attr = fields,address=address)
		


				



# issuer= Issuer(schema = 'schemas/job_application.yaml')

# m = MerkleTools()
# l = ['name:loda', 'age:15']
# m.add_leaf(l, True)
# m.make_tree()
# leaf = m.get_leaf(1)
# proof = m.get_proof(1)
# root = m.get_merkle_root()

# kp = rsa.newkeys(1024)
# signature = rsa.sign(root, kp[1], 'SHA-256')
# print(issuer.verify_field(key = 'age', value = 15, signature = signature, root = root, proof = proof, pkey = kp[0]))