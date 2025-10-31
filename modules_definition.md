# 🍽️ Restaurant Management System — Module Architecture

This document defines the modular architecture for the Restaurant QR Order System.

---

## 🧩 Overview

The system is divided into **bounded context modules**, each owning its domain logic with minimal coupling.  
Designed for Django but easily adaptable to a service-oriented or microservice environment.

---

## 🧱 Module Breakdown

| Module | Domain Focus | Key Models | Depends On |
|---------|---------------|-------------|-------------|
| **users/** | Authentication, RBAC, staff roles | `UserProfile` | Django `auth` |
| **menu/** | Menu management & versioning | `ItemCategory`, `Item`, `MenuVersion`, `MenuItem` | none |
| **tables/** | Physical restaurant tables & sessions | `Table`, `TableSession` | `users` |
| **orders/** | Order lifecycle, items, totals, tax logic | `Order`, `OrderItem` | `menu`, `tables`, `users` |
| **billing/** *(optional, later)* | POS, payments, receipts, discounts | — | `orders` |
| **notifications/** *(optional, later)* | Real-time updates (kitchen display, waiter alerts, etc.) | — | `orders`, `tables` |
| **core/** | Common utilities, base models, enums, audit mixins | `BaseModel`, constants | used by all |

---

## 1. `users/`
Handles staff accounts, roles, and RBAC.

- **Models**: `UserProfile`
- **Services**: role checks, staff creation, permissions
- **Depends on**: Django `auth`

**Structure:**
```
users/
 ├── models.py
 ├── services.py
 ├── permissions.py
 ├── signals.py
 ├── admin.py
 ├── tests/
```

---

## 2. `menu/`
Manages versioned menus & product catalog.

- **Models**: `ItemCategory`, `Item`, `MenuVersion`, `MenuItem`
- **Services**: activate/deactivate versions, clone menus
- **Depends on**: none

**Structure:**
```
menu/
 ├── models.py
 ├── services.py
 ├── admin.py
 ├── serializers.py
 ├── views.py
 ├── tests/
```

---

## 3. `tables/`
Physical table management and waiter-controlled sessions.

- **Models**: `Table`, `TableSession`
- **Services**: open/close session, active session lookup
- **Depends on**: `users`

**Structure:**
```
tables/
 ├── models.py
 ├── services.py
 ├── admin.py
 ├── serializers.py
 ├── views.py
 ├── tests/
```

---

## 4. `orders/`
Handles order lifecycle, kitchen workflow, totals, and taxes.

- **Models**: `Order`, `OrderItem`
- **Services**: `place_order()`, `recalc_order_totals()`, `update_item_status()`
- **Depends on**: `menu`, `tables`, `users`

**Structure:**
```
orders/
 ├── models.py
 ├── services.py
 ├── signals.py
 ├── admin.py
 ├── serializers.py
 ├── views.py
 ├── tests/
```

---

## 5. `billing/` *(optional)*
Handles payments, invoices, and discounts.

- **Models**: `Payment`, `Invoice`, `Discount`
- **Depends on**: `orders`

---

## 6. `notifications/` *(optional)*
Handles real-time updates (kitchen and waiter dashboards).

- **Services**: WebSocket / Redis PubSub for events
- **Depends on**: `orders`, `tables`

---

## 7. `core/`
Common base utilities and shared logic.

- **Models/Helpers**: `BaseModel`, constants, enums
- **Depends on**: used by all

**Structure:**
```
core/
 ├── models.py
 ├── enums.py
 ├── utils.py
 ├── mixins.py
 ├── tests/
```

---

## 🧠 Dependency Diagram

```
users      → core
menu       → core
tables     → users, core
orders     → tables, menu, users, core
billing    → orders
notifications → orders, tables
```

No circular imports — communication only flows downward.

---

## ⚙️ Project Folder Layout

```
menuva/
 ├── core/
 ├── users/
 ├── menu/
 ├── tables/
 ├── orders/
 ├── billing/          # optional
 ├── notifications/    # optional
 ├── settings.py
 ├── urls.py
 └── manage.py
```

---

## 🔗 Scaling Vision (optional microservices split)

Later, each module can evolve into an independent service:

- **Menu Service** – versioned menus & catalog  
- **Order Service** – order lifecycle  
- **Table Service** – sessions & QR control  
- **User Service** – auth & RBAC  
- **Notification Service** – real-time updates  
- **Billing Service** – payments & invoices

---

## ✅ Summary

| Module | Focus | Key Models |
|---------|--------|-------------|
| `core` | base mixins/enums | BaseModel, helpers |
| `users` | staff roles, RBAC | UserProfile |
| `menu` | versioned menus | MenuVersion, MenuItem, Item, ItemCategory |
| `tables` | sessions & tables | Table, TableSession |
| `orders` | orders, items, tax totals | Order, OrderItem |
| *(optional)* `billing` | payments, invoices | Payment, Invoice |
| *(optional)* `notifications` | real-time | events, WebSocket |
