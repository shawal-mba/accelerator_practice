"""Test schema definitions — ISP company with 36 tables, PKs, and FKs."""

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
    # support
    ("support_agents", 10),
    ("agent_skills", 20),
    ("support_tickets", 50),
    ("ticket_comments", 100),
    ("customer_ratings", 40),
    # service orders
    ("service_orders", 40),
    # outages
    ("outages", 15),
    ("affected_customers", 30),
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
