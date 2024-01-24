import frappe
from frappe.tests.utils import FrappeTestCase


def get_portal_setting(fieldname):
    return frappe.db.get_single_value("Tourism Portal Settings", fieldname)

def get_print_settings(fieldname):
    return frappe.db.get_single_value("Invoice Print Settings", fieldname)

def format_file_link_print(file_url):
        return frappe.utils.get_url(file_url)

def get_site_logo(src=False):
    if src:
         get_portal_setting("site_logo")
    return frappe.db.get_single_value("Website Settings", "brand_html")

def get_site_name():
    return frappe.db.get_single_value("")

def get_room_extras(hotel):
    extras = frappe.db.get_all("Hotel Extra Service Item", {"parent": hotel, "parenttype": "Hotel"}, ['service', 'extra_price_type', 'extra_price'])
    return extras

def get_room_boards(hotel):
    boards = frappe.db.get_all("Hotel Boarding Table", {"parent": hotel, "parenttype": "Hotel"}, ['boarding_type', 'extra_price_type', 'extra_price'], order_by="idx")
    return boards

def get_room_beds(room_type):
    return frappe.db.sql("""
    SELECT tbl2.type_code, tbl2.bed_type
        FROM `tabRoom Accommodation Bed Type item` as tbl1
        INNER JOIN `tabRoom Bed Type` as tbl2 on tbl1.bed_type=tbl2.name
        WHERE tbl1.parent=%(room_type)s
""",{"room_type": room_type}, as_dict=True)

def delete_expired_invoices():
    expired_invoices = frappe.db.get_all("Sales Invoice", {"session_expires": ["<", frappe.utils.now()], "docstatus": 0})
    for invoice in expired_invoices:
        frappe.delete_doc("Sales Invoice", invoice['name'], ignore_permissions=True)
        # frappe.db.commit()

def get_absolute_path(file_name):
	if(file_name.startswith('/files/')):
		file_path = f'{frappe.utils.get_bench_path()}/sites/{frappe.utils.get_site_base_path()[2:]}/public{file_name}'
	if(file_name.startswith('/private/')):
		file_path = f'{frappe.utils.get_bench_path()}/sites/{frappe.utils.get_site_base_path()[2:]}{file_name}'
	return file_path

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

def get_postal_code_transfer_area(postal_code):
    return frappe.db.get_value("Postal Code Item", {"postal_code": postal_code}, 'parent')

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
import datetime
def get_cancellation_refund(policy, total_price, check_in, check_out, day_margin=0, day_start_hour=12):
    refund = 0
    policy = frappe.get_doc("Cancellation Policy", policy)
    if type(check_in) == str:
        check_in = frappe.utils.datetime.datetime.strptime(check_in, "%Y-%m-%d").date()
    if type(check_out) == str:
        check_out = frappe.utils.datetime.datetime.strptime(check_out, "%Y-%m-%d").date()
    total_price = float(total_price)
    # cancellations = frappe.db.get_all("Cancellation Policy Item", 
    #                                 {"parent": policy}, 
    #         ['duration_type', 'duration', 'refund_type', 'refund', 'is_deduction'], order_by="idx")
    cancellation_policy = frappe.get_cached_doc("Cancellation Policy", policy)
    days = frappe.utils.date_diff(check_out, check_in) + day_margin
    day_diff = frappe.utils.date_diff(check_in, frappe.utils.now())
    check_in_datetime = datetime.datetime.combine(check_in, datetime.time(day_start_hour))

    time_difference = check_in_datetime - frappe.utils.datetime.datetime.now()
    total_seconds = time_difference.total_seconds()
    hour_diff = total_seconds / 3600
    price_per_day = total_price / days
    selected_cncl = None
    for cncl in cancellation_policy.refunds:
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

def get_hotel_total_nights(check_in, check_out):
    total_nights = frappe.utils.date_diff(check_out, check_in)
    if total_nights > 0:
        return total_nights
    frappe.throw("Check out cannot be before check in or in the same day")

class TestEvent(FrappeTestCase):
    def test_get_cancellation_refund(self):
        refund = get_cancellation_refund("24 Hours Refundable", 1000, "2024-01-04", "2024-01-07")
        print("Test 1 Refund:", refund)
        self.assertTrue(refund == 1000)
        refund = get_cancellation_refund("24 Hours Refundable", 1000, "2024-01-03", "2024-01-08")
        print("Test 2 Refund:", refund)
        self.assertTrue(refund == 800)
        refund = get_cancellation_refund("24 Hours Refundable", 1000, "2024-01-02", "2024-01-07")
        print("Test 3 Refund:", refund)
        self.assertTrue(refund == 600)

def get_subagency_extra_price(price, subagency_margin):
    return price + (price * subagency_margin) / 100


def parse_transfer_date(transfer_date: any) -> datetime.datetime:
    if type(transfer_date) == str:
        transfer_date = frappe.utils.get_datetime(transfer_date)
    transfer_hour = 10
    transfer_date = transfer_date.replace(hour=transfer_hour, minute=0, second=0)
    return transfer_date

def parse_invoice_checkout_date(checkout_date):
    if type(checkout_date) == str:
        checkout_date = frappe.utils.get_datetime(checkout_date)
    elif type(checkout_date) == datetime.date:
        checkout_date = frappe.utils.get_datetime(checkout_date.strftime("%Y-%m-%d"))
    checkout_date = checkout_date.replace(hour=10, minute=0, second=0)
    return checkout_date

def parse_date(date):
    if type(date) == str:
        date = frappe.utils.get_datetime(date)
    elif type(date) == datetime.date:
        date = frappe.utils.get_datetime(date.strftime("%Y-%m-%d"))
    return date.date()