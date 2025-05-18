# Copyright (c) 2025, SymonMuchemi and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": "Posting Date",
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 100,
        },
        {
            "label": "Item",
            "fieldname": "item",
            "fieldtype": "Link",
            "options": "Item",
            "width": 150,
        },
        {
            "label": "Warehouse",
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 150,
        },
        {
            "label": "Actual Quantity",
            "fieldname": "actual_quantity",
            "fieldtype": "Float",
            "width": 100,
        },
        {
            "label": "Valuation Rate",
            "fieldname": "valuation_rate",
            "fieldtype": "Currency",
            "width": 120,
        },
        {"label": "Value", "fieldname": "value", "fieldtype": "Currency", "width": 120},
        {
            "label": "Voucher Type",
            "fieldname": "voucher_type",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": "Voucher No",
            "fieldname": "voucher_no",
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
            "width": 120,
        },
    ]


def get_data(filters):
    conditions = []

    if filters.get("item"):
        conditions.append("item = %(item)s")

    if filters.get("warehouse"):
        conditions.append("warehouse = %(warehouse)s")

    if filters.get("from_date"):
        conditions.append("posting_date >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("posting_date <= %(to_date)s")

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT
            posting_date,
            item,
            warehouse,
            actual_quantity,
            valuation_rate,
            (actual_quantity * valuation_rate) AS value,
            voucher_type,
            voucher_no
        FROM `tabStock Ledger Entry`
        {where_clause}
        ORDER BY posting_date ASC
    """

    return frappe.db.sql(query, filters, as_dict=True)
