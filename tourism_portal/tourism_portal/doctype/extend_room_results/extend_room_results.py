# Copyright (c) 2024, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ExtendRoomResults(Document):
	def confirm_extend_accommodation(self):
		if self.status == "Confirmed":
			#frappe.throw("This request is already confirmed")
			return {
				"success_key": 0,
				"message": "This request is already confirmed"
			}
		invoice = frappe.get_doc("Sales Invoice", self.invoice)
		extend_room = None
		if len(self.contracts) == 0:
			#frappe.throw("Something went wrong")
			return {
				"success_key": 0,
				"message": "Something went wrong"
			}
		for room in invoice.rooms:
			if room.name == self.row_id:
				extend_room = room
				break
		if not extend_room:
			#frappe.throw("Room not found")
			return {
				"success_key": 0,
				"message": "Room not found"
			}
		extend_room.check_out = self.check_out
		for contract in self.contracts:
			invoice.append("room_price",{
				"hotel_search": contract.hotel_search,
				"room_name": contract.room_name,
				"check_in": contract.check_in,
				"check_out": contract.check_out,
				"nights": contract.nights,
				"selling_price": contract.selling_price,
				"total_selling_price": contract.total_selling_price,
				"selling_price_company": contract.selling_price_company,
				"total_selling_price_company": contract.total_selling_price_company,
				"contract_id": contract.contract_id,
				"contract_price": contract.contract_price,
				"buying_currency": contract.buying_currency,
				"buying_price": contract.buying_price,
				"cancellation_policy": contract.cancellation_policy,
			})
		invoice.save(ignore_permissions=True)
		return {
			"success_key": 1
		}
		
