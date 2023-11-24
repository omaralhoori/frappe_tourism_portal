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
        invc_room.qty = 1
        invc_room.price_per_item = room['price']
        invc_room.total_price = room['price']
        for i in range(room['pax_info'].get('adults')):
            guest = invc_room.append("guests")
            guest.guest_type = 'Adult'
        for child_age in room['pax_info'].get('child_ages'):
            guest = invc_room.append("guests")
            guest.guest_type = 'Child'
            guest.guest_age = child_age
    invoice.insert(ignore_permissions=True)
    