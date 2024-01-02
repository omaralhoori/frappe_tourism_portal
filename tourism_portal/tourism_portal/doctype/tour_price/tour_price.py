# Copyright (c) 2023, omaralhoori and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from tourism_portal.utils import calculate_discount_price, calculate_extra_price, get_location_postal_code, get_postal_code_transfer_area

class TourPrice(Document):
	pass


def get_available_tours_and_prices(params):
	available_tours = []
	tour_packages = []
	paxes = params['paxes']
	for tour in params.get('tours'):
		params['tour-id'] = tour#params['tours'][tour]
		params['tour-date'] = params['checkin']
		# VIP Tours Return Price For Each Tour
		if params['tour-type'] == 'vip':
			tour_details = get_available_tours(params)
			if tour_details:
				available_tours.append({
					"tour_id": tour,#params['tours'][tour],
					"pickup": tour_details['search_params']['params']['location'],
					"tour_price": tour_details['transfer_price'],
					"tour_name": tour_details['search_params']['tour_name'],
					"tour_description": tour_details['search_params']['tour_description'],
					"tour_type": "vip",
					"tour_date": params['tour-date']
				})
		else:
			tour_details = get_available_tours(params)
			available_tours.append({
				"tour_id":tour,# params['tours'][tour],
				"pickup": tour_details['search_params']['params']['location'],
				"adult_price": tour_details['adult_price'],
				"children_prices": tour_details['children_prices'],
				"tour_name": tour_details['search_params']['tour_name'],
				"tour_description": tour_details['search_params']['tour_description'],
				"tour_type": "package",
				"tour_date": params['tour-date']
			})
	available_tours = sorted(available_tours, key=lambda x: x['tour_date'])
	if params['tour-type'] in ('group-premium', 'group-economic', 'package'):
		for adultPax in range(int(paxes['adults'])):
			tour_packages.append({
				"tour_type": "package",
				"pickup": available_tours[0]['pickup'],
				"tours": [ {
					"tour_date": avT['tour_date'], 
					"tour_id": avT['tour_id'],
					"pickup": avT['pickup'],
					"tour_name": avT['tour_name'],
					"tour_description": avT['tour_description'],
						"tour_type": avT['tour_type'],
						"tour_price": avT['adult_price'],
						} for avT in available_tours],
				"package_price": 0,

			})
			for tt in tour_packages[-1]['tours']:
				tour_packages[-1]['package_price'] += tt['tour_price']
		for childAge in range(int(paxes['children'])):
			pp = []
			for avT in available_tours:
				childPkg = {
					"tour_date": avT['tour_date'], 
					"tour_id": avT['tour_id'],
					"tour_type": avT['tour_type'],
					"tour_price": avT['children_prices'][childAge],
					"tour_name": avT['tour_name'],
					"tour_description": avT['tour_description'],
					}
				pp.append(childPkg) 
			tour_packages.append({
				"tour_type": "package",
				"pickup": available_tours[0]['pickup'],
				"tours": pp,
				"package_price": 0,
			})
			for tt in tour_packages[-1]['tours']:
				tour_packages[-1]['package_price'] += tt['tour_price']
		
		# Group Tours Return Price For Each Package
	if params['tour-type'] == 'vip':
		return available_tours
	else:
		
		return tour_packages
