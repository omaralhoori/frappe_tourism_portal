// Copyright (c) 2023, omaralhoori and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hotel Room Contract', {
	refresh: function(frm) {
		if (!frm.is_new()){
			frm.add_custom_button(__('Add Price'), function(){
				frm.events.add_price(frm);
			});
			if (!frm.doc.agency && frm.doc.qty > 0 && frm.doc.docstatus == 1){
				frm.add_custom_button(__('Allocate Agency Rooms'), function(){
					frm.events.allocate_agency_rooms(frm);
				});	
			}
			frm.add_custom_button(__('View All Prices'), function(){
				frm.events.view_all_prices(frm);
			});
		}
		frm.set_query("room_type", function() {
			return {
				query: "tourism_portal.controllers.queries.hotel_room_type",
				filters:
					{"hotel": frm.doc.hotel}
			};
		});
	},
	add_price(frm) {
		frappe.new_doc('Hotel Room Price', {
			room_contract: frm.doc.name
		})
	},
	view_all_prices(frm){
		frappe.route_options = {'room_contract': frm.doc.name};
			frappe.set_route('List', 'Hotel Room Price');
	},
	allocate_agency_rooms(frm){
		let d = new frappe.ui.Dialog({
			title: __('Enter User'),
			fields: [
				{
					label: 'Agency',
					fieldname: 'agency',
					fieldtype: 'Link',
					options: 'Company',
					reqd: 1
				},
				{
					label: 'From Date',
					fieldname: 'from_date',
					fieldtype: 'Date',
					reqd: 1
				},
				{
					label: 'To Date',
					fieldname: 'to_date',
					fieldtype: 'Date',
					reqd: 1
				},
				{
					label: 'Quantity',
					fieldname: 'qty',
					fieldtype: 'Int',
					reqd: 1
				},
			],
			size: 'small', // small, large, extra-large 
			primary_action_label: __('Allocate'),
			primary_action(values) {
				frm.events.validate_agency_allocation(frm, values);
				frm.call({
					"method": "tourism_portal.tourism_portal.doctype.hotel_room_contract.hotel_room_contract.allocate_agency_rooms",
					args: {
						"contract_no": frm.doc.name,
						"allocation_details": values
					},
					callback: (res) => {
						if (res.message){
							frappe.msgprint(`Rooms allocated successfully. New contract created: <a href="/app/hotel-room-contract/${res.message}">${res.message}</a>. Please update the prices for the new contract.`);
						}
					}
				})
				d.hide();
			}
		});
		
		d.show();
	},
	validate_agency_allocation(frm, values){
		if (values.from_date > values.to_date){
			frappe.throw(__("From Date must be before To Date"));
		}
		if (values.qty <= 0){
			frappe.throw(__("Quantity must be greater than 0"));
		}
		if (values.qty > frm.doc.qty){
			frappe.throw(__("Quantity must be less than or equal to the contract quantity"));
		}
		if (values.from_date < frm.doc.check_in_from_date){
			frappe.throw(__("From Date must be after the contract check in from date"));
		}
		if (values.to_date > frm.doc.check_in_to_date){
			frappe.throw(__("To Date must be before the contract check in to date"));
		}
	},
});
