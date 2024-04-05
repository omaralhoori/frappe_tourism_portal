# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class Hotel(Document):
	def before_save(self):
		self.set_priority()
	def set_priority(self):
		if self.priority == 'High Priority':
			self.hotel_priority = 10
		elif self.priority == 'Medium Priority':
			self.hotel_priority = 5
		elif self.priority == 'Low Priority':
			self.hotel_priority = 2