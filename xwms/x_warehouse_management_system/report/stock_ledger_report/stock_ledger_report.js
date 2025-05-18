// Copyright (c) 2025, SymonMuchemi and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Ledger Report"] = {
	filters: [
		{
			fieldname: "item",
			label: "Item",
			fieldtype: "Link",
			options: "Item",
			reqd: 0,
		},
		{
			fieldname: "warehouse",
			label: "Warehouse",
			fieldtype: "Link",
			options: "Warehouse",
			reqd: 0,
		},
		{
			fieldname: "from_date",
			label: "From Date",
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.nowdate(), -1),
		},
		{
			fieldname: "to_date",
			label: "To Date",
			fieldtype: "Date",
			default: frappe.datetime.nowdate(),
		},
	],
};
