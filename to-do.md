# Frappe Stock Management System

## 🚀 PHASE 1: Project Setup

### ✅ Tasks

- [x] Scaffold new Frappe app:  
    `bench new-app xms`
- [x] Install app on a site:  
    `bench --site xms.local install-app xms`
- [x] Set up Git repo and commit the initial boilerplate

---

## 🧱 PHASE 2: Core DocTypes (Data Models)

### ✅ 1. Item

- [ ] **Fields:** `item_code`, `name`, `description`, `unit`
- [ ] **Optional:** `item_group`, `is_stock_item`

### ✅ 2. Warehouse (Tree DocType)

- [ ] Enable `is_tree = 1`
- [ ] **Fields:** `warehouse_name`, `parent_warehouse`, `is_group`

### ✅ 3. Stock Entry

- [ ] **Parent fields:** `stock_entry_type`, `posting_date`, `remarks`
- [ ] **Child table:** Stock Entry Detail with:  
    `item`, `qty`, `valuation_rate`, `from_warehouse`, `to_warehouse`

### ✅ 4. Stock Ledger Entry (Stateless)

- [ ] **Fields:** `item`, `warehouse`, `posting_date`, `actual_qty`, `valuation_rate`, `voucher_type`, `voucher_no`

---

## 🔁 PHASE 3: Business Logic

### ✅ Stock Entry Submission Flow

- [ ] Add `on_submit` method to Stock Entry
- [ ] Validate required fields per transaction type
- [ ] Generate corresponding Stock Ledger Entry rows
- [ ] Skip any state caching (stateless design)

### ✅ Moving Average Valuation

- [ ] Create helper: `get_valuation_rate(item, warehouse)`
- [ ] On Receipt, recalculate valuation using SLE history
- [ ] On Consume/Transfer, use latest valuation without changing it

---

## 📊 PHASE 4: Reports

### ✅ 1. Stock Ledger Report

- [ ] Show line-by-line movement: `item`, `warehouse`, `date`, `qty`, `rate`
- [ ] Add filters (`item`, `warehouse`, `date range`)

### ✅ 2. Stock Balance Report

- [ ] Calculate `SUM(actual_qty)` grouped by item & warehouse
- [ ] Filter by cutoff date

---

## 🧪 PHASE 5: Testing

### ✅ Functional Tests

- [ ] Test stock entry types: Receipt, Consume, Transfer
- [ ] Assert correct SLEs are created
- [ ] Validate error cases (e.g. consume without enough stock)

### ✅ Valuation Tests

- [ ] Check moving average calculations
- [ ] Check impact of multiple receipts with varying costs

### ✅ Report Tests

- [ ] Validate report results match expected balances
- [ ] Optionally use snapshot testing for SLE data

---

## 🎨 PHASE 6: (Optional) Frontend Polish

- [ ] Add a basic Web View or List View for items or reports
- [ ] Clean up print formats or dashboards if needed

---

## ✅ FINAL TASKS

- [ ] Push clean commits to GitHub with a README
- [ ] Document system design, assumptions, and known limitations
- [ ] Write brief usage instructions for testing the flows
