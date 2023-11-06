import frappe
from frappe import _
from tourism_portal.utils import get_portal_setting
import json

def get_context(context):
	context.no_cache = 1
	if frappe.session.user == "Guest":
		frappe.throw(_("Log in to access this page."), frappe.PermissionError)
	params = frappe.form_dict.params
	params = json.loads(params)

	context.rooms = get_available_hotel_rooms(params)
	context.rooms = json.dumps(context.rooms)
	return context

"""
	search_params: [
		{
			location: ,
			location-type: ,
			nationality: ,
			checkin: ,
			checkout: ,
			room: ,
			paxInfo: [{
				adults: ,
				children: ,
				childrenInfo: [],
			}]
		}
	]
"""
def get_available_hotel_rooms(search_params):
	
	hotels = []
	for hotel in search_params:
		avilables = search_for_available_hotel(hotel)
		hotels.append(avilables)
	return hotels

"""
		
"""

def search_for_available_hotel(hotel_params):
	if not hotel_params.get('paxInfo'): return []
	condation = "AND tbl1.area=%(location)s"
	if hotel_params.get('location-type') == 'hotel':
		condation = 'AND tbl1.name=%(location)s'
	all_hotels  = frappe.db.sql("""
		select 
		tbl1.name as hotel_id, tbl1.hotel_name, 
		tbl2.room_type, tbl2.room_accommodation_type, 
		tbl2.name as room_id,
		cntrct.name as contract_id,
		file.file_url as room_image,
		IFNULL(cntrct.accommodation_type_rule, tbl1.hotel_accommodation_type_rule) as hotel_accommodation_type_rule,
		IFNULL(cntrct.cancellation_policy, tbl1.hotel_cancellation_policy) as hotel_cancellation_policy
		FROM `tabHotel Room` tbl2 
		INNER JOIN `tabHotel` tbl1 ON tbl1.name=tbl2.hotel
		LEFT JOIN `tabHotel Room Contract` cntrct ON cntrct.hotel=tbl2.hotel AND cntrct.room_type=tbl2.room_type 
			AND (cntrct.check_in_from_date is null or %(checkin)s BETWEEN cntrct.check_in_from_date and cntrct.check_in_to_date)
			AND ( %(checkout)s BETWEEN cntrct.check_in_from_date and cntrct.check_in_to_date)
			AND (cntrct.selling_from_date  is null or now() BETWEEN cntrct.selling_from_date and cntrct.selling_to_date)
			AND (cntrct.release_days =0 or DATEDIFF(%(checkin)s, now()) > cntrct.release_days )
			AND cntrct.docstatus=1
		LEFT JOIN `tabFile` as file on file.attached_to_name=tbl2.name AND file.attached_to_doctype='Hotel Room'
		WHERE	tbl2.disabled=0 AND tbl1.disabled=0  {condation}
		;
	""".format(condation=condation), {"location": hotel_params.get('location'), 
				   'checkin': hotel_params.get('checkin'), 'checkout': hotel_params.get('checkout')}, as_dict=True)
	hotels = {}
	print(all_hotels, hotel_params)
	for hotel in all_hotels:
		if not hotels.get(hotel.get('hotel_id')):
			hotels[hotel.get('hotel_id')] = []
		hotels[hotel.get('hotel_id')].append(hotel)
	availables = {}
	for name, hotel in hotels.items():
		if rooms := search_for_available_room(hotel_params.get('paxInfo'), hotel):
			availables[name] = rooms
	# for pax_info in hotel_params.get('paxInfo'):
	# 	availables = search_for_available_room(pax_info, all_hotels)
	# 	hotels.append(availables)
	for hotel in availables:
		for roomName in availables[hotel]:
			for room in availables[hotel][roomName]:
				# Get Room Price
				room['price'] = get_room_price(room, hotel_params)
				# Get Room Availabilities
				room['qty'] = get_room_qty(room, hotel_params)
				# Get Room Features
				room['features'] = get_room_features(room)
				if not room['price'] or not room['qty']:
					room = get_enquery_result(room, hotel_params)
	return availables

def  get_room_features(room):
	features = frappe.db.get_all("Feature Item", {"parent": room.get('room_id'), "parenttype": "Hotel Room"}, ["feature"])
	features = [ ff.get('feature') for ff in features]
	return features
def get_enquery_result(room, hotel_params):
	if result := frappe.db.exists("Hotel Inquiry Request", {
		"customer": frappe.session.user,
		"room": room.get('room_id'),
		"valid_datetime": [">", frappe.utils.now()],
		"docstatus": 1
	}):
		result_doc = frappe.get_doc("Hotel Inquiry Request", result)
		selling_price, selling_currency = result_doc.selling_price, result_doc.selling_currency
		if result_doc.selling_price_based_on == 'Profit Margin':
			selling_price, selling_currency = get_profit_margin_based_price(
				room.get('hotel_id'),
				room.get('room_accommodation_type'),
				result_doc.buying_price,
				result_doc.buying_currency,
				  )
		date_format = "%Y-%m-%d"
		delta = datetime.strptime(hotel_params.get('checkout'), date_format) - datetime.strptime(hotel_params.get('checkin'), date_format)
		days = delta.days
		room['price'] = (selling_price * days, days, selling_currency)
		room['qty'] = result_doc.qty
	ff = ['name', 'qty', 'selling_price_based_on', 'valid_datetime', 
  'buying_currency', 'buying_price', 'selling_currency', 'selling_price']
	
	return room

