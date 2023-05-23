import os
from datetime import datetime, timedelta

from VersionBaseTest import VersionBaseTest

class PySysTest(VersionBaseTest):
	def __init__ (self, descriptor, outsubdir, runner):
		VersionBaseTest.__init__(self, descriptor, outsubdir, runner)

	def execute(self):
		db = self.get_db_connection()
		coll = db.test
		self.DOC_COUNT = 10
		FIELD_COUNT = 5
		self.create_test_docs(coll, self.DOC_COUNT, FIELD_COUNT)

		self.index_to_correct = int(self.DOC_COUNT / 2)
		self.create_correction(coll, self.index_to_correct, 'user_1', 'field_1', 'value_corrected_1')
		self.create_correction(coll, self.index_to_correct, 'user_2', 'field_3', 'value_corrected_2')


	def validate(self):
		db = self.get_db_connection()
		coll = db.test
		filter = { '_id' : self.index_to_correct }
		
		# User 1
		docs = list(self.get_user_version_of_docs(coll, filter, 'user_1'))
		self.assertTrue(len(docs) == 1)
		doc = docs[0]
		self.assertTrue(doc['field_1'] == 'value_corrected_1')

		# User 2
		docs = list(self.get_user_version_of_docs(coll, filter, 'user_2'))
		self.assertTrue(len(docs) == 1)
		doc = docs[0]
		self.assertTrue(doc['field_1'] == 'value_1')
