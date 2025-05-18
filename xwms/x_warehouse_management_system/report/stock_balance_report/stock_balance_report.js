// Copyright (c) 2025, SymonMuchemi and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Balance Report"] = {
  filters: [
    {
      fieldname: "posting_date",
      label: "Posting Date",
      fieldtype: "Date",
      default: frappe.datetime.nowdate(),
      reqd: 1
    },
    {
      fieldname: "item",
      label: "Item",
      fieldtype: "Link",
      options: "Item"
    },
    {
      fieldname: "warehouse",
      label: "Warehouse",
      fieldtype: "Link",
      options: "Warehouse"
    }
  ]
};
