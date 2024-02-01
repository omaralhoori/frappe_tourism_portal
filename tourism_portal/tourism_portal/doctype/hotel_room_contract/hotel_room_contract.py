# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta

from frappe.model.naming import make_autoname
class HotelRoomContract(Document):
	def on_submit(self):
		if self.check_in_from_date > self.check_in_to_date:
			frappe.throw("Check in to date is greater than check in from date")
		date_list = []
		if self.qty > 0:
			current_date = datetime.strptime(self.check_in_from_date, "%Y-%m-%d")
			to_date = datetime.strptime(self.check_in_to_date, "%Y-%m-%d")
			while current_date <= to_date:
				date_list.append(current_date)
				current_date += timedelta(days=1)
		self.create_room_availabilities(date_list)
		self.add_contract_no()
	def add_contract_no(self):
		format_ser = 'RMCNT-.YY.-.#####'
		prg_serial = make_autoname(format_ser, "Hotel Room Contract")
		self.contract_no = prg_serial
		self.db_set('contract_no', prg_serial)
	def create_room_availabilities(self, date_list):
		for date in date_list:
			frappe.get_doc({
				"doctype":"Room Availability",
				"contract_no": self.name,
				"date": date,
				"available_qty": self.qty
			}).insert(ignore_permissions=True)

	def on_cancel(self):
		frappe.db.delete("Room Availability", {"contract_no": self.name})
		frappe.db.delete("Hotel Room Price", {"room_contract": self.name})


@frappe.whitelist()
def allocate_agency_rooms(contract_no, allocation_details):
	"""
		allocation_details = {
			"agency": Company Link,
			"from_date": Date,
			"to_date": Date,
			"qty": Int,
		}
	"""
	if type(allocation_details) == str:
		allocation_details = frappe._dict(frappe.parse_json(allocation_details))
	if not frappe.db.exists("Hotel Room Price", {"room_contract": contract_no}):
		frappe.throw("Please create room prices for this contract")
	contract = frappe.get_doc("Hotel Room Contract", contract_no)
	if contract.qty < allocation_details.qty:
		frappe.throw("Allocation qty is greater than contract qty")
	if contract.check_in_from_date > frappe.utils.datetime.datetime.strptime(allocation_details.from_date, "%Y-%m-%d").date():
		frappe.throw("Allocation from date is less than contract from date")
	if contract.check_in_to_date < frappe.utils.datetime.datetime.strptime(allocation_details.to_date, "%Y-%m-%d").date():
		frappe.throw("Allocation to date is greater than contract to date")
	room_availabilities = frappe.db.get_all("Room Availability", {"contract_no": contract_no, "date": ("between", [allocation_details.from_date, allocation_details.to_date])}, ["name", "available_qty", "date"])
	for room_availability in room_availabilities:
		if room_availability.available_qty < allocation_details.qty:
			frappe.throw("Allocation qty is greater than available qty for date {}".format(room_availability.date))
		frappe.db.set_value("Room Availability", room_availability.name, "available_qty", room_availability.available_qty - allocation_details.qty)
		
	new_room_contract = frappe.get_doc({
		"doctype": "Hotel Room Contract",
		 "hotel": contract.hotel,
		 "contract_type": contract.contract_type,
		 "room_type": contract.room_type,
		 "qty": allocation_details.get("qty"),
		 "check_in_from_date": allocation_details.get("from_date"),
		 "check_in_to_date": allocation_details.get("to_date"),
		 "agency": allocation_details.get("agency"),
		 "selling_from_date": contract.selling_from_date,
		 "selling_to_date": contract.selling_to_date,
		 "cancellation_policy": contract.cancellation_policy,
		 "accommodation_type_rule": contract.accommodation_type_rule,
		 "profit_margin": contract.profit_margin,
	})
	new_room_contract.insert(ignore_permissions=True)
	new_room_contract.ignore_hotel_boarding = contract.ignore_hotel_boarding
	for board in contract.boardings:
		board_row = new_room_contract.append("boardings", )
		board_row.boarding_type = board.boarding_type
		board_row.extra_price_type = board.extra_price_type
		board_row.extra_price = board.extra_price
	new_room_contract.ignore_hotel_extra_services = contract.ignore_hotel_extra_services
	for extra in contract.extra_services:
		extra_row = new_room_contract.append("extra_services", )
		extra_row.service = extra.service
		extra_row.extra_price_type = extra.extra_price_type
		extra_row.extra_price = extra.extra_price
	new_room_contract.save()
	new_room_contract.submit()
	prices = frappe.db.get_all("Hotel Room Price", {"room_contract": contract_no}, )
	for price in prices:
		price_doc = frappe.get_doc("Hotel Room Price", price.name)
		new_price = frappe.new_doc("Hotel Room Price")
		new_price.update(price_doc.as_dict())
		new_price.room_contract = new_room_contract.name
		new_price.check_in_from_date = allocation_details.from_date
		new_price.check_in_to_date = allocation_details.to_date
		new_price.company_classes = []
		new_price.save()
	return new_room_contract.name