def get_available_tours(params):
	"""
	Get available tours based on the given parameters.

	Args:
		params (dict): A dictionary containing the tour parameters.

	Returns:
		list: A list of available tours.

	"""
	check_tour_params(params)
	from_postal_code = get_location_postal_code(params['location-type'], params['location'])
	from_area = get_postal_code_transfer_area(from_postal_code)
	tour_id = params['tour-id']
	where_stmt = ""
	if params['tour-type'] == "vip":
		search_columns = "vip.transfer_type, vip.transfer_price"
		join_table = "INNER JOIN `tabVIP Transfer Price` vip ON vip.parent=tp.name and vip.parenttype='Tour VIP Price'"
		parenttype = "Tour VIP Price"
		where_stmt = "WHERE tour_type=%(tour_id)s AND tp.pickup_postal_code=%(from_postal_code)s"
	elif params['tour-type'] == "group-premium":
		search_columns = "tp.adult_premium_price as group_adult_price, tp.tour_child_policy"
		join_table = ""
		parenttype = "Tour Price"
		where_stmt = "WHERE tour_type=%(tour_id)s"
	elif params['tour-type'] == "group-economic":
		search_columns = "tp.adult_economic_price as group_adult_price, tp.tour_child_policy"
		join_table = ""
		parenttype = "Tour Price"
		where_stmt = "WHERE tour_type=%(tour_id)s"
	elif params['tour-type'] == "package":
		search_columns = "tp.package_price as group_adult_price, tp.tour_child_policy"
		join_table = ""
		parenttype = "Tour Package"
		where_stmt = "WHERE tp.name=%(tour_id)s"
	available_transfers = frappe.db.sql("""
	SELECT {search_columns} FROM `tab{parenttype}` tp
	{join_table}
	{where_stmt}
	""".format(where_stmt=where_stmt, search_columns=search_columns, join_table=join_table, parenttype=parenttype),
	{"from_postal_code": from_area, "tour_id": tour_id,
	 "tour_date": params['tour-date']}, as_dict=True)    
	transfer_price = 0
	trasfers = []
	if params['tour-type'] == "package":
		tour_data = frappe.db.get_value("Tour Package", tour_id, ["package_name", "description" ])
	else:
		tour_data = frappe.db.get_value("Tour Type", tour_id, ["tour_name", "tour_description" ])
	search_params = {
		"params": params,
		"from_postal_code": from_postal_code,
		'tour_date': params['tour-date'],
		"tour_id": tour_id,
		"tour_name": tour_data[0],
		"tour_description": tour_data[1],
	}
	if params['tour-type'] == "vip":
		for available_transfer in available_transfers:
			if check_available_vip_transfer(available_transfer, params['paxes']):
				trasfers.append(available_transfer)
	elif params['tour-type'] == "group-premium" or params['tour-type'] == "group-economic" or params['tour-type'] == "package":
		transfer_price = get_group_transfer_price(params['paxes'], available_transfers)
		if not transfer_price:
			return None
		transfer_type = "group_transfer"
		trasfers.append({
			"transfer_type": transfer_type,
			"tour_type": params['tour-type'],
			"adult_price": transfer_price[0],
			"children_prices": transfer_price[1]
		})
	for transfer in trasfers:
		transfer['transfer_details'] = get_transfer_details(transfer)
		transfer['search_params'] = search_params
	if params['tour-type'] == "vip":
		trasfers = sorted(trasfers, key=lambda x: x['transfer_price'])
	return trasfers[0] if len(trasfers) > 0 else None

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
		return None
	child_policy = available_transfers[0]['tour_child_policy']
	if not child_policy:
		return None
	adult_price = available_transfers[0]['group_adult_price']
	policies = frappe.db.get_all("Transfer Child Price", {"parent": child_policy},
	 ["child_order", "from_age", "to_age", "adult_price_percentage"], order_by="idx, child_order")
	transfer_price = 0
	adults = int(paxes['adults'])
	children = int(paxes['children'])
	child_ages = paxes['child-ages']
	child_ages.sort()
	child_prices = []
	for child_age in child_ages:
		for policy in policies:
			if policy['from_age'] <= int(child_age) <= policy['to_age'] and policy['child_order'] == len(child_prices) + 1:
				child_prices.append(adult_price * policy['adult_price_percentage'] / 100)
				break
			elif policy['from_age'] <= int(child_age) <= policy['to_age'] and policy['child_order'] == 0:
				child_prices.append(adult_price * policy['adult_price_percentage'] / 100)
				break
	adults = adults + children - len(child_prices)
	transfer_price = adult_price * adults
	for child_price in child_prices:
		transfer_price += child_price
	return adult_price, child_prices

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
	print("paxes", paxes)
	for capacity in capacities:
		adults = int(paxes['adults'])
		children = int(paxes['children'])
		child_ages = paxes['child-ages']
		child_ages.sort()
		allowed_childs = 0
		for child_age in child_ages:
			if int(child_age) <= capacity['max_child_age']:
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
	if not params.get('location-type'):
		frappe.throw("Please enter from location type")
	if not params.get('location'):
		frappe.throw("Please enter from location")
	if not params.get('tour-date'):
		frappe.throw("Please enter tour date")
	if not params.get('tour-id'):
		frappe.throw("Please enter tour id")
	if not params.get('tour-type'):
		frappe.throw("Please enter tour type")

def apply_tour_discount(tourPackages, total_nights=None):
	tour_discount = frappe.get_single("Tour Discount")
	tour_total_price = 0
	new_tour_total_price = 0
	if total_nights:
		for free_tour in tour_discount.free_tour:
			if free_tour.min_nights <= total_nights:
				for package in tourPackages:
					updatePackage = False
					for tour in package['tours']:
						if tour['tour_id'] == free_tour.tour_type:
							tour['tour_price'] = calculate_discount_price(tour['tour_price'], "Percent", free_tour.discount)
							updatePackage = True
							break

					if updatePackage:
						package['package_price'] = 0
						for tour in package['tours']:
							package['package_price'] += tour['tour_price']
							
	new_tour_total_price = tour_total_price
	pacakge_discounts = tour_discount.package_discount
	pacakge_discounts.sort(key=lambda x: x.min_tour_count, reverse=True)
	for package in tourPackages:
		for package_discount in pacakge_discounts:
			if package_discount.min_tour_count <= len(package.get('tours')):
				package['package_price'] = calculate_discount_price(package.get('package_price'), package_discount.discount_type, package_discount.discount)
				break
	return tourPackages