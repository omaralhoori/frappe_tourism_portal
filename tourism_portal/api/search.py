import frappe
from frappe import _
from tourism_portal.tourism_portal.doctype.tour_price.tour_price import get_available_tours
# from tourism_portal.www.search.index import get_available_hotel_rooms
from tourism_portal.tourism_portal.doctype.transfer_price.transfer_price import get_available_transfers
import json

from tourism_portal.utils import get_portal_setting
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


@frappe.whitelist(allow_guest=True)
def get_available_hotels():
    search_params = frappe.form_dict.hotels_params#json.loads(frappe.form_dict)
    return get_available_hotel_rooms(search_params)


def get_available_hotel_rooms(search_params):
	
	hotels = {}
	for search in search_params:
		hotel = search_params[search]
		avilables = search_for_available_hotel(hotel)
		hotels[search] = avilables
	return hotels

def search_for_available_hotel(hotel):
	if hotel["location-type"] == "area" or hotel["location-type"] == "town":
		return search_for_available_hotel_by_area(hotel)
	elif hotel["location-type"] == "hotel":
		return search_for_available_hotel_by_hotel(hotel)
	else:
		return {}
		
def search_for_available_hotel_by_area(hotel):
	return {}

def search_for_available_hotel_by_hotel(hotel_params):
	# Get All Hotel Rooms
	all_rooms = get_hotel_all_rooms(hotel_params.get("location"))
	available_rooms = {}
	# Filter Rooms by Pax
	for roomPax in hotel_params.get('paxInfo'):
		available_rooms[roomPax.get('roomName')] = {}
		available_rooms[roomPax.get('roomName')]['rooms'] = filter_hotel_rooms_by_pax(all_rooms, roomPax)
		if len(available_rooms[roomPax.get('roomName')]['rooms']) == 0:
			return {}
		available_rooms[roomPax.get('roomName')]['roomPax'] = roomPax
	
	# Get Room Contracts
	for roomName in available_rooms:
		rooms = available_rooms[roomName]['rooms']
		for room in rooms:
			room_contracts = get_hotel_contracts(hotel_params.get("location"), hotel_params.get('checkin'), hotel_params.get('checkout'), room.get('room_accommodation_type'), hotel_params.get('nationality'))
			
			room['contracts'] = room_contracts


	return available_rooms

def get_hotel_contracts(hotel, checkin, checkout, room_acmnd_type, nationality):
	contracts = get_hotel_availabilities(hotel, checkin, checkout)
	contracts = filter_contracts(contracts, checkin, checkout)
	for roomType in contracts:
		room_contracts = contracts[roomType]
		for contract in room_contracts:
			contract['prices'] = get_contract_prices(contract, room_acmnd_type, nationality)
	return contracts

# Get Contract Price
	# every contract has multiple prices based on room_acmnd_type
	# every contract may have multiple prices based on checkin and checkout dates
	# every contract may have multiple prices based on selling_date
	# every contract may have multiple prices based on nationality
def get_contract_prices(contract, room_acmnd_type, nationality):
	selling_date = frappe.utils.nowdate()
	prices = frappe.db.sql("""
		SELECT prc.name as item_price_name ,prc.company_class, prc.selling_type, prc.hotel, 
		prc.buying_currency, prc.buying_price,
		prc.check_in_from_date, prc.check_in_to_date, 
		 prc.selling_currency, prc.selling_price FROM  `tabHotel Room Price` prc
		WHERE prc.room_contract=%(contract_id)s 
		AND (prc.nationality=%(nationality)s OR prc.nationality IS NULL OR prc.nationality='')
		AND (
			   prc.room_accommodation_type=%(room_accommodation_type)s 
			   OR prc.room_accommodation_type IS NULL  
			   OR prc.room_accommodation_type='')
		AND (prc.selling_from_date <= %(selling_date)s AND prc.selling_to_date >= %(selling_date)s)
		AND ((prc.check_in_from_date <= %(checkin)s AND prc.check_in_to_date >= %(checkin)s)
		OR (prc.check_in_from_date <= %(checkout)s AND prc.check_in_to_date >= %(checkout)s))
""", {
	"contract_id": contract.get('contract_no'),
	"nationality": nationality,
	"room_accommodation_type": room_acmnd_type,
	"selling_date": selling_date,
	"checkin": contract.get('from_date'),
	"checkout": contract.get('to_date')
	}, as_dict=True)
	return prices

