import frappe
from frappe import _
from tourism_portal.api.company import get_company_details
from tourism_portal.tourism_portal.doctype.tour_price.tour_price import get_available_tours, get_available_tours_and_prices
# from tourism_portal.www.search.index import get_available_hotel_rooms
from tourism_portal.tourism_portal.doctype.transfer_price.transfer_price import get_available_transfers
import json

from tourism_portal.utils import calculate_extra_price, get_company_class, get_location_city, get_portal_setting, get_subagency_extra_price
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


@frappe.whitelist()
def get_available_hotels():
    search_params = frappe.form_dict.hotels_params#json.loads(frappe.form_dict)
    return get_available_hotel_rooms(search_params)


def get_available_hotel_rooms(search_params, start=0, limit=10):
	hotels = {}
	for search in search_params:
		hotel = search_params[search]
		avilables = search_for_available_hotel(hotel, start, limit)
		hotels[search] = avilables
	return hotels

def search_for_available_hotel(hotel, start=0, limit=10):
	if hotel["location-type"] == "area" or hotel["location-type"] == "town" or hotel['location-type'] == "city":
		return search_for_available_hotel_by_area(hotel, start, limit)
	elif hotel["location-type"] == "hotel":
		return search_for_available_hotel_by_hotel(hotel)
	else:
		return {}
@frappe.whitelist()
def load_more_hotels(hotel_params, start=0, limit=10):
	hotels = get_available_hotel_rooms(json.loads(hotel_params), start, limit)
	return hotels
def search_for_available_hotel_by_area(hotel_params, start=0, limit=10):
	hotels = frappe.db.get_all("Hotel", filters={hotel_params.get('location-type'): hotel_params.get("location")}, fields=["name"], order_by="hotel_priority desc", )#start=start, limit=limit
	results = {}
	for hotel in hotels:
		copy_params = hotel_params.copy()
		copy_params['location-type'] = "hotel"
		copy_params['location'] = hotel.get('name')
		hotel_data = search_for_available_hotel_by_hotel(copy_params)
		if len(hotel_data) > 0:
			results.update(hotel_data)
	return results

def search_for_available_hotel_by_hotel(hotel_params):
	hotel = frappe.get_cached_doc("Hotel", hotel_params.get("location"))
	company_class = get_company_class(hotel_params)
	if hotel.disabled:
		return {}
	hotel_rooms = get_hotel_rooms(hotel.name)
	available_rooms = {}
	for roomPax in hotel_params.get('paxInfo'):
		available_rooms[roomPax.get('roomName')] = {}
		available_rooms[roomPax.get('roomName')]['roomPax'] = roomPax
		available_rooms[roomPax.get('roomName')]['rooms'] = []
		paxRooms = filter_hotel_rooms_by_pax(hotel_rooms, roomPax, hotel.hotel_accommodation_type_rule)
		if len(paxRooms) == 0:
			return {}
		available_rooms[roomPax.get('roomName')]['rooms'] = paxRooms
		for room in available_rooms[roomPax.get('roomName')]['rooms']:
			room['room_type_name'] = frappe.db.get_value("Room Type", room.get('room_type'), "room_type")
			room['room_accommodation_type_name'] = frappe.db.get_value("Room Accommodation Type", room['room_accommodation_type'], "accommodation_type_name", cache=True)
			get_room_contracts(room, hotel_params, roomPax, company_class)
	return {
		hotel.name:{
			  "details":get_hotel_data(hotel),
			  "rooms": available_rooms
		}
	}

def get_room_contracts(room, hotel_params, roomPax, company_class):
	room['contracts'] = []
	all_room_contracts = get_all_room_contracts(room, hotel_params)
	all_room_contracts = filter_contracts(all_room_contracts, hotel_params.get('checkin'), hotel_params.get('checkout'))
	for contract in all_room_contracts:
		contract['child_rate_contract'] = frappe.db.get_value("Hotel", room.get('hotel'), "hotel_child_rate_policy", cache=True)
		contract['cancellation_policy_description'] = frappe.db.get_value("Cancellation Policy", contract.get('hotel_cancellation_policy'), "policy_description", cache=True)
		get_room_contract_price(contract, room.get('room_accommodation_type'), hotel_params.get('nationality'), company_class, roomPax, room.get('min_pax'))
	room['contracts'] = all_room_contracts
	for contract in room['contracts']:
		contract['remain_qty'] = get_contract_availabilities(contract.get('contract_id'), contract.get('from_date'), contract.get('to_date'))
	remains = [contract.get('remain_qty', 0) for contract in room['contracts']]
	if len(remains)  == 0:
		room['remain_qty'] = 0
	else:
		room['remain_qty'] = min(remains)

