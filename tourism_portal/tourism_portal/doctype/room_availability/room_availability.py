# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RoomAvailability(Document):
	def on_update(self):
		if self.available_qty < 0:
			frappe.throw("Room Qty cannot be less than 0")


def reserve_room(contract_id, from_date, to_date):
	room_qtys = frappe.db.sql("""
	 SELECT date, available_qty, name FROM `tabRoom Availability` WHERE contract_no=%(contract_id)s AND date >= %(from_date)s AND date <= %(to_date)s
     """, {"contract_id": contract_id, "from_date": from_date, "to_date": to_date}, as_dict=True)

	for room_qty in room_qtys:
		if room_qty['available_qty'] < 1:
			return False
	for room_qty in room_qtys:
		qty_doc = frappe.get_doc("Room Availability", room_qty['name'])
		qty_doc.available_qty = qty_doc.available_qty - 1
		qty_doc.save(ignore_permissions=True)
	return True


def free_room(contract_id, check_in, check_out):
	room_qtys = frappe.db.sql("""
	 SELECT date, available_qty, name FROM `tabRoom Availability` WHERE contract_no=%(contract_id)s AND date >= %(check_in)s AND date <= %(check_out)s
     """, {"contract_id": contract_id, "check_in": check_in, "check_out": check_out}, as_dict=True)

	# for room_qty in room_qtys:
	# 	if room_qty['available_qty'] < 1:
	# 		return False
	for room_qty in room_qtys:
		qty_doc = frappe.get_doc("Room Availability", room_qty['name'])
		qty_doc.available_qty = qty_doc.available_qty + 1
		qty_doc.save(ignore_permissions=True)
	return True