import frappe
from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification
from frappe.tests.utils import FrappeTestCase
from uuid import uuid4


def create_uuid():
    unique_id = str(uuid4())
    return unique_id

def get_portal_setting(fieldname):
    return frappe.db.get_single_value("Tourism Portal Settings", fieldname)

def get_print_settings(fieldname):
    return frappe.db.get_single_value("Invoice Print Settings", fieldname)

def format_file_link_print(file_url):
        return frappe.utils.get_url(file_url)

def user_has_subagency():
    user_roles = frappe.get_roles()
    company_details = get_utils_company_details()
    if company_details['is_child_company']:
        return False
    if 'Agency Creator' in user_roles:
        return True
    return False
def can_add_user():
    user_roles = frappe.get_roles()
    if 'Agency User Creator' in user_roles:
        return True
    return False
    # company_details = get_utils_company_details()
    # return not company_details['is_child_company']

def get_site_logo(src=False):
    if src:
         get_portal_setting("site_logo")
    return frappe.db.get_single_value("Website Settings", "brand_html")
def user_has_desk_access():
    #frappe.local.cookie_manager.init_cookies()
    if frappe.db.get_value("User", frappe.session.user, "user_type") == "System User":
        return True
    return False
def has_user_tariff():
    company = frappe.db.get_value("User", frappe.session.user, "company", cache=True)
    if not company:
         return False
    return frappe.db.get_value("Company", company, "has_tariff", cache=True)

def can_update_agency():
    user_roles = frappe.get_roles()
    if 'Agency Profile Editor' in user_roles:
        return True
    return False

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
    SELECT tbl2.type_code, tbl2.bed_type, tbl1.note
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

def get_utils_company_details():
    company = frappe.db.get_value("User", frappe.session.user, "company")
    company_doc = frappe.get_cached_doc("Company", company)
    company_details = {
    }
    if company_doc.is_child_company:
        company_details['is_child_company'] = True
        company_details['company'] = company_doc.parent_company
        company_details['child_company'] = company_doc.name
        company_details['hotel_margin'] = company_doc.hotel_margin
        company_details['tour_margin'] = company_doc.tour_margin
        company_details['transfer_margin'] = company_doc.transfer_margin
    else:
        company_details['is_child_company'] = False
        company_details['company'] = company_doc.name
    return company_details

def get_company_class(search_params):
    location_type = search_params.get('location-type')
    location = search_params.get('location')
    city = get_location_city(location_type, location)
    #company = frappe.db.get_value("User", frappe.session.user, "company", cache=True)
    company_details = get_utils_company_details()
    company = company_details['company']
    company_class= frappe.db.get_value("Company Assigned Class", {
        "company": company, "city": city, 
        "from_date": ["<=", frappe.utils.nowdate()], 
        "to_date": [">=", frappe.utils.nowdate()]},
        ["company_class", "extra_price_type", "extra_price"], as_dict=True
        ) or {}
    return company_class


def publish_agency_notification(title, message, doctype, docname):
    notification_doc = {
		"type": "Alert",
		"document_type": doctype,
		"subject": title,
        "email_content": message,
		"document_name": docname,
		"from_user": frappe.session.user,
	}
    users = frappe.db.get_values("User", {"company":["!=", ""], "enabled": 1}, "email", pluck=True)
    enqueue_create_notification(users, notification_doc)

def publish_user_notification(title, message, user, doctype, docname):
    notification_doc = {
		"type": "Alert",
		"document_type": doctype,
		"subject": title,
        "email_content": message,
		"document_name": docname,
		"from_user": frappe.session.user,
	}
    enqueue_create_notification([user], notification_doc)

def get_location_full_name(location, location_type):
    if location_type == 'hotel':
        return frappe.db.get_value("Hotel", location, "hotel_name", cache=True)
    elif location_type == 'area':
        return frappe.db.get_value("Area", location, "area_name", cache=True)
    elif location_type == 'town':
        return frappe.db.get_value("Town", location, "town_name", cache=True)
    elif location_type == 'city':
        return frappe.db.get_value("City", location, "city_name", cache=True)
    elif location_type == 'airport':
        return frappe.db.get_value("Airport", location, "airport_name", cache=True)
    else:
        return location

def is_time_passed(date, hours):
    if type(date) == str:
        date = frappe.utils.get_datetime(date)
    elif type(date) == datetime.date:
        date = frappe.utils.get_datetime(date.strftime("%Y-%m-%d"))
    timedelta = date - frappe.utils.now_datetime()
    if timedelta.total_seconds() > hours * 3600:
        return False
    return True

def get_website_setting(field_name):
    return frappe.db.get_single_value("Tourism Website Settings", field_name)

def send_system_email(email, subject, message, doctype=None, docname=None):
    frappe.enqueue('tourism_portal.utils.send_email', email=email, subject=subject, message=message, doctype=doctype, docname=docname)

def send_email(email, subject, message, doctype=None, docname=None):
    frappe.sendmail(
		recipients=[email],
		doctype=doctype,
		name=docname,
		message= message,
		subject=subject,
		now=1,
		)

def get_hotel_stars(hotel_stars):
    stars = {
        "One Star": "1",
        "Two-Star": "2",
        "Three-Star": "3",
        "Four-Star": "4",
        "Five-Star": "5",
    }
    return stars.get(hotel_stars)

def format_url(url):
    if url.startswith("http"):
        return url
    if url.startswith("/files"):
        return frappe.utils.get_url(url)
    return f"https://{url}"