# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from tourism_portal.tourism_portal.doctype.company_payment.company_payment import add_company_refund, create_payment
from tourism_portal.tourism_portal.doctype.room_availability.room_availability import free_room, reserve_room
from tourism_portal.tourism_portal.doctype.sales_invoice.reserve import add_transfers_to_invoice
from tourism_portal.tourism_portal.doctype.tour_schedule_order.tour_schedule_order import schedule_tours_dates
class SalesInvoice(Document):
	def after_insert(self):
		session_expires_in = frappe.db.get_single_value("Tourism Portal Settings", "session_expires_in")
		session_expires = frappe.utils.now_datetime()+frappe.utils.datetime.timedelta(seconds=int(session_expires_in))
		self.db_set('session_expires',session_expires)
		self.reserve_rooms()
		self.schedule_tours()
	def on_update(self):
		self.calculate_total_hotel_fees()
		self.calculate_total_transfer_fees()
		self.calculate_total_fees()
	def schedule_tours(self):
		all_tours = {}
		for tour_search in self.tours:
			search_name = tour_search.search_name
			check_in = tour_search.from_date
			check_out = tour_search.to_date
			tour_type = tour_search.tour_type
			if not all_tours.get(search_name):
				all_tours[search_name] = {
					"check_in": check_in,
					"check_out": check_out,
					"tours": [],
					"tour_type": tour_type,
					"pickup": tour_search.pick_up,
					"pickup_type": tour_search.pick_up_type,
				}

		for tour in self.tour_types:
			search_name = tour.search_name
			all_tours[search_name]['tours'].append({
				"tour_type": tour.tour_type,
				"tour": tour.tour_name,
				"tour_date": tour.tour_date,
				"package": tour.package_id,
			})
		for search_name in all_tours:
			tour_search = all_tours[search_name]
			schedule_dates = schedule_tours_dates( tour_search)
			for sDate in schedule_dates:
				for tour in self.tour_types:
					if tour.search_name == search_name and tour.tour_name == sDate['tour']:
						print("Setting tour date")
						tour.tour_date = sDate['date']
						tour.db_set('tour_date', sDate['date'])
						break
	def reserve_rooms(self):
		for room in self.room_price:
			if room.contract_id:
				if not reserve_room(room.contract_id, room.check_in, room.check_out):
					frappe.throw('Room is not avilable')
	def free_rooms(self):
		for room in self.rooms:
			if room.contract_id:
				if not free_room(room.contract_id, room.check_in, room.check_out):
					frappe.throw('Room is not avilable')

	def calculate_total_hotel_fees(self):
		total = 0
		for room in self.rooms:
			for room_extra in self.room_extras:
				if room_extra.room_row_id == room.name:
					total  += room_extra.extra_price
					# ToDo make for percentage too
			total += room.total_price

		self.hotel_fees = total
		self.db_set('hotel_fees', total)
	def calculate_total_transfer_fees(self):
		total = 0
		for transfer in self.transfers:
			# for room_extra in self.room_extras:
			# 	if room_extra.room_row_id == room.name:
			# 		total  += room_extra.extra_price
					# ToDo make for percentage too
			total += transfer.transfer_price

		self.transfer_fees = total
		self.db_set('transfer_fees', total)
	
	def calculate_total_fees(self):
		total = 0
		total += self.hotel_fees
		total += self.transfer_fees
		self.grand_total = total
		self.db_set('grand_total', total)
	def on_trash(self):
		print("On Trash")
		self.free_rooms()

	def add_transfer(self, transfer):
		add_transfers_to_invoice(self, [transfer])
	def add_nights(self, row_id, check_in=None, check_out=None):
		if not check_out and not check_in:
			frappe.throw("Please enter new checkin or checkout")
		selected_room = None
		for room in self.rooms:
			if room.name == row_id:
				selected_room = room

		if not selected_room:
			frappe.throw("You have entered wrong room row id")

		new_check_in = None
		new_check_out= None
		if room.check_in != check_in:
			new_check_in = check_in
		if room.check_out != check_out:
			new_check_out = check_out
		if not new_check_out and not new_check_in:
			frappe.throw("Please enter new checkin or checkout")
		if new_check_in:
			self.add_new_nights_before(room, new_check_in)
		if new_check_out:
			self.add_new_nights_after(room, new_check_out)

	def add_new_nights_before(self, room, new_check_in):
		make_room_request(room, new_check_in, room.check_in)
	def add_new_nights_after(self, room, new_check_out):
		pass
	# def before_cancel(self):
	# 	self.cancel_payment()
	def cancel_payment(self):
		payments = frappe.db.get_all("Company Payment", {"voucher_type": "Sales Invoice", "voucher_no": self.name})
		for payment in payments:
			pmnt = frappe.get_doc("Company Payment", payment['name'])
			pmnt.cancel()
			#pmnt.save(ignore_permissions=True)
	# def on_cancel(self):

	# 	self.cancel_invoice()
	def cancel_invoice(self):
		self.cancel_hotels()
		self.db_set("status", "Cancelled")
	def cancel_hotels(self):
		# ToDo cannot cancel any room if checkin is passed
		total_refunds = 0
		for room in self.rooms:
			if room.contract_id:
				if not free_room(room.contract_id, room.check_in, room.check_out):
					frappe.throw('Room is not avilable')
			refund = refund_room(room.cancellation_policy, room.total_price, room.check_in, room.check_out)
			room.refund = refund
			room.is_canceled = 1
			total_refunds += refund
		if total_refunds > 0:
			add_company_refund( company=self.company, refund=total_refunds, voucher_no=self.name, voucher_type=self.doctype)
	def on_submit(self):
		create_payment(self.company, self.grand_total,'Pay',against_doctype= 'Sales Invoice', against_docname=self.name)
		self.db_set("status", "Submitted")