def get_all_room_contracts(room, hotel_params):
	contracts = frappe.db.sql("""
		SELECT 
		cntrct.name as contract_id, 
		contract_type, qty, release_days,
		check_in_from_date as from_date, check_in_to_date as to_date,
		accommodation_type_rule as hotel_accommodation_type_rule, 
		cancellation_policy as hotel_cancellation_policy
			FROM `tabHotel Room Contract` as cntrct
		WHERE hotel=%(hotel)s AND room_type=%(room_type)s
						   	AND ( now() BETWEEN cntrct.selling_from_date and cntrct.selling_to_date)
		AND (cntrct.release_days =0 or DATEDIFF(%(checkin)s, now()) > cntrct.release_days )
		AND ((%(checkin)s >= cntrct.check_in_from_date and %(checkin)s <= cntrct.check_in_to_date)
			OR ( %(checkout)s >= cntrct.check_in_from_date and  %(checkout)s <= cntrct.check_in_to_date))
		AND cntrct.docstatus=1
	""", {"hotel": room.get('hotel'), 'room_type': room.get('room_type'),
       'checkin': hotel_params.get('checkin'), 'checkout': hotel_params.get('checkout')
	   }, as_dict=True)
	
	return contracts

def get_hotel_data(hotel):
	return {
			"hotel_id": hotel.name,
			"hotel_name": hotel.hotel_name,
			"hotel_image": hotel.hotel_image,
			"address": hotel.address,
			"gps_location": hotel.gps_location,
			"star_rating": hotel.star_rating,
			"town": hotel.town,
			"area": hotel.area,
		}

def search_for_available_hotel_by_hotel_old(hotel_params):
	# Get All Hotel Rooms
	#all_rooms = get_hotel_all_rooms(hotel_params.get("location"))
	#available_rooms = {}
	# Filter Rooms by Pax
	company_class = get_company_class(hotel_params)
	all_hotel_contracts = get_hotel_contracts(
					hotel_params.get("location"),
					  hotel_params.get('checkin'), hotel_params.get('checkout'), )
	available_rooms = {}
	for roomPax in hotel_params.get('paxInfo'):
		available_rooms[roomPax.get('roomName')] = {}
		available_rooms[roomPax.get('roomName')]['contracts'] = []
		available_rooms[roomPax.get('roomName')]['roomPax'] = roomPax
		for room_type in all_hotel_contracts:
			room_type_contracts = []
			contracts = all_hotel_contracts[room_type]
			for contract in contracts:
				copy_contract = contract.copy()
				accommondation_rule = get_hotel_accommodation_type_rule(contract=copy_contract.get('contract_no'))
				room_acmnd_type = get_available_amnd_hotel_room_by_pax(accommondation_rule, roomPax)
				copy_contract['profit_margin'] = frappe.db.get_value("Hotel Room Contract", copy_contract.get('contract_no'), "profit_margin", cache=True)
				copy_contract['child_rate_contract'] = frappe.db.get_value("Hotel", copy_contract.get('hotel'), "hotel_child_rate_policy", cache=True)
				copy_contract['room_type_name'] = frappe.db.get_value("Room Type", copy_contract.get('room_type'), "room_type")
				copy_contract['room_accommodation_type'] = room_acmnd_type
				copy_contract['room_accommodation_type_name'] = frappe.db.get_value("Room Accommodation Type", room_acmnd_type, "accommodation_type_name", cache=True)
				room_type_contracts.append(copy_contract)
				get_room_contract_price(copy_contract, room_acmnd_type, hotel_params.get('nationality'), company_class, roomPax)
		
			if len(room_type_contracts) > 0:
				available_rooms[roomPax.get('roomName')]['contracts'].append(room_type_contracts)
		# if len(available_rooms[roomPax.get('roomName')]['contracts']) == 0:
		# 	available_rooms[roomPax.get('roomName')]['contracts'] = get_hotel_
	return available_rooms
	# for roomPax in hotel_params.get('paxInfo'):
	# 	room_contracts = get_hotel_contracts(
	# 				hotel_params.get("location"),
	# 				  hotel_params.get('checkin'), hotel_params.get('checkout'), 
	# 				  roomPax, hotel_params.get('nationality'))
	# 	# available_rooms[roomPax.get('roomName')] = {}
	# 	# available_rooms[roomPax.get('roomName')]['rooms'] = filter_hotel_rooms_by_pax(all_rooms, roomPax)
	# 	# if len(available_rooms[roomPax.get('roomName')]['rooms']) == 0:
	# 	# 	return {}
	# 	# available_rooms[roomPax.get('roomName')]['roomPax'] = roomPax	


	# return available_rooms

