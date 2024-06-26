import frappe
from frappe import _
from tourism_portal.api.company import get_company_details
from tourism_portal.api.search import get_available_hotel_rooms, get_hotel_total_days, search_for_tours, search_for_transfers
from tourism_portal.tourism_portal.doctype.tour_price.tour_price import apply_tour_discount, get_available_tours, get_available_tours_and_prices
from tourism_portal.tourism_portal.doctype.transfer_price.transfer_price import get_available_transfers
from tourism_portal.utils import calculate_extra_price, get_portal_setting
import json
no_cache=1
def get_context(context):
	context.no_cache = 1
	if frappe.session.user == "Guest":
		frappe.throw(_("Log in to access this page."), frappe.PermissionError)
	search = frappe.form_dict.search
	#params = json.loads(params)
	search_doc = frappe.get_doc("Search Result",
					  {"name": search, "user": frappe.session.user},
					    )
	hotelParams = json.loads(search_doc.hotel_params)#params.get('hotelParams')
	transferParams = json.loads(search_doc.transfer_params)#params.get('transferParams')
	tourParams = json.loads(search_doc.tour_params)#params.get('toursparams')
	transfers = search_for_transfers(transferParams, bool(hotelParams))
	total_days = get_hotel_total_days(hotelParams)
	context.tours = search_for_tours(tourParams, total_days, bool(hotelParams))
	# context.rooms = get_available_hotel_rooms(hotelParams)
	# context.rooms = json.dumps(context.rooms, default=str)
	rooms = get_available_hotel_rooms(hotelParams)
	# search_doc.room_results = context.rooms
	# search_doc.save(ignore_permissions=True)
	context.hotel_search_params = json.dumps(hotelParams, default=str)
	context.transfer_search_params = json.dumps(transferParams, default=str)
	context.tour_search_params = json.dumps(tourParams, default=str)
	frappe.db.set_value("Search Result", search, "room_results", json.dumps(rooms, default=str))
	frappe.db.commit()
	context.transfers = transfers

	context.nationalities = frappe.db.get_all("Nationality")
	context.max_rooms = get_portal_setting("max_hotel_rooms_selected")
	context.max_room_adults = get_portal_setting("max_adults_per_room")
	context.max_room_children = get_portal_setting("max_children_per_room")

	context.max_adults_per_transfer = get_portal_setting("max_adults_per_transfer")
	context.max_children_per_transfer = get_portal_setting("max_children_per_transfer")
	context.max_adults_per_tour = get_portal_setting("max_adults_per_tour")
	context.max_children_per_tour = get_portal_setting("max_children_per_tour")
	context.max_child_age = get_portal_setting("max_child_age")
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
def get_available_hotel_rooms_old(search_params):
	
	hotels = {}
	for search in search_params:
		hotel = search_params[search]
		avilables = search_for_available_hotel(hotel)
		hotels[search] = avilables
	return hotels

"""
		
"""

