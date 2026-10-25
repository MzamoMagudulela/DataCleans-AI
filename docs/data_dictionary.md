# Data Dictionary — Sample Dataset (Customer Churn)

This document outlines the schema, expected data types, and intentional data-quality flaws present in `data/samples/customer_churn_dirty.csv`. This dataset serves as a benchmark for profiling, cleaning, and validation tests.

---

## 1. Field Specifications

| Field Name | Expected Type | Description | Allowed / Valid Values | Example |
| :--- | :--- | :--- | :--- | :--- |
| `customer_id` | String | Unique customer identifier | Format `CUST-XXXX` | `CUST-1001` |
| `full_name` | String | Customer's full name | Trimmed, capitalized words | `John Doe` |
| `gender` | Categorical | Customer gender | `Male`, `Female` | `Female` |
| `age` | Integer | Customer age | Between 18 and 100 | `34` |
| `join_date` | Date | Date customer joined service | `YYYY-MM-DD` | `2022-01-15` |
| `contract_type` | Categorical | Type of customer contract | `Month-to-month`, `One year`, `Two year` | `Month-to-month` |
| `monthly_charges` | Float | Recurring monthly cost in USD | Numeric > 0.0 | `65.50` |
| `total_charges` | Float | Total spend to date in USD | Numeric >= monthly_charges | `786.00` |
| `payment_method` | Categorical | Chosen billing method | `Credit Card`, `Bank Transfer`, `Electronic Check`, `Mailed Check` | `Credit Card` |
| `churn` | Boolean | Whether customer left service | `Yes` / `No` (or `True` / `False`) | `No` |

---

## 2. Seeded Data Quality Issues for Testing

The sample dataset deliberately contains common real-world data quality anomalies:

1. **Duplicates**:
   - `CUST-1001` appears twice as an exact duplicate row.
2. **Missing Values**:
   - `gender`: Missing value for `CUST-1006`.
   - `join_date`: Missing value for `CUST-1009`.
   - `monthly_charges`: Sentinel string `'N/A'` for `CUST-1013`.
   - `total_charges`: Empty value for `CUST-1006`; text `'Unknown'` for `CUST-1014`.
   - `payment_method`: Empty value for `CUST-1010`.
3. **Whitespaces & Casing**:
   - `full_name`: Leading/trailing spaces (` John Doe `, ` Grace Hopper `).
   - `gender`: Inconsistent casing (`Male`, `female`, `MALE`, `M`, `F`).
4. **Invalid Formats & Type Contamination**:
   - `monthly_charges`: Currency symbol present (`$65.50`, `$110.00`).
   - `join_date`: Multiple date string patterns (`YYYY-MM-DD`, `YYYY/MM/DD`, `DD-MM-YYYY`).
   - `churn`: Inconsistent boolean representations (`No`, `no`, `Y`, `False`, `TRUE`, `0`).
5. **Outliers / Invalid Ranges**:
   - `age`: Negative value (`-5`), unrealistically high ages (`120`, `999`).
