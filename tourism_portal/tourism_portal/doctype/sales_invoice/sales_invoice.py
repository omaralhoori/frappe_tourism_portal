# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

from tourism_portal.tourism_portal.doctype.sales_invoice.email_service import notifiy_flight_changed, send_agency_invoice_email, send_agency_voucher_email
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.model.naming import make_autoname
from frappe.tests.utils import FrappeTestCase
from tourism_portal.tourism_portal.doctype.company_payment.company_payment import add_child_company_refund, add_company_refund, create_child_company_payment, create_payment, get_child_company_balance, get_company_balance
from tourism_portal.tourism_portal.doctype.room_availability.room_availability import free_room, reserve_room
from tourism_portal.tourism_portal.doctype.sales_invoice.reserve import add_tours_to_invoice, add_transfers_to_invoice
from tourism_portal.tourism_portal.doctype.tour_price.tour_price import get_tour_price_with_child_prices
from tourism_portal.tourism_portal.doctype.tour_schedule_order.tour_schedule_order import schedule_tours_dates
from tourism_portal.utils import get_cancellation_refund, get_hotel_total_nights, get_location_city, is_time_passed, parse_date, parse_invoice_checkout_date, parse_transfer_date, send_system_email
class SalesInvoice(Document):
	def after_insert(self):
		session_expires_in = frappe.db.get_single_value("Tourism Portal Settings", "session_expires_in")
		session_expires = frappe.utils.now_datetime()+frappe.utils.datetime.timedelta(seconds=int(session_expires_in))
		self.db_set('session_expires',session_expires)
		self.reserve_rooms()
		self.add_free_tours()
		self.schedule_tours()
	def validate(self):
		if self.status == "Cancelled":
			frappe.throw(_("Invoice is already cancelled"))
	def validate_invoice_check_out(self):
		if frappe.session.user == 'admin@venus.com':
			return
		if self.invoice_check_out and parse_date(self.invoice_check_out) < parse_date(frappe.utils.now()):
			frappe.throw(_("Invoice is already expired"))
	def on_update(self):
		self.calculate_total_hotel_fees()
		self.calculate_total_transfer_fees()
		self.calculate_total_tour_fees()
		self.calculate_total_fees()
		self.set_invoice_check_out()
	def on_update_after_submit(self):
		self.set_invoice_check_out()
		self.validate_invoice_check_out()
		self.calculate_room_fees()
		self.calculate_total_hotel_fees()
		self.calculate_total_transfer_fees()
		self.calculate_total_tour_fees()
		self.calculate_total_fees()
		self.notifiy_transfer_changes()
		
	def notifiy_transfer_changes(self):
		old_doc = self.get_doc_before_save()
		for transfer in self.transfers:
			for old_t in old_doc.transfers:
				if transfer.name == old_t.name:
					if old_t.flight_no != transfer.flight_no:
						notifiy_flight_changed(self, transfer)
					break

	def calculate_room_fees(self):
		prices = {}
		for room_price in self.room_price:
			room_key = room_price.hotel_search + "-" + room_price.room_name
			if not prices.get(room_key):
				prices[room_key] = {
					"selling_price": 0,
					"selling_price_company": 0,
				}
			prices[room_key]['selling_price'] += room_price.total_selling_price
			prices[room_key]['selling_price_company'] += room_price.total_selling_price_company
		for room in self.rooms:
			room_key = room.hotel_search + "-" + room.room_name
			room.total_price = prices[room_key]['selling_price']
			room.total_price_company = prices[room_key]['selling_price_company']
			
	def set_invoice_check_out(self):
		check_out = self.invoice_check_out
		if check_out:
			check_out = parse_date(check_out)
		for room in self.rooms:
			room_date = parse_date(room.check_out)
			if not check_out or check_out < room_date:
				check_out = room_date
		for transfer in self.transfers:
			transfer_date = parse_date(transfer.transfer_date)
			if not check_out or check_out < transfer_date:
				check_out = transfer_date
		for tour in self.tours:
			tour_date = parse_date(tour.to_date)
			if not check_out or check_out < tour_date:
				check_out = tour_date
		self.invoice_check_out = check_out
		self.db_set('invoice_check_out', check_out)
	def add_free_tours(self):
		if len(self.rooms) == 0 or len(self.transfers) == 0:
			return
		# GET FREE TOURS
		discount_doc = frappe.get_single("Tour Discount")
		for free_tour in discount_doc.free_tour:
			tour_added = False
			for tour in self.tour_types:
				if tour.tour_name == free_tour.tour_type:
					tour_added = True
					break
			if tour_added:
				continue
			print("0----------------------------------------")
			print("Adding Free Tour", free_tour.tour_type)
			tour_city = frappe.db.get_value("Tour Type", free_tour.tour_type, "tour_pickup_city", cache=True)
			for room in self.rooms:
				town = frappe.db.get_value("Hotel", room.hotel, "town", cache=True)
				hotel_city = frappe.db.get_value("Town", town, "city", cache=True)
				if tour_city == hotel_city and frappe.utils.date_diff(room.check_out, room.check_in) >= free_tour.min_nights:
					for transfer in self.transfers:
						transfer_city = get_location_city(transfer.drop_off_type, transfer.drop_off)
						if transfer_city == tour_city:
							tour_added = self.add_free_tour(free_tour, tour_city, room.hotel_search,room.hotel ,room.check_in, room.check_out)
							
						if tour_added: break
				if tour_added: break
		self.save(ignore_permissions=True)
	def add_free_tour(self, free_tour, free_tour_city, hotel_search,pickup_hotel, from_date, to_date):
		tour_search = None
		adults = 0
		childs = 0
		child_ages = []
		new_tour = False
		print("Add free Tour", free_tour.tour_type, free_tour_city, hotel_search,pickup_hotel, from_date, to_date)
		for tour in self.tours:
			if tour.tour_type != "package":
				tour_city = get_location_city(tour.pick_up_type, tour.pick_up)
				if tour_city == free_tour_city:
					tour_search = tour
					break
		for room_pax in self.room_pax_info:
			if room_pax.hotel_search == hotel_search and room_pax.guest_type == "Adult":
				adults += 1
			elif room_pax.hotel_search == hotel_search and room_pax.guest_type == "Child":
				childs += 1
				child_ages.append(room_pax.guest_age)
		if tour_search:
			tour_adults = 0
			tour_childs = 0
			tour_child_ages = []
			for tour_pax in self.tour_pax_info:
				if tour_search.search_name == tour_pax.search_name  and tour_pax.guest_type == "Adult":
					tour_adults += 1
				elif tour_search.search_name == tour_pax.search_name  and tour_pax.guest_type == "Child":
					tour_childs += 1
					tour_child_ages.append(tour_pax.guest_age)
			if tour_adults != adults or tour_childs != childs or sorted(child_ages) != sorted(tour_child_ages):
				new_tour = True

		tour_price = self.get_tour_price(free_tour.tour_type, adults, childs, child_ages)
		print("Tour Price", tour_price)
		if not tour_price: return False
		discount_price = tour_price - (tour_price * free_tour.discount / 100)
		print("Discount Price", discount_price) 
		if not tour_search or new_tour:
			tour_search = self.append("tours")
			tour_search.search_name = "Free " + free_tour.tour_type
			tour_search.tour_type = self.map_tours_type(frappe.db.get_value("Tour Type", free_tour.tour_type, "tour_type", cache=True))
			tour_search.pick_up = pickup_hotel
			tour_search.pick_up_type = "hotel"
			tour_search.from_date = frappe.utils.add_days(from_date, 1)
			tour_search.to_date = frappe.utils.add_days(to_date, -1)
			tour_search.tour_price = discount_price
			tour_search.tour_price_company = discount_price
			tour_search.adults = adults
			tour_search.children = childs
			for room_pax in self.room_pax_info:
				if room_pax.hotel_search == hotel_search: 
					tour_pax = self.append("tour_pax_info")
					tour_pax.search_name = tour_search.search_name
					tour_pax.guest_type = room_pax.guest_type
					tour_pax.guest_age = room_pax.guest_age
		tour_type = self.append("tour_types")
		tour_type.search_name = tour_search.search_name
		tour_type.tour_type = "single"
		tour_type.tour_name = free_tour.tour_type
		tour_type.tour_price= discount_price
		tour_type.tour_price_company= discount_price
		return True
	def update_transfers(self, transfer_infos):
		allowed_hours = frappe.db.get_single_value("Tourism Portal Settings", "transfer_flight_no_last_update")
		for search_name in transfer_infos:
			for transfer_name in transfer_infos[search_name]:
				transfer_info = transfer_infos[search_name][transfer_name]
				if transfer_info.get('paxes'):
					for pax_row in transfer_info['paxes']:
						pax = transfer_info['paxes'][pax_row]
						for transfer_pax in self.transfer_pax_info:
							if pax.get('row_id') == transfer_pax.name:
								transfer_pax.guest_salutation = pax.get('salut')
								transfer_pax.guest_name = pax.get('guest_name')
								break
				if transfer_info.get('flight_no'):
					for transfer in self.transfers:
						if transfer.transfer_name == transfer_name and transfer.transfer_search == search_name:
							if transfer.flight_no != transfer_info['flight_no']:
								if is_time_passed(transfer.transfer_date, allowed_hours):
									frappe.throw("You cannot update filght no " + str(allowed_hours) + " hours before transfer date" )
							transfer.flight_no = transfer_info['flight_no']
							break
	def update_tours(self, tour_infos):
		for search_name in tour_infos:
			tour_info = tour_infos[search_name]
			for pax_row in tour_info:
				pax = tour_info[pax_row]
				for tour_pax in self.tour_pax_info:
					if pax.get('row_id') == tour_pax.name:
						tour_pax.guest_salutation = pax.get('salut')
						tour_pax.guest_name = pax.get('guest_name')
						break
	def get_tour_price(self, tour_type, adults, childs, child_ages):
		tour_price = None
		adult_price = 0
		tour_price_doc = frappe.get_value("Tour Price", {"tour_type": tour_type}, ["adult_economic_price", "adult_premium_price", "tour_child_policy"])
		if not tour_price_doc: return
		tour = frappe.db.get_value("Tour Type",  tour_type, "tour_type")
		if tour == "Economic":
			adult_price = tour_price_doc[0]
		elif tour == "Premium":
			adult_price = tour_price_doc[1]
		tour_price = get_tour_price_with_child_prices(tour_price_doc[2], adult_price, adults, childs, child_ages)
		return tour_price
	def map_tours_type(self, tour_type):
		return {
			"VIP": "vip",
			"Premium": "group-premium",
			"Economic": "group-economic",
		}.get(tour_type)
	def schedule_tours(self, search=None):
		all_tours = {}
		if search:
			for tour_search in self.tours:
				if search == tour_search.search_name:
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
		else:
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
			if all_tours.get(search_name):
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
			self.reserve_room_contract(room)
	def reserve_room_contract(self, room):
		if room.contract_id:
			if not reserve_room(room.contract_id, room.check_in, room.check_out):
				frappe.throw('Room is not avilable')
	def free_rooms(self):
		for room in self.room_price:
			if room.contract_id:
				if not free_room(room.contract_id, room.check_in, room.check_out):
					frappe.throw('Room is not avilable')
	def get_board_price(self, board, room, board_price=None):
		board_details = frappe.db.get_value("Hotel Boarding Table", {"parent": room.hotel, "boarding_type": board}, ["extra_price_type", "extra_price", "child_price", "min_child_age"], as_dict=True)
		if not board_details:
			frappe.throw("Board Type not found")
		if board_price and board_details.extra_price != board_price:
			frappe.throw("Board Price is not correct")
		paxes = self.get_room_pax_info(room.hotel_search, room.room_name)
		child_price = 0
		for child in paxes['childs']:
			if child >= int(board_details.min_child_age or 0):
				child_price += int(board_details.child_price or 0)
		total_board_price = board_price * paxes['adults'] + child_price
		return total_board_price

	def get_room_pax_info(self, hotel_search, room_name):
		room_pax = {
			"adults": 0,
			"childs": []
		}
		for pax in self.room_pax_info:
			if pax.hotel_search == hotel_search and pax.room_name == room_name:
				if pax.guest_type == "Adult":
					room_pax['adults'] += 1
				elif pax.guest_type == "Child":
					room_pax['childs'].append(pax.guest_age)
		return room_pax
	def calculate_total_hotel_fees(self):
		total = 0
		total_company = 0
		for room in self.rooms:
			for room_extra in self.room_extras:
				if room_extra.room_row_id == room.name:
					total  += room_extra.extra_price
					total_company += room_extra.extra_price
					# ToDo make for percentage too
			total += room.total_price
			total_company += room.total_price_company
			if room.board_extra_price:
				nights = get_hotel_total_nights(room.check_in, room.check_out)
				board_price = room.board_extra_price * nights
				total += board_price
				total_company += board_price
		self.hotel_fees = total
		self.hotel_fees_company = total_company
		self.db_set('hotel_fees', total)
		self.db_set('hotel_fees_company', total_company)
	def calculate_total_transfer_fees(self):
		total = 0
		total_company = 0
		for transfer in self.transfers:
			# for room_extra in self.room_extras:
			# 	if room_extra.room_row_id == room.name:
			# 		total  += room_extra.extra_price
					# ToDo make for percentage too
			if transfer.is_canceled:
				continue
			total += transfer.transfer_price
			total_company += transfer.transfer_price_company
		self.transfer_fees = total
		self.transfer_fees_company = total_company
		self.db_set('transfer_fees', total)
		self.db_set('transfer_fees_company', total_company)
	def calculate_total_tour_fees(self):
		total = 0
		total_company = 0
		for tour in self.tours:
			# for room_extra in self.room_extras:
			# 	if room_extra.room_row_id == room.name:
			# 		total  += room_extra.extra_price
					# ToDo make for percentage too
			if tour.is_canceled:
				continue
			total += tour.tour_price
			total_company += tour.tour_price_company
		self.tour_fees = total
		self.tour_fees_company = total_company
		self.db_set('tour_fees', total)
		self.db_set('tour_fees_company', total_company)
	
	def calculate_total_fees(self):
		total_company = 0
		total = 0
		total += self.hotel_fees
		total += self.transfer_fees
		total += self.tour_fees
		total_company += self.hotel_fees_company
		total_company += self.transfer_fees_company
		total_company += self.tour_fees_company
		self.grand_total = total
		self.grand_total_company = total_company
		self.db_set('grand_total', total)
		self.db_set('grand_total_company', total_company)
	def on_trash(self):
		print("On Trash")
		self.free_rooms()
	def allowed_to_add_transfers(self, transfers):
		if self.status == "Cancelled":
			return "Invoice is already cancelled"
		# if self.invoice_check_out and parse_invoice_checkout_date(self.invoice_check_out) < frappe.utils.now_datetime():
		# 	return "Invoice is already expired"
		for transferName in transfers:
			transfer = transfers[transferName]
			if 	parse_transfer_date(transfer['transfer_date']) < frappe.utils.now_datetime() + frappe.utils.datetime.timedelta(hours=24) :
				return "You cannot add transfer with date less than 24 hours from now"
		return None
	def allowed_to_add_tours(self, tourSearch):
		if self.status == "Cancelled":
			return "Invoice is already cancelled"
		# if self.invoice_check_out and parse_invoice_checkout_date(self.invoice_check_out) < frappe.utils.now_datetime():
		# 	return "Invoice is already expired"

		if 	parse_transfer_date(tourSearch['check_in']) < frappe.utils.now_datetime() + frappe.utils.datetime.timedelta(hours=24) :
			return "You cannot add tour with date less than 24 hours from now"
		return None
	def add_transfers(self, transfers):
		if msg:= self.allowed_to_add_transfers(transfers):
			frappe.throw(msg)
		search_name = self.get_search_name('transfers')
		total_amounts = add_transfers_to_invoice(self, {
			search_name: transfers
		}, 0)
		if total_amounts:
			total_amount, total_company_amount = total_amounts
			if total_amount > 0:
				self.create_additional_payment(total_amount, total_company_amount)
		self.save(ignore_permissions=True)
		return search_name
	def add_tours(self, tours):
		if msg:= self.allowed_to_add_tours(tours):
			frappe.throw(msg)
		search_name = self.get_search_name('tours')
		total_amounts = add_tours_to_invoice(self, {
			search_name: tours
		}, 0)
		if total_amounts:
			total_amount, total_company_amount = total_amounts
			if total_amount > 0:
				self.create_additional_payment(total_amount, total_company_amount)
		self.schedule_tours(search_name)
		self.save(ignore_permissions=True)
		return search_name

	def get_search_name(self, table):
		search_name = None
		if table == 'transfers':
			search_name = "Transfer Search "
			searches = set([ transfer.transfer_search for transfer in self.transfers])
			search_name += str(len(searches) + 1)
		elif table == 'tours':
			search_name = "Tour Search "
			searches = set([ tour.search_name for tour in self.tours])
			search_name += str(len(searches) + 1)
		elif table == 'rooms':
			search_name = "Hotel Search "
			searches = set([ room.hotel_search for room in self.rooms])
			search_name += str(len(searches) + 1)

		return search_name
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
		
	def add_voucher_no(self):
		format_ser =  "VOCH-"+self.company+"-.#######"
		prg_serial = make_autoname(format_ser, "Sales Invoice")
		self.voucher_no = prg_serial
		self.db_set('voucher_no', prg_serial)
	def add_invoice_no(self):
		format_ser =  "INVC-.#######"
		prg_serial = make_autoname(format_ser, "Sales Invoice")
		self.invoice_no = prg_serial
		self.db_set('invoice_no', prg_serial)
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
		print("Cancel Invoice")
		if self.status == "Cancelled":
			frappe.throw(_("Invoice is already cancelled"))
		try:
			self.cancel_hotels()
			self.cancel_transfers()
			self.cancel_tours()
			self.notifiy_invoice_edit("Invoice " + self.name + " has been cancelled","Invoice " + self.name + " has been cancelled")
		except:
			if self.child_company:
				get_child_company_balance(self.child_company, update_cache=True)
			get_company_balance(self.company, update_cache=True)
			frappe.throw("Error in cancelling invoice")
		self.db_set("status", "Cancelled")
	def cancel_transfers(self):
		cancellation_policy = frappe.db.get_single_value("Tourism Portal Settings", "transfer_cancellation_policy")
		total_refunds = 0
		for transfer in self.transfers:
			# transfer.is_canceled = 1
			if transfer.is_canceled:
				continue
			total_refunds += get_cancellation_refund(cancellation_policy, transfer.transfer_price_company, transfer.transfer_date, transfer.transfer_date, day_margin=1, day_start_hour=0)
		if total_refunds > 0:
			add_company_refund( company=self.company, refund=total_refunds, voucher_no=self.name, voucher_type=self.doctype, remarks="Transfer Refund for voucher "+self.voucher_no)
			if self.child_company:
				commission_refund = get_commission_refund(self.transfer_fees_company, self.transfer_fees, total_refunds)
				create_payment(self.company, commission_refund,'Reserve', remarks="Reserve for "+self.child_company)
				add_child_company_refund( company=self.child_company, parent_company=self.company,refund=commission_refund,parent_refund=total_refunds, voucher_no=self.name, voucher_type=self.doctype, remarks="Transfer Refund for voucher "+self.voucher_no)
			
	def cancel_tours(self):
		cancellation_policy = frappe.db.get_single_value("Tourism Portal Settings", "tour_cancellation_policy")
		total_refunds = 0
		for tour in self.tours:
			if tour.is_canceled:
				continue
			if tour.tour_type == "package":
				total_refunds += get_cancellation_refund(cancellation_policy, tour.tour_price_company, tour.from_date, tour.to_date, day_margin=1, day_start_hour=0)
			else:
				total_refunds += self.get_single_tour_refund(tour, cancellation_policy)
			#tour.is_canceled = 1
			#tour.save(ignore_permissions=True)
		if total_refunds > 0:
			add_company_refund( company=self.company, refund=total_refunds, voucher_no=self.name, voucher_type=self.doctype, remarks="Tour Refund for voucher "+self.voucher_no)
			if self.child_company:
				commission_refund = get_commission_refund(self.tour_fees_company, self.tour_fees, total_refunds)
				create_payment(self.company, commission_refund,'Reserve', remarks="Reserve for "+self.child_company)
				add_child_company_refund( company=self.child_company, parent_company=self.company, refund=commission_refund, parent_refund=total_refunds,voucher_no=self.name, voucher_type=self.doctype, remarks="Tour Refund for voucher "+self.voucher_no)
	def cancel_tour(self, tour_search):
		cancellation_policy = frappe.db.get_single_value("Tourism Portal Settings", "tour_cancellation_policy")
		total_refunds = 0
		canceled_tour = None
		for tour in self.tours:
			if tour.search_name == tour_search:
				if tour.is_canceled:
					break
				if tour.tour_type == "package":
					total_refunds += get_cancellation_refund(cancellation_policy, tour.tour_price_company, tour.from_date, tour.to_date, day_margin=1, day_start_hour=0)
				else:
					total_refunds += self.get_single_tour_refund(tour, cancellation_policy)
				canceled_tour = tour
				canceled_tour.is_canceled = 1
			#tour.save(ignore_permissions=True)
		if total_refunds > 0:
			add_company_refund( company=self.company, refund=total_refunds, voucher_no=self.name, voucher_type=self.doctype, remarks="Tour Refund for voucher "+self.voucher_no)
			canceled_tour.refund = total_refunds
			canceled_tour.company_refund = total_refunds
			if self.child_company:
				commission_refund = get_commission_refund(self.tour_fees_company, self.tour_fees, total_refunds)
				create_payment(self.company, commission_refund,'Reserve', remarks="Reserve for "+self.child_company)
				add_child_company_refund( company=self.child_company, parent_company=self.company, refund=commission_refund, parent_refund=total_refunds,voucher_no=self.name, voucher_type=self.doctype, remarks="Tour Refund for voucher "+self.voucher_no)
				canceled_tour.refund = commission_refund
	def get_single_tour_refund(self,tour, cancellation_policy):
		total_refund = 0
		for tour_type in self.tour_types:
			if tour_type.search_name == tour.search_name:
				total_refund += get_cancellation_refund(cancellation_policy, tour_type.tour_price_company, tour_type.tour_date or tour.from_date, tour_type.tour_date or tour.from_date, day_margin=1, day_start_hour=0)
		return total_refund
		# if tour.tour_date:
		# 	refund = refund_tour(cancellation_policy, tour.tour_price, tour.tour_date)
		# return refund
	def cancel_hotels(self):
		# ToDo cannot cancel any room if checkin is passed
		total_refunds = 0
		
		for room in self.room_price:
			if room.contract_id:
				if not free_room(room.contract_id, room.check_in, room.check_out):
					frappe.throw('Room is not avilable')
			
			refund = refund_room(room.cancellation_policy, room.total_selling_price_company, room.check_in, room.check_out, 1, 14)
			room.refund = refund
			room.is_canceled = 1
			total_refunds += refund
		if total_refunds > 0:
			add_company_refund( company=self.company, refund=total_refunds, voucher_no=self.name, voucher_type=self.doctype, remarks="Hotel Refund for voucher "+self.voucher_no)
			if self.child_company:
				commission_refund = get_commission_refund(self.hotel_fees_company, self.hotel_fees, total_refunds)
				create_payment(self.company, commission_refund,'Reserve', remarks="Reserve for "+self.child_company)
				add_child_company_refund( company=self.child_company, parent_company=self.company, refund=commission_refund,parent_refund=total_refunds, voucher_no=self.name, voucher_type=self.doctype, remarks="Hotel Refund for voucher "+self.voucher_no)
	
	def create_additional_payment(self, amount, company_amount, remarks=""):
		if self.child_company:
			create_child_company_payment(self.child_company, self.company, amount, company_amount,'Payment',against_doctype= 'Sales Invoice', against_docname=self.name, remarks=remarks)
			create_payment(self.company, company_amount,'Pay',against_doctype= 'Sales Invoice', against_docname=self.name, remarks="Payment for "+self.child_company)
		else:
			create_payment(self.company, amount,'Pay',against_doctype= 'Sales Invoice', against_docname=self.name, remarks=remarks)
	def on_submit(self):
		if self.child_company:
			create_child_company_payment(self.child_company, self.company, self.grand_total, self.grand_total_company,'Payment',against_doctype= 'Sales Invoice', against_docname=self.name)
			create_payment(self.company, self.grand_total_company,'Pay',against_doctype= 'Sales Invoice', against_docname=self.name, remarks="Payment for "+self.child_company)
		else:
			create_payment(self.company, self.grand_total,'Pay',against_doctype= 'Sales Invoice', against_docname=self.name)
		self.add_voucher_no()
		self.add_invoice_no()
		self.db_set("status", "Submitted")
		self.notifiy_agency_invoice()
		self.notifiy_agency_voucher()
		self.notifiy_new_reservation()
	def notifiy_new_reservation(self):
		if not frappe.db.get_single_value("Portal Notification Settings", "send_invoice_creation"):
			return
		reservation_email = frappe.db.get_single_value("Portal Notification Settings", "reservation_email")
		if not reservation_email:
			return
		subject = "New Reservation: " + self.voucher_no
		msg = "New Reservation has been created for " + self.voucher_no + " from " + frappe.db.get_value("Company", self.company, "company_name", cache=True)
		send_system_email(reservation_email, subject, msg)
	def notifiy_invoice_edit(self, subject, edit_msg):
		if not frappe.db.get_single_value("Portal Notification Settings", "send_on_invoice_update"):
			return
		reservation_email = frappe.db.get_single_value("Portal Notification Settings", "reservation_email")
		if not reservation_email:
			return
		send_system_email(reservation_email, subject, edit_msg)
	def get_invoice_print_details(self):
		if self.child_company:
			operator = frappe.db.get_value("Company", self.child_company, "company_name", cache=True)
		else:
			operator = frappe.db.get_value("Company", self.company, "company_name", cache=True)
		return {
			"voucher_no": self.voucher_no.split("-")[-1],
			"invoice_no": self.invoice_no.split("-")[-1],
			"operator": operator,
		}
	def get_invoice_room_and_group(self):
		room_groups = {}
		extras_cnt = 0
		for room in self.rooms:
			extras = []
			for room_extra in self.room_extras:
				if room_extra.hotel_search == room.hotel_search and room_extra.room_name == room.room_name:
					extras.append({
						"extra": room_extra.extra,
						"extra_price": room_extra.extra_price,
					})
			room_key = room.hotel_search + room.room + room.board 
			if len(extras) > 0:
				room_key += str(extras_cnt)
				extras_cnt += 1
			if not room_groups.get(room_key):
				room_type = frappe.db.get_value("Hotel Room", room.room, "room_type", cache=True)
				acmd_type = frappe.db.get_value("Hotel Room", room.room, "room_accommodation_type", cache=True)
				room_groups[room_key] = {
					"room_type": frappe.db.get_value("Room Type", room_type, "room_type", cache=True),
					"acmd_type": frappe.db.get_value("Room Accommodation Type", acmd_type, "accommodation_type_name", cache=True),
					"board": frappe.db.get_value("Hotel Boarding Type", room.board, "boarding_type_name", cache=True),
					"hotel": frappe.db.get_value("Hotel", room.hotel, "hotel_name", cache=True),
					"address": frappe.db.get_value("Hotel", room.hotel, "address", cache=True),
					"check_in": room.check_in,
					"check_out": room.check_out,
					"qty": 0,
					"adults": [],
					"childs": [],
					"selling_details": [],
					"extras": extras
				}
			room_groups[room_key]['qty'] += 1
			for room_pax in self.room_pax_info:
				if room_pax.hotel_search == room.hotel_search and room_pax.room_name == room.room_name:
					if room_pax.guest_type == "Adult":
						room_groups[room_key]['adults'].append(room_pax.guest_salutation + ". " + room_pax.guest_name)
					elif room_pax.guest_type == "Child":
						room_groups[room_key]['childs'].append(room_pax.guest_name + ", Age: " + str(room_pax.guest_age))
			
			for room_price in self.room_price:
				if room_price.hotel_search == room.hotel_search and room_price.room_name == room.room_name:
					comulated = False
					for selling_details in room_groups[room_key]['selling_details']:
						if selling_details['from_date'] == room_price.check_in and selling_details['to_date'] == room_price.check_out and selling_details['selling_price'] == room_price.selling_price:
							selling_details['total_selling_price'] += room_price.total_selling_price
							comulated = True
							break
					if not comulated:
						room_groups[room_key]['selling_details'].append({
						"from_date": room_price.check_in, 
						"to_date": room_price.check_out,
						"selling_price": room_price.selling_price,
						"total_selling_price": room_price.total_selling_price,
					})
		return room_groups
	def get_room_and_group(self):
		room_groups = {}
		extras_cnt = 0
		for room in self.rooms:
			extras = []
			for room_extra in self.room_extras:
				if room_extra.hotel_search == room.hotel_search and room_extra.room_name == room.room_name:
					extras.append(room_extra.extra)
			room_key = room.hotel_search + room.room + room.board + str(room.bed_type)
			if len(extras) > 0:
				room_key += str(extras_cnt)
				extras_cnt += 1
			if not room_groups.get(room_key):
				room_type = frappe.db.get_value("Hotel Room", room.room, "room_type", cache=True)
				acmd_type = frappe.db.get_value("Hotel Room", room.room, "room_accommodation_type", cache=True)
				room_groups[room_key] = {
					"room_type": frappe.db.get_value("Room Type", room_type, "room_type", cache=True),
					"acmd_type": frappe.db.get_value("Room Accommodation Type", acmd_type, "accommodation_type_name", cache=True),
					"board": frappe.db.get_value("Hotel Boarding Type", room.board, "boarding_type_name", cache=True),
					"hotel": frappe.db.get_value("Hotel", room.hotel, "hotel_name", cache=True),
					"bed_type": frappe.db.get_value("Room Bed Type", room.bed_type, "bed_type", cache=True),
					"bed_note": frappe.db.get_value("Room Accommodation Bed Type item", {"parent": acmd_type, "bed_type": room.bed_type}, "note", cache=True),
					"address": frappe.db.get_value("Hotel", room.hotel, "address", cache=True),
					"check_in": room.check_in,
					"check_out": room.check_out,
					"qty": 0,
					"adults": [],
					"childs": [],
					"extras": extras
				}
			room_groups[room_key]['qty'] += 1
			for room_pax in self.room_pax_info:
				if room_pax.hotel_search == room.hotel_search and room_pax.room_name == room.room_name:
					if room_pax.guest_type == "Adult":
						room_groups[room_key]['adults'].append(room_pax.guest_salutation + ". " + room_pax.guest_name)
					elif room_pax.guest_type == "Child":
						room_groups[room_key]['childs'].append(room_pax.guest_name + ", Age: " + str(room_pax.guest_age))
			
			
		return room_groups
	def get_invoice_transfer_groups(self):
		transfer_groups = {}

		for transfer in self.transfers:
			if transfer.is_canceled:
				continue
			transfer_key =  transfer.transfer_search + transfer.transfer_name
			if not transfer_groups.get(transfer_key):
				transfer_groups[transfer_key] = {
					"transfer": frappe.db.get_value("Transfer Type", transfer.transfer, "transfer_type", cache=True),
					"pickup": get_location_name(transfer.pick_up, transfer.pick_up_type),
					"drop_off": get_location_name(transfer.drop_off, transfer.drop_off_type),
					"qty": 0,
					"transfer_date": transfer.transfer_date,
					"flight_no": transfer.flight_no,
					"adults": [],
					"childs": [],
					"selling_price": transfer.transfer_price
				}
			transfer_groups[transfer_key]['qty'] += 1
			for transfer_pax in self.transfer_pax_info:
				if transfer_pax.transfer_search == transfer.transfer_search and transfer_pax.transfer_name == transfer.transfer_name:
					if transfer_pax.guest_type == "Adult":
						transfer_groups[transfer_key]['adults'].append(transfer_pax.guest_salutation + ". " + transfer_pax.guest_name)
					elif transfer_pax.guest_type == "Child":
						transfer_groups[transfer_key]['childs'].append(transfer_pax.guest_name + ", Age: " + str(transfer_pax.guest_age))

		return transfer_groups
	def cancel_transfer(self, transfer_search, transfer_name):
		cancellation_policy = frappe.db.get_single_value("Tourism Portal Settings", "transfer_cancellation_policy")
		total_refunds = 0
		cancelled_transfer = None
		for transfer in self.transfers:
			# transfer.is_canceled = 1
			if transfer.transfer_search == transfer_search and transfer.transfer_name == transfer_name:
				if transfer.is_canceled:
					break
				total_refunds += get_cancellation_refund(cancellation_policy, transfer.transfer_price_company, transfer.transfer_date, transfer.transfer_date, day_margin=1, day_start_hour=0)
				cancelled_transfer = transfer
				cancelled_transfer.is_canceled = 1
				break
		if total_refunds > 0:
			add_company_refund( company=self.company, refund=total_refunds, voucher_no=self.name, voucher_type=self.doctype, remarks="Transfer Refund for voucher "+self.voucher_no)
			cancelled_transfer.refund_company = total_refunds
			cancelled_transfer.refund = total_refunds
			if self.child_company:
				commission_refund = get_commission_refund(self.transfer_fees_company, self.transfer_fees, total_refunds)
				create_payment(self.company, commission_refund,'Reserve', remarks="Reserve for "+self.child_company)
				add_child_company_refund( company=self.child_company, parent_company=self.company,refund=commission_refund,parent_refund=total_refunds, voucher_no=self.name, voucher_type=self.doctype, remarks="Transfer Refund for voucher "+self.voucher_no)
				cancelled_transfer.refund = commission_refund
	def get_transfer_groups(self):
		transfer_groups = {}

		for transfer in self.transfers:
			if transfer.is_canceled:
				continue
			transfer_key =  transfer.transfer_search + transfer.transfer_name
			if not transfer_groups.get(transfer_key):
				transfer_groups[transfer_key] = {
					"transfer": frappe.db.get_value("Transfer Type", transfer.transfer, "transfer_type", cache=True),
					"pickup": get_location_name(transfer.pick_up, transfer.pick_up_type),
					"drop_off": get_location_name(transfer.drop_off, transfer.drop_off_type),
					"qty": 0,
					"transfer_date": transfer.transfer_date,
					"flight_no": transfer.flight_no,
					"adults": [],
					"childs": [],
				}
			transfer_groups[transfer_key]['qty'] += 1
			for transfer_pax in self.transfer_pax_info:
				if transfer_pax.transfer_search == transfer.transfer_search and transfer_pax.transfer_name == transfer.transfer_name:
					if transfer_pax.guest_type == "Adult":
						transfer_groups[transfer_key]['adults'].append(transfer_pax.guest_salutation + ". " + transfer_pax.guest_name)
					elif transfer_pax.guest_type == "Child":
						transfer_groups[transfer_key]['childs'].append(transfer_pax.guest_name + ", Age: " + str(transfer_pax.guest_age))	

		return transfer_groups
	
	def get_invoice_tour_groups(self):
		tour_groups = {}
		for tour in self.tours:
			if tour.is_canceled:
				continue
			tour_key = tour.search_name
			if not tour_groups.get(tour_key):
				tour_groups[tour_key] = {
					"tour_type": get_voucher_tour_type(tour.tour_type),
					"pickup": get_location_name(tour.pick_up, tour.pick_up_type),
					"qty": 0,
					"selling_price": tour.tour_price,
					"from_date": tour.from_date,
					"to_date": tour.to_date,
					"adults": [],
					"childs": [],
					"tours": []
				}
			tour_groups[tour_key]['qty'] += 1
			for tour_type in self.tour_types:
				if tour_type.search_name == tour.search_name:
					tour_groups[tour_key]['tours'].append({
						"tour_name": frappe.db.get_value("Tour Type", tour_type.tour_name, "tour_name", cache=True),
						"tour_date": tour_type.tour_date or "Not Scheduled",
						"selling_price": tour_type.tour_price,
					})
			for tour_pax in self.tour_pax_info:
				if tour_pax.search_name == tour.search_name:
					if tour_pax.guest_type == "Adult":
						tour_groups[tour_key]['adults'].append(tour_pax.guest_salutation + ". " + tour_pax.guest_name)
					elif tour_pax.guest_type == "Child":
						tour_groups[tour_key]['childs'].append(tour_pax.guest_name + ", Age: " + str(tour_pax.guest_age))
		return tour_groups
	def get_tour_groups(self):
		tour_groups = {}
		for tour in self.tours:
			if tour.is_canceled:
				continue
			tour_key = tour.search_name
			if not tour_groups.get(tour_key):
				tour_groups[tour_key] = {
					"tour_type": get_voucher_tour_type(tour.tour_type),
					"pickup": get_location_name(tour.pick_up, tour.pick_up_type),
					"qty": 0,
					"from_date": tour.from_date,
					"to_date": tour.to_date,
					"adults": [],
					"childs": [],
					"tours": []
				}
			tour_groups[tour_key]['qty'] += 1
			for tour_type in self.tour_types:
				if tour_type.search_name == tour.search_name:
					tour_groups[tour_key]['tours'].append({
						"tour_name": frappe.db.get_value("Tour Type", tour_type.tour_name, "tour_name", cache=True),
						"tour_date": tour_type.tour_date or "Not Scheduled",
					})
			for tour_pax in self.tour_pax_info:
				if tour_pax.search_name == tour.search_name:
					if tour_pax.guest_type == "Adult":
						tour_groups[tour_key]['adults'].append(tour_pax.guest_salutation + ". " + tour_pax.guest_name)
					elif tour_pax.guest_type == "Child":
						tour_groups[tour_key]['childs'].append(tour_pax.guest_name + ", Age: " + str(tour_pax.guest_age))
		return tour_groups
	def notifiy_agency_invoice(self):
		if frappe.db.get_single_value("Tourism Portal Settings", "send_invoice_email"):
			send_agency_invoice_email(self)
	def notifiy_agency_voucher(self):
		if frappe.db.get_single_value("Tourism Portal Settings", "send_voucher_email"):
			send_agency_voucher_email(self)