def search_for_available_hotel(hotel_params):
	if not hotel_params.get('paxInfo'): return []
	condation = "AND tbl1.area=%(location)s"
	if hotel_params.get('location-type') == 'hotel':
		condation = 'AND tbl1.name=%(location)s'
	elif hotel_params.get('location-type') == 'town':
		condation = 'AND tbl1.town=%(location)s'
	# ToDo check if there more than one image per room =
	all_hotels  = frappe.db.sql("""
		select 
		tbl1.name as hotel_id, tbl1.hotel_name,
		tbl1.hotel_image, tbl1.address, tbl1.gps_location, tbl1.star_rating,
		tbl2.room_type, tbl2.room_accommodation_type, 
		tbl2.name as room_id,
		file.file_url as room_image,
		tbl1.hotel_child_rate_policy,
		tbl1.hotel_accommodation_type_rule,
		tbl1.hotel_cancellation_policy
		FROM `tabHotel Room` tbl2 
		INNER JOIN `tabHotel` tbl1 ON tbl1.name=tbl2.hotel
		LEFT JOIN `tabFile` as file on file.attached_to_name=tbl2.name AND file.attached_to_doctype='Hotel Room'
		WHERE	tbl2.disabled=0 AND tbl1.disabled=0  {condation}
		;
	""".format(condation=condation), {"location": hotel_params.get('location'), 
				   'checkin': hotel_params.get('checkin'), 'checkout': hotel_params.get('checkout')}, as_dict=True)
	hotels = {}
	for hotel in all_hotels:
		hotel['contracts'] = get_hotel_room_contracts(hotel, hotel_params)
		if hotel['hotel_cancellation_policy']:
			hotel['cancellation_policy_description'] = frappe.db.get_value("Cancellation Policy", hotel['hotel_cancellation_policy'], "policy_description")
		if len(hotel['contracts']) > 0: hotel['contract_id'] = hotel['contracts'][0]['contract_id'] 
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
"""
	cntrct.name as contract_id,

	IFNULL(cntrct.accommodation_type_rule, tbl1.hotel_accommodation_type_rule) as hotel_accommodation_type_rule,
	IFNULL(cntrct.cancellation_policy, tbl1.hotel_cancellation_policy) as hotel_cancellation_policy

LEFT JOIN `tabHotel Room Contract` cntrct ON cntrct.hotel=tbl2.hotel AND cntrct.room_type=tbl2.room_type 
			AND (cntrct.check_in_from_date is null or %(checkin)s BETWEEN cntrct.check_in_from_date and cntrct.check_in_to_date)
			AND ( %(checkout)s BETWEEN cntrct.check_in_from_date and cntrct.check_in_to_date)

"""
def get_hotel_room_contracts(hotel_room, search_params):
	contracts = frappe.db.sql("""
		SELECT cntrct.name as contract_id, contract_type, check_in_from_date, check_in_to_date,
		accommodation_type_rule as hotel_accommodation_type_rule, 
		cancellation_policy as hotel_cancellation_policy
			FROM `tabHotel Room Contract` as cntrct
		WHERE hotel=%(hotel)s AND room_type=%(room_type)s
		AND (cntrct.selling_from_date  is null or now() BETWEEN cntrct.selling_from_date and cntrct.selling_to_date)
		AND (cntrct.release_days =0 or DATEDIFF(%(checkin)s, now()) > cntrct.release_days )
		AND ((%(checkin)s >= cntrct.check_in_from_date and %(checkin)s < cntrct.check_in_to_date)
			OR ( %(checkout)s >= cntrct.check_in_from_date and  %(checkout)s < cntrct.check_in_to_date))
		AND cntrct.docstatus=1
	""", {"hotel": hotel_room.get('hotel_id'), 'room_type': hotel_room.get('room_type'),
       'checkin': search_params.get('checkin'), 'checkout': search_params.get('checkout')
	   }, as_dict=True)

	return contracts
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
		WHERE contract_no=%(contract_no)s AND date >= %(checkin)s AND date < %(checkout)s
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
	company_class = get_company_class(search_params)
	room_price = frappe.db.sql("""
		SELECT prc.name as item_price_name ,prc.company_class, prc.selling_type, prc.hotel, 
		prc.buying_currency, prc.buying_price,
		 prc.selling_currency, prc.selling_price FROM  `tabHotel Room Price` prc
		WHERE prc.room_contract=%(contract_id)s 
		AND (prc.nationality=%(nationality)s OR prc.nationality IS NULL OR prc.nationality='')
		AND (prc.room_accommodation_type=%(room_accommodation_type)s OR prc.room_accommodation_type IS NULL  OR prc.room_accommodation_type='')
	""", {"contract_id": room.get('contract_id'),
       "company_class": company_class.get('company_class'),
       "room_accommodation_type": room.get('room_accommodation_type'),
       	"nationality": search_params.get('nationality')},as_dict=True)
	if len(room_price) == 0:return
	room_price = room_price[0]
	date_format = "%Y-%m-%d"
	delta = datetime.strptime(search_params.get('checkout'), date_format) - datetime.strptime(search_params.get('checkin'), date_format)
	days = delta.days
	selling_price, selling_currency = get_room_selling_price(room, room_price, company_class)
	# calculate company class extraprice
	if selling_price:
		# calculate extra child price
		room_price_with_children = get_room_price_with_children(room, selling_price)
		return (room_price_with_children * days, days, selling_currency, room_price.get('item_price_name'))

