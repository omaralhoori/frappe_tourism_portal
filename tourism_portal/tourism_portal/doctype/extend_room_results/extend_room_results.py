# Copyright (c) 2024, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ExtendRoomResults(Document):
	def confirm_extend_accommodation(self):
		if self.status == "Confirmed":
			frappe.throw("This request is already confirmed")
		invoice = frappe.get_doc("Sales Invoice", self.invoice)
		extend_room = None
		if len(self.contracts) == 0:
			frappe.throw("Something went wrong")
		for room in invoice.rooms:
			if room.name == self.row_id:
				extend_room = room
				break
		if not extend_room:
			frappe.throw("Room not found")
		extend_room.check_out = self.check_out
		invoice.save(ignore_permissions=True)
		return {
			"success_key": 1
		}
		
