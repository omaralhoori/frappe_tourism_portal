import frappe


def get_portal_setting(fieldname):
    return frappe.db.get_single_value("Tourism Portal Settings", fieldname)

def get_site_logo():
    return frappe.db.get_single_value("Website Settings", "brand_html")

def get_site_name():
    return frappe.db.get_single_value("")

def get_room_extras(hotel):
    return frappe.db.get_all("Hotel Extra Service Item", {"parent": hotel}, ['service', 'extra_price_type', 'extra_price'])

def delete_expired_invoices():
    expired_invoices = frappe.db.get_all("Sales Invoice", {"session_expires": ["<", frappe.utils.now()], "docstatus": 0})
    for invoice in expired_invoices:
        frappe.delete_doc("Sales Invoice", invoice['name'], ignore_permissions=True)
        # frappe.db.commit()


def get_location_postal_code(location_type, location):
    area = None
    if location_type == 'area':
        area = location
    elif location_type == 'hotel':
        area = frappe.db.get_value("Hotel", location, "area", cache=True)
    elif location_type =='airport':
        area = frappe.db.get_value("Airport", location, 'airport_area', cache=True)
    if not area:
        frappe.throw("Please enter valid location type")
    return frappe.db.get_value("Area", area, 'postal_code', cache=True)

def get_location_city(location_type, location):
    area = None
    if location_type == 'area':
        area = location
    elif location_type == 'hotel':
        area = frappe.db.get_value("Hotel", location, "area", cache=True)
    elif location_type =='airport':
        area = frappe.db.get_value("Airport", location, 'airport_area', cache=True)
    if not area:
        frappe.throw("Please enter valid location type")
    town = frappe.db.get_value("Area", area, 'town', cache=True)
    city = frappe.db.get_value("Town", town, 'city', cache=True)
    return city


def calculate_extra_price(selling_price: float, extra_type: str, extra_price: float) -> float:
	if extra_type == 'Amount':
			selling_price += extra_price
	else:
		selling_price += (selling_price * extra_price) / 100
	return selling_price 

def calculate_discount_price(selling_price, extra_type, extra_price):
	if extra_type == 'Amount':
			selling_price -= extra_price
	else:
		selling_price -= (selling_price * extra_price) / 100
	return selling_price 

def get_date_weekday(date):
    if type(date) == str:
        date = frappe.utils.get_datetime(date)
    #weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday =  frappe.utils.get_weekday(date)
    #print(weekday_number)
    return weekday#weekdays[weekday_number]