def get_hotel_contracts(hotel, checkin, checkout):
	contracts = get_hotel_availabilities(hotel, checkin, checkout)
	contracts = filter_contracts(contracts, checkin, checkout)
	return contracts

def get_room_contract_price(contract, room_acmnd_type, nationality, company_class, roomPax, min_pax):
	contract['prices'] = get_contract_prices(contract, room_acmnd_type, nationality)
	contract['prices'] = restart_price_dates(contract['prices'], contract['from_date'], contract['to_date'])
	for price in contract['prices']:
		if not price.get('selling_price'):
			get_selling_price_profit_margin_based(contract, price, room_acmnd_type)
		del price['buying_price']
		price['selling_price'] = get_room_selling_price_based_on_class(price['selling_price'], price['item_price_name'], company_class)
		price['selling_price_with_childs'] = get_room_price_with_children(roomPax, price['selling_price'], contract.get('child_rate_contract'), min_pax)
		# Child Company Price
		price['child_company_price'] = get_child_company_hotel_price(price['selling_price_with_childs'])

def get_child_company_hotel_price(selling_price):
	company_details = get_company_details()
	if company_details.get('is_child_company'):
		if company_details.get('hotel_margin'):
			return get_subagency_extra_price( selling_price, float(company_details.get('hotel_margin')))
	return selling_price
def get_room_selling_price_based_on_class(selling_price: float, item_price_name: str, company_class: dict) -> float:
	class_extra_price = frappe.db.get_value("Hotel Room Price Company", {"parent": item_price_name, "company_class": company_class.get('company_class')}, ['extra_type', 'extra_profit'])
	if not class_extra_price: return selling_price
	extra_type, extra_price = class_extra_price
	return calculate_extra_price(selling_price, extra_type, extra_price)

def get_selling_price_profit_margin_based(contract, room_price, room_acmnd_type):
	contract['profit_margin'] = frappe.db.get_value("Hotel Room Contract", contract.get('contract_id'), "profit_margin", cache=True)
	selling_price = None
	selling_currency = None
	profit_margin_doc = frappe.get_cached_doc("Profit Margin", contract.get('profit_margin'))
	profit_margin_item = None
	for item in profit_margin_doc.profit_margins:
		if item.room_type == room_acmnd_type:#contract.get('room_accommodation_type'):
			profit_margin_item = item
			break
	if profit_margin_item:
		selling_price, selling_currency = get_currency_based_price(room_price.get('buying_price'), room_price.get('buying_currency'))
		if selling_price:
			selling_price = calculate_extra_price(selling_price, profit_margin_item.get('margin_type'), profit_margin_item.get('profit_margin'))
			room_price['selling_price'] = selling_price
			room_price['selling_currency'] = selling_currency
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
	currency_rate = frappe.db.get_single_value("Currency Convertor", from_currency.lower() )
	# if not currency_rates  or currency_rates.get('success') == False:
	# 	return to_price
	# if not currency_rates.get('quotes'):
	# 	return to_price
	if not currency_rate:
		return None
	to_price = from_price / currency_rate
	return to_price



# Get Contract Price
	# every contract has multiple prices based on room_acmnd_type
	# every contract may have multiple prices based on checkin and checkout dates
	# every contract may have multiple prices based on selling_date
	# every contract may have multiple prices based on nationality
