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
            "width": 120,
        },
        {"label": "Quantity", "fieldname": "qty", "fieldtype": "Float", "width": 120},
        {
            "label": "Valuation Rate",
            "fieldname": "valuation_rate",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": "Stock Value",
            "fieldname": "stock_value",
            "fieldtype": "Currency",
            "width": 150,
        },
    ]


def get_data(filters):
    conditions = []

    if filters.get("item"):
        conditions.append("item = %(item)s")

    if filters.get("warehouse"):
        conditions.append("warehouse = %(warehouse)s")

    if filters.get("posting_date"):
        conditions.append("posting_date <= %(posting_date)s")

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT 
            item,
            warehouse,
            SUM(actual_quantity) AS qty,
            CASE 
                WHEN SUM(actual_quantity) <= 0 THEN 0
                ELSE SUM(actual_quantity * valuation_rate) / SUM(actual_quantity)
            END AS valuation_rate,
            SUM(actual_quantity * valuation_rate) AS stock_value
        FROM `tabStock Ledger Entry`
        {where_clause}
        GROUP BY item, warehouse
        HAVING qty >= 0
        ORDER BY item, warehouse
    """

    return frappe.db.sql(query, filters, as_dict=True)
