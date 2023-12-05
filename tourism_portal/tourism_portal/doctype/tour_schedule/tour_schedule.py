# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TourSchedule(Document):
	def validate(self):
		self.validate_date()
		
	def validate_date(self):
		if frappe.db.get_value("Tour Schedule", {"tour_type": self.tour_type, "schedule_date": self.schedule_date, "name": ("!=", self.name)}, ['name']):
			frappe.throw("Tour Schedule already exists for this date.")