def filter_contracts(contracts, checkin, checkout):
	# Filter Contracts by Remain Room Qty
	contracts = filter_contracts_by_remain_qty(contracts)
	# Concat Contracts with same rome type
	contracts = concat_contracts(contracts, checkin, checkout)
	return contracts

def concat_contracts(contracts, checkin, checkout):
	room_type_contracts = {}
	for contract in contracts:
		if not room_type_contracts.get(contract.get('room_type')):
			room_type_contracts[contract.get('room_type')] = []
		room_type_contracts[contract.get('room_type')].append(contract)
	
	contracts = {}
	for room_type in room_type_contracts:
		room_contracts = filter_contracts_by_dates(room_type_contracts[room_type], checkin, checkout)
		if len(room_contracts) > 0:
			contracts[room_type] = room_contracts
	return contracts
from datetime import datetime, timedelta
def convert_date_to_object(date):
	if type(date) is str:
		return datetime.strptime(date, "%Y-%m-%d").date()
	return date
def filter_contracts_by_dates(contracts, checkin_date, checkout_date):
	checkin_date = convert_date_to_object(checkin_date)
	checkout_date = convert_date_to_object(checkout_date)

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
			current_date = to_date + timedelta(days=1)
			filtered_contracts.append(contract)

		# If the current date range covers the requested date range, return the result
		if current_date >= checkout_date:
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
	contracts = [contract for contract in contracts if contract.get('remain_qty') > 0]
	return contracts

def get_contract_availabilities(contract, checkin, checkout):
	room_qty = frappe.db.sql("""
		SELECT min(available_qty) as qty FROM `tabRoom Availability`
		WHERE contract_no=%(contract_no)s AND date >= %(checkin)s AND date < %(checkout)s
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
		

def filter_hotel_rooms_by_pax(all_rooms, roomPax):
	available_rooms = []
	for room in all_rooms:
		room_accommodation_type = room.get("hotel_accommodation_type_rule")
		room_accommodation_type_doc = frappe.get_cached_doc("Room Accommodation Type Rule", room_accommodation_type)
		for room_type in room_accommodation_type_doc.rules:
			if room_type.room_type == room.get('room_accommodation_type'):
				if is_room_suitable_for_pax(room_type, roomPax):
					available_rooms.append(room)
	return available_rooms

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

def get_hotel_all_rooms(hotel):
	all_rooms  = frappe.db.sql("""
		select 
		tbl1.name as hotel_id, tbl1.hotel_name,
		tbl1.hotel_image, tbl1.address, tbl1.gps_location, tbl1.star_rating,
		tbl2.room_type, tbl2.room_accommodation_type, 
		tbl2.name as room_id,
		tbl2.room_image,
		tbl1.hotel_child_rate_policy,
		tbl1.hotel_accommodation_type_rule,
		tbl1.hotel_cancellation_policy
		FROM `tabHotel Room` tbl2 
		INNER JOIN `tabHotel` tbl1 ON tbl1.name=tbl2.hotel
		WHERE	tbl2.disabled=0 AND tbl1.disabled=0  AND tbl1.name=%(hotel)s
		;
	""", {"hotel": hotel }, as_dict=True)
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
def set_new_search_results(search, params):
	search_doc = frappe.get_doc("Search Result", 
				{"name": search, "user": frappe.session.user})
	search_doc.hotel_params = params
	search_doc.save(ignore_permissions=True)
	return search