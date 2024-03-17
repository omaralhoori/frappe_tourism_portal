// Copyright (c) 2023, omaralhoori and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hotel Inquiry Request', {
	refresh: function(frm) {
		frm.add_custom_button(__("Add Empty Prices"), function() {
			frm.call({
				method: "add_empty_prices",
				doc: frm.doc,
				callback: function(r) {
					frm.refresh();
				}
			})
		});
	}
});
