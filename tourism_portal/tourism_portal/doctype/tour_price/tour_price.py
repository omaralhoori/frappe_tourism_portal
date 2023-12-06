# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from tourism_portal.utils import get_location_postal_code

class TourPrice(Document):
	pass




def get_available_tours(params):
	"""
	Get available tours based on the given parameters.

	Args:
		params (dict): A dictionary containing the tour parameters.

	Returns:
		list: A list of available tours.

	"""
	check_tour_params(params)
	from_postal_code = get_location_postal_code(params['from-location-type'], params['from-location'])
	tour_id = params['tour-id']
	where_stmt = ""
	if params['tour-type'] == "vip":
		search_columns = "vip.transfer_type, vip.transfer_price"
		join_table = "INNER JOIN `tabVIP Transfer Price` vip ON vip.parent=tp.name and vip.parenttype='Tour VIP Price'"
		parenttype = "Tour VIP Price"
		where_stmt = "AND tp.pickup_postal_code=%(from_postal_code)s"
	elif params['tour-type'] == "premium-group":
		search_columns = "tp.adult_premium_price as group_adult_price, tp.tour_child_policy"
		join_table = ""
		parenttype = "Tour Price"
	elif params['tour-type'] == "economic-group":
		search_columns = "tp.adult_economic_price as group_adult_price, tp.tour_child_policy"
		join_table = ""
		parenttype = "Tour Price"
	available_transfers = frappe.db.sql("""
	SELECT {search_columns} FROM `tab{parenttype}` tp
	{join_table}
	WHERE tour_type=%(tour_id)s {where_stmt}
	""".format(where_stmt=where_stmt, search_columns=search_columns, join_table=join_table, parenttype=parenttype),
	{"from_postal_code": from_postal_code, "tour_id": tour_id,
	 "tour_date": params['tour-date']}, as_dict=True)    
	transfer_price = 0
	trasfers = []
	search_params = {
		"params": params,
		"from_postal_code": from_postal_code,
		"tour_id": tour_id
	}
	if params['tour-type'] == "vip":
		for available_transfer in available_transfers:
			if check_available_vip_transfer(available_transfer, params['paxes']):
				trasfers.append(available_transfer)
	elif params['tour-type'] == "premium-group" or params['tour-type'] == "economic-group":
		transfer_price = get_group_transfer_price(params['paxes'], available_transfers)
		if not transfer_price:
			return []
		transfer_type = "group_transfer"
		trasfers.append({
			"transfer_type": transfer_type,
			"tour_type": params['tour-type'],
			"transfer_price": transfer_price
		})
	for transfer in trasfers:
		transfer['transfer_details'] = get_transfer_details(transfer)
		transfer['search_params'] = search_params
	return trasfers

def get_transfer_details(transfer):
	return frappe.db.get_value("Transfer Type", transfer['transfer_type'],
	['transfer_type', 'transfer_image', 'transfer_description'], as_dict=True)

def get_group_transfer_price(paxes, available_transfers):
	"""
	Get the group transfer price based on the given passenger details and available transfers.

	Args:
		paxes (dict): The passenger details including number of adults, children, and child ages.
		available_transfers (list): A list of available transfers.

	Returns:
		float: The group transfer price.
	"""                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
	if len(available_transfers) == 0:
		return 0
	child_policy = available_transfers[0]['tour_child_policy']
	if not child_policy:
		return 0
	adult_price = available_transfers[0]['group_adult_price']
	policies = frappe.db.get_all("Transfer Child Price", {"parent": child_policy},
	 ["child_order", "from_age", "to_age", "adult_price_percentage"], order_by="idx, child_order")
	transfer_price = 0
	adults = paxes['adults']
	children = paxes['children']
	child_ages = paxes['child-ages']
	child_ages.sort()
	child_prices = []
	for child_age in child_ages:
		for policy in policies:
			if policy['from_age'] <= child_age <= policy['to_age'] and policy['child_order'] == len(child_prices) + 1:
				child_prices.append(adult_price * policy['adult_price_percentage'] / 100)
				break
			elif policy['from_age'] <= child_age <= policy['to_age'] and policy['child_order'] == 0:
				child_prices.append(adult_price * policy['adult_price_percentage'] / 100)
				break
	adults = adults + children - len(child_prices)
	transfer_price = adult_price * adults
	for child_price in child_prices:
		transfer_price += child_price
	return transfer_price

def check_available_vip_transfer(available_transfer, paxes):
	"""
	Check if a VIP transfer is available based on the available transfer and passenger details.

	Args:
		available_transfer (dict): The available transfer details.
		paxes (dict): The passenger details including number of adults, children, and child ages.

	Returns:
		bool: True if a VIP transfer is available, False otherwise.
	"""
	capacities = frappe.db.get_all("Transfer Capacity", {"parent": available_transfer['transfer_type']}, 
	["min_adults", "max_adults", "min_child", "max_child", "max_child_age"])
	available = False
	
	for capacity in capacities:
		adults = paxes['adults']
		children = paxes['children']
		child_ages = paxes['child-ages']
		child_ages.sort()
		allowed_childs = 0
		for child_age in child_ages:
			if child_age <= capacity['max_child_age']:
				allowed_childs += 1
		adult_childs = - (allowed_childs - children)
		adults = adults + adult_childs
		if allowed_childs > capacity['max_child']:
			over_childs = allowed_childs - capacity['max_child']
			allowed_childs = capacity['max_child']
			adults = adults + over_childs
		if capacity['min_adults'] <= adults <= capacity['max_adults'] and \
			capacity['min_child'] <= allowed_childs <= capacity['max_child']:
					return True
	return available
	
def check_tour_params(params):
	if not params.get('from-location-type'):
		frappe.throw("Please enter from location type")
	if not params.get('from-location'):
		frappe.throw("Please enter from location")
	if not params.get('tour-date'):
		frappe.throw("Please enter tour date")
	if not params.get('tour-id'):
		frappe.throw("Please enter tour id")
	if not params.get('tour-type'):
		frappe.throw("Please enter tour type")