def get_room_selling_price(room, room_price, company_class):
	if room_price.get('selling_price') :
		selling_price, selling_currency = room_price.get('selling_price'), room_price.get('selling_currency')
	else:
		selling_price, selling_currency = get_selling_price_profit_margin_based(room, room_price)
	if not selling_price:
		return None, None
	selling_price = get_room_selling_price_based_on_class(selling_price, room_price.get('item_price_name'), company_class.get('company_class'))
	if company_class.get('company_class') and room_price.get('company_class') == company_class.get('company_class'):
		selling_price = calculate_extra_price(selling_price, company_class.get('extra_price_type'), company_class.get('extra_price'))
	
	return selling_price, selling_currency

def get_room_selling_price_based_on_class(selling_price, item_price_name, company_class):
	class_extra_price = frappe.db.get_value("Hotel Room Price Company", {"parent": item_price_name, "company_class": company_class}, ['extra_type', 'extra_profit'])
	if not class_extra_price: return selling_price
	extra_type, extra_price = class_extra_price
	return calculate_extra_price(selling_price, extra_type, extra_price)


def get_selling_price_profit_margin_based(room, room_price):
	hotel_profit_margin = frappe.db.get_value("Hotel", room_price.get('hotel'), ['hotel_profit_margin']) or frappe.db.get_single_value("Tourism Portal Settings", "default_hotel_profit_margin")
	selling_price = None
	selling_currency = None
	profit_margin = frappe.db.sql("""
		SELECT margin_type,profit_margin
		FROM `tabProfit Margin Item`
		WHERE parent=%(profit_margin)s AND 
		(room_type=%(room_type)s OR room_type IS NULL OR room_type='')
		ORDER BY room_type DESC
	""", {"room_type":room.get('room_accommodation_type') , "profit_margin": hotel_profit_margin},as_dict=True)
	if len(profit_margin) > 0:
		profit_margin = profit_margin[0]
		# convert currencies
		selling_price, selling_currency = get_currency_based_price(room_price.get('buying_price'), room_price.get('buying_currency'))
		if selling_price:
			selling_price = calculate_extra_price(selling_price, profit_margin.get('margin_type'), profit_margin.get('profit_margin'))

	return selling_price, selling_currency

def get_currency_based_price(from_price, from_currency):
	selling_currency = frappe.db.get_single_value("Tourism Portal Settings", "selling_currency")
	if selling_currency == from_currency:
		selling_price = from_price
	else:
		selling_price = convert_currency(from_price, from_currency, selling_currency)
	return selling_price,selling_currency


def convert_currency(from_price, from_currency, to_currency):
	to_price = 0
	currency_rates = get_currencies()
	if not currency_rates  or currency_rates.get('success') == False:
		return to_price
	if not currency_rates.get('quotes'):
		return to_price
	rate = currency_rates['quotes'].get(to_currency + from_currency)
	to_price = from_price / rate
	return to_price


import requests
def get_external_currencies():
	"""
		return: 
			{
			"success": true,
			"source": "USD",
			"quotes": {
				"USDAED": 3.67279,
				"USDAFN": 69.028845,
	"""
	res = requests.get("http://api.exchangerate.host/live?access_key=227c4880c3db5de4aca693c565636e1e")
	return res.content.decode()

def get_currencies():
	last_update = frappe.db.get_single_value("Tourism Currency", "last_fetch", cache=True)
	if last_update and (frappe.utils.datetime.datetime.now() - last_update).total_seconds() < 3600:
		return json.loads(frappe.db.get_single_value("Tourism Currency", "rates", cache=True))
	else:
		rates = get_external_currencies()
		frappe.db.set_single_value("Tourism Currency", "last_fetch", frappe.utils.now())
		frappe.db.set_single_value("Tourism Currency", "rates", str(rates))
		frappe.db.commit()
		return json.loads(rates)

def get_company_class(search_params):
	location_type = search_params.get('location-type')
	location = search_params.get('location')
	city = get_location_city(location_type, location)
	company = frappe.db.get_value("User", frappe.session.user, "company", cache=True)
	return frappe.db.get_value("Company Assigned Class", {
		"company": company, "city": city, 
		"from_date": ["<=", frappe.utils.nowdate()], 
		"to_date": [">=", frappe.utils.nowdate()]},
		["company_class", "extra_price_type", "extra_price"], as_dict=True
		) or {}
	
	