def get_profit_margin_based_price(hotel, room_type, buying_price,buying_currency):
	profit_policy = frappe.db.get_value("Hotel", hotel, "hotel_profit_margin") or frappe.db.get_single_value("Tourism Portal Settings", "default_hotel_profit_margin")
	results = frappe.db.sql("""
		SELECT margin_type, profit_margin FROM `tabProfit Margin Item` 
		WHERE parent=%(profit_policy)s
		AND (room_type=%(room_type)s OR room_type IS NULL OR room_type="")
	""", {"profit_policy": profit_policy, "room_type": room_type}, as_dict=True)
	if len(results) < 1: return None, None
	selling_price = buying_price
	if results[0].get('margin_type') == 'Amount':
		selling_price += results[0].get('profit_margin')
	else:
		selling_price = selling_price + ((selling_price *  results[0].get('profit_margin')) / 100)
	return selling_price, buying_currency

def get_room_qty(room, hotel_params):
	room_qty = frappe.db.sql("""
		SELECT min(available_qty) as qty FROM `tabRoom Availability`
		WHERE contract_no=%(contract_no)s AND date between %(checkin)s AND %(checkout)s
	""", {"contract_no": room.get('contract_id'), 
       "checkin": hotel_params.get('checkin'), "checkout": hotel_params.get('checkout')}, as_dict=True)
	if len(room_qty) > 0:
		return room_qty[0]['qty']
	return 0

def search_for_available_room(pax_info, hotel_rooms):
	suitable_rooms = {}
	all_found = True
	for pax in pax_info:
		all_found = False
		for room in hotel_rooms:
			if is_hotel_suitable(pax, room):
				all_found = True
				if not suitable_rooms.get(pax.get('roomName')):
					suitable_rooms[pax.get('roomName')] = []
				copy_room = {**room}
				copy_room['pax'] = pax
				suitable_rooms[pax.get('roomName')].append(copy_room)
				
		if not all_found: break
	return suitable_rooms if all_found else []

from datetime import datetime

def get_room_price(room, search_params):
	if not room.get('contract_id'): return
	room_price = frappe.db.sql("""
		SELECT prc.company_class, prc.selling_type, 
		prc.buying_currency, prc.buying_price,
		 prc.selling_currency, prc.selling_price FROM  `tabHotel Room Price` prc
		WHERE prc.room_contract=%(contract_id)s 
		AND (prc.nationality=%(nationality)s OR prc.nationality IS NULL OR prc.nationality='')
		AND (prc.room_accommodation_type=%(room_accommodation_type)s OR prc.room_accommodation_type IS NULL  OR prc.room_accommodation_type='')
	""", {"contract_id": room.get('contract_id'), 
       "room_accommodation_type": room.get('room_accommodation_type'),
       	"nationality": search_params.get('nationality')},as_dict=True)
	if len(room_price) == 0:return
	room_price = room_price[0]
	date_format = "%Y-%m-%d"
	delta = datetime.strptime(search_params.get('checkout'), date_format) - datetime.strptime(search_params.get('checkin'), date_format)
	days = delta.days
	if room_price.get('selling_price') :
		return (room_price.get('selling_price') * days, days, room_price.get('selling_currency'))
def is_hotel_suitable(pax_info, hotel):
	hotel_acmnd = frappe.db.sql("""
	SELECT
	tbl4.max_pax, tbl4.min_pax, tbl4.max_adults, tbl4.min_adults, tbl4.max_childs, tbl4.min_childs, tbl4.max_child_age
		FROM `tabRoom Accommodation Type Item` tbl4 
		 WHERE tbl4.parent=%(accommodation_rule)s and tbl4.room_type=%(room_accommodation_type)s 
	""", {"accommodation_rule": hotel.get('hotel_accommodation_type_rule'), 
       	"room_accommodation_type": hotel.get('room_accommodation_type')}, as_dict=True)

	if len(hotel_acmnd) < 1: return False

	adults =int(pax_info.get('adults'))
	children = int(pax_info.get('children'))
	for childPax in pax_info.get('childrenInfo'):
		if hotel_acmnd[0].get('max_child_age'):
			if int(childPax) > hotel_acmnd[0].get('max_child_age'):
				adults += 1
				children -= 1
	
	pax = adults + children
	if pax < hotel_acmnd[0].get('min_pax') or pax > hotel_acmnd[0].get('max_pax'): return False
	if adults < hotel_acmnd[0].get('min_adults') or adults > hotel_acmnd[0].get('max_adults'): return False
	if children < hotel_acmnd[0].get('min_childs') or children > hotel_acmnd[0].get('max_childs'): return False
	return True

@frappe.whitelist()
def ask_for_availability(room_id):
	now_datetime = frappe.utils.now()
	inquiries = frappe.db.sql("""
		select name from `tabHotel Inquiry Request`
		WHERE customer=%(customer)s AND room=%(room)s AND 
		(docstatus=0 OR valid_datetime > %(now_datetime)s)
	""", {"customer": frappe.session.user, "room": room_id, "now_datetime": now_datetime})
	if len(inquiries) > 0:
		return {
			"success_key": 0,
			"error": _("You have asked for this room before.")
		}
	frappe.get_doc({
		"doctype": "Hotel Inquiry Request", 
		"customer": frappe.session.user,
		"room": room_id,
	}).insert(ignore_permissions=True)
	return {
		"success_key": 1,
		"msg": _("The request has been submitted successfully")
	}