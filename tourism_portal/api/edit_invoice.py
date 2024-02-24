import unittest
import frappe
from frappe.tests.test_commands import BaseTestCommands
from tourism_portal.api.search import get_room_contracts
from tourism_portal.utils import get_company_class, get_utils_company_details


class TestCommands(BaseTestCommands, unittest.TestCase):
    def test_execute(self):
        # No Contracts -> No Availability
        results = check_hotel_search_extend_availability("INV-24-02-00139", "Hotel Search 1", "2024-02-24", "2024-03-27")
        print("Test 1 : No Contracts -> No Availability")
        print("Results", results)
        assert results == None
        # No Prices -> No Availability
        results = check_hotel_search_extend_availability("INV-24-02-00140", "Hotel Search 1", "2024-02-27", "2024-02-29")
        print("Test 2 : No Pirces -> No Availability")
        print("Results", results)
        # No Qty Left -> No Availability
        results = check_hotel_search_extend_availability("INV-24-02-00141", "Hotel Search 1", "2024-02-26", "2024-02-27")
        print("Test 3 : No Qty left -> No Availability")
        print("Results", results)
        # Requested 2 available 1 only -> No Availability
        results = check_hotel_search_extend_availability("INV-24-02-00143", "Hotel Search 1", "2024-02-26", "2024-02-27")
        print("Test 4 : equested 2 available 1 only  -> No Availability")
        print("Results", results)
        # No Qty Left in one day -> No Availability
        results = check_hotel_search_extend_availability("INV-24-02-00146", "Hotel Search 1", "2024-02-26", "2024-02-28")
        print("Test 5 : No Qty Left in one day -> No Availability")
        print("Results", results)
        # No Qty Left in one day in one contract but there are in another contract -> No Availability
        results = check_hotel_search_extend_availability("INV-24-02-00151", "Hotel Search 1", "2024-02-23", "2024-02-24")
        print("Test 6 : No Qty Left in one day in one contract but there are in another contract -> No Availability")
        print("Results", results)
        assert results == None
        # Multiple price found for differen period -> concat prices
        results = check_hotel_search_extend_availability("INV-24-02-00152", "Hotel Search 1", "2024-02-27", "2024-03-03")
        print("Test 7 : Multiple price found for differen period -> concat prices")
        print("Results", results)
        # Multiple price found for differen period -> concat prices
        results = check_hotel_search_extend_availability("INV-24-02-00153", "Hotel Search 1", "2024-02-27", "2024-03-03")
        print("Test 7 : Multiple contract found for differen period -> concat prices")
        #print("Results", get_results(results))
        print(results)
        assert results != None
@frappe.whitelist()
def check_hotel_search_extend_availability(sales_invoice, hotel_search, check_in, check_out):
    #print("Check Hotel Search Extend Availability FOR " + check_in, check_out)
    company_details = get_utils_company_details()
    invoice_doc = frappe.get_doc("Sales Invoice", {"name": sales_invoice, "company": company_details.get('company')})
    results = {}
    contracts = {}
    for row in invoice_doc.rooms:
        if row.hotel_search == hotel_search:
            room_details = check_room_extend_availability(invoice_doc, row, check_in, check_out)
            if not check_room_details(room_details):
                #print("result not found for " + row.room_name )
                return None
            for contract in room_details.get('contracts'):
                if contract.get('contract_id') in contracts:
                    contracts[contract.get('contract_id')]['requested_qty'] += 1
                else:
                    contracts[contract.get('contract_id')] = {
                        "remain_qty": room_details.get('remain_qty'),
                        "requested_qty": 1,
                    }
            results[row.name] = room_details
    for contract in contracts:
        if contracts[contract].get('requested_qty') > contracts[contract].get('remain_qty'):
            return None
    return create_room_extend_availability_results(invoice_doc, hotel_search, check_in, check_out, results)

def create_room_extend_availability_results(invoice,hotel_search, check_in, check_out, results):
    results_docs = {}
    for row in invoice.rooms:
        if row.name in results:
            if result_id := frappe.db.exists("Extend Room Results", {"invoice": invoice.name, "row_id": row.name}):
                frappe.delete_doc("Extend Room Results", result_id, ignore_permissions=True)
            extend_result = frappe.get_doc({
                "doctype": "Extend Room Results",
                "invoice": invoice.name,
                "row_id": row.name,
                "hotel_search": hotel_search,
                "check_in": check_in,
                "check_out": check_out,
                "user": frappe.session.user,             
            })
            total_price = 0
            total_nights = 0
            for contract in results[row.name].get('contracts'):
                for price in contract.get('prices'):
                    nights = frappe.utils.date_diff(price.get('to_date'), price.get('from_date'))
                    buying= frappe.db.get_value("Hotel Room Price", price.get("item_price_name"), ["buying_currency", "buying_price"], as_dict=True)
                    if not buying:
                        frappe.throw("Something went wrong, please contact system manager")
                    cancellation = contract.get('hotel_cancellation_policy')
                    extend_result.append("contracts", {
                        "hotel_search": row.hotel_search,
                        "room_name": row.room_name,
                        "contract_id": contract.get('contract_id'),
                        "contract_price": price.get('item_price_name'),
                        "check_in": contract.get('from_date'),
                        "check_out": contract.get('to_date'),
                        "nights": nights,
                        "selling_price": price.get('child_company_price'), 
                        "selling_price_company": price.get('selling_price_with_childs'),
                        "cancellation_policy": cancellation,
                        "buying_currency": buying.get('buying_currency'),
                        "buying_price": buying.get('buying_price'),
                    })
                    total_price += price.get('child_company_price') * nights
                    total_nights += nights
            extend_result.save(ignore_permissions=True)
            results_docs[row.name] = {
                "row_id": row.name,
                "room_name": row.room_name,
                "hotel_search": row.hotel_search,
                "invoice": invoice.name,
                "extend_id":extend_result.name,
                "total_price": total_price,
                "total_nights": total_nights,
            }
    return results_docs