def get_contract_prices(contract, room_acmnd_type, nationality):
	selling_date = frappe.utils.nowdate()
	prices = frappe.db.sql("""
		SELECT prc.name as item_price_name , prc.selling_type, prc.hotel, 
		prc.buying_currency, prc.buying_price,
						prc.room_accommodation_type,
		prc.check_in_from_date as from_date, prc.check_in_to_date as to_date, 
		 prc.selling_currency, prc.selling_price FROM  `tabHotel Room Price` prc
		WHERE prc.room_contract=%(contract_id)s 
		AND (prc.nationality=%(nationality)s OR prc.nationality IS NULL OR prc.nationality='')
		AND (
			   prc.room_accommodation_type=%(room_accommodation_type)s 
			   )
		AND (prc.selling_from_date <= %(selling_date)s AND prc.selling_to_date >= %(selling_date)s)
		AND ((prc.check_in_from_date <= %(checkin)s AND prc.check_in_to_date >= %(checkin)s)
		OR (prc.check_in_from_date <= %(checkout)s AND prc.check_in_to_date >= %(checkout)s))
""", {
	"contract_id": contract.get('contract_id'),
	"nationality": nationality,
	"room_accommodation_type": room_acmnd_type,
	"selling_date": selling_date,
	"checkin": contract.get('from_date'),
	"checkout": contract.get('to_date')
	}, as_dict=True)
	return prices

def filter_contracts(contracts, checkin, checkout):
	# Filter Contracts by Remain Room Qty
	qtycontracts, noncontracts = filter_contracts_by_remain_qty(contracts)
	# Concat Contracts with same rome type
	if filteredContracts := concat_contracts(qtycontracts, checkin, checkout):
		return filteredContracts
	elif filteredContracts := concat_contracts(noncontracts, checkin, checkout):
		return filteredContracts
	else: return concat_contracts(contracts, checkin, checkout)

def concat_contracts(contracts, checkin, checkout):
	# room_type_contracts = {}
	# for contract in contracts:
	# 	if not room_type_contracts.get(contract.get('room_type')):
	# 		room_type_contracts[contract.get('room_type')] = []
	# 	room_type_contracts[contract.get('room_type')].append(contract)
	
	# contracts = {}
	# for room_type in room_type_contracts:
	# 	room_contracts = filter_contracts_by_dates(room_type_contracts[room_type], checkin, checkout)
	# 	if len(room_contracts) > 0:
	# 		contracts[room_type] = room_contracts
	contracts = filter_contracts_by_dates(contracts, checkin, checkout)
	return contracts
from datetime import datetime, timedelta
def convert_date_to_object(date):
	if type(date) is str:
		return datetime.strptime(date, "%Y-%m-%d").date()
	return date

def restart_price_dates(prices, checkin, checkout):
	checkin_date = convert_date_to_object(checkin)
	checkout_date = convert_date_to_object(checkout) 

	for price in prices:
		price['from_date'] = str(max([checkin_date, convert_date_to_object(price['from_date'])]))
		price['to_date'] = str(min([checkout_date, convert_date_to_object(price['to_date'])]))
	return prices

def filter_contracts_by_dates(contracts, checkin_date, checkout_date):
	checkin_date = convert_date_to_object(checkin_date)
	checkout_date = convert_date_to_object(checkout_date) + timedelta(days= - 1)

	filtered_contracts = []

	# Sort contracts by start date
	sorted_contracts = sorted(contracts, key=lambda x: convert_date_to_object(x["from_date"]))

	current_date = checkin_date

	for contract in sorted_contracts:
		from_date = convert_date_to_object(contract["from_date"])
		to_date = convert_date_to_object(contract["to_date"])

		# If there's a gap, return an empty list
		if current_date < from_date:
			return []

		# Extend the current date range if the current contract covers it
		if from_date <= current_date <= to_date:
			contract['from_date'] = str(max([current_date, from_date]))
			contract['to_date'] = str(min([to_date, checkout_date]))
			current_date = to_date + timedelta(days=1)
			filtered_contracts.append(contract)
		# If the current date range covers the requested date range, return the result
		if current_date > checkout_date:
			return filtered_contracts

	# If we reach this point, there's a gap at the end, return an empty list
	return []


def test_filter_contracts_by_dates():
	contracts = [
		{"contract_id": "1", "from_date": "2019-01-01", "to_date": "2019-01-10"},
		{"contract_id": "2", "from_date": "2019-01-10", "to_date": "2019-01-20"},
		{"contract_id": "3", "from_date": "2019-01-01", "to_date": "2019-01-30"},
		{"contract_id": "4", "from_date": "2019-01-30", "to_date": "2019-02-10"},
		{"contract_id": "5", "from_date": "2019-02-10", "to_date": "2019-02-20"},
		{"contract_id": "6", "from_date": "2019-02-20", "to_date": "2019-02-28"}
	]
	test_1_checkin = "2019-01-05"
	test_1_checkout = "2019-01-15"
	test_2_checkin = "2019-02-05"
	test_2_checkout = "2019-02-15"
	test_1_output = [
				{"contract_id": "3", "from_date": "2019-01-01", "to_date": "2019-01-30"},
	]
	test_2_output = [
				{"contract_id": "4", "from_date": "2019-01-30", "to_date": "2019-02-10"},
				{"contract_id": "5", "from_date": "2019-02-10", "to_date": "2019-02-20"},
	]
	assert filter_contracts_by_dates(contracts, test_1_checkin, test_1_checkout) == test_1_output
	assert filter_contracts_by_dates(contracts, test_2_checkin, test_2_checkout) == test_2_output


