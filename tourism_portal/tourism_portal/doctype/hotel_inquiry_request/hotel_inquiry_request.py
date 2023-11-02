# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class HotelInquiryRequest(Document):
	def before_submit(self):
		self.validate_required_fields()
		self.valid_datetime = frappe.utils.now_datetime()+frappe.utils.datetime.timedelta(seconds=self.valid_until)
	def validate_required_fields(self):
		if not self.valid_until:
			frappe.throw("Please enter Valid Until field")
		if not self.buying_currency:
			frappe.throw("Please enter Buying Currency field")
		if not self.buying_price:
			frappe.throw("Please enter Buying Price field")