def get_location_city(location_type, location):
	city = None
	area = None
	if location_type == 'hotel':
		area = frappe.db.get_value("Hotel", location, "area")
	elif location_type == 'area':
		area = location
	if area:	
		town = frappe.db.get_value('Area', area, "town", cache=True)
		city = frappe.db.get_value("Town", town, "city", cache=True)
	return city
def get_room_price_with_children(room, selling_price):
	room_price = selling_price
	child_policies = frappe.db.sql("""
		SELECT from_age, to_age, room_child_order, adult_price_percentage
			FROM `tabChild Rate Policy Item`
		WHERE parent=%(child_rate_policy)s 
		order BY room_child_order, from_age
	""", {"child_rate_policy": room.get('hotel_child_rate_policy')},as_dict=True)
	pax = room.get('pax')
	if pax:
		adult_price = selling_price / float(pax.get('adults'))
		child_ages = [int(child) for  child in pax.get('childrenInfo')]
		child_ages.sort()
		child_order = 0
		for child in child_ages:
			child_order += 1
			
			for plc in child_policies:
				if int(plc.get('room_child_order')) == child_order:
					if child >= plc.get('from_age') and child <= plc.get('to_age'):
						room_price += ((adult_price * plc.get('adult_price_percentage')) / 100)
						break
	return room_price
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
"""
	args:
		room_id: str,
		hotel_search: str,
		adults: int,
		children: int,
		requested_qty: int,
		from_date: str,
		to_date: str,
		nationality: str,
		contracts: list,
		prices: list
"""
@frappe.whitelist()
def ask_for_availability():
	args = frappe.form_dict
	args = verify_ask_for_availability_args(args)
	now_datetime = frappe.utils.now()
	inquiries = frappe.db.sql("""
		select name from `tabHotel Inquiry Request`
		WHERE customer=%(customer)s AND room=%(room)s 
		AND from_date=%(from_date)s AND to_date=%(to_date)s 
		AND (docstatus=0 OR valid_datetime > %(now_datetime)s)
		AND used=0
	""", {"customer": frappe.session.user, "room": args.get('room_id'), "now_datetime": now_datetime, 
       "from_date": args.get('from_date'), "to_date": args.get('to_date')})
	if len(inquiries) > 0:
		return {
			"success_key": 0,
			"error": _("You have asked for this room before.")
		}
	company_details = get_company_details()
	ask_doc = frappe.get_doc({
		"doctype": "Hotel Inquiry Request", 
		"customer": frappe.session.user,
		"company": company_details.get('company'),
		"room": args.get('room_id'),
		"hotel_search": args.get('hotel_search'),
		"adults": args.get('adults'),
		"children": args.get('children'),
		"requested_qty": args.get('requested_qty'),
		"from_date": args.get('from_date'),
		"to_date": args.get('to_date'),
		"nationality": args.get('nationality'),
	})
	ask_doc.insert(ignore_permissions=True)
	ask_doc.update_buying_price(args.get('contracts'), args.get('prices'))
	ask_doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {
		"success_key": 1,
		"msg": _("Your request has been received successfully. Kindly reload this page after a few minutes to receive the rate and availability")
	}

def verify_ask_for_availability_args(args):
	args = {
		"room_id": args.get('room_id'),
		"hotel_search": args.get('hotel_search'),
		"adults": int(args.get('adults')),
		"children": int(args.get('children')),
		"requested_qty": int(args.get('requested_qty')),
		"from_date": args.get('from_date'),
		"to_date": args.get('to_date'),
		"nationality": args.get('nationality'),
		"contracts": args.get('contracts'),
		"prices": args.get('prices')
	}
	if type(args.get('contracts')) == str:
		args['contracts'] = json.loads(args.get('contracts'))
	if type(args.get('prices')) == str:
		args['prices'] = json.loads(args.get('prices'))

	print(args)
	if not args.get('room_id') or not args.get('hotel_search') or not args.get('adults') or not args.get('requested_qty') or not args.get('from_date') or not args.get('to_date'):
		frappe.throw(_("Invalid request"))
	return args
	