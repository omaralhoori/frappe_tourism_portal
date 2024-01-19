// Copyright (c) 2023, omaralhoori and contributors
// For license information, please see license.txt
frappe.listview_settings['Room Availability'] = {
	hide_name_column: true,
	onload: function (listview) {
		listview.page.add_inner_button(__("Add Availability"), function () {
			var selected = listview.get_checked_items().map(item => `${item.name}`)
			if (selected.length < 1) {
				frappe.throw("Please select at least one row")
			}
			
			let d = new frappe.ui.Dialog({
				title: 'Enter details',
				fields: [
					{
						label: 'Quantity',
						fieldname: 'qty',
						fieldtype: 'Int'
					},
				],
				size: 'small', // small, large, extra-large 
				primary_action_label: 'Submit',
				primary_action(values) {
					frappe.call({
						"method": "tourism_portal.tourism_portal.doctype.room_availability.room_availability.add_availability",
						"args": {
							"qty": values.qty,
							"rooms": selected
						},
						"callback": function (response) {
							if (response.message) {
								frappe.msgprint(response.message)
								listview.refresh()
							}
						}
					})
					d.hide();
				}
			});
			
			d.show();
		});
	}
}