def create_reservation():
	pass
import datetime

def make_room_request(room, check_in, check_out):
	return {
		"location": room.hotel,
		"location-type": "hotel",
		"nationality": room.nationality,
		"checkin": room.check_in,
		"checkout": room.check_out,
		"room": 1,
		"paxInfo": [
			""
		]
	}

@frappe.whitelist()
def refund_room(cancellation_policy, total_price, check_in, check_out):
	if type(check_in) == str:
		check_in = frappe.utils.datetime.datetime.strptime(check_in, "%Y-%m-%d").date()
	if type(check_out) == str:
		check_out = frappe.utils.datetime.datetime.strptime(check_out, "%Y-%m-%d").date()
	total_price = float(total_price)
	cancellations = frappe.db.get_all("Cancellation Policy Item", 
								   {"parent": cancellation_policy}, 
			['duration_type', 'duration', 'refund_type', 'refund', 'is_deduction'], order_by="idx")
	days = frappe.utils.date_diff(check_out, check_in)
	day_diff = frappe.utils.date_diff(check_in, frappe.utils.now())
	check_in_datetime = datetime.datetime.combine(check_in, datetime.time(12))

	time_difference = check_in_datetime - frappe.utils.datetime.datetime.now()
	total_seconds = time_difference.total_seconds()
	hour_diff = total_seconds / 3600
	price_per_day = total_price / days
	selected_cncl = None
	for cncl in cancellations:
		if cncl.duration_type == 'Hour':
			if cncl.duration >= hour_diff:
				selected_cncl = cncl
				break
		elif cncl.duration_type == 'Day':
			if cncl.duration >= day_diff:
				selected_cncl = cncl
				break
	refund = total_price
	if selected_cncl:
		if selected_cncl.refund_type == 'Day':
			refund =  price_per_day * selected_cncl.refund
		elif selected_cncl.refund_type == 'Percentage':
			refund = (total_price * selected_cncl.refund) / 100
		elif selected_cncl.refund_type == 'Amount':
			refund = selected_cncl.refund
		if selected_cncl.is_deduction:
			refund = total_price - refund
	if not selected_cncl: selected_cncl = {}
	return refund


@frappe.whitelist()
def test_schedule(invoice):
	invoice = frappe.get_doc("Sales Invoice", invoice)
	invoice.schedule_tours()
	invoice.save(ignore_permissions=True)
	frappe.db.commit()