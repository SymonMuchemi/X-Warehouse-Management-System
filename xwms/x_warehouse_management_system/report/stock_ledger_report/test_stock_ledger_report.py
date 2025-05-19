# Copyright (c) 2025, SymonMuchemi and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from .stock_ledger_report import execute

class TestStockLedgerReport(FrappeTestCase):
    def setUp(self):
        # create a test item
        self.item = frappe.get_doc({
            "doctype": "Item",
            "code": "REPORT-TV",
            "item_name": "Report TV",
            "unit": "Nos"
        }).insert()

        # create a test warehouse
        self.warehouse = frappe.get_doc({
            "doctype": "Warehouse",
            "warehouse_name": "Report Bin A",
            "is_group": 0
        }).insert()

        # create a stock entry (receipt)
        doc = frappe.get_doc({
            "doctype": "Stock Entry",
            "type": "Receipt",
            "posting_date": "2025-05-16",
            "to_warehouse": self.warehouse.name,
            "items": [{
                "item": self.item.name,
                "quantity": 5,
                "valuation_rate": 15000
            }]
        }).insert()
        doc.submit()
        self.receipt_name = doc.name

    def test_stock_ledger_reflects_receipt(self):
        filters = {
            "item": self.item.name,
            "warehouse": self.warehouse.name,
            "from_date": "2025-05-01",
            "to_date": "2025-05-31"
        }

        columns, data = execute(filters)

        self.assertTrue(any(
            row["voucher_no"] == self.receipt_name and row["item"] == self.item.name
            for row in data
        ), "Stock Ledger Report should include the receipt entry.")