def get_results(results):
    formated = {}
    for res in results.keys():
        formated[res] = {
        "remain_qty": results[res].get('remain_qty'),
        "contracts_len": len(results[res].get('contracts')), 
       "contracts": [{
           "prices_len": len(contract.get('prices')),
           "contract_id": contract.get('contract_id'),
            "prices": [ {
                "selling_price": price.get('selling_price'),
                "from_date": price.get('from_date'),
                "to_date": price.get('to_date'),
            } for price in contract.get('prices')]           
       } for contract in results[res].get('contracts')]
            }
    return formated
def check_room_details(room_details=None):
    if not room_details:
        return False
    if not room_details.get('contracts') or len(room_details.get('contracts')) == 0:
        return False
    if not room_details.get('remain_qty') or room_details.get('remain_qty') < 1:
        return False
    
    return True

def check_room_extend_availability(invoice_doc, reserve_row, check_in, check_out):
    # reserve_row = None
    # for row in invoice_doc.rooms:
    #     if row.name == row_id:
    #         reserve_row = row
    #         break
    # if not reserve_row:
    #     frappe.throw("Room not found")
    
    room_details = get_room_details(reserve_row)
    hotel_params = get_hotel_params(invoice_doc, reserve_row, check_in, check_out)
    company_class = get_company_class(hotel_params)
    get_room_contracts(room_details, hotel_params, hotel_params.get('pax'), company_class)
    return room_details
    # hotel_search = frappe.db.get_value("Sales Invoice Room", {
    #     "parent": sales_invoice, "room": 
    #     row_id, "is_cancelled": 0}, ["room"], as_dict=True)
    # if not hotel_search:
    #     frappe.throw("Room not found")
    
def get_room_details(room_row):
    room_type = frappe.db.get_value("Hotel Room", room_row.room, "room_type", cache=True)
    room_accommodation_type = frappe.db.get_value("Hotel Room", room_row.room, "room_accommodation_type", cache=True)
    if not room_type:
        frappe.throw("Room not found")
    min_pax = None
    hotel_accommodation_type_rule = frappe.db.get_value("Hotel", room_row.hotel, "hotel_accommodation_type_rule", cache=True)
    room_accommodation_type_doc = frappe.get_cached_doc("Room Accommodation Type Rule", hotel_accommodation_type_rule)
    for room_type_acmd in room_accommodation_type_doc.rules:
        if room_type_acmd.room_type == room_accommodation_type:
            min_pax =  room_type_acmd.get('min_pax')
    
    return {
        "room_type": room_type,
        "hotel": room_row.hotel,
        "room": room_row.room,
        "min_pax": min_pax,
        "board": room_row.board,
        "room_accommodation_type": room_accommodation_type,
        "bed_type": room_row.bed_type,
    }

def get_hotel_params(invoice, room_row, check_in, check_out):
    pax = {
        "adults": 0,
        "children": 0,
        "childrenInfo": []
    }
    for pax_row in invoice.room_pax_info:
        if pax_row.hotel_search == room_row.hotel_search and pax_row.room_name == room_row.room_name:
            if pax_row.guest_type == 'Adult':
                pax['adults'] += 1
            else:
                pax['children'] += 1
                pax['childrenInfo'].append(pax_row.guest_age)
    return {
        "checkin": check_in,
        "checkout": check_out,
        "location-type": "hotel",
        "location": room_row.hotel,
        "pax": pax,
    }

@frappe.whitelist()
def extend_accommodation(invoice, hotel_search, nights):
    old_check_out = frappe.db.get_value("Sales Invoice Room Item", {"parent": invoice, "hotel_search": hotel_search}, "check_out")
    new_check_out = frappe.utils.add_days(old_check_out, int(nights))
    results = check_hotel_search_extend_availability(invoice, hotel_search, old_check_out, new_check_out)
    if not results:
        return {
            "message": "No availability found",
            "data": None
        }
    return {
        "data": results
    }

def confirm_extend_accommodation(extend_id):
    try:
        frappe.get_doc("Extend Room Results", {"name": extend_id, "user": frappe.session.user}).confirm_extend_accommodation()
    except Exception as e:
        frappe.throw(str(e))