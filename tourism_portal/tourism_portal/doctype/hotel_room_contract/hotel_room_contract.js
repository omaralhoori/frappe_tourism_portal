// Copyright (c) 2023, omaralhoori and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hotel Room Contract', {
	refresh: function(frm) {
		if (!frm.is_new()){
			frm.add_custom_button(__('Add Price'), function(){
				frm.events.add_price(frm);
			});
			frm.add_custom_button(__('View All Prices'), function(){
				frm.events.view_all_prices(frm);
			});
		}
		
	},
	add_price(frm) {
		frappe.new_doc('Hotel Room Price', {
			room_contract: frm.doc.name
		})
	},
	view_all_prices(frm){
		frappe.route_options = {'room_contract': frm.doc.name};
			frappe.set_route('List', 'Hotel Room Price');
	}
});
