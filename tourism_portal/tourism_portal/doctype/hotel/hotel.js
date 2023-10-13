// Copyright (c) 2023, omaralhoori and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hotel', {
	refresh: function(frm) {
		if (!frm.is_new()){
			frm.add_custom_button(__('Add Room Contract'), function(){
				frm.events.add_room_contract(frm);
			});
			frm.add_custom_button(__('View All Contracts'), function(){
				frm.events.view_all_contracts(frm);
			});
		}
	},
	add_room_contract(frm) {
		frappe.new_doc('Hotel Room Contract', {
			hotel: frm.doc.name,
		})
	},
	view_all_contracts(frm){
		frappe.route_options = {'hotel': frm.doc.name};
			frappe.set_route('List', 'Hotel Room Contract');
	},
});
