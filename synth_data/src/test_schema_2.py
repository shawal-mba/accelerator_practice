"""Test schema definitions — ISP company with 100 tables, PKs, and FKs."""

from __future__ import annotations

from typing import Any, TypedDict


class BQColumnDict(TypedDict, total=False):
    name: str
    type: str
    mode: str
    fields: list[BQColumnDict]
    description: str


class BQTableDef(TypedDict):
    name: str
    columns: list[BQColumnDict]
    description: str


# ── BigQuery test tables ─────────────────────────────────────────────────────

BQ_TEST_TABLES: list[BQTableDef] = [
    # ── Employees & Departments ───────────────────────────────────────────────
    {
        "name": "departments",
        "columns": [
            {"name": "dept_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "dept_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "location", "type": "STRING", "mode": "NULLABLE"},
            {"name": "budget", "type": "NUMERIC", "mode": "NULLABLE"},
        ],
        "description": "Company departments.",
    },
    {
        "name": "employees",
        "columns": [
            {"name": "employee_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "first_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "last_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "email", "type": "STRING", "mode": "NULLABLE"},
            {"name": "phone", "type": "STRING", "mode": "NULLABLE"},
            {"name": "job_title", "type": "STRING", "mode": "NULLABLE"},
            {"name": "dept_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "manager_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "hire_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "salary", "type": "NUMERIC", "mode": "NULLABLE"},
        ],
        "description": "Employee records. manager_id references employees.employee_id (self-ref).",
    },
    # ── Products & Plans ──────────────────────────────────────────────────────
    {
        "name": "product_categories",
        "columns": [
            {"name": "category_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "category_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "description", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Product category lookup.",
    },
    {
        "name": "products",
        "columns": [
            {"name": "product_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "product_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "category_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "base_price", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "is_active", "type": "BOOLEAN", "mode": "NULLABLE"},
            {"name": "launch_date", "type": "DATE", "mode": "NULLABLE"},
        ],
        "description": "ISP products (fibre, wireless, etc.).",
    },
    {
        "name": "service_plans",
        "columns": [
            {"name": "plan_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "plan_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "product_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "monthly_price", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "speed_mbps", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "data_cap_gb", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "contract_months", "type": "INTEGER", "mode": "NULLABLE"},
        ],
        "description": "Service plans tied to products.",
    },
    {
        "name": "plan_features",
        "columns": [
            {"name": "feature_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "plan_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "feature_name", "type": "STRING", "mode": "NULLABLE"},
            {"name": "feature_value", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Features included in each plan.",
    },
    # ── Customers & Accounts ──────────────────────────────────────────────────
    {
        "name": "customers",
        "columns": [
            {"name": "customer_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "first_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "last_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "email", "type": "STRING", "mode": "NULLABLE"},
            {"name": "phone", "type": "STRING", "mode": "NULLABLE"},
            {"name": "id_number", "type": "STRING", "mode": "NULLABLE"},
            {"name": "date_of_birth", "type": "DATE", "mode": "NULLABLE"},
            {"name": "signup_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "loyalty_tier", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Customer master table.",
    },
    {
        "name": "addresses",
        "columns": [
            {"name": "address_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "street", "type": "STRING", "mode": "NULLABLE"},
            {"name": "city", "type": "STRING", "mode": "NULLABLE"},
            {"name": "province", "type": "STRING", "mode": "NULLABLE"},
            {"name": "postcode", "type": "STRING", "mode": "NULLABLE"},
            {"name": "country", "type": "STRING", "mode": "NULLABLE"},
            {"name": "latitude", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "longitude", "type": "FLOAT64", "mode": "NULLABLE"},
        ],
        "description": "Customer service addresses.",
    },
    {
        "name": "customer_accounts",
        "columns": [
            {"name": "account_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "account_number", "type": "STRING", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
            {"name": "opened_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "credit_limit", "type": "NUMERIC", "mode": "NULLABLE"},
        ],
        "description": "Customer billing accounts.",
    },
    {
        "name": "sim_cards",
        "columns": [
            {"name": "sim_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "account_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "iccid", "type": "STRING", "mode": "NULLABLE"},
            {"name": "msisdn", "type": "STRING", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
            {"name": "activated_date", "type": "DATE", "mode": "NULLABLE"},
        ],
        "description": "SIM cards linked to accounts.",
    },
    {
        "name": "devices",
        "columns": [
            {"name": "device_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "device_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "brand", "type": "STRING", "mode": "NULLABLE"},
            {"name": "model", "type": "STRING", "mode": "NULLABLE"},
            {"name": "serial_number", "type": "STRING", "mode": "NULLABLE"},
            {"name": "purchase_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "warranty_expiry", "type": "DATE", "mode": "NULLABLE"},
        ],
        "description": "Customer devices (routers, modems, phones).",
    },
    {
        "name": "customer_subscriptions",
        "columns": [
            {"name": "subscription_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "plan_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "start_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "end_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
            {"name": "monthly_fee", "type": "NUMERIC", "mode": "NULLABLE"},
        ],
        "description": "Active customer subscriptions.",
    },
    # ── Network ───────────────────────────────────────────────────────────────
    {
        "name": "towers",
        "columns": [
            {"name": "tower_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "tower_name", "type": "STRING", "mode": "NULLABLE"},
            {"name": "latitude", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "longitude", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "tower_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "capacity_users", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "install_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Cell towers / access points.",
    },
    {
        "name": "tower_equipment",
        "columns": [
            {"name": "equipment_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "tower_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "equipment_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "brand", "type": "STRING", "mode": "NULLABLE"},
            {"name": "model", "type": "STRING", "mode": "NULLABLE"},
            {"name": "serial_number", "type": "STRING", "mode": "NULLABLE"},
            {"name": "install_date", "type": "DATE", "mode": "NULLABLE"},
        ],
        "description": "Equipment installed at each tower.",
    },
    {
        "name": "tower_coverage",
        "columns": [
            {"name": "coverage_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "tower_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "radius_km", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "signal_strength", "type": "STRING", "mode": "NULLABLE"},
            {"name": "frequency_band", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Coverage area per tower.",
    },
    {
        "name": "customer_connections",
        "columns": [
            {"name": "connection_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "account_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "tower_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "connection_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "connected_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "monthly_data_gb", "type": "FLOAT64", "mode": "NULLABLE"},
        ],
        "description": "Which account connects to which tower.",
    },
    # ── Service Orders ────────────────────────────────────────────────────────
    {
        "name": "service_orders",
        "columns": [
            {"name": "order_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "account_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "order_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
            {"name": "requested_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "completed_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "assigned_agent_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "notes", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Service provisioning orders.",
    },
    # ── Support ───────────────────────────────────────────────────────────────
    {
        "name": "support_agents",
        "columns": [
            {"name": "agent_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "first_name", "type": "STRING", "mode": "NULLABLE"},
            {"name": "last_name", "type": "STRING", "mode": "NULLABLE"},
            {"name": "email", "type": "STRING", "mode": "NULLABLE"},
            {"name": "department", "type": "STRING", "mode": "NULLABLE"},
            {"name": "hire_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "is_active", "type": "BOOLEAN", "mode": "NULLABLE"},
        ],
        "description": "Support team agents.",
    },
    {
        "name": "support_tickets",
        "columns": [
            {"name": "ticket_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "account_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "agent_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "subject", "type": "STRING", "mode": "NULLABLE"},
            {"name": "description", "type": "STRING", "mode": "NULLABLE"},
            {"name": "priority", "type": "STRING", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
            {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "resolved_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Customer support tickets.",
    },
    {
        "name": "ticket_comments",
        "columns": [
            {"name": "comment_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "ticket_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "author", "type": "STRING", "mode": "NULLABLE"},
            {"name": "comment_text", "type": "STRING", "mode": "NULLABLE"},
            {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Comments on support tickets.",
    },
    {
        "name": "customer_ratings",
        "columns": [
            {"name": "rating_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "ticket_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "score", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "feedback", "type": "STRING", "mode": "NULLABLE"},
            {"name": "rated_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Customer satisfaction ratings.",
    },
    {
        "name": "agent_skills",
        "columns": [
            {"name": "skill_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "agent_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "category_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "proficiency", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Agent skills by product category.",
    },
    # ── Usage ─────────────────────────────────────────────────────────────────
    {
        "name": "data_usage",
        "columns": [
            {"name": "usage_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "account_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "usage_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "data_mb", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "upload_mb", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "download_mb", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "peak_hours", "type": "BOOLEAN", "mode": "NULLABLE"},
        ],
        "description": "Daily data usage per account.",
    },
    {
        "name": "call_logs",
        "columns": [
            {"name": "call_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "account_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "call_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "duration_seconds", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "destination_number", "type": "STRING", "mode": "NULLABLE"},
            {"name": "call_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "cost", "type": "NUMERIC", "mode": "NULLABLE"},
        ],
        "description": "Voice call records.",
    },
    {
        "name": "sms_logs",
        "columns": [
            {"name": "sms_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "account_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "sms_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "destination_number", "type": "STRING", "mode": "NULLABLE"},
            {"name": "direction", "type": "STRING", "mode": "NULLABLE"},
            {"name": "cost", "type": "NUMERIC", "mode": "NULLABLE"},
        ],
        "description": "SMS records.",
    },
    # ── Billing ───────────────────────────────────────────────────────────────
    {
        "name": "payment_methods",
        "columns": [
            {"name": "method_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "method_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "card_last_four", "type": "STRING", "mode": "NULLABLE"},
            {"name": "is_default", "type": "BOOLEAN", "mode": "NULLABLE"},
            {"name": "added_date", "type": "DATE", "mode": "NULLABLE"},
        ],
        "description": "Customer payment methods.",
    },
    {
        "name": "invoices",
        "columns": [
            {"name": "invoice_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "account_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "invoice_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "due_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "total_amount", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
            {"name": "paid_date", "type": "DATE", "mode": "NULLABLE"},
        ],
        "description": "Customer invoices.",
    },
    {
        "name": "invoice_items",
        "columns": [
            {"name": "item_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "invoice_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "description", "type": "STRING", "mode": "NULLABLE"},
            {"name": "quantity", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "unit_price", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "total", "type": "NUMERIC", "mode": "NULLABLE"},
        ],
        "description": "Line items on invoices.",
    },
    {
        "name": "payments",
        "columns": [
            {"name": "payment_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "invoice_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "method_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "amount", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "payment_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
            {"name": "reference_number", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Payment transactions.",
    },
    # ── Outages ───────────────────────────────────────────────────────────────
    {
        "name": "outages",
        "columns": [
            {"name": "outage_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "tower_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "start_time", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "end_time", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "cause", "type": "STRING", "mode": "NULLABLE"},
            {"name": "severity", "type": "STRING", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Network outage incidents.",
    },
    {
        "name": "affected_customers",
        "columns": [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "outage_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "account_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "impact_minutes", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "compensation_applied", "type": "BOOLEAN", "mode": "NULLABLE"},
        ],
        "description": "Customers affected by each outage.",
    },
    # ── Notifications ─────────────────────────────────────────────────────────
    {
        "name": "notifications",
        "columns": [
            {"name": "notification_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "channel", "type": "STRING", "mode": "NULLABLE"},
            {"name": "subject", "type": "STRING", "mode": "NULLABLE"},
            {"name": "body", "type": "STRING", "mode": "NULLABLE"},
            {"name": "sent_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "read_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Customer notifications (email, SMS, push).",
    },
    # ── Audit ─────────────────────────────────────────────────────────────────
    {
        "name": "audit_log",
        "columns": [
            {"name": "log_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "action", "type": "STRING", "mode": "NULLABLE"},
            {"name": "table_name", "type": "STRING", "mode": "NULLABLE"},
            {"name": "old_value", "type": "STRING", "mode": "NULLABLE"},
            {"name": "new_value", "type": "STRING", "mode": "NULLABLE"},
            {"name": "changed_by", "type": "STRING", "mode": "NULLABLE"},
            {"name": "changed_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Audit trail for customer changes.",
    },
    # ── Communications ────────────────────────────────────────────────────────
    {
        "name": "customer_communications",
        "columns": [
            {"name": "comm_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "channel", "type": "STRING", "mode": "NULLABLE"},
            {"name": "subject", "type": "STRING", "mode": "NULLABLE"},
            {"name": "body", "type": "STRING", "mode": "NULLABLE"},
            {"name": "sent_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "direction", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Customer communications history.",
    },
    {
        "name": "communication_templates",
        "columns": [
            {"name": "template_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "template_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "channel", "type": "STRING", "mode": "NULLABLE"},
            {"name": "subject_template", "type": "STRING", "mode": "NULLABLE"},
            {"name": "body_template", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Reusable communication templates.",
    },
    # ── Field Service ─────────────────────────────────────────────────────────
    {
        "name": "field_technicians",
        "columns": [
            {"name": "tech_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "first_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "last_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "phone", "type": "STRING", "mode": "NULLABLE"},
            {"name": "speciality", "type": "STRING", "mode": "NULLABLE"},
            {"name": "hire_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "is_active", "type": "BOOLEAN", "mode": "NULLABLE"},
        ],
        "description": "Field service technicians.",
    },
    {
        "name": "technician_assignments",
        "columns": [
            {"name": "assignment_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "tech_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "order_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "assigned_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "completed_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
            {"name": "notes", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Technician job assignments.",
    },
    {
        "name": "parts_inventory",
        "columns": [
            {"name": "part_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "part_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "part_number", "type": "STRING", "mode": "NULLABLE"},
            {"name": "category", "type": "STRING", "mode": "NULLABLE"},
            {"name": "unit_cost", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "stock_quantity", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "reorder_level", "type": "INTEGER", "mode": "NULLABLE"},
        ],
        "description": "Parts inventory for field service.",
    },
    {
        "name": "parts_used",
        "columns": [
            {"name": "usage_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "assignment_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "part_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "quantity_used", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "unit_cost", "type": "NUMERIC", "mode": "NULLABLE"},
        ],
        "description": "Parts consumed per technician assignment.",
    },
    # ── Training ──────────────────────────────────────────────────────────────
    {
        "name": "training_courses",
        "columns": [
            {"name": "course_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "course_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "description", "type": "STRING", "mode": "NULLABLE"},
            {"name": "duration_hours", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "provider", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Available training courses.",
    },
    {
        "name": "employee_training",
        "columns": [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "employee_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "course_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "completion_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "score", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "certificate_number", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Employee training completion records.",
    },
    # ── Contracts ─────────────────────────────────────────────────────────────
    {
        "name": "contracts",
        "columns": [
            {"name": "contract_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "contract_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "start_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "end_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "total_value", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
            {"name": "signed_date", "type": "DATE", "mode": "NULLABLE"},
        ],
        "description": "Customer contracts.",
    },
    {
        "name": "contract_terms",
        "columns": [
            {"name": "term_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "contract_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "term_name", "type": "STRING", "mode": "NULLABLE"},
            {"name": "term_value", "type": "STRING", "mode": "NULLABLE"},
            {"name": "description", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Individual terms within contracts.",
    },
    {
        "name": "sla_agreements",
        "columns": [
            {"name": "sla_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "contract_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "service_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "uptime_percent", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "response_time_hours", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "penalty_clause", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Service level agreements per contract.",
    },
    {
        "name": "sla_violations",
        "columns": [
            {"name": "violation_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "sla_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "incident_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "violation_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "resolution_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "penalty_applied", "type": "NUMERIC", "mode": "NULLABLE"},
        ],
        "description": "SLA breach records.",
    },
    # ── Network Incidents ─────────────────────────────────────────────────────
    {
        "name": "network_incidents",
        "columns": [
            {"name": "incident_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "tower_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "incident_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "severity", "type": "STRING", "mode": "NULLABLE"},
            {"name": "description", "type": "STRING", "mode": "NULLABLE"},
            {"name": "reported_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "resolved_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Network incident records.",
    },
    {
        "name": "incident_updates",
        "columns": [
            {"name": "update_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "incident_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "updated_by", "type": "STRING", "mode": "NULLABLE"},
            {"name": "update_text", "type": "STRING", "mode": "NULLABLE"},
            {"name": "update_time", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Status updates for network incidents.",
    },
    # ── Feedback ──────────────────────────────────────────────────────────────
    {
        "name": "customer_feedback",
        "columns": [
            {"name": "feedback_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "feedback_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "subject", "type": "STRING", "mode": "NULLABLE"},
            {"name": "message", "type": "STRING", "mode": "NULLABLE"},
            {"name": "submitted_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Customer feedback submissions.",
    },
    {
        "name": "surveys",
        "columns": [
            {"name": "survey_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "survey_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "description", "type": "STRING", "mode": "NULLABLE"},
            {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "is_active", "type": "BOOLEAN", "mode": "NULLABLE"},
        ],
        "description": "Survey definitions.",
    },
    {
        "name": "survey_questions",
        "columns": [
            {"name": "question_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "survey_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "question_text", "type": "STRING", "mode": "NULLABLE"},
            {"name": "question_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "sort_order", "type": "INTEGER", "mode": "NULLABLE"},
        ],
        "description": "Questions within surveys.",
    },
    {
        "name": "survey_responses",
        "columns": [
            {"name": "response_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "survey_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "submitted_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Survey response headers.",
    },
    {
        "name": "survey_answers",
        "columns": [
            {"name": "answer_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "response_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "question_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "answer_text", "type": "STRING", "mode": "NULLABLE"},
            {"name": "answer_value", "type": "INTEGER", "mode": "NULLABLE"},
        ],
        "description": "Individual answers to survey questions.",
    },
    # ── Promotions ────────────────────────────────────────────────────────────
    {
        "name": "promotions",
        "columns": [
            {"name": "promo_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "promo_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "description", "type": "STRING", "mode": "NULLABLE"},
            {"name": "discount_percent", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "start_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "end_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "is_active", "type": "BOOLEAN", "mode": "NULLABLE"},
        ],
        "description": "Promotional campaigns.",
    },
    {
        "name": "promotion_targets",
        "columns": [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "promo_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "targeted_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Promotion targeting records.",
    },
    {
        "name": "promotion_redemptions",
        "columns": [
            {"name": "redemption_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "promo_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "redeemed_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "discount_amount", "type": "NUMERIC", "mode": "NULLABLE"},
        ],
        "description": "Promotion redemption records.",
    },
    # ── Inventory ─────────────────────────────────────────────────────────────
    {
        "name": "inventory_items",
        "columns": [
            {"name": "item_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "item_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "sku", "type": "STRING", "mode": "NULLABLE"},
            {"name": "category", "type": "STRING", "mode": "NULLABLE"},
            {"name": "unit_price", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "quantity_in_stock", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "reorder_point", "type": "INTEGER", "mode": "NULLABLE"},
        ],
        "description": "Inventory master list.",
    },
    {
        "name": "inventory_transactions",
        "columns": [
            {"name": "transaction_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "item_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "transaction_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "quantity", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "unit_price", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "transaction_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "reference_number", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Inventory movement transactions.",
    },
    {
        "name": "purchase_orders",
        "columns": [
            {"name": "po_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "supplier_name", "type": "STRING", "mode": "NULLABLE"},
            {"name": "order_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "total_amount", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
            {"name": "expected_delivery", "type": "DATE", "mode": "NULLABLE"},
        ],
        "description": "Purchase orders to suppliers.",
    },
    {
        "name": "purchase_order_items",
        "columns": [
            {"name": "po_item_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "po_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "item_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "quantity", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "unit_price", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "total", "type": "NUMERIC", "mode": "NULLABLE"},
        ],
        "description": "Line items on purchase orders.",
    },
    # ── Vendor ────────────────────────────────────────────────────────────────
    {
        "name": "vendors",
        "columns": [
            {"name": "vendor_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "vendor_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "contact_person", "type": "STRING", "mode": "NULLABLE"},
            {"name": "email", "type": "STRING", "mode": "NULLABLE"},
            {"name": "phone", "type": "STRING", "mode": "NULLABLE"},
            {"name": "address", "type": "STRING", "mode": "NULLABLE"},
            {"name": "category", "type": "STRING", "mode": "NULLABLE"},
            {"name": "rating", "type": "INTEGER", "mode": "NULLABLE"},
        ],
        "description": "Vendor/supplier master.",
    },
    {
        "name": "vendor_contracts",
        "columns": [
            {"name": "vc_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "vendor_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "service_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "start_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "end_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "monthly_value", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Vendor service contracts.",
    },
    # ── Asset Management ──────────────────────────────────────────────────────
    {
        "name": "assets",
        "columns": [
            {"name": "asset_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "asset_tag", "type": "STRING", "mode": "REQUIRED"},
            {"name": "asset_name", "type": "STRING", "mode": "NULLABLE"},
            {"name": "category", "type": "STRING", "mode": "NULLABLE"},
            {"name": "purchase_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "purchase_cost", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
            {"name": "location", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Company assets registry.",
    },
    {
        "name": "asset_maintenance",
        "columns": [
            {"name": "maintenance_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "asset_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "maintenance_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "description", "type": "STRING", "mode": "NULLABLE"},
            {"name": "scheduled_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "completed_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "cost", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "technician_id", "type": "INTEGER", "mode": "NULLABLE"},
        ],
        "description": "Asset maintenance history.",
    },
    # ── Customer Notes & Preferences ──────────────────────────────────────────
    {
        "name": "customer_notes",
        "columns": [
            {"name": "note_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "note_text", "type": "STRING", "mode": "NULLABLE"},
            {"name": "created_by", "type": "STRING", "mode": "NULLABLE"},
            {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "note_type", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Internal customer notes.",
    },
    {
        "name": "customer_preferences",
        "columns": [
            {"name": "pref_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "preference_key", "type": "STRING", "mode": "NULLABLE"},
            {"name": "preference_value", "type": "STRING", "mode": "NULLABLE"},
            {"name": "updated_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Customer preference settings.",
    },
    # ── Loyalty ───────────────────────────────────────────────────────────────
    {
        "name": "loyalty_programs",
        "columns": [
            {"name": "program_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "program_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "description", "type": "STRING", "mode": "NULLABLE"},
            {"name": "points_per_rand", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "is_active", "type": "BOOLEAN", "mode": "NULLABLE"},
        ],
        "description": "Loyalty program definitions.",
    },
    {
        "name": "loyalty_rewards",
        "columns": [
            {"name": "reward_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "program_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "reward_name", "type": "STRING", "mode": "NULLABLE"},
            {"name": "points_required", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "description", "type": "STRING", "mode": "NULLABLE"},
            {"name": "is_available", "type": "BOOLEAN", "mode": "NULLABLE"},
        ],
        "description": "Loyalty rewards catalogue.",
    },
    {
        "name": "loyalty_points",
        "columns": [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "program_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "points_balance", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "earned_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "expiry_date", "type": "DATE", "mode": "NULLABLE"},
        ],
        "description": "Loyalty points balances.",
    },
    {
        "name": "loyalty_redemptions",
        "columns": [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "reward_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "points_spent", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "redeemed_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Loyalty reward redemption history.",
    },
    # ── Referrals ─────────────────────────────────────────────────────────────
    {
        "name": "referral_programs",
        "columns": [
            {"name": "ref_program_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "program_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "referrer_reward", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "referee_reward", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "is_active", "type": "BOOLEAN", "mode": "NULLABLE"},
        ],
        "description": "Referral program definitions.",
    },
    {
        "name": "referral_rewards",
        "columns": [
            {"name": "ref_reward_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "ref_program_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "referred_customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "reward_amount", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
            {"name": "earned_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Referral reward records.",
    },
    # ── Email/SMS Marketing ───────────────────────────────────────────────────
    {
        "name": "email_campaigns",
        "columns": [
            {"name": "campaign_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "campaign_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "subject", "type": "STRING", "mode": "NULLABLE"},
            {"name": "body_template", "type": "STRING", "mode": "NULLABLE"},
            {"name": "sent_count", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "open_count", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "click_count", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "sent_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Email marketing campaigns.",
    },
    {
        "name": "email_recipients",
        "columns": [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "campaign_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "email_address", "type": "STRING", "mode": "NULLABLE"},
            {"name": "sent_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "opened_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "clicked_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Email campaign recipients.",
    },
    {
        "name": "sms_campaigns",
        "columns": [
            {"name": "sms_campaign_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "campaign_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "message_template", "type": "STRING", "mode": "NULLABLE"},
            {"name": "sent_count", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "sent_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "SMS marketing campaigns.",
    },
    {
        "name": "sms_recipients",
        "columns": [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "sms_campaign_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "phone_number", "type": "STRING", "mode": "NULLABLE"},
            {"name": "sent_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "delivered_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "SMS campaign recipients.",
    },
    # ── Web and App ───────────────────────────────────────────────────────────
    {
        "name": "user_accounts",
        "columns": [
            {"name": "user_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "username", "type": "STRING", "mode": "NULLABLE"},
            {"name": "password_hash", "type": "STRING", "mode": "NULLABLE"},
            {"name": "email", "type": "STRING", "mode": "NULLABLE"},
            {"name": "last_login", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "is_active", "type": "BOOLEAN", "mode": "NULLABLE"},
            {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Web portal user accounts.",
    },
    {
        "name": "user_roles",
        "columns": [
            {"name": "role_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "role_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "description", "type": "STRING", "mode": "NULLABLE"},
            {"name": "permissions", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "User role definitions.",
    },
    {
        "name": "user_role_assignments",
        "columns": [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "user_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "role_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "assigned_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "User-role mappings.",
    },
    {
        "name": "api_keys",
        "columns": [
            {"name": "key_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "user_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "key_name", "type": "STRING", "mode": "NULLABLE"},
            {"name": "api_key", "type": "STRING", "mode": "NULLABLE"},
            {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "expires_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "is_active", "type": "BOOLEAN", "mode": "NULLABLE"},
        ],
        "description": "API key management.",
    },
    {
        "name": "api_usage_logs",
        "columns": [
            {"name": "log_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "key_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "endpoint", "type": "STRING", "mode": "NULLABLE"},
            {"name": "method", "type": "STRING", "mode": "NULLABLE"},
            {"name": "status_code", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "response_time_ms", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "logged_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "API request logs.",
    },
    {
        "name": "app_sessions",
        "columns": [
            {"name": "session_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "user_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "device_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "ip_address", "type": "STRING", "mode": "NULLABLE"},
            {"name": "user_agent", "type": "STRING", "mode": "NULLABLE"},
            {"name": "started_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "ended_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "User session tracking.",
    },
    # ── Product Reviews ───────────────────────────────────────────────────────
    {
        "name": "product_reviews",
        "columns": [
            {"name": "review_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "product_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "rating", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "title", "type": "STRING", "mode": "NULLABLE"},
            {"name": "review_text", "type": "STRING", "mode": "NULLABLE"},
            {"name": "review_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "is_verified", "type": "BOOLEAN", "mode": "NULLABLE"},
        ],
        "description": "Customer product reviews.",
    },
    {
        "name": "product_review_votes",
        "columns": [
            {"name": "vote_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "review_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "vote_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "voted_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Helpful/not helpful votes on reviews.",
    },
    # ── Wishlists ─────────────────────────────────────────────────────────────
    {
        "name": "wishlists",
        "columns": [
            {"name": "wishlist_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Customer wishlists.",
    },
    {
        "name": "wishlist_items",
        "columns": [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "wishlist_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "product_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "added_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "priority", "type": "INTEGER", "mode": "NULLABLE"},
        ],
        "description": "Items in customer wishlists.",
    },
    # ── Reports ───────────────────────────────────────────────────────────────
    {
        "name": "report_definitions",
        "columns": [
            {"name": "report_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "report_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "report_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "query_template", "type": "STRING", "mode": "NULLABLE"},
            {"name": "created_by", "type": "STRING", "mode": "NULLABLE"},
            {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Report template definitions.",
    },
    {
        "name": "report_schedules",
        "columns": [
            {"name": "schedule_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "report_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "frequency", "type": "STRING", "mode": "NULLABLE"},
            {"name": "next_run", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "last_run", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "is_active", "type": "BOOLEAN", "mode": "NULLABLE"},
        ],
        "description": "Scheduled report configurations.",
    },
    {
        "name": "report_history",
        "columns": [
            {"name": "history_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "report_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "schedule_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "generated_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "row_count", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "file_path", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Report generation history.",
    },
    # ── Tariff Changes ────────────────────────────────────────────────────────
    {
        "name": "tariff_changes",
        "columns": [
            {"name": "change_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "plan_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "old_price", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "new_price", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "effective_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "approved_by", "type": "STRING", "mode": "NULLABLE"},
            {"name": "reason", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Plan price change history.",
    },
    # ── Service Level History ─────────────────────────────────────────────────
    {
        "name": "service_level_history",
        "columns": [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "account_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "old_level", "type": "STRING", "mode": "NULLABLE"},
            {"name": "new_level", "type": "STRING", "mode": "NULLABLE"},
            {"name": "changed_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "reason", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Customer service tier change history.",
    },
    # ── Network Capacity Metrics ──────────────────────────────────────────────
    {
        "name": "network_capacity_metrics",
        "columns": [
            {"name": "metric_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "tower_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "recorded_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "cpu_utilization", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "memory_utilization", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "bandwidth_utilization", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "connected_users", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "throughput_mbps", "type": "NUMERIC", "mode": "NULLABLE"},
        ],
        "description": "Tower capacity and performance metrics.",
    },
    # ── Customer Segments ─────────────────────────────────────────────────────
    {
        "name": "customer_segments",
        "columns": [
            {"name": "segment_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "segment_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "description", "type": "STRING", "mode": "NULLABLE"},
            {"name": "criteria", "type": "STRING", "mode": "NULLABLE"},
            {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Marketing customer segments.",
    },
    {
        "name": "customer_segment_members",
        "columns": [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "segment_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "added_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Customer-segment membership.",
    },
    # ── Complaints ────────────────────────────────────────────────────────────
    {
        "name": "complaint_categories",
        "columns": [
            {"name": "category_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "category_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "description", "type": "STRING", "mode": "NULLABLE"},
            {"name": "severity_default", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Complaint category definitions.",
    },
    {
        "name": "complaints",
        "columns": [
            {"name": "complaint_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "customer_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "category_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "ticket_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "subject", "type": "STRING", "mode": "NULLABLE"},
            {"name": "description", "type": "STRING", "mode": "NULLABLE"},
            {"name": "severity", "type": "STRING", "mode": "NULLABLE"},
            {"name": "status", "type": "STRING", "mode": "NULLABLE"},
            {"name": "filed_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "resolved_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Formal customer complaints.",
    },
    {
        "name": "complaint_escalations",
        "columns": [
            {"name": "escalation_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "complaint_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "escalated_to", "type": "STRING", "mode": "NULLABLE"},
            {"name": "reason", "type": "STRING", "mode": "NULLABLE"},
            {"name": "escalated_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "resolved_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        ],
        "description": "Complaint escalation records.",
    },
    # ── Service Quality Metrics ───────────────────────────────────────────────
    {
        "name": "service_quality_metrics",
        "columns": [
            {"name": "sqm_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "account_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "recorded_date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "latency_ms", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "jitter_ms", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "packet_loss_percent", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "download_speed_mbps", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "upload_speed_mbps", "type": "NUMERIC", "mode": "NULLABLE"},
        ],
        "description": "Per-account quality of service metrics.",
    },
    # ── Network Equipment Models ──────────────────────────────────────────────
    {
        "name": "network_equipment_models",
        "columns": [
            {"name": "model_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "manufacturer", "type": "STRING", "mode": "NULLABLE"},
            {"name": "model_name", "type": "STRING", "mode": "NULLABLE"},
            {"name": "equipment_type", "type": "STRING", "mode": "NULLABLE"},
            {"name": "max_throughput_mbps", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "supported_bands", "type": "STRING", "mode": "NULLABLE"},
            {"name": "unit_cost", "type": "NUMERIC", "mode": "NULLABLE"},
        ],
        "description": "Network equipment model catalogue.",
    },
    # ── Service Regions ───────────────────────────────────────────────────────
    {
        "name": "service_regions",
        "columns": [
            {"name": "region_id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "region_name", "type": "STRING", "mode": "REQUIRED"},
            {"name": "province", "type": "STRING", "mode": "NULLABLE"},
            {"name": "population_estimate", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "coverage_priority", "type": "STRING", "mode": "NULLABLE"},
        ],
        "description": "Service coverage regions.",
    },
    {
        "name": "region_coverage",
        "columns": [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "region_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "tower_id", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "coverage_percent", "type": "NUMERIC", "mode": "NULLABLE"},
            {"name": "last_assessed", "type": "DATE", "mode": "NULLABLE"},
        ],
        "description": "Tower coverage per region.",
    },
]


# ── Teradata test tables ─────────────────────────────────────────────────────

TD_TEST_TABLES_RAW: list[tuple[str, str, str]] = [
    # ── Employees & Departments ───────────────────────────────────────────────
    (
        "departments",
        """CREATE TABLE {db}.departments (
            dept_id       INTEGER NOT NULL PRIMARY KEY,
            dept_name     VARCHAR(100) NOT NULL,
            location      VARCHAR(100),
            budget        DECIMAL(12,2)
        )""",
        "Company departments.",
    ),
    (
        "employees",
        """CREATE TABLE {db}.employees (
            employee_id   INTEGER NOT NULL PRIMARY KEY,
            first_name    VARCHAR(50) NOT NULL,
            last_name     VARCHAR(50) NOT NULL,
            email         VARCHAR(100),
            phone         VARCHAR(20),
            job_title     VARCHAR(100),
            dept_id       INTEGER REFERENCES {db}.departments(dept_id),
            manager_id    INTEGER REFERENCES {db}.employees(employee_id),
            hire_date     DATE,
            salary        DECIMAL(12,2)
        )""",
        "Employee records with self-referencing manager FK.",
    ),
    # ── Products & Plans ──────────────────────────────────────────────────────
    (
        "product_categories",
        """CREATE TABLE {db}.product_categories (
            category_id   INTEGER NOT NULL PRIMARY KEY,
            category_name VARCHAR(100) NOT NULL,
            description   VARCHAR(255)
        )""",
        "Product category lookup.",
    ),
    (
        "products",
        """CREATE TABLE {db}.products (
            product_id    INTEGER NOT NULL PRIMARY KEY,
            product_name  VARCHAR(100) NOT NULL,
            category_id   INTEGER REFERENCES {db}.product_categories(category_id),
            base_price    DECIMAL(10,2),
            is_active     BYTEINT DEFAULT 1,
            launch_date   DATE
        )""",
        "ISP products.",
    ),
    (
        "service_plans",
        """CREATE TABLE {db}.service_plans (
            plan_id       INTEGER NOT NULL PRIMARY KEY,
            plan_name     VARCHAR(100) NOT NULL,
            product_id    INTEGER REFERENCES {db}.products(product_id),
            monthly_price DECIMAL(10,2),
            speed_mbps    INTEGER,
            data_cap_gb   INTEGER,
            contract_months INTEGER
        )""",
        "Service plans tied to products.",
    ),
    (
        "plan_features",
        """CREATE TABLE {db}.plan_features (
            feature_id    INTEGER NOT NULL PRIMARY KEY,
            plan_id       INTEGER REFERENCES {db}.service_plans(plan_id),
            feature_name  VARCHAR(100),
            feature_value VARCHAR(100)
        )""",
        "Features included in each plan.",
    ),
    # ── Customers & Accounts ──────────────────────────────────────────────────
    (
        "customers",
        """CREATE TABLE {db}.customers (
            customer_id   INTEGER NOT NULL PRIMARY KEY,
            first_name    VARCHAR(50) NOT NULL,
            last_name     VARCHAR(50) NOT NULL,
            email         VARCHAR(100),
            phone         VARCHAR(20),
            id_number     VARCHAR(30),
            date_of_birth DATE,
            signup_date   DATE,
            loyalty_tier  VARCHAR(20)
        )""",
        "Customer master table.",
    ),
    (
        "addresses",
        """CREATE TABLE {db}.addresses (
            address_id    INTEGER NOT NULL PRIMARY KEY,
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            street        VARCHAR(150),
            city          VARCHAR(100),
            province      VARCHAR(100),
            postcode      VARCHAR(10),
            country       VARCHAR(50),
            latitude      FLOAT,
            longitude     FLOAT
        )""",
        "Customer service addresses.",
    ),
    (
        "customer_accounts",
        """CREATE TABLE {db}.customer_accounts (
            account_id    INTEGER NOT NULL PRIMARY KEY,
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            account_number VARCHAR(30),
            status        VARCHAR(20),
            opened_date   DATE,
            credit_limit  DECIMAL(12,2)
        )""",
        "Customer billing accounts.",
    ),
    (
        "sim_cards",
        """CREATE TABLE {db}.sim_cards (
            sim_id        INTEGER NOT NULL PRIMARY KEY,
            account_id    INTEGER REFERENCES {db}.customer_accounts(account_id),
            iccid         VARCHAR(30),
            msisdn        VARCHAR(20),
            status        VARCHAR(20),
            activated_date DATE
        )""",
        "SIM cards linked to accounts.",
    ),
    (
        "devices",
        """CREATE TABLE {db}.devices (
            device_id     INTEGER NOT NULL PRIMARY KEY,
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            device_type   VARCHAR(50),
            brand         VARCHAR(50),
            model         VARCHAR(50),
            serial_number VARCHAR(50),
            purchase_date DATE,
            warranty_expiry DATE
        )""",
        "Customer devices.",
    ),
    (
        "customer_subscriptions",
        """CREATE TABLE {db}.customer_subscriptions (
            subscription_id INTEGER NOT NULL PRIMARY KEY,
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            plan_id       INTEGER REFERENCES {db}.service_plans(plan_id),
            start_date    DATE,
            end_date      DATE,
            status        VARCHAR(20),
            monthly_fee   DECIMAL(10,2)
        )""",
        "Active customer subscriptions.",
    ),
    # ── Network ───────────────────────────────────────────────────────────────
    (
        "towers",
        """CREATE TABLE {db}.towers (
            tower_id      INTEGER NOT NULL PRIMARY KEY,
            tower_name    VARCHAR(100),
            latitude      FLOAT,
            longitude     FLOAT,
            tower_type    VARCHAR(50),
            capacity_users INTEGER,
            install_date  DATE,
            status        VARCHAR(20)
        )""",
        "Cell towers / access points.",
    ),
    (
        "tower_equipment",
        """CREATE TABLE {db}.tower_equipment (
            equipment_id  INTEGER NOT NULL PRIMARY KEY,
            tower_id      INTEGER REFERENCES {db}.towers(tower_id),
            equipment_type VARCHAR(50),
            brand         VARCHAR(50),
            model         VARCHAR(50),
            serial_number VARCHAR(50),
            install_date  DATE
        )""",
        "Equipment installed at each tower.",
    ),
    (
        "tower_coverage",
        """CREATE TABLE {db}.tower_coverage (
            coverage_id   INTEGER NOT NULL PRIMARY KEY,
            tower_id      INTEGER REFERENCES {db}.towers(tower_id),
            radius_km     FLOAT,
            signal_strength VARCHAR(20),
            frequency_band VARCHAR(20)
        )""",
        "Coverage area per tower.",
    ),
    (
        "customer_connections",
        """CREATE TABLE {db}.customer_connections (
            connection_id INTEGER NOT NULL PRIMARY KEY,
            account_id    INTEGER REFERENCES {db}.customer_accounts(account_id),
            tower_id      INTEGER REFERENCES {db}.towers(tower_id),
            connection_type VARCHAR(30),
            connected_date DATE,
            monthly_data_gb FLOAT
        )""",
        "Account-to-tower connections.",
    ),
    # ── Service Orders ────────────────────────────────────────────────────────
    (
        "service_orders",
        """CREATE TABLE {db}.service_orders (
            order_id      INTEGER NOT NULL PRIMARY KEY,
            account_id    INTEGER REFERENCES {db}.customer_accounts(account_id),
            order_type    VARCHAR(50),
            status        VARCHAR(20),
            requested_date DATE,
            completed_date DATE,
            assigned_agent_id INTEGER,
            notes         VARCHAR(500)
        )""",
        "Service provisioning orders.",
    ),
    # ── Support ───────────────────────────────────────────────────────────────
    (
        "support_agents",
        """CREATE TABLE {db}.support_agents (
            agent_id      INTEGER NOT NULL PRIMARY KEY,
            first_name    VARCHAR(50),
            last_name     VARCHAR(50),
            email         VARCHAR(100),
            department    VARCHAR(50),
            hire_date     DATE,
            is_active     BYTEINT DEFAULT 1
        )""",
        "Support team agents.",
    ),
    (
        "support_tickets",
        """CREATE TABLE {db}.support_tickets (
            ticket_id     INTEGER NOT NULL PRIMARY KEY,
            account_id    INTEGER REFERENCES {db}.customer_accounts(account_id),
            agent_id      INTEGER REFERENCES {db}.support_agents(agent_id),
            subject       VARCHAR(200),
            description   VARCHAR(2000),
            priority      VARCHAR(20),
            status        VARCHAR(20),
            created_at    TIMESTAMP(0),
            resolved_at   TIMESTAMP(0)
        )""",
        "Customer support tickets.",
    ),
    (
        "ticket_comments",
        """CREATE TABLE {db}.ticket_comments (
            comment_id    INTEGER NOT NULL PRIMARY KEY,
            ticket_id     INTEGER REFERENCES {db}.support_tickets(ticket_id),
            author        VARCHAR(100),
            comment_text  VARCHAR(2000),
            created_at    TIMESTAMP(0)
        )""",
        "Comments on support tickets.",
    ),
    (
        "customer_ratings",
        """CREATE TABLE {db}.customer_ratings (
            rating_id     INTEGER NOT NULL PRIMARY KEY,
            ticket_id     INTEGER REFERENCES {db}.support_tickets(ticket_id),
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            score         INTEGER,
            feedback      VARCHAR(500),
            rated_at      TIMESTAMP(0)
        )""",
        "Customer satisfaction ratings.",
    ),
    (
        "agent_skills",
        """CREATE TABLE {db}.agent_skills (
            skill_id      INTEGER NOT NULL PRIMARY KEY,
            agent_id      INTEGER REFERENCES {db}.support_agents(agent_id),
            category_id   INTEGER REFERENCES {db}.product_categories(category_id),
            proficiency   VARCHAR(20)
        )""",
        "Agent skills by product category.",
    ),
    # ── Usage ─────────────────────────────────────────────────────────────────
    (
        "data_usage",
        """CREATE TABLE {db}.data_usage (
            usage_id      INTEGER NOT NULL PRIMARY KEY,
            account_id    INTEGER REFERENCES {db}.customer_accounts(account_id),
            usage_date    DATE,
            data_mb       FLOAT,
            upload_mb     FLOAT,
            download_mb   FLOAT,
            peak_hours    BYTEINT
        )""",
        "Daily data usage per account.",
    ),
    (
        "call_logs",
        """CREATE TABLE {db}.call_logs (
            call_id       INTEGER NOT NULL PRIMARY KEY,
            account_id    INTEGER REFERENCES {db}.customer_accounts(account_id),
            call_date     DATE,
            duration_seconds INTEGER,
            destination_number VARCHAR(20),
            call_type     VARCHAR(20),
            cost          DECIMAL(8,2)
        )""",
        "Voice call records.",
    ),
    (
        "sms_logs",
        """CREATE TABLE {db}.sms_logs (
            sms_id        INTEGER NOT NULL PRIMARY KEY,
            account_id    INTEGER REFERENCES {db}.customer_accounts(account_id),
            sms_date      DATE,
            destination_number VARCHAR(20),
            direction     VARCHAR(10),
            cost          DECIMAL(6,2)
        )""",
        "SMS records.",
    ),
    # ── Billing ───────────────────────────────────────────────────────────────
    (
        "payment_methods",
        """CREATE TABLE {db}.payment_methods (
            method_id     INTEGER NOT NULL PRIMARY KEY,
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            method_type   VARCHAR(30),
            card_last_four VARCHAR(4),
            is_default    BYTEINT DEFAULT 0,
            added_date    DATE
        )""",
        "Customer payment methods.",
    ),
    (
        "invoices",
        """CREATE TABLE {db}.invoices (
            invoice_id    INTEGER NOT NULL PRIMARY KEY,
            account_id    INTEGER REFERENCES {db}.customer_accounts(account_id),
            invoice_date  DATE,
            due_date      DATE,
            total_amount  DECIMAL(12,2),
            status        VARCHAR(20),
            paid_date     DATE
        )""",
        "Customer invoices.",
    ),
    (
        "invoice_items",
        """CREATE TABLE {db}.invoice_items (
            item_id       INTEGER NOT NULL PRIMARY KEY,
            invoice_id    INTEGER REFERENCES {db}.invoices(invoice_id),
            description   VARCHAR(200),
            quantity      INTEGER,
            unit_price    DECIMAL(10,2),
            total         DECIMAL(12,2)
        )""",
        "Line items on invoices.",
    ),
    (
        "payments",
        """CREATE TABLE {db}.payments (
            payment_id    INTEGER NOT NULL PRIMARY KEY,
            invoice_id    INTEGER REFERENCES {db}.invoices(invoice_id),
            method_id     INTEGER REFERENCES {db}.payment_methods(method_id),
            amount        DECIMAL(12,2),
            payment_date  DATE,
            status        VARCHAR(20),
            reference_number VARCHAR(50)
        )""",
        "Payment transactions.",
    ),
    # ── Outages ───────────────────────────────────────────────────────────────
    (
        "outages",
        """CREATE TABLE {db}.outages (
            outage_id     INTEGER NOT NULL PRIMARY KEY,
            tower_id      INTEGER REFERENCES {db}.towers(tower_id),
            start_time    TIMESTAMP(0),
            end_time      TIMESTAMP(0),
            cause         VARCHAR(200),
            severity      VARCHAR(20),
            status        VARCHAR(20)
        )""",
        "Network outage incidents.",
    ),
    (
        "affected_customers",
        """CREATE TABLE {db}.affected_customers (
            id            INTEGER NOT NULL PRIMARY KEY,
            outage_id     INTEGER REFERENCES {db}.outages(outage_id),
            account_id    INTEGER REFERENCES {db}.customer_accounts(account_id),
            impact_minutes INTEGER,
            compensation_applied BYTEINT DEFAULT 0
        )""",
        "Customers affected by each outage.",
    ),
    # ── Notifications ─────────────────────────────────────────────────────────
    (
        "notifications",
        """CREATE TABLE {db}.notifications (
            notification_id INTEGER NOT NULL PRIMARY KEY,
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            channel       VARCHAR(20),
            subject       VARCHAR(200),
            body          VARCHAR(2000),
            sent_at       TIMESTAMP(0),
            read_at       TIMESTAMP(0)
        )""",
        "Customer notifications.",
    ),
    # ── Audit ─────────────────────────────────────────────────────────────────
    (
        "audit_log",
        """CREATE TABLE {db}.audit_log (
            log_id        INTEGER NOT NULL PRIMARY KEY,
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            action        VARCHAR(50),
            table_name    VARCHAR(50),
            old_value     VARCHAR(500),
            new_value     VARCHAR(500),
            changed_by    VARCHAR(100),
            changed_at    TIMESTAMP(0)
        )""",
        "Audit trail for customer changes.",
    ),
    # ── Communications ────────────────────────────────────────────────────────
    (
        "customer_communications",
        """CREATE TABLE {db}.customer_communications (
            comm_id       INTEGER NOT NULL PRIMARY KEY,
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            channel       VARCHAR(20),
            subject       VARCHAR(200),
            body          VARCHAR(2000),
            sent_at       TIMESTAMP(0),
            direction     VARCHAR(10)
        )""",
        "Customer communications history.",
    ),
    (
        "communication_templates",
        """CREATE TABLE {db}.communication_templates (
            template_id   INTEGER NOT NULL PRIMARY KEY,
            template_name VARCHAR(100) NOT NULL,
            channel       VARCHAR(20),
            subject_template VARCHAR(200),
            body_template VARCHAR(2000)
        )""",
        "Reusable communication templates.",
    ),
    # ── Field Service ─────────────────────────────────────────────────────────
    (
        "field_technicians",
        """CREATE TABLE {db}.field_technicians (
            tech_id       INTEGER NOT NULL PRIMARY KEY,
            first_name    VARCHAR(50) NOT NULL,
            last_name     VARCHAR(50) NOT NULL,
            phone         VARCHAR(20),
            speciality    VARCHAR(50),
            hire_date     DATE,
            is_active     BYTEINT DEFAULT 1
        )""",
        "Field service technicians.",
    ),
    (
        "technician_assignments",
        """CREATE TABLE {db}.technician_assignments (
            assignment_id INTEGER NOT NULL PRIMARY KEY,
            tech_id       INTEGER REFERENCES {db}.field_technicians(tech_id),
            order_id      INTEGER REFERENCES {db}.service_orders(order_id),
            assigned_date DATE,
            completed_date DATE,
            status        VARCHAR(20),
            notes         VARCHAR(500)
        )""",
        "Technician job assignments.",
    ),
    (
        "parts_inventory",
        """CREATE TABLE {db}.parts_inventory (
            part_id       INTEGER NOT NULL PRIMARY KEY,
            part_name     VARCHAR(100) NOT NULL,
            part_number   VARCHAR(50),
            category      VARCHAR(50),
            unit_cost     DECIMAL(10,2),
            stock_quantity INTEGER,
            reorder_level INTEGER
        )""",
        "Parts inventory for field service.",
    ),
    (
        "parts_used",
        """CREATE TABLE {db}.parts_used (
            usage_id      INTEGER NOT NULL PRIMARY KEY,
            assignment_id INTEGER REFERENCES {db}.technician_assignments(assignment_id),
            part_id       INTEGER REFERENCES {db}.parts_inventory(part_id),
            quantity_used INTEGER,
            unit_cost     DECIMAL(10,2)
        )""",
        "Parts consumed per technician assignment.",
    ),
    # ── Training ──────────────────────────────────────────────────────────────
    (
        "training_courses",
        """CREATE TABLE {db}.training_courses (
            course_id     INTEGER NOT NULL PRIMARY KEY,
            course_name   VARCHAR(100) NOT NULL,
            description   VARCHAR(500),
            duration_hours INTEGER,
            provider      VARCHAR(100)
        )""",
        "Available training courses.",
    ),
    (
        "employee_training",
        """CREATE TABLE {db}.employee_training (
            id            INTEGER NOT NULL PRIMARY KEY,
            employee_id   INTEGER REFERENCES {db}.employees(employee_id),
            course_id     INTEGER REFERENCES {db}.training_courses(course_id),
            completion_date DATE,
            score         INTEGER,
            certificate_number VARCHAR(50)
        )""",
        "Employee training completion records.",
    ),
    # ── Contracts ─────────────────────────────────────────────────────────────
    (
        "contracts",
        """CREATE TABLE {db}.contracts (
            contract_id   INTEGER NOT NULL PRIMARY KEY,
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            contract_type VARCHAR(50),
            start_date    DATE,
            end_date      DATE,
            total_value   DECIMAL(12,2),
            status        VARCHAR(20),
            signed_date   DATE
        )""",
        "Customer contracts.",
    ),
    (
        "contract_terms",
        """CREATE TABLE {db}.contract_terms (
            term_id       INTEGER NOT NULL PRIMARY KEY,
            contract_id   INTEGER REFERENCES {db}.contracts(contract_id),
            term_name     VARCHAR(100),
            term_value    VARCHAR(500),
            description   VARCHAR(500)
        )""",
        "Individual terms within contracts.",
    ),
    (
        "sla_agreements",
        """CREATE TABLE {db}.sla_agreements (
            sla_id        INTEGER NOT NULL PRIMARY KEY,
            contract_id   INTEGER REFERENCES {db}.contracts(contract_id),
            service_type  VARCHAR(50),
            uptime_percent DECIMAL(5,2),
            response_time_hours INTEGER,
            penalty_clause VARCHAR(500)
        )""",
        "Service level agreements per contract.",
    ),
    (
        "sla_violations",
        """CREATE TABLE {db}.sla_violations (
            violation_id  INTEGER NOT NULL PRIMARY KEY,
            sla_id        INTEGER REFERENCES {db}.sla_agreements(sla_id),
            incident_id   INTEGER,
            violation_date DATE,
            resolution_date DATE,
            penalty_applied DECIMAL(12,2)
        )""",
        "SLA breach records.",
    ),
    # ── Network Incidents ─────────────────────────────────────────────────────
    (
        "network_incidents",
        """CREATE TABLE {db}.network_incidents (
            incident_id   INTEGER NOT NULL PRIMARY KEY,
            tower_id      INTEGER REFERENCES {db}.towers(tower_id),
            incident_type VARCHAR(50),
            severity      VARCHAR(20),
            description   VARCHAR(2000),
            reported_at   TIMESTAMP(0),
            resolved_at   TIMESTAMP(0),
            status        VARCHAR(20)
        )""",
        "Network incident records.",
    ),
    (
        "incident_updates",
        """CREATE TABLE {db}.incident_updates (
            update_id     INTEGER NOT NULL PRIMARY KEY,
            incident_id   INTEGER REFERENCES {db}.network_incidents(incident_id),
            updated_by    VARCHAR(100),
            update_text   VARCHAR(2000),
            update_time   TIMESTAMP(0)
        )""",
        "Status updates for network incidents.",
    ),
    # ── Feedback ──────────────────────────────────────────────────────────────
    (
        "customer_feedback",
        """CREATE TABLE {db}.customer_feedback (
            feedback_id   INTEGER NOT NULL PRIMARY KEY,
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            feedback_type VARCHAR(30),
            subject       VARCHAR(200),
            message       VARCHAR(2000),
            submitted_at  TIMESTAMP(0),
            status        VARCHAR(20)
        )""",
        "Customer feedback submissions.",
    ),
    (
        "surveys",
        """CREATE TABLE {db}.surveys (
            survey_id     INTEGER NOT NULL PRIMARY KEY,
            survey_name   VARCHAR(100) NOT NULL,
            description   VARCHAR(500),
            created_at    TIMESTAMP(0),
            is_active     BYTEINT DEFAULT 1
        )""",
        "Survey definitions.",
    ),
    (
        "survey_questions",
        """CREATE TABLE {db}.survey_questions (
            question_id   INTEGER NOT NULL PRIMARY KEY,
            survey_id     INTEGER REFERENCES {db}.surveys(survey_id),
            question_text VARCHAR(500),
            question_type VARCHAR(30),
            sort_order    INTEGER
        )""",
        "Questions within surveys.",
    ),
    (
        "survey_responses",
        """CREATE TABLE {db}.survey_responses (
            response_id   INTEGER NOT NULL PRIMARY KEY,
            survey_id     INTEGER REFERENCES {db}.surveys(survey_id),
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            submitted_at  TIMESTAMP(0)
        )""",
        "Survey response headers.",
    ),
    (
        "survey_answers",
        """CREATE TABLE {db}.survey_answers (
            answer_id     INTEGER NOT NULL PRIMARY KEY,
            response_id   INTEGER REFERENCES {db}.survey_responses(response_id),
            question_id   INTEGER REFERENCES {db}.survey_questions(question_id),
            answer_text   VARCHAR(500),
            answer_value  INTEGER
        )""",
        "Individual answers to survey questions.",
    ),
    # ── Promotions ────────────────────────────────────────────────────────────
    (
        "promotions",
        """CREATE TABLE {db}.promotions (
            promo_id      INTEGER NOT NULL PRIMARY KEY,
            promo_name    VARCHAR(100) NOT NULL,
            description   VARCHAR(500),
            discount_percent DECIMAL(5,2),
            start_date    DATE,
            end_date      DATE,
            is_active     BYTEINT DEFAULT 1
        )""",
        "Promotional campaigns.",
    ),
    (
        "promotion_targets",
        """CREATE TABLE {db}.promotion_targets (
            id            INTEGER NOT NULL PRIMARY KEY,
            promo_id      INTEGER REFERENCES {db}.promotions(promo_id),
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            targeted_at   TIMESTAMP(0),
            status        VARCHAR(20)
        )""",
        "Promotion targeting records.",
    ),
    (
        "promotion_redemptions",
        """CREATE TABLE {db}.promotion_redemptions (
            redemption_id INTEGER NOT NULL PRIMARY KEY,
            promo_id      INTEGER REFERENCES {db}.promotions(promo_id),
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            redeemed_at   TIMESTAMP(0),
            discount_amount DECIMAL(10,2)
        )""",
        "Promotion redemption records.",
    ),
    # ── Inventory ─────────────────────────────────────────────────────────────
    (
        "inventory_items",
        """CREATE TABLE {db}.inventory_items (
            item_id       INTEGER NOT NULL PRIMARY KEY,
            item_name     VARCHAR(100) NOT NULL,
            sku           VARCHAR(50),
            category      VARCHAR(50),
            unit_price    DECIMAL(10,2),
            quantity_in_stock INTEGER,
            reorder_point INTEGER
        )""",
        "Inventory master list.",
    ),
    (
        "inventory_transactions",
        """CREATE TABLE {db}.inventory_transactions (
            transaction_id INTEGER NOT NULL PRIMARY KEY,
            item_id       INTEGER REFERENCES {db}.inventory_items(item_id),
            transaction_type VARCHAR(30),
            quantity      INTEGER,
            unit_price    DECIMAL(10,2),
            transaction_date DATE,
            reference_number VARCHAR(50)
        )""",
        "Inventory movement transactions.",
    ),
    (
        "purchase_orders",
        """CREATE TABLE {db}.purchase_orders (
            po_id         INTEGER NOT NULL PRIMARY KEY,
            supplier_name VARCHAR(100),
            order_date    DATE,
            total_amount  DECIMAL(12,2),
            status        VARCHAR(20),
            expected_delivery DATE
        )""",
        "Purchase orders to suppliers.",
    ),
    (
        "purchase_order_items",
        """CREATE TABLE {db}.purchase_order_items (
            po_item_id    INTEGER NOT NULL PRIMARY KEY,
            po_id         INTEGER REFERENCES {db}.purchase_orders(po_id),
            item_id       INTEGER REFERENCES {db}.inventory_items(item_id),
            quantity      INTEGER,
            unit_price    DECIMAL(10,2),
            total         DECIMAL(12,2)
        )""",
        "Line items on purchase orders.",
    ),
    # ── Vendor ────────────────────────────────────────────────────────────────
    (
        "vendors",
        """CREATE TABLE {db}.vendors (
            vendor_id     INTEGER NOT NULL PRIMARY KEY,
            vendor_name   VARCHAR(100) NOT NULL,
            contact_person VARCHAR(100),
            email         VARCHAR(100),
            phone         VARCHAR(20),
            address       VARCHAR(200),
            category      VARCHAR(50),
            rating        INTEGER
        )""",
        "Vendor/supplier master.",
    ),
    (
        "vendor_contracts",
        """CREATE TABLE {db}.vendor_contracts (
            vc_id         INTEGER NOT NULL PRIMARY KEY,
            vendor_id     INTEGER REFERENCES {db}.vendors(vendor_id),
            service_type  VARCHAR(50),
            start_date    DATE,
            end_date      DATE,
            monthly_value DECIMAL(12,2),
            status        VARCHAR(20)
        )""",
        "Vendor service contracts.",
    ),
    # ── Asset Management ──────────────────────────────────────────────────────
    (
        "assets",
        """CREATE TABLE {db}.assets (
            asset_id      INTEGER NOT NULL PRIMARY KEY,
            asset_tag     VARCHAR(50) NOT NULL,
            asset_name    VARCHAR(100),
            category      VARCHAR(50),
            purchase_date DATE,
            purchase_cost DECIMAL(12,2),
            status        VARCHAR(20),
            location      VARCHAR(100)
        )""",
        "Company assets registry.",
    ),
    (
        "asset_maintenance",
        """CREATE TABLE {db}.asset_maintenance (
            maintenance_id INTEGER NOT NULL PRIMARY KEY,
            asset_id      INTEGER REFERENCES {db}.assets(asset_id),
            maintenance_type VARCHAR(30),
            description   VARCHAR(500),
            scheduled_date DATE,
            completed_date DATE,
            cost          DECIMAL(10,2),
            technician_id INTEGER REFERENCES {db}.field_technicians(tech_id)
        )""",
        "Asset maintenance history.",
    ),
    # ── Customer Notes & Preferences ──────────────────────────────────────────
    (
        "customer_notes",
        """CREATE TABLE {db}.customer_notes (
            note_id       INTEGER NOT NULL PRIMARY KEY,
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            note_text     VARCHAR(2000),
            created_by    VARCHAR(100),
            created_at    TIMESTAMP(0),
            note_type     VARCHAR(30)
        )""",
        "Internal customer notes.",
    ),
    (
        "customer_preferences",
        """CREATE TABLE {db}.customer_preferences (
            pref_id       INTEGER NOT NULL PRIMARY KEY,
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            preference_key VARCHAR(100),
            preference_value VARCHAR(500),
            updated_at    TIMESTAMP(0)
        )""",
        "Customer preference settings.",
    ),
    # ── Loyalty ───────────────────────────────────────────────────────────────
    (
        "loyalty_programs",
        """CREATE TABLE {db}.loyalty_programs (
            program_id    INTEGER NOT NULL PRIMARY KEY,
            program_name  VARCHAR(100) NOT NULL,
            description   VARCHAR(500),
            points_per_rand DECIMAL(5,2),
            is_active     BYTEINT DEFAULT 1
        )""",
        "Loyalty program definitions.",
    ),
    (
        "loyalty_rewards",
        """CREATE TABLE {db}.loyalty_rewards (
            reward_id     INTEGER NOT NULL PRIMARY KEY,
            program_id    INTEGER REFERENCES {db}.loyalty_programs(program_id),
            reward_name   VARCHAR(100),
            points_required INTEGER,
            description   VARCHAR(500),
            is_available  BYTEINT DEFAULT 1
        )""",
        "Loyalty rewards catalogue.",
    ),
    (
        "loyalty_points",
        """CREATE TABLE {db}.loyalty_points (
            id            INTEGER NOT NULL PRIMARY KEY,
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            program_id    INTEGER REFERENCES {db}.loyalty_programs(program_id),
            points_balance INTEGER,
            earned_date   DATE,
            expiry_date   DATE
        )""",
        "Loyalty points balances.",
    ),
    (
        "loyalty_redemptions",
        """CREATE TABLE {db}.loyalty_redemptions (
            id            INTEGER NOT NULL PRIMARY KEY,
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            reward_id     INTEGER REFERENCES {db}.loyalty_rewards(reward_id),
            points_spent  INTEGER,
            redeemed_at   TIMESTAMP(0)
        )""",
        "Loyalty reward redemption history.",
    ),
    # ── Referrals ─────────────────────────────────────────────────────────────
    (
        "referral_programs",
        """CREATE TABLE {db}.referral_programs (
            ref_program_id INTEGER NOT NULL PRIMARY KEY,
            program_name  VARCHAR(100) NOT NULL,
            referrer_reward DECIMAL(10,2),
            referee_reward DECIMAL(10,2),
            is_active     BYTEINT DEFAULT 1
        )""",
        "Referral program definitions.",
    ),
    (
        "referral_rewards",
        """CREATE TABLE {db}.referral_rewards (
            ref_reward_id INTEGER NOT NULL PRIMARY KEY,
            ref_program_id INTEGER REFERENCES {db}.referral_programs(ref_program_id),
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            referred_customer_id INTEGER REFERENCES {db}.customers(customer_id),
            reward_amount DECIMAL(10,2),
            status        VARCHAR(20),
            earned_at     TIMESTAMP(0)
        )""",
        "Referral reward records.",
    ),
    # ── Email/SMS Marketing ───────────────────────────────────────────────────
    (
        "email_campaigns",
        """CREATE TABLE {db}.email_campaigns (
            campaign_id   INTEGER NOT NULL PRIMARY KEY,
            campaign_name VARCHAR(100) NOT NULL,
            subject       VARCHAR(200),
            body_template VARCHAR(2000),
            sent_count    INTEGER,
            open_count    INTEGER,
            click_count   INTEGER,
            created_at    TIMESTAMP(0),
            sent_at       TIMESTAMP(0)
        )""",
        "Email marketing campaigns.",
    ),
    (
        "email_recipients",
        """CREATE TABLE {db}.email_recipients (
            id            INTEGER NOT NULL PRIMARY KEY,
            campaign_id   INTEGER REFERENCES {db}.email_campaigns(campaign_id),
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            email_address VARCHAR(100),
            sent_at       TIMESTAMP(0),
            opened_at     TIMESTAMP(0),
            clicked_at    TIMESTAMP(0)
        )""",
        "Email campaign recipients.",
    ),
    (
        "sms_campaigns",
        """CREATE TABLE {db}.sms_campaigns (
            sms_campaign_id INTEGER NOT NULL PRIMARY KEY,
            campaign_name VARCHAR(100) NOT NULL,
            message_template VARCHAR(500),
            sent_count    INTEGER,
            created_at    TIMESTAMP(0),
            sent_at       TIMESTAMP(0)
        )""",
        "SMS marketing campaigns.",
    ),
    (
        "sms_recipients",
        """CREATE TABLE {db}.sms_recipients (
            id            INTEGER NOT NULL PRIMARY KEY,
            sms_campaign_id INTEGER REFERENCES {db}.sms_campaigns(sms_campaign_id),
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            phone_number  VARCHAR(20),
            sent_at       TIMESTAMP(0),
            delivered_at  TIMESTAMP(0)
        )""",
        "SMS campaign recipients.",
    ),
    # ── Web and App ───────────────────────────────────────────────────────────
    (
        "user_accounts",
        """CREATE TABLE {db}.user_accounts (
            user_id       INTEGER NOT NULL PRIMARY KEY,
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            username      VARCHAR(50),
            password_hash VARCHAR(200),
            email         VARCHAR(100),
            last_login    TIMESTAMP(0),
            is_active     BYTEINT DEFAULT 1,
            created_at    TIMESTAMP(0)
        )""",
        "Web portal user accounts.",
    ),
    (
        "user_roles",
        """CREATE TABLE {db}.user_roles (
            role_id       INTEGER NOT NULL PRIMARY KEY,
            role_name     VARCHAR(50) NOT NULL,
            description   VARCHAR(200),
            permissions   VARCHAR(500)
        )""",
        "User role definitions.",
    ),
    (
        "user_role_assignments",
        """CREATE TABLE {db}.user_role_assignments (
            id            INTEGER NOT NULL PRIMARY KEY,
            user_id       INTEGER REFERENCES {db}.user_accounts(user_id),
            role_id       INTEGER REFERENCES {db}.user_roles(role_id),
            assigned_at   TIMESTAMP(0)
        )""",
        "User-role mappings.",
    ),
    (
        "api_keys",
        """CREATE TABLE {db}.api_keys (
            key_id        INTEGER NOT NULL PRIMARY KEY,
            user_id       INTEGER REFERENCES {db}.user_accounts(user_id),
            key_name      VARCHAR(50),
            api_key       VARCHAR(200),
            created_at    TIMESTAMP(0),
            expires_at    TIMESTAMP(0),
            is_active     BYTEINT DEFAULT 1
        )""",
        "API key management.",
    ),
    (
        "api_usage_logs",
        """CREATE TABLE {db}.api_usage_logs (
            log_id        INTEGER NOT NULL PRIMARY KEY,
            key_id        INTEGER REFERENCES {db}.api_keys(key_id),
            endpoint      VARCHAR(200),
            method        VARCHAR(10),
            status_code   INTEGER,
            response_time_ms INTEGER,
            logged_at     TIMESTAMP(0)
        )""",
        "API request logs.",
    ),
    (
        "app_sessions",
        """CREATE TABLE {db}.app_sessions (
            session_id    INTEGER NOT NULL PRIMARY KEY,
            user_id       INTEGER REFERENCES {db}.user_accounts(user_id),
            device_type   VARCHAR(50),
            ip_address    VARCHAR(45),
            user_agent    VARCHAR(500),
            started_at    TIMESTAMP(0),
            ended_at      TIMESTAMP(0)
        )""",
        "User session tracking.",
    ),
    # ── Product Reviews ───────────────────────────────────────────────────────
    (
        "product_reviews",
        """CREATE TABLE {db}.product_reviews (
            review_id     INTEGER NOT NULL PRIMARY KEY,
            product_id    INTEGER REFERENCES {db}.products(product_id),
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            rating        INTEGER,
            title         VARCHAR(200),
            review_text   VARCHAR(2000),
            review_date   DATE,
            is_verified   BYTEINT DEFAULT 0
        )""",
        "Customer product reviews.",
    ),
    (
        "product_review_votes",
        """CREATE TABLE {db}.product_review_votes (
            vote_id       INTEGER NOT NULL PRIMARY KEY,
            review_id     INTEGER REFERENCES {db}.product_reviews(review_id),
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            vote_type     VARCHAR(10),
            voted_at      TIMESTAMP(0)
        )""",
        "Helpful/not helpful votes on reviews.",
    ),
    # ── Wishlists ─────────────────────────────────────────────────────────────
    (
        "wishlists",
        """CREATE TABLE {db}.wishlists (
            wishlist_id   INTEGER NOT NULL PRIMARY KEY,
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            created_at    TIMESTAMP(0)
        )""",
        "Customer wishlists.",
    ),
    (
        "wishlist_items",
        """CREATE TABLE {db}.wishlist_items (
            id            INTEGER NOT NULL PRIMARY KEY,
            wishlist_id   INTEGER REFERENCES {db}.wishlists(wishlist_id),
            product_id    INTEGER REFERENCES {db}.products(product_id),
            added_at      TIMESTAMP(0),
            priority      INTEGER
        )""",
        "Items in customer wishlists.",
    ),
    # ── Reports ───────────────────────────────────────────────────────────────
    (
        "report_definitions",
        """CREATE TABLE {db}.report_definitions (
            report_id     INTEGER NOT NULL PRIMARY KEY,
            report_name   VARCHAR(100) NOT NULL,
            report_type   VARCHAR(50),
            query_template VARCHAR(2000),
            created_by    VARCHAR(100),
            created_at    TIMESTAMP(0)
        )""",
        "Report template definitions.",
    ),
    (
        "report_schedules",
        """CREATE TABLE {db}.report_schedules (
            schedule_id   INTEGER NOT NULL PRIMARY KEY,
            report_id     INTEGER REFERENCES {db}.report_definitions(report_id),
            frequency     VARCHAR(30),
            next_run      TIMESTAMP(0),
            last_run      TIMESTAMP(0),
            is_active     BYTEINT DEFAULT 1
        )""",
        "Scheduled report configurations.",
    ),
    (
        "report_history",
        """CREATE TABLE {db}.report_history (
            history_id    INTEGER NOT NULL PRIMARY KEY,
            report_id     INTEGER REFERENCES {db}.report_definitions(report_id),
            schedule_id   INTEGER REFERENCES {db}.report_schedules(schedule_id),
            generated_at  TIMESTAMP(0),
            row_count     INTEGER,
            file_path     VARCHAR(500)
        )""",
        "Report generation history.",
    ),
    # ── Tariff Changes ────────────────────────────────────────────────────────
    (
        "tariff_changes",
        """CREATE TABLE {db}.tariff_changes (
            change_id     INTEGER NOT NULL PRIMARY KEY,
            plan_id       INTEGER REFERENCES {db}.service_plans(plan_id),
            old_price     DECIMAL(10,2),
            new_price     DECIMAL(10,2),
            effective_date DATE,
            approved_by   VARCHAR(100),
            reason        VARCHAR(500)
        )""",
        "Plan price change history.",
    ),
    # ── Service Level History ─────────────────────────────────────────────────
    (
        "service_level_history",
        """CREATE TABLE {db}.service_level_history (
            id            INTEGER NOT NULL PRIMARY KEY,
            account_id    INTEGER REFERENCES {db}.customer_accounts(account_id),
            old_level     VARCHAR(30),
            new_level     VARCHAR(30),
            changed_at    TIMESTAMP(0),
            reason        VARCHAR(500)
        )""",
        "Customer service tier change history.",
    ),
    # ── Network Capacity Metrics ──────────────────────────────────────────────
    (
        "network_capacity_metrics",
        """CREATE TABLE {db}.network_capacity_metrics (
            metric_id     INTEGER NOT NULL PRIMARY KEY,
            tower_id      INTEGER REFERENCES {db}.towers(tower_id),
            recorded_at   TIMESTAMP(0),
            cpu_utilization DECIMAL(5,2),
            memory_utilization DECIMAL(5,2),
            bandwidth_utilization DECIMAL(5,2),
            connected_users INTEGER,
            throughput_mbps DECIMAL(10,2)
        )""",
        "Tower capacity and performance metrics.",
    ),
    # ── Customer Segments ─────────────────────────────────────────────────────
    (
        "customer_segments",
        """CREATE TABLE {db}.customer_segments (
            segment_id    INTEGER NOT NULL PRIMARY KEY,
            segment_name  VARCHAR(100) NOT NULL,
            description   VARCHAR(500),
            criteria      VARCHAR(500),
            created_at    TIMESTAMP(0)
        )""",
        "Marketing customer segments.",
    ),
    (
        "customer_segment_members",
        """CREATE TABLE {db}.customer_segment_members (
            id            INTEGER NOT NULL PRIMARY KEY,
            segment_id    INTEGER REFERENCES {db}.customer_segments(segment_id),
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            added_at      TIMESTAMP(0)
        )""",
        "Customer-segment membership.",
    ),
    # ── Complaints ────────────────────────────────────────────────────────────
    (
        "complaint_categories",
        """CREATE TABLE {db}.complaint_categories (
            category_id   INTEGER NOT NULL PRIMARY KEY,
            category_name VARCHAR(100) NOT NULL,
            description   VARCHAR(500),
            severity_default VARCHAR(20)
        )""",
        "Complaint category definitions.",
    ),
    (
        "complaints",
        """CREATE TABLE {db}.complaints (
            complaint_id  INTEGER NOT NULL PRIMARY KEY,
            customer_id   INTEGER REFERENCES {db}.customers(customer_id),
            category_id   INTEGER REFERENCES {db}.complaint_categories(category_id),
            ticket_id     INTEGER REFERENCES {db}.support_tickets(ticket_id),
            subject       VARCHAR(200),
            description   VARCHAR(2000),
            severity      VARCHAR(20),
            status        VARCHAR(20),
            filed_at      TIMESTAMP(0),
            resolved_at   TIMESTAMP(0)
        )""",
        "Formal customer complaints.",
    ),
    (
        "complaint_escalations",
        """CREATE TABLE {db}.complaint_escalations (
            escalation_id INTEGER NOT NULL PRIMARY KEY,
            complaint_id  INTEGER REFERENCES {db}.complaints(complaint_id),
            escalated_to  VARCHAR(100),
            reason        VARCHAR(500),
            escalated_at  TIMESTAMP(0),
            resolved_at   TIMESTAMP(0)
        )""",
        "Complaint escalation records.",
    ),
    # ── Service Quality Metrics ───────────────────────────────────────────────
    (
        "service_quality_metrics",
        """CREATE TABLE {db}.service_quality_metrics (
            sqm_id        INTEGER NOT NULL PRIMARY KEY,
            account_id    INTEGER REFERENCES {db}.customer_accounts(account_id),
            recorded_date DATE,
            latency_ms    INTEGER,
            jitter_ms     INTEGER,
            packet_loss_percent DECIMAL(5,2),
            download_speed_mbps DECIMAL(10,2),
            upload_speed_mbps DECIMAL(10,2)
        )""",
        "Per-account quality of service metrics.",
    ),
    # ── Network Equipment Models ──────────────────────────────────────────────
    (
        "network_equipment_models",
        """CREATE TABLE {db}.network_equipment_models (
            model_id      INTEGER NOT NULL PRIMARY KEY,
            manufacturer  VARCHAR(100),
            model_name    VARCHAR(100),
            equipment_type VARCHAR(50),
            max_throughput_mbps INTEGER,
            supported_bands VARCHAR(200),
            unit_cost     DECIMAL(10,2)
        )""",
        "Network equipment model catalogue.",
    ),
    # ── Service Regions ───────────────────────────────────────────────────────
    (
        "service_regions",
        """CREATE TABLE {db}.service_regions (
            region_id     INTEGER NOT NULL PRIMARY KEY,
            region_name   VARCHAR(100) NOT NULL,
            province      VARCHAR(100),
            population_estimate INTEGER,
            coverage_priority VARCHAR(20)
        )""",
        "Service coverage regions.",
    ),
    (
        "region_coverage",
        """CREATE TABLE {db}.region_coverage (
            id            INTEGER NOT NULL PRIMARY KEY,
            region_id     INTEGER REFERENCES {db}.service_regions(region_id),
            tower_id      INTEGER REFERENCES {db}.towers(tower_id),
            coverage_percent DECIMAL(5,2),
            last_assessed DATE
        )""",
        "Tower coverage per region.",
    ),
]


def _fmt_td(ddl: str) -> str:
    return ddl.format(db="{db}")


TD_TEST_TABLES = [(name, _fmt_td(ddl), desc) for name, ddl, desc in TD_TEST_TABLES_RAW]

# ── Shared seed order & FK map ───────────────────────────────────────────────

SEED_ORDER: list[tuple[str, int]] = [
    # parents first
    ("departments", 10),
    ("employees", 30),
    ("product_categories", 10),
    ("products", 20),
    ("service_plans", 15),
    ("plan_features", 30),
    ("customers", 50),
    # children of customers
    ("addresses", 50),
    ("customer_accounts", 50),
    ("devices", 30),
    ("payment_methods", 30),
    ("notifications", 50),
    ("audit_log", 50),
    ("customer_notes", 40),
    ("customer_preferences", 40),
    ("customer_feedback", 30),
    ("customer_communications", 40),
    # children of accounts
    ("sim_cards", 40),
    ("customer_subscriptions", 40),
    ("customer_connections", 40),
    ("data_usage", 100),
    ("call_logs", 80),
    ("sms_logs", 80),
    # children of subscriptions
    ("invoices", 60),
    # children of invoices
    ("invoice_items", 100),
    # children of customers (payment_methods)
    ("payments", 80),
    # network
    ("towers", 15),
    ("tower_equipment", 30),
    ("tower_coverage", 20),
    ("network_capacity_metrics", 100),
    # support
    ("support_agents", 10),
    ("agent_skills", 20),
    ("support_tickets", 50),
    ("ticket_comments", 100),
    ("customer_ratings", 40),
    # service orders
    ("service_orders", 40),
    # field service
    ("field_technicians", 15),
    ("technician_assignments", 40),
    ("parts_inventory", 30),
    ("parts_used", 60),
    # training
    ("training_courses", 10),
    ("employee_training", 30),
    # contracts
    ("contracts", 30),
    ("contract_terms", 60),
    ("sla_agreements", 20),
    ("sla_violations", 15),
    # network incidents
    ("network_incidents", 25),
    ("incident_updates", 50),
    # outages
    ("outages", 15),
    ("affected_customers", 30),
    # feedback & surveys
    ("surveys", 5),
    ("survey_questions", 20),
    ("survey_responses", 40),
    ("survey_answers", 80),
    # promotions
    ("promotions", 10),
    ("promotion_targets", 40),
    ("promotion_redemptions", 30),
    # inventory
    ("inventory_items", 40),
    ("inventory_transactions", 80),
    ("purchase_orders", 20),
    ("purchase_order_items", 50),
    # vendors
    ("vendors", 15),
    ("vendor_contracts", 20),
    # assets
    ("assets", 30),
    ("asset_maintenance", 40),
    # loyalty
    ("loyalty_programs", 5),
    ("loyalty_rewards", 15),
    ("loyalty_points", 50),
    ("loyalty_redemptions", 30),
    # referrals
    ("referral_programs", 3),
    ("referral_rewards", 20),
    # email/sms marketing
    ("email_campaigns", 15),
    ("email_recipients", 100),
    ("sms_campaigns", 15),
    ("sms_recipients", 100),
    # web & app
    ("user_accounts", 50),
    ("user_roles", 5),
    ("user_role_assignments", 50),
    ("api_keys", 30),
    ("api_usage_logs", 200),
    ("app_sessions", 100),
    # product reviews
    ("product_reviews", 60),
    ("product_review_votes", 100),
    # wishlists
    ("wishlists", 30),
    ("wishlist_items", 50),
    # reports
    ("report_definitions", 10),
    ("report_schedules", 10),
    ("report_history", 50),
    # tariff changes
    ("tariff_changes", 20),
    # service level history
    ("service_level_history", 30),
    # customer segments
    ("customer_segments", 5),
    ("customer_segment_members", 40),
    # complaints
    ("complaint_categories", 8),
    ("complaints", 30),
    ("complaint_escalations", 15),
    # service quality metrics
    ("service_quality_metrics", 100),
    # network equipment models
    ("network_equipment_models", 20),
    # service regions
    ("service_regions", 10),
    ("region_coverage", 30),
    # communication templates (no FK, can go early)
    ("communication_templates", 10),
]

FK_MAP: dict[str, dict[str, tuple[str, str]]] = {
    "employees": {
        "dept_id": ("departments", "dept_id"),
        "manager_id": ("employees", "employee_id"),
    },
    "products": {
        "category_id": ("product_categories", "category_id"),
    },
    "service_plans": {
        "product_id": ("products", "product_id"),
    },
    "plan_features": {
        "plan_id": ("service_plans", "plan_id"),
    },
    "addresses": {
        "customer_id": ("customers", "customer_id"),
    },
    "customer_accounts": {
        "customer_id": ("customers", "customer_id"),
    },
    "sim_cards": {
        "account_id": ("customer_accounts", "account_id"),
    },
    "devices": {
        "customer_id": ("customers", "customer_id"),
    },
    "customer_subscriptions": {
        "customer_id": ("customers", "customer_id"),
        "plan_id": ("service_plans", "plan_id"),
    },
    "tower_equipment": {
        "tower_id": ("towers", "tower_id"),
    },
    "tower_coverage": {
        "tower_id": ("towers", "tower_id"),
    },
    "customer_connections": {
        "account_id": ("customer_accounts", "account_id"),
        "tower_id": ("towers", "tower_id"),
    },
    "service_orders": {
        "account_id": ("customer_accounts", "account_id"),
    },
    "support_tickets": {
        "account_id": ("customer_accounts", "account_id"),
        "agent_id": ("support_agents", "agent_id"),
    },
    "ticket_comments": {
        "ticket_id": ("support_tickets", "ticket_id"),
    },
    "customer_ratings": {
        "ticket_id": ("support_tickets", "ticket_id"),
        "customer_id": ("customers", "customer_id"),
    },
    "agent_skills": {
        "agent_id": ("support_agents", "agent_id"),
        "category_id": ("product_categories", "category_id"),
    },
    "data_usage": {
        "account_id": ("customer_accounts", "account_id"),
    },
    "call_logs": {
        "account_id": ("customer_accounts", "account_id"),
    },
    "sms_logs": {
        "account_id": ("customer_accounts", "account_id"),
    },
    "payment_methods": {
        "customer_id": ("customers", "customer_id"),
    },
    "invoices": {
        "account_id": ("customer_accounts", "account_id"),
    },
    "invoice_items": {
        "invoice_id": ("invoices", "invoice_id"),
    },
    "payments": {
        "invoice_id": ("invoices", "invoice_id"),
        "method_id": ("payment_methods", "method_id"),
    },
    "outages": {
        "tower_id": ("towers", "tower_id"),
    },
    "affected_customers": {
        "outage_id": ("outages", "outage_id"),
        "account_id": ("customer_accounts", "account_id"),
    },
    "notifications": {
        "customer_id": ("customers", "customer_id"),
    },
    "audit_log": {
        "customer_id": ("customers", "customer_id"),
    },
    # Communications
    "customer_communications": {
        "customer_id": ("customers", "customer_id"),
    },
    # Field Service
    "technician_assignments": {
        "tech_id": ("field_technicians", "tech_id"),
        "order_id": ("service_orders", "order_id"),
    },
    "parts_used": {
        "assignment_id": ("technician_assignments", "assignment_id"),
        "part_id": ("parts_inventory", "part_id"),
    },
    # Training
    "employee_training": {
        "employee_id": ("employees", "employee_id"),
        "course_id": ("training_courses", "course_id"),
    },
    # Contracts
    "contracts": {
        "customer_id": ("customers", "customer_id"),
    },
    "contract_terms": {
        "contract_id": ("contracts", "contract_id"),
    },
    "sla_agreements": {
        "contract_id": ("contracts", "contract_id"),
    },
    "sla_violations": {
        "sla_id": ("sla_agreements", "sla_id"),
    },
    # Network Incidents
    "network_incidents": {
        "tower_id": ("towers", "tower_id"),
    },
    "incident_updates": {
        "incident_id": ("network_incidents", "incident_id"),
    },
    # Feedback
    "customer_feedback": {
        "customer_id": ("customers", "customer_id"),
    },
    "survey_questions": {
        "survey_id": ("surveys", "survey_id"),
    },
    "survey_responses": {
        "survey_id": ("surveys", "survey_id"),
        "customer_id": ("customers", "customer_id"),
    },
    "survey_answers": {
        "response_id": ("survey_responses", "response_id"),
        "question_id": ("survey_questions", "question_id"),
    },
    # Promotions
    "promotion_targets": {
        "promo_id": ("promotions", "promo_id"),
        "customer_id": ("customers", "customer_id"),
    },
    "promotion_redemptions": {
        "promo_id": ("promotions", "promo_id"),
        "customer_id": ("customers", "customer_id"),
    },
    # Inventory
    "inventory_transactions": {
        "item_id": ("inventory_items", "item_id"),
    },
    "purchase_order_items": {
        "po_id": ("purchase_orders", "po_id"),
        "item_id": ("inventory_items", "item_id"),
    },
    # Vendor
    "vendor_contracts": {
        "vendor_id": ("vendors", "vendor_id"),
    },
    # Asset Management
    "asset_maintenance": {
        "asset_id": ("assets", "asset_id"),
        "technician_id": ("field_technicians", "tech_id"),
    },
    # Customer Notes & Preferences
    "customer_notes": {
        "customer_id": ("customers", "customer_id"),
    },
    "customer_preferences": {
        "customer_id": ("customers", "customer_id"),
    },
    # Loyalty
    "loyalty_rewards": {
        "program_id": ("loyalty_programs", "program_id"),
    },
    "loyalty_points": {
        "customer_id": ("customers", "customer_id"),
        "program_id": ("loyalty_programs", "program_id"),
    },
    "loyalty_redemptions": {
        "customer_id": ("customers", "customer_id"),
        "reward_id": ("loyalty_rewards", "reward_id"),
    },
    # Referrals
    "referral_rewards": {
        "ref_program_id": ("referral_programs", "ref_program_id"),
        "customer_id": ("customers", "customer_id"),
        "referred_customer_id": ("customers", "customer_id"),
    },
    # Email/SMS Marketing
    "email_recipients": {
        "campaign_id": ("email_campaigns", "campaign_id"),
        "customer_id": ("customers", "customer_id"),
    },
    "sms_recipients": {
        "sms_campaign_id": ("sms_campaigns", "sms_campaign_id"),
        "customer_id": ("customers", "customer_id"),
    },
    # Web & App
    "user_accounts": {
        "customer_id": ("customers", "customer_id"),
    },
    "user_role_assignments": {
        "user_id": ("user_accounts", "user_id"),
        "role_id": ("user_roles", "role_id"),
    },
    "api_keys": {
        "user_id": ("user_accounts", "user_id"),
    },
    "api_usage_logs": {
        "key_id": ("api_keys", "key_id"),
    },
    "app_sessions": {
        "user_id": ("user_accounts", "user_id"),
    },
    # Product Reviews
    "product_reviews": {
        "product_id": ("products", "product_id"),
        "customer_id": ("customers", "customer_id"),
    },
    "product_review_votes": {
        "review_id": ("product_reviews", "review_id"),
        "customer_id": ("customers", "customer_id"),
    },
    # Wishlists
    "wishlists": {
        "customer_id": ("customers", "customer_id"),
    },
    "wishlist_items": {
        "wishlist_id": ("wishlists", "wishlist_id"),
        "product_id": ("products", "product_id"),
    },
    # Reports
    "report_schedules": {
        "report_id": ("report_definitions", "report_id"),
    },
    "report_history": {
        "report_id": ("report_definitions", "report_id"),
        "schedule_id": ("report_schedules", "schedule_id"),
    },
    # Tariff Changes
    "tariff_changes": {
        "plan_id": ("service_plans", "plan_id"),
    },
    # Service Level History
    "service_level_history": {
        "account_id": ("customer_accounts", "account_id"),
    },
    # Network Capacity Metrics
    "network_capacity_metrics": {
        "tower_id": ("towers", "tower_id"),
    },
    # Customer Segments
    "customer_segment_members": {
        "segment_id": ("customer_segments", "segment_id"),
        "customer_id": ("customers", "customer_id"),
    },
    # Complaints
    "complaints": {
        "customer_id": ("customers", "customer_id"),
        "category_id": ("complaint_categories", "category_id"),
        "ticket_id": ("support_tickets", "ticket_id"),
    },
    "complaint_escalations": {
        "complaint_id": ("complaints", "complaint_id"),
    },
    # Service Quality Metrics
    "service_quality_metrics": {
        "account_id": ("customer_accounts", "account_id"),
    },
    # Service Regions
    "region_coverage": {
        "region_id": ("service_regions", "region_id"),
        "tower_id": ("towers", "tower_id"),
    },
}


def _make_schema_field(f: Any) -> Any:
    """Convert a dict to a BigQuery SchemaField."""
    from google.cloud import bigquery

    d = dict(f)
    if "type" in d:
        d["field_type"] = d.pop("type")
    if "fields" in d:
        d["fields"] = [_make_schema_field(sub) for sub in d["fields"]]
    return bigquery.SchemaField(**d)