def get_location_name(location, location_type):
	if location_type == 'hotel':
		return frappe.db.get_value("Hotel", location, "hotel_name", cache=True)
	elif location_type == 'airport':
		return frappe.db.get_value("Airport", location, "airport_name", cache=True)
	elif location_type == 'area':
		return frappe.db.get_value("Area", location, "area_name", cache=True)
	else:
		return location
def get_voucher_tour_type(tour_type):
	return "VIP" if tour_type == "vip" else "Group"
def create_reservation():
	pass
import datetime
def get_commission_refund(selling_price, selling_price_with_commission, total_refund):
	if selling_price == 0:
		return 0
	commission =  selling_price_with_commission - selling_price
	refund_ratio = total_refund   / selling_price
	return (commission * refund_ratio) + total_refund
	
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
def refund_room(cancellation_policy, total_price, check_in, check_out, margin_date=0, margin_hour=0):
	if type(check_in) == str:
		check_in = frappe.utils.datetime.datetime.strptime(check_in, "%Y-%m-%d").date()
	if type(check_out) == str:
		check_out = frappe.utils.datetime.datetime.strptime(check_out, "%Y-%m-%d").date()
	total_price = float(total_price)
	cancellations = frappe.db.get_all("Cancellation Policy Item", 
								   {"parent": cancellation_policy}, 
			['duration_type', 'duration', 'refund_type', 'refund', 'is_deduction'], order_by="idx")
	days = frappe.utils.date_diff(check_out, check_in) + margin_date
	if days < 1:
		frappe.throw("Check out cannot be before check in")
	day_diff = frappe.utils.date_diff(check_in, frappe.utils.now())
	check_in_datetime = datetime.datetime.combine(check_in, datetime.time(margin_hour))

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


class TestEvent(FrappeTestCase):
	def test_add_free_tour(self):
		sales_invoice = frappe.get_doc("Sales Invoice", "INV-24-01-00007")
		sales_invoice.add_free_tours()