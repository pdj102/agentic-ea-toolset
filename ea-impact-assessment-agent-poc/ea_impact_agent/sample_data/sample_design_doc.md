# Design Document: Customer Loyalty Platform

**Version:** 0.3 — For EA Review  
**Date:** 2026-05-28  
**Author:** Marketing Technology Team  
**Domain:** Marketing  
**Status:** Proposed

---

## 1. Executive Summary

RetailCo's Marketing Technology team proposes a new **Customer Loyalty Platform** to
replace ad-hoc loyalty tracking currently managed within the CRM System. The platform
will introduce a points-based reward scheme, enabling customers to earn points on
purchases and redeem them for discounts and rewards.

The solution requires integrations with the CRM System, E-Commerce Platform, Analytics
Dashboard, and Legacy Promotions Engine. A new data entity — Loyalty Points Transaction
— will be introduced to track earning and redemption events.

---

## 2. Business Context

Churn analysis shows that 38% of customers make only one purchase. A loyalty programme
is projected to increase repeat purchase rate by 15% within 12 months. The programme
has board approval and must be live by Q4 2026.

---

## 3. Proposed Architecture

### 3.1 Systems Involved

**New System — Customer Loyalty Platform**
- A new microservice built by the Marketing Technology team
- Manages loyalty points balances, earning rules, and redemption workflows
- Domain: Marketing
- Technology choices: MongoDB (for flexible schema to handle varied reward types),
  Python 3.11, Apache Kafka (for event-driven points earning triggers)
- Will own the Loyalty Points Transaction data entity
- Will also manage Customer Profile data for loyalty-specific attributes
  (overriding current CRM ownership for loyalty-related fields)

**Existing System — CRM System (APP-0001)**
- Source of customer identity and profile data
- The Loyalty Platform will read customer records from CRM via a direct database
  connection (database_link integration pattern) for real-time balance lookups
- Integration: database_link, Loyalty Platform → CRM System

**Existing System — E-Commerce Platform (APP-0002)**
- Triggers points earning events on order completion
- Integration: async_event, E-Commerce Platform → Loyalty Platform (via Kafka)

**Existing System — Analytics Dashboard (APP-0004)**
- Loyalty events will be forwarded for reporting
- Integration: async_event, Loyalty Platform → Analytics Dashboard

**Existing System — Legacy Promotions Engine (APP-0003)**
- The Loyalty Platform will integrate with Legacy Promotions Engine to apply
  bonus point multipliers during active promotional campaigns
- Integration: sync_api, Loyalty Platform → Legacy Promotions Engine

**New Component — Loyalty API Gateway**
- A lightweight API gateway exposing the Loyalty Platform to mobile and web clients
- Technology: FastAPI (Python), AWS Lambda
- Pattern: sync_api to Customer Loyalty Platform
- Fully compliant with approved EA technology standards

### 3.2 Data Entities

**New: Loyalty Points Transaction**
- Tracks individual earn and redeem events per customer
- Fields: transaction_id, customer_id, points_delta, transaction_type
  (earn/redeem/expire), source_event_id, timestamp, balance_after
- Not currently in the EA data catalogue — new entry required
- Domain ownership: Marketing (Customer Loyalty Platform)

**Existing: Customer Profile (DE-0001)**
- The Loyalty Platform will manage loyalty-specific fields of Customer Profile
  (loyalty tier, opt-in status, communication preferences)
- Note: Customer Profile is currently owned by the CRM System (Sales domain)

### 3.3 Integration Summary

| Source | Target | Pattern | Technology | Status |
|---|---|---|---|---|
| E-Commerce Platform | Customer Loyalty Platform | async_event | Apache Kafka | New |
| Customer Loyalty Platform | Analytics Dashboard | async_event | Apache Kafka | New |
| Customer Loyalty Platform | CRM System | database_link | MongoDB | New |
| Customer Loyalty Platform | Legacy Promotions Engine | sync_api | FastAPI | New |
| Loyalty API Gateway | Customer Loyalty Platform | sync_api | FastAPI, AWS Lambda | New |

---

## 4. Technology Choices

| Technology | Version | Rationale |
|---|---|---|
| MongoDB | 7.0 | Flexible document schema to support evolving reward type structures without schema migrations |
| Python | 3.11 | Standard RetailCo backend language |
| Apache Kafka | 3.5 | Event streaming for points earning triggers |
| FastAPI | 0.104 | API framework for Loyalty API Gateway |
| AWS Lambda | N/A | Serverless deployment for Loyalty API Gateway |

---

## 5. Non-Functional Requirements

- **Availability:** 99.9% uptime SLA
- **Latency:** Points balance reads < 200ms at p95
- **Scalability:** Must support 10,000 concurrent users during peak promotional events
- **Data Retention:** Loyalty Points Transactions retained for 7 years (regulatory)
- **Security:** Customer loyalty data classified as confidential; encrypted at rest and in transit

---

## 6. Open Questions

1. Should Loyalty Points Transaction data be replicated to the Data Lake for ML feature engineering?
2. Does the Marketing domain have an approved Redis allocation for balance caching?
3. Who will own the EA catalogue entry for Loyalty Points Transaction — Marketing Technology or Data Architecture?