def filter_contracts_by_remain_qty(contracts):
	contracts = [contract for contract in contracts if contract.get('qty') > 0]
	noncontracts = [contract for contract in contracts if contract.get('qty') == 0]
	return contracts, noncontracts

def get_contract_availabilities(contract, checkin, checkout):
	room_qty = frappe.db.sql("""
		SELECT min(available_qty) as qty FROM `tabRoom Availability` as tbl1
		WHERE tbl1.contract_no=%(contract_no)s AND tbl1.date >= %(checkin)s AND tbl1.date <= %(checkout)s
	""", {"contract_no": contract, 
       "checkin": checkin, "checkout": checkout}, as_dict=True)
	if len(room_qty) > 0:
		return room_qty[0]['qty']
	return 0

def get_hotel_availabilities(hotel, checkin, checkout):
	selling_date = frappe.utils.nowdate()
	room_qty = frappe.db.sql("""
		SELECT 
			contract_no , hotel, min(available_qty) as remain_qty, room_type,
			release_days,
			min(date) as from_date, max(date) as to_date, count(name) as nights  
		FROM `tabRoom Availability`
		WHERE hotel=%(hotel)s AND date >= %(checkin)s AND date < %(checkout)s
		AND (selling_from_date <= %(selling_date)s AND selling_to_date >= %(selling_date)s)
		AND (release_days =0 or DATEDIFF(%(checkin)s, now()) > release_days )
		GROUP BY contract_no;
	""", {"hotel": hotel,	"checkin": checkin, 
	   "checkout": checkout, "selling_date": selling_date}, as_dict=True)
	return room_qty

def get_hotel_accommodation_type_rule(hotel=None,contract=None):
	if hotel:
		return frappe.db.get_value("Hotel", hotel, "hotel_accommodation_type_rule", cache=True)
	elif contract:
		return frappe.db.get_value("Hotel Room Contract", contract, "accommodation_type_rule", cache=True)
	else:
		return None
def filter_hotel_rooms_by_pax(all_rooms, roomPax, room_accommodation_type):
	available_rooms = []
	for room in all_rooms:
		# room_accommodation_type = room.get("hotel_accommodation_type_rule")
		room_accommodation_type_doc = frappe.get_cached_doc("Room Accommodation Type Rule", room_accommodation_type)
		for room_type in room_accommodation_type_doc.rules:
			if room_type.room_type == room.get('room_accommodation_type'):
				if is_room_suitable_for_pax(room_type, roomPax):
					# return room
					room['min_pax'] = room_type.get('min_pax')
					available_rooms.append(room)
	return available_rooms
def get_available_amnd_hotel_room_by_pax(amnd_rule, roomPax):
	room_accommodation_type_doc = frappe.get_cached_doc("Room Accommodation Type Rule", amnd_rule)
	for room_type in room_accommodation_type_doc.rules:
		if is_room_suitable_for_pax(room_type, roomPax):
			return room_type.room_type
	return None

def is_room_suitable_for_pax(room_rule, pax_info):
	adults =int(pax_info.get('adults'))
	children = int(pax_info.get('children'))
	for childPax in pax_info.get('childrenInfo'):
		if room_rule.get('max_child_age'):
			if int(childPax) > room_rule.get('max_child_age'):
				adults += 1
				children -= 1
	
	pax = adults + children
	if pax < room_rule.get('min_pax') or pax > room_rule.get('max_pax'): return False
	if adults < room_rule.get('min_adults') or adults > room_rule.get('max_adults'): return False
	if children < room_rule.get('min_childs') or children > room_rule.get('max_childs'): return False
	return True

