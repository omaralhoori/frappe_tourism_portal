// Copyright (c) 2023, omaralhoori and contributors
// For license information, please see license.txt

frappe.ui.form.on('Company', {
	refresh: function(frm) {
		if (!frm.is_new()){
			frm.add_custom_button(__('Add User'), function(){
				frm.events.add_user(frm);
			});
			frm.add_custom_button(__('Add Credit'), function(){
				frm.events.add_credit(frm);
			});

			frm.events.get_company_balance(frm)

		}

		frm.set_query("parent_company", function() {
			return {
				filters:
					{"is_child_company": 0}
			};
		});

	},
	get_company_balance: function(frm){
		frappe.call({
			"method": "get_company_balance",
			"doc": frm.doc,
			callback: (res)=> {
				var balanceHtml = `<h3>Balance: ${res.message}</h3>`  
				$(frm.fields_dict.company_blance.wrapper).html(balanceHtml)
			}
		})
	},

	add_user: function(frm){
		let d = new frappe.ui.Dialog({
			title: __('Enter User'),
			fields: [
				{
					label: 'Email',
					fieldname: 'email',
					fieldtype: 'Data',
					reqd: 1
				},
				{
					label: 'First Name',
					fieldname: 'first_name',
					fieldtype: 'Data',
					reqd: 1
				},
				{
					label: 'Last Name',
					fieldname: 'last_name',
					fieldtype: 'Data',
				},
				{
					label: 'Password',
					fieldname: 'password',
					fieldtype: 'Data',
					reqd: 1
				},
			],
			size: 'small', // small, large, extra-large 
			primary_action_label: __('Save'),
			primary_action(values) {
				frm.call({
					"method": "add_user",
					doc:frm.doc,
					args: {
						"email": values.email,
						"first_name": values.first_name,
						"last_name": values.last_name,
						"password": values.password,
					},
					callback: (message) => {
						frm.reload_doc();
					}
				})
				d.hide();
			}
		});
		
		d.show();
	},
	add_credit: function(frm){
		let d = new frappe.ui.Dialog({
			title: __('Enter Credit'),
			fields: [
				{
					label: 'Credit',
					fieldname: 'credit',
					fieldtype: 'Float',
					reqd: 1
				},
			],
			size: 'small', // small, large, extra-large 
			primary_action_label: __('Save'),
			primary_action(values) {
				frm.call({
					"method": "add_credit",
					doc:frm.doc,
					args: {
						"credit": values.credit,
					},
					callback: (message) => {
						frm.reload_doc();
					}
				})
				d.hide();
			}
		});
		
		d.show();
	}
});
