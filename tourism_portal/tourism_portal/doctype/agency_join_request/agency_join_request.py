# Copyright (c) 2024, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AgencyJoinRequest(Document):
	def before_insert(self):
		if self.i_agree_to_the_terms_and_conditions == 0:
			frappe.throw("You must agree to the terms and conditions to continue")