def get_hotel_rooms(hotel):
	all_rooms  = frappe.db.sql("""
		select 
		tbl2.room_type, 
		tbl2.room_accommodation_type, 
		tbl2.name as room_id,
		tbl2.room_image,
		tbl2.hotel
		FROM `tabHotel Room` tbl2 
		WHERE tbl2.disabled=0 AND tbl2.hotel=%(hotel)s
		;
	""", {"hotel": hotel }, as_dict=True)
	for room in all_rooms:
		room['features'] =  []
	return all_rooms
@frappe.whitelist()
def ask_for_availability(room_id, room_qty):
	now_datetime = frappe.utils.now()
	inquiries = frappe.db.sql("""
		select name from `tabHotel Inquiry Request`
		WHERE customer=%(customer)s AND room=%(room)s AND 
		(docstatus=0 OR valid_datetime > %(now_datetime)s)
	""", {"customer": frappe.session.user, "room": room_id, "now_datetime": now_datetime})
	if len(inquiries) > 0:
		return {
			"success_key": 0,
			"message": _("You have asked for this room before.")
		}
	frappe.get_doc({
		"doctype": "Hotel Inquiry Request", 
		"customer": frappe.session.user,
		"room": room_id,
		"qty": room_qty
	}).insert(ignore_permissions=True)
	return {
		"success_key": 1,
		"message": _("The request has been submitted successfully")
	}

"""
Params {
	from-location-type: ["airport", "hotel","area"],
	to-location-type: ["airport", "hotel","area"],
	from-location: ,
	to-location: ,
	transfer-date: ,
	note?: ,
	transfer-type: ["vip", "group"],
	flight-no?:,
	paxes: {
		adults: num,
		children: num,
		child-ages: [num]
	}
}
return {

}
"""
@frappe.whitelist()
def search_for_transfer():
	params = frappe.form_dict
	return get_available_transfers(params)

"""
Params {
	from-location-type: ["hotel","area"],
	from-location: ,
	tour-date: ,
	tour-id: ,
	tour-type: ["vip", "premium-group", "economic-group"],
	paxes: {
		adults: num,
		children: num,
		child-ages: [num]
	}
}
return {
	transfer_type: ,
	transfer_price: ,
	transfer_details: {
		transfer_type: ,
		transfer_image: ,
	},
	search_params: {
		params: "",
		from_postal_code: "",
	}

}
"""
@frappe.whitelist()
def get_tour_price():
	params = frappe.form_dict
	return get_available_tours(params)

@frappe.whitelist()
def get_search_results(search):
	room_results = frappe.db.get_value("Search Result", {"name": search, "user": frappe.session.user}, "room_results")
	return room_results

@frappe.whitelist()
def set_new_search_results(search, hotel_params=None, transfer_params=None, tour_params=None):
	search_doc = frappe.get_doc("Search Result", 
				{"name": search, "user": frappe.session.user})
	if hotel_params:
		search_doc.hotel_params = hotel_params
	if transfer_params:
		search_doc.transfer_params = transfer_params
	if tour_params:
		search_doc.tour_params = tour_params
	search_doc.save(ignore_permissions=True)
	return search

def get_room_price_with_children(pax, selling_price, hotel_child_rate_policy, min_pax):
	room_price = selling_price
	child_policy = frappe.get_cached_doc("Child Rate Policy", hotel_child_rate_policy)
	adults = int(pax.get('adults'))
	if pax:
		child_ages = [int(child) for  child in pax.get('childrenInfo')]
		child_ages.sort()
		if adults < min_pax:
			while adults < min_pax and len(child_ages) > 0:
				adults += 1
				child_ages.pop()
		adult_price = selling_price / float(adults)
		child_order = 0
		for child in child_ages:
			child_order += 1
			for plc in child_policy.policy_details:
				if int(plc.get('room_child_order')) == child_order:
					if child >= plc.get('from_age') and child <= plc.get('to_age'):
						room_price += ((adult_price * plc.get('adult_price_percentage')) / 100)
						break
	return room_price

@frappe.whitelist()
def get_transfer_search_results(invoiceId, transfer_params):
	if type(transfer_params) == str:
		transfer_params = json.loads(transfer_params)
	available_transfers = {}
	for tt in transfer_params:
		transfer = transfer_params[tt]
		available_transfers[tt] = get_available_transfers(transfer)
	return available_transfers

@frappe.whitelist()
def get_tour_search_results(invoiceId, tour_params):
	if type(tour_params) == str:
		tour_params = json.loads(tour_params)
	available_tours = {}
	return  get_available_tours_and_prices(tour_params)
