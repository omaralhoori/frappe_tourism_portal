import frappe
from frappe import _

"""
rooms -> [{
    room_name,
	room_id,
	contract_id-> nullable,
	price_id -> nullable,
	inquiry_id -> nullable,
	pax_info -> {
		adults: num,
		children: num,
		child_ages: [num]
	},
	price:
}]
"""

@frappe.whitelist()
def create_reservation():
    params = frappe.form_dict
    print(params)
    user = frappe.session.user
    company = frappe.db.get_value("User", user, "company")
    invoice = frappe.get_doc({
        "doctype": "Sales Invoice",
        "company": company,
        "customer": user,
        "post_date": frappe.utils.nowdate(),
        "post_time": frappe.utils.nowtime()
    })
    for room in params.rooms:
        invc_room = invoice.append("rooms")
        invc_room.room = room['room_id']
        invc_room.room_name = room['room_name']
        invc_room.qty = 1
        invc_room.price_per_item = room['price']
        invc_room.total_price = room['price']
        invc_room.contract_id = room.get('contract_id')
        invc_room.contract_price_id = room.get('price_id')
        invc_room.inquiry_id = room.get('inquiry_id')
        for i in range(room['pax_info'].get('adults')):
            guest = invoice.append("room_pax_info")
            guest.room_name = room['room_name']
            guest.guest_type = 'Adult'
        for child_age in room['pax_info'].get('child_ages'):
            guest = invoice.append("room_pax_info")
            guest.guest_type = 'Child'
            guest.room_name = room['room_name']
            guest.guest_age = child_age
    invoice.insert(ignore_permissions=True)
    return invoice.name

@frappe.whitelist()
def get_invoice_data(sales_invoice):
    invoice = frappe.get_doc("Sales Invoice", {"name": sales_invoice, "customer": frappe.session.user})
    rooms = {}
    for room in invoice.rooms:
        if not rooms.get(room.get('hotel')):
            rooms[room.get('hotel')] = {}
            rooms[room.get('hotel')]['rooms'] = []
            rooms[room.get('hotel')]['details'] = frappe.db.get_value("Hotel", room.get('hotel'), ["hotel_name"], as_dict=True)
        hotel_room = {
            "room_name": room.room_name,
            "total_price": room.total_price,
            "hotel": room.hotel,
        }
        adult_paxes = []
        child_paxes = []
        for pax in invoice.room_pax_info:
            if pax.room_name == room.room_name:
                if pax.guest_type == 'Adult':
                    adult_paxes.append({
                        "guest_name": pax.guest_name,
                        "guest_type": pax.guest_type,
                        "guest_age": pax.guest_age
                    })
                if pax.guest_type == 'Child':
                    child_paxes.append({
                        "guest_name": pax.guest_name,
                        "guest_type": pax.guest_type,
                        "guest_age": pax.guest_age
                    })
        extras = []
        for extra in invoice.room_extras:
            if extra.room_name == room.room_name:
                extras.append({
                    "extra": extra.extra,
                    "extra_price": extra.extra_price,
                })

        hotel_room['adult_paxes'] = adult_paxes
        hotel_room['child_paxes'] = child_paxes
        hotel_room['extras'] = extras
        rooms[room.get('hotel')]['rooms'].append(hotel_room)
    return {
        "session_expires": invoice.session_expires,
        "post_date": invoice.post_date,
        "post_time": invoice.post_time,
        "grand_total": invoice.grand_total,
        "rooms": rooms,
        "sales_invoice": sales_invoice, 
        "customer_name": invoice.customer_name,
        "customer_email": invoice.customer_email,
        "customer_mobile_no": invoice.customer_mobile_no
    }


@frappe.whitelist()
def get_all_invoices(start=0, limit=20):
    return frappe.db.get_all("Sales Invoice", {"customer": frappe.session.user}, [
        "name", "grand_total", "post_date",
          "post_time", "session_expires", "docstatus"], order_by="creation DESC" ,limit=limit, start=start)