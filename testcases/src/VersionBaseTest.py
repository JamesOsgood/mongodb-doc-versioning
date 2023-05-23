from pymongo import MongoClient
from pysys.basetest import BaseTest
from datetime import datetime

class VersionBaseTest(BaseTest):
	def __init__ (self, descriptor, outsubdir, runner):
		BaseTest.__init__(self, descriptor, outsubdir, runner)

		self.db_connection = None
		self.connectionString = self.project.CONNECTION_STRING.replace("~", "=")
		
	# open db connection
	def get_db_connection(self, dbname = None):
		if self.db_connection is None:
			self.log.info("Connecting to: %s" % self.connectionString)
			client = MongoClient(self.connectionString)
			if dbname:
				self.db_connection = client.get_database(dbname)
			else:
				self.db_connection = client.get_database()

		return self.db_connection
	
	def create_test_doc(self, index, field_count):
		doc = { '_id' : index }
		for field in range(field_count):
			field_name = f'field_{field}'
			field_value = f'value_{field}'
			doc[field_name] = field_value

		return doc
	
	def create_test_docs(self, coll, doc_count, field_count):
		coll.drop()
		docs = []
		for index in range(doc_count):
			docs.append(self.create_test_doc(index, field_count))

		coll.insert_many(docs)

	def create_correction(self, coll, index, user, field_name, new_field_value):
		filter = { '_id' : index }
		update = { '$push' : 
	    				{ 'corrections' : 
	  						{ 'user' : user,
	  	                      'field' : field_name,
	  						  'value' : new_field_value,
							   'ts' : datetime.now()
							} 
						} 
					}
		res = coll.update_one(filter, update)

	def get_user_version_of_docs(self, coll, filter, user):
		pipeline = [ {
			'$match': filter
			}, {
				'$set': {
				'myc_v': {
					'$map': {
					'input': {
						'$filter': {
						'input': '$corrections', 
						'as': 'correction', 
						'cond': {
							'$eq': [
							'$$correction.user', user
							]
						}
						}
					}, 
				'as': 'item', 
				'in': {
					'k': '$$item.field', 
					'v': '$$item.value'
				}
				}
			}
			}
		}, {
			'$unset': 'corrections'
		}, {
			'$set': {
			'new_obj': {
				'$arrayToObject': {
				'$concatArrays': [
					{
					'$objectToArray': '$$ROOT'
					}, '$myc_v'
				]
				}
			}
			}
		}, {
			'$unset': [
			'new_obj.myc_v'
			]
		}, {
			'$replaceRoot': {
			'newRoot': '$new_obj'
			}
		}
		]	

		self.log.info(pipeline)

		return coll.aggregate(pipeline)





