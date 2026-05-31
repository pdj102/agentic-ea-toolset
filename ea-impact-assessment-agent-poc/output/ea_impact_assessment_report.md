# EA Impact Assessment Report
*Generated: 2026-05-31 15:28*

---

## Executive Summary

**Overall Status:** 🔴 Red

| Finding Type | Count |
|---|---|
| Gaps (missing catalogue entries) | 9 |
| Conflicts (rule violations) | 9 |
| Catalogue quality issues | 15 |
| Cross-catalogue consistency issues | 4 |

### Pre-existing Catalogue Quality Issues

The following issues were found in the EA catalogue files at startup:

- **[MEDIUM]** `DE-0012` — Entry status is 'deprecated' but no retirement date, successor entity, or migration deadline is recorded in any catalogue field. The description mentions ownership was migrated from a retired Supplier Portal, but no owning application transition or deprecation policy metadata is captured. Consumers of this entry have no machine-readable signal for when to stop using it.
- **[LOW]** `CATALOGUE-WIDE` — ID sequence gap detected: DE-0004 is absent from the catalogue. IDs jump from DE-0003 to DE-0005. This may indicate a deleted or unpublished entry, an error in ID assignment, or an intentional retirement without a catalogue record. The gap is relevant because the draft entry for 'Loyalty Points Transaction' may be a candidate for DE-0004 if the sequence was reserved.
- **[LOW]** `DE-0001` — The description ('Core customer record including contact details, preferences, and account history') does not reflect the expanded scope being introduced by the Customer Loyalty Platform (loyalty tier, opt-in status, communication preferences). If any ownership resolution results in DE-0001 retaining these fields, the description must be updated to remain accurate and authoritative.
- **[LOW]** `TECH-0005` — Field 'version_in_use' is null. While not strictly required by schema, this is inconsistent with all other database entries and reduces catalogue utility. The design document references v7.0 — this should be recorded to support future exception or approval tracking.
- **[LOW]** `TECH-0007` — Field 'vendor' is present ('Oracle Corporation') but field 'version_in_use' is absent. More importantly, the entry has status 'retired' with a lifecycle_end_date of 2023-12-31. While not referenced in this design, the entry is valid but should carry a prominent warning comment or condition_notes field to guide consumers. 'condition_notes' is absent — recommended to document migration path explicitly.
- **[LOW]** `TECH-0006` — Status is 'conditional' but no 'condition_notes' field is missing — this entry is COMPLIANT (condition_notes IS present). However, 'version_in_use' is recorded as '7.2' which should be validated as current given Redis's rapid release cadence.
- **[LOW]** `TECH-0009` — Status is 'conditional' and condition_notes IS present — compliant. However, 'vendor' field value is 'Elastic NV' — the legal entity name changed to 'Elastic N.V.' (stylistic). Minor data quality issue for consistency.
- **[LOW]** `TECH-0010` — Field 'vendor' is absent. While not required by schema, XML/SOAP is a protocol standard — the vendor field could reference 'W3C / OASIS' for traceability. Additionally, 'version_in_use' is absent — acceptable for a protocol, but noting for completeness.
- **[LOW]** `TECH-0001` — Field 'approved_domains' is an empty array [], implying approval across all domains — this is correct per schema comment. However, the description states 'Primary backend programming language for all new RetailCo services' which confirms intent. No issue — informational only.
- **[LOW]** `TECH-0008` — Field 'version_in_use' is absent. For a managed AWS cloud service this is expected and acceptable (AWS manages versioning). However, the schema does not exempt cloud_service entries from this field. Recommend adding a note such as 'managed-service — versioning abstracted by vendor' for clarity.
- **[MEDIUM]** `INT-0001` — The source_app value 'APP-0001' and target_app value 'APP-0002' are application reference IDs but the schema requires items to resolve to ref:application. No application register was provided for validation — these references cannot be confirmed as resolvable. Same concern applies to technology_ref 'TECH-0003' and data entity 'DE-0001'. This is a systemic issue across all catalogue entries.
- **[MEDIUM]** `INT-0005` — Status is set to 'conditional' which is a valid enum value, but the description explicitly states this integration is 'to be decommissioned when IMS is fully retired'. If decommissioning has commenced or IMS retirement is in-flight, the status should be reviewed for transition to 'retired'. No retirement date or dependency tracking is recorded in the entry, creating a governance blind spot.
- **[LOW]** `INT-0002` — INT-0002 is superficially similar in target (Analytics Dashboard / APP-0004) and technology (TECH-0003 / Kafka) to the design entity 'Customer Loyalty Platform → Analytics Dashboard'. The catalogue entry name 'E-Commerce to Analytics Order Events' and its data entity (DE-0002 / Order Events) are sufficiently distinct, but the similarity creates a risk of future duplicate registration. Recommend adding a 'related_integrations' or 'notes' field at schema level to cross-reference related flows.
- **[MEDIUM]** `INT-0008` — The target application is recorded as APP-0011 with name 'Promotions Service'. The design document refers to a 'Legacy Promotions Engine' interacting with the Customer Loyalty Platform. It is ambiguous whether APP-0011 and the Legacy Promotions Engine are the same system. If they are, the catalogue entry name 'Promotions Service' does not reflect the legacy nature of the application, which has governance implications (legacy systems typically require additional review gates). The application catalogue entry for APP-0011 should clarify its legacy status.
- **[LOW]** `INT-0009` — INT-0009 uses pattern_type 'streaming' which is a valid schema enum value, but it is the only streaming entry in the catalogue and no streaming technology standard appears to be defined separately from the Kafka entries (TECH-0003). If TECH-0003 covers both async_event and streaming use cases, this creates an implicit dual-use technology reference without formal pattern differentiation. The schema does not enforce a mapping between pattern_type and technology_ref, which may lead to inconsistent future registrations.

---

## Design Document Summary

### Extracted Systems / Applications

- **Customer Loyalty Platform** (domain: Marketing, status: proposed)
  - Technologies: MongoDB 7.0, Python 3.11, Apache Kafka 3.5
  - Integrations with: E-Commerce Platform → Customer Loyalty Platform, Customer Loyalty Platform → Analytics Dashboard, Customer Loyalty Platform → CRM System, Customer Loyalty Platform → Legacy Promotions Engine, Loyalty API Gateway → Customer Loyalty Platform
- **Loyalty API Gateway** (domain: Marketing, status: proposed)
  - Technologies: FastAPI 0.104, AWS Lambda, Python 3.11
  - Integrations with: Loyalty API Gateway → Customer Loyalty Platform
- **CRM System** (domain: Sales, status: live)
  - Integrations with: Customer Loyalty Platform → CRM System
- **E-Commerce Platform** (domain: Marketing, status: live)
  - Technologies: Apache Kafka 3.5
  - Integrations with: E-Commerce Platform → Customer Loyalty Platform
- **Analytics Dashboard** (domain: Marketing, status: live)
  - Technologies: Apache Kafka 3.5
  - Integrations with: Customer Loyalty Platform → Analytics Dashboard
- **Legacy Promotions Engine** (domain: Marketing, status: live)
  - Technologies: FastAPI 0.104
  - Integrations with: Customer Loyalty Platform → Legacy Promotions Engine

### Extracted Data Entities

- **Loyalty Points Transaction** (domain: Marketing, classification: Confidential)
- **Customer Profile** (domain: Sales, classification: Confidential)

### Extracted Technologies

- **MongoDB** (category: Database / Document Store)
- **Python** (category: Programming Language)
- **Apache Kafka** (category: Event Streaming / Message Broker)
- **FastAPI** (category: API Framework)
- **AWS Lambda** (category: Serverless Compute / Cloud Platform)

### Extracted Integrations

- **E-Commerce Platform** → **Customer Loyalty Platform** (pattern: async_event, tech: Apache Kafka 3.5)
- **Customer Loyalty Platform** → **Analytics Dashboard** (pattern: async_event, tech: Apache Kafka 3.5)
- **Customer Loyalty Platform** → **CRM System** (pattern: database_link, tech: MongoDB)
- **Customer Loyalty Platform** → **Legacy Promotions Engine** (pattern: sync_api, tech: FastAPI 0.104)
- **Loyalty API Gateway** → **Customer Loyalty Platform** (pattern: sync_api, tech: FastAPI 0.104, AWS Lambda)

---

## Findings by Catalogue Domain

### Application

**Matches**

| Design Entity | Catalogue Entry | Confidence | Notes |
|---|---|---|---|
| CRM System | `APP-0001` | 100% | Exact match. Design document explicitly references APP-0001. Name, owner_domain (Sales), and status (live) all align perfectly. |
| E-Commerce Platform | `APP-0002` | 100% | Exact match. Design document explicitly references APP-0002. Name and status (live) align. Note: owner_domain conflict — design states 'Marketing', catalogue states 'Retail' (see conflicts). |
| Legacy Promotions Engine | `APP-0003` | 100% | Exact match. Design document explicitly references APP-0003. Matched via aliases 'PromoEngine' / 'Promo System'. Critical status conflict: APP-0003 is 'retired' (lifecycle_end_date 2023-06-30) — see conflicts. |
| Analytics Dashboard | `APP-0004` | 100% | Exact match. Design document explicitly references APP-0004. Name aligns; also matches aliases 'BI Dashboard' and 'Analytics'. Note: owner_domain conflict — design states 'Marketing', catalogue states 'Data' (see conflicts). |

**Gaps** *(no catalogue entry found)*

- **[HIGH]** `Customer Loyalty Platform` — No existing catalogue entry found for the Customer Loyalty Platform. This is a net-new proposed application that must be registered in the EA catalogue before delivery proceeds. Additionally, the Loyalty Points Transaction data entity it claims to own has no existing DE catalogue entry and must also be registered. Ownership claim over Customer Profile attributes overlaps with APP-0001 (see conflicts). Technology references (MongoDB 7.0, Python 3.11, Apache Kafka 3.5) must be validated against the technology catalogue for REL-003/REL-005 compliance before a catalogue entry can be approved.
  ```json
  {
    "id": "REQUIRED - TO BE CONFIRMED (suggest next available APP-XXXX)",
    "name": "Customer Loyalty Platform",
    "alias": [
      "Loyalty Platform",
      "Loyalty Service"
    ],
    "status": "proposed",
    "owner_domain": "Marketing",
    "technology_refs": [
      "REQUIRED - TO BE CONFIRMED: TECH-ID for MongoDB 7.0 (approval status must be verified per REL-003)",
      "REQUIRED - TO BE CONFIRMED: TECH-ID for Python 3.11 (approval status must be verified per REL-003)",
      "REQUIRED - TO BE CONFIRMED: TECH-ID for Apache Kafka 3.5 (approval status must be verified per REL-003)"
    ],
    "data_entity_refs": [
      "REQUIRED - TO BE CONFIRMED: DE-ID for 'Loyalty Points Transaction' (new entity \u2014 must be registered in data catalogue)",
      "DE-0001 (Customer Profile \u2014 ownership conflict with APP-0001, see conflicts; ownership scope must be clarified)"
    ],
    "integration_refs": [
      "REQUIRED - TO BE CONFIRMED: INT-ID for E-Commerce Platform \u2192 Customer Loyalty Platform",
      "REQUIRED - TO BE CONFIRMED: INT-ID for Customer Loyalty Platform \u2192 Analytics Dashboard",
      "REQUIRED - TO BE CONFIRMED: INT-ID for Customer Loyalty Platform \u2192 CRM System",
      "REQUIRED - TO BE CONFIRMED: INT-ID for Customer Loyalty Platform \u2192 Legacy Promotions Engine (BLOCKED \u2014 APP-0003 is retired; must be re-pointed to APP-0011 Promotions Service)",
      "REQUIRED - TO BE CONFIRMED: INT-ID for Loyalty API Gateway \u2192 Customer Loyalty Platform"
    ],
    "tags": [
      "marketing",
      "microservice",
      "loyalty",
      "proposed"
    ],
    "description": "New microservice managing loyalty points balances, earning rules, and redemption workflows. Replaces ad-hoc loyalty tracking previously handled within the CRM System. Owns the Loyalty Points Transaction data entity and manages loyalty-specific Customer Profile attributes."
  }
  ```
- **[HIGH]** `Loyalty API Gateway` — No existing catalogue entry found for the Loyalty API Gateway. This is a net-new proposed application that must be registered in the EA catalogue. Technology references (FastAPI 0.104, AWS Lambda, Python 3.11) must be validated against the technology catalogue for REL-003/REL-005 compliance. As an API gateway it has no data entity ownership, which is valid. Only one integration reference is declared (outbound to Customer Loyalty Platform); inbound client integrations from mobile/web may need to be registered as additional integration refs.
  ```json
  {
    "id": "REQUIRED - TO BE CONFIRMED (suggest next available APP-XXXX)",
    "name": "Loyalty API Gateway",
    "alias": [
      "Loyalty Gateway",
      "Loyalty API"
    ],
    "status": "proposed",
    "owner_domain": "Marketing",
    "technology_refs": [
      "REQUIRED - TO BE CONFIRMED: TECH-ID for FastAPI 0.104 (approval status must be verified per REL-003)",
      "REQUIRED - TO BE CONFIRMED: TECH-ID for AWS Lambda (approval status must be verified per REL-003)",
      "REQUIRED - TO BE CONFIRMED: TECH-ID for Python 3.11 (approval status must be verified per REL-003)"
    ],
    "data_entity_refs": [],
    "integration_refs": [
      "REQUIRED - TO BE CONFIRMED: INT-ID for Loyalty API Gateway \u2192 Customer Loyalty Platform",
      "REQUIRED - TO BE CONFIRMED: INT-IDs for inbound mobile/web client integrations (declared in design narrative but not listed as explicit integration_refs)"
    ],
    "tags": [
      "marketing",
      "api-gateway",
      "microservice",
      "serverless",
      "proposed"
    ],
    "description": "Lightweight API gateway deployed serverlessly via AWS Lambda, exposing the Customer Loyalty Platform to mobile and web clients. Declared fully compliant with EA technology standards."
  }
  ```

**Conflicts**

- **[HIGH]** `Customer Loyalty Platform` vs `APP-0003` — The design declares an integration 'Customer Loyalty Platform → Legacy Promotions Engine' (APP-0003). However, APP-0003 has status 'retired' with lifecycle_end_date 2023-06-30. Integrating with a retired application is strictly prohibited. The live replacement, APP-0011 (Promotions Service), already exists in the catalogue and handles promotional rules, discount codes, and campaign orchestration. The design integration must be re-pointed to APP-0011. This integration cannot be registered or approved as-is. *(Violates REL-001: Applications may only integrate with live applications. Target status 'retired' is explicitly blocked.)*
- **[HIGH]** `Customer Loyalty Platform` vs `APP-0001` — The design describes the Customer Loyalty Platform connecting to the CRM System via a 'direct database connection for real-time balance lookups'. Direct database connections to another application's data store are an EA anti-pattern that bypasses the owning application's data governance, API contract, and access controls. APP-0001 exposes registered integrations (INT-0001, INT-0003) which should be used instead. This integration must be re-designed as an API-based call through an approved integration pattern. No direct DB access may be registered as an integration_ref. *(Violates REL-001 (integration must use approved patterns via the owning application's interface); EA integration design principle — no direct cross-application database access.)*
- **[HIGH]** `Customer Loyalty Platform` vs `APP-0001` — Data ownership conflict on the Customer Profile data entity (DE-0001). APP-0001 (CRM System) is the registered sole owner of DE-0001 per the catalogue. The design states the Customer Loyalty Platform 'manages loyalty-specific Customer Profile attributes', implying partial co-ownership or write access to DE-0001. Only one application may own a data entity. Resolution options: (a) the Loyalty Platform reads Customer Profile from APP-0001 via API only (no ownership claim); or (b) loyalty-specific profile attributes are split into a new, distinct data entity (e.g. 'Loyalty Customer Profile') owned by the Customer Loyalty Platform, keeping DE-0001 solely owned by APP-0001. *(Violates REL-002: A data entity may only have one owning application. Maximum owners = 1.)*
- **[MEDIUM]** `E-Commerce Platform` vs `APP-0002` — Owner domain mismatch. The design document records owner_domain as 'Marketing' for the E-Commerce Platform, but the catalogue entry APP-0002 records owner_domain as 'Retail'. This may indicate an error in the design document, an undocumented domain transfer, or a catalogue entry that is out of date. The authoritative domain ownership must be confirmed and one record corrected. *(Violates Data integrity: owner_domain must be consistent between design artefacts and the EA catalogue.)*
- **[MEDIUM]** `Analytics Dashboard` vs `APP-0004` — Owner domain mismatch. The design document records owner_domain as 'Marketing' for the Analytics Dashboard, but the catalogue entry APP-0004 records owner_domain as 'Data'. This may indicate an error in the design document or a catalogue entry that is out of date. The authoritative domain ownership must be confirmed and one record corrected. *(Violates Data integrity: owner_domain must be consistent between design artefacts and the EA catalogue.)*

### Data Entity

**Matches**

| Design Entity | Catalogue Entry | Confidence | Notes |
|---|---|---|---|
| Customer Profile | `DE-0001` | 98% | Exact name match. Owner domain (Sales), owning application (APP-0001 / CRM System), and data classification (confidential) all align with the design document. Design confirms this is the intended catalogue entry. However, the design introduces a dual-ownership concern — see conflicts. |
| Loyalty Points Transaction | `DE-0009` | 12% | Superficial structural similarity as both are transactional records. However DE-0009 is a Payment Transaction owned by Finance/APP-0007 with PCI classification (restricted), whereas Loyalty Points Transaction is a Marketing-domain earn/redeem ledger. Not a valid match. Flagged as a gap — new catalogue entry required. |

**Gaps** *(no catalogue entry found)*

- **[HIGH]** `Loyalty Points Transaction` — No matching catalogue entry exists. The design document explicitly states this is a new entity requiring a catalogue entry. It tracks individual earn, redeem, and expiry events per customer with a 7-year regulatory retention requirement and Confidential classification.
  ```json
  {
    "id": "REQUIRED - TO BE CONFIRMED (next available DE-XXXX, noting DE-0004 is unallocated in sequence)",
    "name": "Loyalty Points Transaction",
    "status": "active",
    "owning_application": "REQUIRED - TO BE CONFIRMED (expected: APP ID for Customer Loyalty Platform \u2014 not yet present in catalogue)",
    "data_classification": "confidential",
    "owner_domain": "Marketing",
    "description": "Individual loyalty points earn, redeem, and expiry event record per customer. Captures points delta, transaction type, source event reference, timestamp, and running balance. Retained for 7 years for regulatory compliance.",
    "tags": [
      "loyalty",
      "transactional",
      "marketing",
      "pii"
    ],
    "_draft_fields_note": {
      "transaction_id": "Primary key \u2014 string/UUID",
      "customer_id": "Foreign key ref to DE-0001 Customer Profile",
      "points_delta": "Integer \u2014 positive for earn, negative for redeem/expire",
      "transaction_type": "Enum: earn | redeem | expire",
      "source_event_id": "Reference to originating business event",
      "timestamp": "ISO-8601 datetime of the transaction",
      "balance_after": "Integer \u2014 customer points balance following this transaction",
      "retention_period": "7 years (regulatory)"
    }
  }
  ```

**Conflicts**

- **[HIGH]** `Customer Profile` vs `DE-0001` — Dual ownership violation. DE-0001 is currently owned exclusively by APP-0001 (CRM System) under the Sales domain. The design document proposes that the Customer Loyalty Platform will manage loyalty-specific fields on this entity (loyalty tier, opt-in status, communication preferences). This introduces a second owning application, which directly violates REL-002 (max_owners: 1). A resolution strategy must be agreed before implementation — options include: (a) sub-entity or extension pattern — create a new 'Customer Loyalty Profile' data entity owned by the Customer Loyalty Platform that references DE-0001 as its master; (b) delegated field ownership — formally document which fields are stearded by which application while retaining a single catalogue owner; (c) domain data ownership transfer — formally re-assign DE-0001 ownership to a cross-domain data steward. *(Violates REL-002: A data entity may only have one owning application (max_owners: 1))*

**Catalogue Quality Issues**

- **[MEDIUM]** `DE-0012` — Entry status is 'deprecated' but no retirement date, successor entity, or migration deadline is recorded in any catalogue field. The description mentions ownership was migrated from a retired Supplier Portal, but no owning application transition or deprecation policy metadata is captured. Consumers of this entry have no machine-readable signal for when to stop using it.
  *Schema rule: status enum includes 'deprecated' but the schema defines no associated deprecation metadata fields (e.g. deprecated_date, successor_id). Recommend extending schema or adding structured tags.*
- **[LOW]** `CATALOGUE-WIDE` — ID sequence gap detected: DE-0004 is absent from the catalogue. IDs jump from DE-0003 to DE-0005. This may indicate a deleted or unpublished entry, an error in ID assignment, or an intentional retirement without a catalogue record. The gap is relevant because the draft entry for 'Loyalty Points Transaction' may be a candidate for DE-0004 if the sequence was reserved.
  *Schema rule: id pattern: DE-[0-9]{4} — sequence integrity not enforced by schema but expected for catalogue navigability and auditability.*
- **[LOW]** `DE-0001` — The description ('Core customer record including contact details, preferences, and account history') does not reflect the expanded scope being introduced by the Customer Loyalty Platform (loyalty tier, opt-in status, communication preferences). If any ownership resolution results in DE-0001 retaining these fields, the description must be updated to remain accurate and authoritative.
  *Schema rule: description: required field — must accurately reflect current entity scope to be fit for purpose.*

### Technology

**Matches**

| Design Entity | Catalogue Entry | Confidence | Notes |
|---|---|---|---|
| Python 3.11 | `TECH-0001` | 100% | Exact name and version match. Status: approved. No constraints. Fully compliant with REL-003 and REL-005. |
| Apache Kafka 3.5 | `TECH-0003` | 100% | Exact name and version match. Status: approved. No domain restrictions. Used across Customer Loyalty Platform, E-Commerce Platform, and Analytics Dashboard — all permissible. |
| FastAPI 0.104 | `TECH-0011` | 100% | Exact name and version match. Status: approved. No domain restrictions. Fully compliant. |
| AWS Lambda | `TECH-0008` | 98% | Exact name match. Version listed as N/A in design — consistent with catalogue (no version_in_use recorded for managed cloud service). Status: approved. Fully compliant. |
| MongoDB 7.0 | `TECH-0005` | 100% | Exact name match. CRITICAL: Status is 'unapproved' in catalogue. version_in_use is null in catalogue but design specifies v7.0. Blocked under REL-003 — Customer Loyalty Platform must not use this technology. |

**Gaps** *(no catalogue entry found)*

- **[HIGH]** `MongoDB 7.0` — MongoDB is present in the catalogue (TECH-0005) but has status 'unapproved'. It is not a missing entry gap, but a BLOCKED technology gap — the design is attempting to use a prohibited technology. No EXTEND draft is appropriate here. The design must either (a) replace MongoDB with an approved alternative (PostgreSQL TECH-0002 for relational workloads, or Redis TECH-0006 for caching in eligible domains), or (b) submit a formal exception request with data governance justification to seek conditional approval.

**Conflicts**

- **[HIGH]** `MongoDB 7.0 — used by: Customer Loyalty Platform` vs `TECH-0005` — REL-003 VIOLATION: MongoDB has status 'unapproved'. Applications may only use technologies with status 'approved' or 'conditional'. The Customer Loyalty Platform's use of MongoDB is blocked. Catalogue guidance explicitly states: 'data governance requires relational or approved NoSQL stores only — use PostgreSQL or Redis instead'. *(Violates REL-003)*

**Catalogue Quality Issues**

- **[LOW]** `TECH-0005` — Field 'version_in_use' is null. While not strictly required by schema, this is inconsistent with all other database entries and reduces catalogue utility. The design document references v7.0 — this should be recorded to support future exception or approval tracking.
  *Schema rule: fields.version_in_use — type: string, required: false*
- **[LOW]** `TECH-0007` — Field 'vendor' is present ('Oracle Corporation') but field 'version_in_use' is absent. More importantly, the entry has status 'retired' with a lifecycle_end_date of 2023-12-31. While not referenced in this design, the entry is valid but should carry a prominent warning comment or condition_notes field to guide consumers. 'condition_notes' is absent — recommended to document migration path explicitly.
  *Schema rule: fields.condition_notes — comment: required if status is conditional; by extension, retired entries benefit from decommission notes*
- **[LOW]** `TECH-0006` — Status is 'conditional' but no 'condition_notes' field is missing — this entry is COMPLIANT (condition_notes IS present). However, 'version_in_use' is recorded as '7.2' which should be validated as current given Redis's rapid release cadence.
  *Schema rule: fields.condition_notes — required when status is conditional*
- **[LOW]** `TECH-0009` — Status is 'conditional' and condition_notes IS present — compliant. However, 'vendor' field value is 'Elastic NV' — the legal entity name changed to 'Elastic N.V.' (stylistic). Minor data quality issue for consistency.
  *Schema rule: fields.vendor — type: string, required: false*
- **[LOW]** `TECH-0010` — Field 'vendor' is absent. While not required by schema, XML/SOAP is a protocol standard — the vendor field could reference 'W3C / OASIS' for traceability. Additionally, 'version_in_use' is absent — acceptable for a protocol, but noting for completeness.
  *Schema rule: fields.vendor — type: string, required: false*
- **[LOW]** `TECH-0001` — Field 'approved_domains' is an empty array [], implying approval across all domains — this is correct per schema comment. However, the description states 'Primary backend programming language for all new RetailCo services' which confirms intent. No issue — informational only.
  *Schema rule: fields.approved_domains — comment: if empty, approved for all domains*
- **[LOW]** `TECH-0008` — Field 'version_in_use' is absent. For a managed AWS cloud service this is expected and acceptable (AWS manages versioning). However, the schema does not exempt cloud_service entries from this field. Recommend adding a note such as 'managed-service — versioning abstracted by vendor' for clarity.
  *Schema rule: fields.version_in_use — type: string, required: false*

### Integration

**Matches**

| Design Entity | Catalogue Entry | Confidence | Notes |
|---|---|---|---|
| E-Commerce Platform → Customer Loyalty Platform | `INT-0002` | 20% | Closest partial match: same source app (E-Commerce Platform / APP-0002) and same async_event pattern via Kafka (TECH-0003). However, INT-0002 targets Analytics Dashboard (APP-0004), not Customer Loyalty Platform. Data entity is Order Events (DE-0002) not Loyalty Points Transaction. This is a weak structural hint only — not a true match. Treated as a GAP. |
| Customer Loyalty Platform → Analytics Dashboard | `INT-0002` | 20% | Closest partial match: same target app (Analytics Dashboard / APP-0004) and same async_event/Kafka pattern. However INT-0002 sources from E-Commerce Platform (APP-0002), not Customer Loyalty Platform. Data entity mismatch (Order Events vs Loyalty Points Transaction). Treated as a GAP. |
| Customer Loyalty Platform → CRM System | `INT-0001` | 15% | INT-0001 involves CRM (APP-0001) and shares Customer Profile (DE-0001) as a data entity, but the direction is reversed (CRM → E-Commerce) and the pattern is async_event not database_link. Technology is Kafka not MongoDB. This is a very weak hint only — treated as a GAP. |
| Customer Loyalty Platform → Legacy Promotions Engine | `INT-0008` | 20% | INT-0008 is the only Promotions-related sync_api in catalogue (E-Commerce → Promotions Service, APP-0002 → APP-0011). Pattern type and technology (sync_api / REST) align loosely, but source is E-Commerce Platform not Customer Loyalty Platform, and target is 'Promotions Service' not 'Legacy Promotions Engine' — likely a different application. Treated as a GAP. |
| Loyalty API Gateway → Customer Loyalty Platform | `INT-0004` | 15% | INT-0004 is the only API Gateway-style sync_api in the catalogue (Mobile App → E-Commerce, APP-0005 → APP-0002). Pattern type aligns (sync_api) but both source and target apps differ. No Customer Loyalty Platform or Loyalty API Gateway appears in the catalogue at all. Treated as a GAP. |

**Gaps** *(no catalogue entry found)*

- **[HIGH]** `E-Commerce Platform → Customer Loyalty Platform` — No catalogue entry exists for an integration from E-Commerce Platform to Customer Loyalty Platform. This async Kafka-based loyalty points earning flow is entirely absent from the EA catalogue and must be registered before implementation.
  ```json
  {
    "id": "INT-XXXX (REQUIRED - TO BE CONFIRMED)",
    "name": "E-Commerce to Customer Loyalty Platform Order Events",
    "pattern_type": "async_event",
    "status": "REQUIRED - TO BE CONFIRMED",
    "source_app": "REQUIRED - TO BE CONFIRMED (E-Commerce Platform / APP-0002 assumed)",
    "target_app": "REQUIRED - TO BE CONFIRMED (Customer Loyalty Platform \u2014 no APP-ID assigned in catalogue)",
    "technology_ref": "TECH-0003 (Apache Kafka \u2014 assumed, consistent with existing Kafka integrations; version 3.5 to be validated against TECH register)",
    "data_entities_exchanged": [
      "REQUIRED - TO BE CONFIRMED (Loyalty Points Transaction \u2014 no DE-ID assigned in catalogue)"
    ],
    "description": "E-Commerce Platform publishes order completion events to Apache Kafka; Customer Loyalty Platform consumes these to trigger points earning."
  }
  ```
- **[HIGH]** `Customer Loyalty Platform → Analytics Dashboard` — No catalogue entry exists for an integration from Customer Loyalty Platform to Analytics Dashboard. Although INT-0002 covers E-Commerce → Analytics via Kafka, this is a distinct source application and data entity (Loyalty Points Transaction) and must be independently catalogued.
  ```json
  {
    "id": "INT-XXXX (REQUIRED - TO BE CONFIRMED)",
    "name": "Customer Loyalty Platform to Analytics Dashboard Loyalty Events",
    "pattern_type": "async_event",
    "status": "REQUIRED - TO BE CONFIRMED",
    "source_app": "REQUIRED - TO BE CONFIRMED (Customer Loyalty Platform \u2014 no APP-ID assigned in catalogue)",
    "target_app": "APP-0004 (Analytics Dashboard \u2014 consistent with INT-0002 and INT-0003)",
    "technology_ref": "TECH-0003 (Apache Kafka \u2014 assumed; version 3.5 to be validated against TECH register)",
    "data_entities_exchanged": [
      "REQUIRED - TO BE CONFIRMED (Loyalty Points Transaction \u2014 no DE-ID assigned in catalogue)"
    ],
    "description": "Customer Loyalty Platform forwards loyalty events to the Analytics Dashboard via Kafka for reporting purposes."
  }
  ```
- **[HIGH]** `Customer Loyalty Platform → CRM System` — No catalogue entry exists for a database_link integration from Customer Loyalty Platform to CRM System. Direct database connections are a recognised anti-pattern in event-driven architectures and violate separation of concerns. The use of MongoDB as a cross-system database link raises significant data sovereignty, coupling, and security concerns that require Architecture Review Board (ARB) approval before proceeding.
  ```json
  {
    "id": "INT-XXXX (REQUIRED - TO BE CONFIRMED)",
    "name": "Customer Loyalty Platform to CRM System Customer Profile DB Link",
    "pattern_type": "database_link",
    "status": "REQUIRED - TO BE CONFIRMED",
    "source_app": "REQUIRED - TO BE CONFIRMED (Customer Loyalty Platform \u2014 no APP-ID assigned in catalogue)",
    "target_app": "APP-0001 (CRM System \u2014 consistent with INT-0001 and INT-0010)",
    "technology_ref": "REQUIRED - TO BE CONFIRMED (MongoDB \u2014 no TECH-ID identified in catalogue; must be registered in technology reference list)",
    "data_entities_exchanged": [
      "DE-0001 (Customer Profile \u2014 consistent with INT-0001 and INT-0010)"
    ],
    "description": "Customer Loyalty Platform reads customer records from the CRM System via a direct MongoDB database connection for real-time balance lookups. NOTE: database_link pattern requires ARB review and explicit approval."
  }
  ```
- **[HIGH]** `Customer Loyalty Platform → Legacy Promotions Engine` — No catalogue entry exists for a sync_api integration from Customer Loyalty Platform to a Legacy Promotions Engine. The 'Legacy' designation suggests this may be a system not yet registered in the application catalogue. Additionally, FastAPI 0.104 must be validated against the approved technology register. The use of a synchronous call to a legacy system introduces availability and latency coupling risks.
  ```json
  {
    "id": "INT-XXXX (REQUIRED - TO BE CONFIRMED)",
    "name": "Customer Loyalty Platform to Legacy Promotions Engine Bonus Multiplier API",
    "pattern_type": "sync_api",
    "status": "REQUIRED - TO BE CONFIRMED",
    "source_app": "REQUIRED - TO BE CONFIRMED (Customer Loyalty Platform \u2014 no APP-ID assigned in catalogue)",
    "target_app": "REQUIRED - TO BE CONFIRMED (Legacy Promotions Engine \u2014 not found in catalogue; APP-ID must be assigned or application registered)",
    "technology_ref": "REQUIRED - TO BE CONFIRMED (FastAPI 0.104 \u2014 not identified in catalogue; must be registered in technology reference list)",
    "data_entities_exchanged": [
      "REQUIRED - TO BE CONFIRMED (Loyalty Points Transaction \u2014 no DE-ID assigned in catalogue)"
    ],
    "description": "Customer Loyalty Platform calls the Legacy Promotions Engine synchronously via FastAPI to apply bonus point multipliers during active promotional campaigns."
  }
  ```
- **[HIGH]** `Loyalty API Gateway → Customer Loyalty Platform` — No catalogue entry exists for a sync_api integration from Loyalty API Gateway to Customer Loyalty Platform. Neither 'Loyalty API Gateway' nor 'Customer Loyalty Platform' appear as registered applications in the catalogue. Both applications and this integration must be registered. Additionally, the combined technology stack (FastAPI 0.104 + AWS Lambda) requires technology reference validation. Two data entities (Loyalty Points Transaction and Customer Profile) are exchanged and both require DE-IDs.
  ```json
  {
    "id": "INT-XXXX (REQUIRED - TO BE CONFIRMED)",
    "name": "Loyalty API Gateway to Customer Loyalty Platform Client API",
    "pattern_type": "sync_api",
    "status": "REQUIRED - TO BE CONFIRMED",
    "source_app": "REQUIRED - TO BE CONFIRMED (Loyalty API Gateway \u2014 not found in catalogue; must be registered as a new application)",
    "target_app": "REQUIRED - TO BE CONFIRMED (Customer Loyalty Platform \u2014 not found in catalogue; must be registered as a new application)",
    "technology_ref": "REQUIRED - TO BE CONFIRMED (FastAPI 0.104 + AWS Lambda \u2014 neither confirmed in catalogue TECH register; may require two technology references or a composite entry)",
    "data_entities_exchanged": [
      "REQUIRED - TO BE CONFIRMED (Loyalty Points Transaction \u2014 no DE-ID assigned in catalogue)",
      "DE-0001 or REQUIRED - TO BE CONFIRMED (Customer Profile \u2014 DE-0001 exists in catalogue but must be confirmed as the same entity definition)"
    ],
    "description": "Loyalty API Gateway exposes the Customer Loyalty Platform to mobile and web clients via a synchronous FastAPI deployed serverlessly on AWS Lambda."
  }
  ```

**Conflicts**

- **[HIGH]** `Customer Loyalty Platform → CRM System` vs `INT-0001` — The design specifies a database_link (direct MongoDB connection) pattern for CRM data access. The only CRM-related integration in the catalogue (INT-0001) uses async_event via Kafka. Direct database links circumvent the established event-driven integration standard observed across the catalogue and represent an architectural pattern violation. This integration must be reviewed by the ARB; the recommended remediation is to replace the database_link with a sync_api call (e.g. mirroring INT-0010 Mobile App → CRM pattern) or an async_event subscription. *(Violates REL-004 — Integrations must use an approved integration pattern consistent with architectural standards. While database_link is a valid schema enum value, it conflicts with the async_event and sync_api patterns established for CRM interactions (INT-0001, INT-0010) and introduces direct coupling to the CRM data store.)*
- **[MEDIUM]** `Customer Loyalty Platform → Legacy Promotions Engine` vs `INT-0008` — INT-0008 establishes the approved pattern for Promotions interactions as E-Commerce Platform → Promotions Service (APP-0011) via sync_api/REST (TECH-0011). The design routes Customer Loyalty Platform → Legacy Promotions Engine using FastAPI 0.104, which is not the catalogued technology reference (TECH-0011). It is unclear whether 'Legacy Promotions Engine' is the same application as APP-0011 ('Promotions Service') under a different name, or a separate, unregistered legacy system. If the same system, the technology reference conflicts; if a different system, it is an unregistered application. Clarification is required. *(Violates REL-004 — technology_ref must resolve to a registered TECH entry. FastAPI 0.104 has no confirmed TECH-ID in the catalogue. If APP-0011 and Legacy Promotions Engine are the same system, the technology used must match or supersede TECH-0011 via a registered update.)*

**Catalogue Quality Issues**

- **[MEDIUM]** `INT-0001` — The source_app value 'APP-0001' and target_app value 'APP-0002' are application reference IDs but the schema requires items to resolve to ref:application. No application register was provided for validation — these references cannot be confirmed as resolvable. Same concern applies to technology_ref 'TECH-0003' and data entity 'DE-0001'. This is a systemic issue across all catalogue entries.
  *Schema rule: source_app.items: ref:application / target_app.items: ref:application / technology_ref.items: ref:technology / data_entities_exchanged.items: ref:data_entity*
- **[MEDIUM]** `INT-0005` — Status is set to 'conditional' which is a valid enum value, but the description explicitly states this integration is 'to be decommissioned when IMS is fully retired'. If decommissioning has commenced or IMS retirement is in-flight, the status should be reviewed for transition to 'retired'. No retirement date or dependency tracking is recorded in the entry, creating a governance blind spot.
  *Schema rule: status enum: [approved, conditional, retired] — current value is valid but may be stale; no deprecation metadata field exists in schema v1.0 to capture planned retirement.*
- **[LOW]** `INT-0002` — INT-0002 is superficially similar in target (Analytics Dashboard / APP-0004) and technology (TECH-0003 / Kafka) to the design entity 'Customer Loyalty Platform → Analytics Dashboard'. The catalogue entry name 'E-Commerce to Analytics Order Events' and its data entity (DE-0002 / Order Events) are sufficiently distinct, but the similarity creates a risk of future duplicate registration. Recommend adding a 'related_integrations' or 'notes' field at schema level to cross-reference related flows.
  *Schema rule: No deduplication or cross-reference field exists in schema v1.0 — informational recommendation for schema enhancement.*
- **[MEDIUM]** `INT-0008` — The target application is recorded as APP-0011 with name 'Promotions Service'. The design document refers to a 'Legacy Promotions Engine' interacting with the Customer Loyalty Platform. It is ambiguous whether APP-0011 and the Legacy Promotions Engine are the same system. If they are, the catalogue entry name 'Promotions Service' does not reflect the legacy nature of the application, which has governance implications (legacy systems typically require additional review gates). The application catalogue entry for APP-0011 should clarify its legacy status.
  *Schema rule: name field should accurately reflect the registered application name (ref:application). Alias or legacy name variants should be captured to prevent ambiguity in design documents.*
- **[LOW]** `INT-0009` — INT-0009 uses pattern_type 'streaming' which is a valid schema enum value, but it is the only streaming entry in the catalogue and no streaming technology standard appears to be defined separately from the Kafka entries (TECH-0003). If TECH-0003 covers both async_event and streaming use cases, this creates an implicit dual-use technology reference without formal pattern differentiation. The schema does not enforce a mapping between pattern_type and technology_ref, which may lead to inconsistent future registrations.
  *Schema rule: No schema-level constraint links pattern_type to technology_ref — informational recommendation to add a pattern-to-technology constraint in schema v1.1.*

---

## Cross-Catalogue Consistency Issues

### Programmatic Rule Violations

- **[HIGH]** Integration target 'Legacy Promotions Engine' has status 'retired'. Only 'live' applications may be integration targets. (Rule: REL-001)
  *Entities: Customer Loyalty Platform → Legacy Promotions Engine*
- **[HIGH]** Data entity 'Customer Profile' is owned by 'APP-0001' in the catalogue but the design claims ownership for 'CRM System'. A data entity may only have one owning application. (Rule: REL-002)
  *Entities: CRM System → Customer Profile*
- **[HIGH]** Integration 'Customer Loyalty Platform' → 'CRM System' uses pattern 'database_link' which is not among approved patterns in the catalogue (async_event, batch_file, streaming, sync_api). (Rule: REL-004)
  *Entities: Customer Loyalty Platform → CRM System*
- **[HIGH]** Proposed application 'Customer Loyalty Platform' does not reference any approved technology. At least one approved technology is required. (Rule: REL-005)
  *Entities: Customer Loyalty Platform → *

*No additional LLM-identified consistency issues.*

---

## Recommended Options

### Finding: Gap: Customer Loyalty Platform — No existing catalogue entry found for the Customer Loyalty Platform. This is a net-new proposed application that must be registered in the EA catalogue before delivery proceeds. Additionally, the Loyalty Points Transaction data entity it claims to own has no existing DE catalogue entry and must also be registered. Ownership claim over Customer Profile attributes overlaps with APP-0001 (see conflicts). Technology references (MongoDB 7.0, Python 3.11, Apache Kafka 3.5) must be validated against the technology catalogue for REL-003/REL-005 compliance before a catalogue entry can be approved.

*Type: gap | Severity: high*

### Finding: Gap: Loyalty API Gateway — No existing catalogue entry found for the Loyalty API Gateway. This is a net-new proposed application that must be registered in the EA catalogue. Technology references (FastAPI 0.104, AWS Lambda, Python 3.11) must be validated against the technology catalogue for REL-003/REL-005 compliance. As an API gateway it has no data entity ownership, which is valid. Only one integration reference is declared (outbound to Customer Loyalty Platform); inbound client integrations from mobile/web may need to be registered as additional integration refs.

*Type: gap | Severity: high*

**Option: CONFORM**
- *Before registering a net-new application entry, conduct a thorough discovery exercise across the EA catalogue to confirm no existing API gateway application (e.g., a shared or domain-level gateway) already serves the Marketing domain. If a conforming gateway exists, onboard the Loyalty API Gateway as a logical service or route within that existing application rather than creating a new APP record. Additionally, validate all three technology references (FastAPI 0.104, AWS Lambda, Python 3.11) against the technology catalogue and, where an unapproved technology is found, substitute it with the nearest approved equivalent (e.g., an EA-approved Python runtime version or an approved serverless platform) before proceeding to catalogue registration.*
- Effort: medium | Risk: low
- Rationale: Conforming to existing catalogue entries and approved technologies avoids catalogue sprawl, eliminates REL-003/REL-005 compliance risk at the source, and reduces the long-term maintenance burden of a net-new application record. This is the lowest-risk path if a suitable existing gateway or approved technology substitution is available.

**Option: EXTEND**
- *Register the Loyalty API Gateway as a net-new application in the EA catalogue using the refined draft entry below. Assign the next available APP-XXXX identifier. Resolve all REQUIRED – TO BE CONFIRMED fields prior to submission: (1) confirm or raise technology catalogue entries for FastAPI 0.104, AWS Lambda, and Python 3.11 and verify each meets REL-003/REL-005 approval status; (2) register the outbound integration to the Customer Loyalty Platform as a new INT record; (3) register each inbound mobile/web client integration as additional INT records and add them to integration_refs; (4) obtain an assigned APP-XXXX ID from the EA catalogue administrator before final submission.*
- Effort: medium | Risk: medium
- Rationale: As a net-new proposed application with no existing catalogue entry, an EXTEND is the primary remediation path. The draft entry (refined from the supplied draft — not regenerated) is schema-valid per the application schema v1.0. The medium risk reflects that technology approval statuses and integration IDs are still unresolved and must be confirmed before the entry can be considered fully compliant.
- Draft catalogue entry:
  ```json
  {
    "object_type": "application",
    "id": "REQUIRED - TO BE CONFIRMED (assign next available APP-XXXX)",
    "name": "Loyalty API Gateway",
    "alias": [
      "Loyalty Gateway",
      "Loyalty API"
    ],
    "status": "proposed",
    "owner_domain": "Marketing",
    "technology_refs": [
      "REQUIRED - TO BE CONFIRMED: TECH-XXXX for FastAPI 0.104 \u2014 verify catalogue entry exists and status is 'approved' or 'conditional' per REL-003; if absent, raise a new TECH entry or substitute with EA-approved framework",
      "REQUIRED - TO BE CONFIRMED: TECH-XXXX for AWS Lambda \u2014 verify catalogue entry exists and status is 'approved' or 'conditional' per REL-003; confirm approved_domains includes 'Marketing' or is unrestricted",
      "REQUIRED - TO BE CONFIRMED: TECH-XXXX for Python 3.11 \u2014 verify catalogue entry exists and status is 'approved' or 'conditional' per REL-003/REL-005; confirm version_in_use is recorded as '3.11'"
    ],
    "data_entity_refs": [],
    "integration_refs": [
      "REQUIRED - TO BE CONFIRMED: INT-XXXX \u2014 register outbound integration: Loyalty API Gateway \u2192 Customer Loyalty Platform (pattern_type: sync_api, status: approved); confirm target APP-ID for Customer Loyalty Platform",
      "REQUIRED - TO BE CONFIRMED: INT-XXXX \u2014 register inbound integration: Mobile Client \u2192 Loyalty API Gateway (pattern_type: sync_api); one INT record per distinct client application",
      "REQUIRED - TO BE CONFIRMED: INT-XXXX \u2014 register inbound integration: Web Client \u2192 Loyalty API Gateway (pattern_type: sync_api); one INT record per distinct client application"
    ],
    "tags": [
      "marketing",
      "api-gateway",
      "microservice",
      "serverless",
      "proposed"
    ],
    "description": "Lightweight API gateway deployed serverlessly via AWS Lambda, exposing the Customer Loyalty Platform to mobile and web clients. Declared fully compliant with EA technology standards; technology_refs and integration_refs must be resolved and confirmed before status is advanced from 'proposed' to 'live'."
  }
  ```

**Option: EXCEPTION**
- *If one or more of the three technology references (FastAPI 0.104, AWS Lambda, Python 3.11) is found to be 'unapproved' or 'conditional' in the technology catalogue with unsatisfied conditions, raise a time-boxed EA exception to permit use of the non-compliant technology for the initial delivery of the Loyalty API Gateway. The exception must: (1) document the specific technology and its current catalogue status; (2) provide a business justification for why an approved substitute cannot be used within the project timeline; (3) define a remediation deadline (recommended: ≤12 months) by which the technology will either be formally approved, substituted, or the gateway retired; (4) be signed off by the EA Review Board and the Marketing domain owner; and (5) be linked to the APP catalogue entry via a condition_notes annotation on the relevant TECH record.*
- Effort: low | Risk: medium
- Rationale: An exception provides a governed, time-limited path to proceed with delivery where a technology compliance gap cannot be resolved before project go-live. This avoids an indefinite block on the Loyalty API Gateway while ensuring the deviation is visible, accountable, and tracked to closure. Risk is medium because unapproved technologies introduce residual REL-003/REL-005 compliance exposure that persists until the exception is remediated.

**Option: RETIRE**
- *If the technology catalogue review reveals that existing entries for FastAPI, AWS Lambda, or Python 3.11 are recorded against outdated or incorrect versions (e.g., Python 3.9 marked as the current approved version when 3.11 is already in production use), trigger a formal technology catalogue review for those entries. Raise a TECH record update request to either advance the lifecycle to a current approved version or mark the outdated version entry as 'retired', replacing it with an updated entry reflecting the version actually in use. This must be completed in parallel with the EXTEND option so the new APP entry can reference accurate, current TECH-IDs.*
- Effort: low | Risk: low
- Rationale: Stale or version-mismatched technology catalogue entries are a common root cause of false REL-003/REL-005 compliance failures. Retiring outdated TECH entries and replacing them with current approved versions improves catalogue accuracy for all future consumers, not just this application, and reduces the likelihood of repeated findings of this type across the Marketing domain.

### Finding: Conflict: Customer Loyalty Platform vs APP-0003 — The design declares an integration 'Customer Loyalty Platform → Legacy Promotions Engine' (APP-0003). However, APP-0003 has status 'retired' with lifecycle_end_date 2023-06-30. Integrating with a retired application is strictly prohibited. The live replacement, APP-0011 (Promotions Service), already exists in the catalogue and handles promotional rules, discount codes, and campaign orchestration. The design integration must be re-pointed to APP-0011. This integration cannot be registered or approved as-is.

*Type: conflict | Severity: high*

**Option: CONFORM**
- *Re-point the design integration from APP-0003 (Legacy Promotions Engine, retired 2023-06-30) to APP-0011 (Promotions Service, live). Update the integration's `target_app` field to reference APP-0011 and validate that all data entities exchanged (promotional rules, discount codes, campaign orchestration payloads) are correctly mapped to those owned or exposed by APP-0011. Submit the corrected integration record for EA review and approval before registration. No new catalogue entries are required — this is a direct substitution using an already-live, purpose-built replacement.*
- Effort: low | Risk: low
- Rationale: APP-0011 (Promotions Service) is the designated live replacement for APP-0003 and already handles the exact capabilities required (promotional rules, discount codes, campaign orchestration). Re-pointing is a targeted design correction that fully resolves the REL-001 violation with minimal effort, no architectural change, and no deviation from EA standards. This is the strongly preferred and fastest path to compliance.

**Option: EXTEND**
- *If no approved integration catalogue entry currently exists for the `Customer Loyalty Platform → APP-0011 (Promotions Service)` integration, create and register a new integration record in the EA catalogue to formally govern this link. The draft entry below captures all schema-required fields. Unknown values (e.g., specific technology ref, data entities) must be confirmed by the owning team before submission. Once registered as `approved`, the design can reference this entry and REL-001 compliance is fully satisfied.*
- Effort: low | Risk: low
- Rationale: A CONFORM re-point (Option 1) resolves the design conflict, but a corresponding approved integration record in the EA catalogue is necessary to formally govern the Customer Loyalty Platform → APP-0011 link under standard EA registration rules. This EXTEND option ensures the catalogue reflects the corrected architectural state and provides a reusable, governed integration entry for future designs referencing the same path.
- Draft catalogue entry:
  ```json
  {
    "object_type": "integration",
    "version": "1.0",
    "id": "REQUIRED - TO BE CONFIRMED",
    "name": "Customer Loyalty Platform \u2192 Promotions Service",
    "pattern_type": "REQUIRED - TO BE CONFIRMED",
    "status": "approved",
    "source_app": "REQUIRED - TO BE CONFIRMED (ref: Customer Loyalty Platform application ID)",
    "target_app": "APP-0011",
    "technology_ref": "REQUIRED - TO BE CONFIRMED (ref: technology used for this integration, e.g. REST/sync_api, messaging platform)",
    "data_entities_exchanged": [
      "REQUIRED - TO BE CONFIRMED (ref: data entity IDs for promotional rules, discount codes, campaign data owned/exposed by APP-0011)"
    ],
    "description": "Integration from the Customer Loyalty Platform to the Promotions Service (APP-0011) for retrieval and orchestration of promotional rules, discount codes, and campaign logic. Replaces the previously deprecated integration targeting the retired Legacy Promotions Engine (APP-0003)."
  }
  ```

**Option: EXCEPTION**
- *⚠️ NOT RECOMMENDED — An exception to REL-001 to permit integration with the retired APP-0003 is not a viable path. APP-0003 reached its lifecycle_end_date on 2023-06-30 and its live replacement (APP-0011) is already available in the catalogue with equivalent capability. REL-001 explicitly blocks integration with retired applications, and EA policy provides no exception basis when a functional replacement exists. Any exception request would be rejected. Teams must pursue CONFORM (Option 1) or EXTEND (Option 2) instead.*
- Effort: high | Risk: high
- Rationale: Documented here for completeness and to explicitly close off this path. Exceptions are reserved for cases where no compliant alternative exists or where decommissioning timelines create an unavoidable transitional gap. Neither condition applies: APP-0011 is live, functional, and covers all required capabilities. Pursuing an exception would introduce high governance risk, delay compliance resolution, and would not receive EA board approval under current policy.

**Option: RETIRE**
- *Trigger a catalogue hygiene review to formally retire or remove any existing integration records that list APP-0003 (Legacy Promotions Engine) as a `target_app`. Ensure all such integration entries have their `status` updated to `retired`, that no live application's `integration_refs` still references them, and that APP-0003's own catalogue entry is fully annotated with its successor (APP-0011) to prevent future mis-reference. Assign ownership of this clean-up to the EA Catalogue Governance team with a defined completion date.*
- Effort: low | Risk: low
- Rationale: The existence of this conflict suggests that stale integration records referencing APP-0003 remain navigable in the catalogue, enabling designs to inadvertently reference a retired application. Formally retiring these records and annotating APP-0003's entry with its successor eliminates the root cause of future REL-001 violations of this type, reduces catalogue noise, and improves the integrity of the EA repository. This option complements CONFORM/EXTEND and should be executed in parallel.

### Finding: Conflict: Customer Loyalty Platform vs APP-0001 — The design describes the Customer Loyalty Platform connecting to the CRM System via a 'direct database connection for real-time balance lookups'. Direct database connections to another application's data store are an EA anti-pattern that bypasses the owning application's data governance, API contract, and access controls. APP-0001 exposes registered integrations (INT-0001, INT-0003) which should be used instead. This integration must be re-designed as an API-based call through an approved integration pattern. No direct DB access may be registered as an integration_ref.

*Type: conflict | Severity: high*

**Option: CONFORM**
- *Redesign the Customer Loyalty Platform integration to consume one of the existing approved integrations already registered on APP-0001 (INT-0001 or INT-0003). The design document must be updated to replace the 'direct database connection for real-time balance lookups' with an explicit API-based call through the applicable registered integration. The integration_ref on the Customer Loyalty Platform application record must reference INT-0001 or INT-0003 (whichever covers loyalty balance data), and no database_link pattern may be referenced. The solution architect must confirm which of INT-0001 / INT-0003 provides the required balance lookup capability and align the interaction model accordingly.*
- Effort: low | Risk: low
- Rationale: INT-0001 and INT-0003 are already approved and registered against APP-0001, meaning no new catalogue entries, technology approvals, or governance reviews are required. This is the fastest, lowest-risk path to compliance with REL-001 and the EA no-direct-DB-access principle. Consuming an existing interface preserves the CRM System's data governance boundary, API contract, and access controls without any architectural change to the owning application.

**Option: EXTEND**
- *If neither INT-0001 nor INT-0003 satisfies the real-time balance lookup use case (e.g., wrong data entity scope, wrong directionality, or missing SLA), register a new approved sync_api integration from the Customer Loyalty Platform to the CRM System (APP-0001). A draft catalogue entry must be authored, reviewed by the CRM System's domain owner, and approved through the standard EA integration governance process before the design may proceed. The Customer Loyalty Platform application record must then reference this new integration ID in its integration_refs. The direct database connection must be removed from the design.*
- Effort: medium | Risk: low
- Rationale: Where existing integrations do not cover the required capability, extending the catalogue with a new, properly governed integration is the correct EA-compliant path. A sync_api pattern preserves the owning application's interface contract and access controls, fully satisfying REL-001. The medium effort reflects the need for CRM domain-owner engagement, API design/exposure work on APP-0001, and EA governance review — but the architectural risk remains low because the pattern itself is approved.
- Draft catalogue entry:
  ```json
  {
    "object_type": "integration",
    "version": "1.0",
    "id": "REQUIRED - TO BE CONFIRMED",
    "name": "Customer Loyalty Platform \u2192 CRM System: Real-Time Balance Lookup API",
    "pattern_type": "sync_api",
    "status": "approved",
    "source_app": "REQUIRED - TO BE CONFIRMED (Customer Loyalty Platform APP-ID)",
    "target_app": "APP-0001",
    "technology_ref": "REQUIRED - TO BE CONFIRMED (ref to approved REST/GraphQL or equivalent technology entry)",
    "data_entities_exchanged": [
      "REQUIRED - TO BE CONFIRMED (ref to loyalty balance / customer account data entity DE-IDs)"
    ],
    "description": "Synchronous API integration allowing the Customer Loyalty Platform to perform real-time customer loyalty balance lookups against the CRM System (APP-0001) via APP-0001's published API interface. Replaces a non-compliant direct database connection. API contract, authentication, authorisation, and rate-limiting controls are owned and enforced by APP-0001."
  }
  ```

**Option: EXCEPTION**
- *If the Customer Loyalty Platform has an imminent, time-critical go-live and neither INT-0001/INT-0003 nor a new approved integration can be delivered in time, a formal EA exception may be raised to permit the direct database connection on a strictly time-boxed basis (maximum 90 days). The exception request must document: (1) the specific data accessed and query scope, (2) compensating controls (read-only DB credentials, IP restriction, query audit logging, no write access), (3) a named remediation owner, (4) a hard end-date for migration to an approved API pattern, and (5) sign-off from the CRM System domain owner and the EA governance board. The integration_ref must NOT be registered as a database_link; instead, the exception record itself serves as the governance artefact. Breach of the end-date triggers automatic escalation.*
- Effort: medium | Risk: high
- Rationale: An exception is only warranted where a genuine delivery constraint exists and the business cost of delay demonstrably outweighs the architectural risk. Even with compensating controls, a direct database connection bypasses APP-0001's API contract, data governance, and access controls, creating data integrity, security, and coupling risks — hence the high risk classification. The medium effort reflects the governance overhead of preparing, approving, and tracking a formal exception. This option must not be used as a substitute for proper remediation and must have a firm, enforced sunset date.

**Option: RETIRE**
- *If the review of INT-0001 and INT-0003 reveals that one or both of these registered integrations are no longer accurate, actively maintained, or fit for purpose (e.g., they describe a stale pattern, reference deprecated technologies, or have drifted from actual implementation), trigger a formal EA catalogue review of those integration entries. The review should assess whether each integration should be updated to 'retired' status, re-described, or replaced with a current entry. This option runs in parallel with CONFORM or EXTEND — it does not resolve the direct-DB conflict on its own but ensures the catalogue remains trustworthy as the source of truth for APP-0001's approved integration surface.*
- Effort: medium | Risk: medium
- Rationale: If the existing registered integrations on APP-0001 are stale or inaccurate, architects cannot reliably conform to them, which may be the root cause of the direct-DB workaround. Retiring or refreshing outdated catalogue entries improves catalogue integrity and prevents future anti-patterns stemming from the same gap. The medium risk reflects the possibility that retiring an integration record that is still in use by other consumers could have downstream catalogue impacts, requiring a usage impact assessment before retirement is actioned.

### Finding: Conflict: Customer Loyalty Platform vs APP-0001 — Data ownership conflict on the Customer Profile data entity (DE-0001). APP-0001 (CRM System) is the registered sole owner of DE-0001 per the catalogue. The design states the Customer Loyalty Platform 'manages loyalty-specific Customer Profile attributes', implying partial co-ownership or write access to DE-0001. Only one application may own a data entity. Resolution options: (a) the Loyalty Platform reads Customer Profile from APP-0001 via API only (no ownership claim); or (b) loyalty-specific profile attributes are split into a new, distinct data entity (e.g. 'Loyalty Customer Profile') owned by the Customer Loyalty Platform, keeping DE-0001 solely owned by APP-0001.

*Type: conflict | Severity: high*

### Finding: Conflict: E-Commerce Platform vs APP-0002 — Owner domain mismatch. The design document records owner_domain as 'Marketing' for the E-Commerce Platform, but the catalogue entry APP-0002 records owner_domain as 'Retail'. This may indicate an error in the design document, an undocumented domain transfer, or a catalogue entry that is out of date. The authoritative domain ownership must be confirmed and one record corrected.

*Type: conflict | Severity: medium*

**Option: CONFORM**
- *Confirm that the EA catalogue value 'Retail' is the authoritative owner_domain for APP-0002 (E-Commerce Platform), and correct the design document to replace 'Marketing' with 'Retail'. All downstream design artefacts, data entity records (owner_domain on any DE-XXXX referencing APP-0002), and integration specs referencing this application must be reviewed and aligned to 'Retail' in the same change batch. The design document owner must sign off the correction and resubmit the artefact for EA review.*
- Effort: low | Risk: low
- Rationale: If 'Retail' is confirmed as correct by the accountable domain owner, this is a straightforward administrative correction with no architectural change. Aligning the design document to the catalogue restores data integrity at lowest cost and risk, and is the preferred path where no actual domain transfer has occurred.

**Option: EXTEND**
- *If a domain transfer from 'Retail' to 'Marketing' has legitimately occurred but was never formally recorded, update the EA catalogue entry for APP-0002 to reflect 'Marketing' as the authoritative owner_domain. The corrected catalogue entry (draft below) must be approved by both the outgoing domain owner ('Retail') and the EA governance board before publication. The design document value of 'Marketing' is then treated as correct and no change to the design artefact is required. Any related data entities and integration records referencing APP-0002 must also be reviewed for owner_domain consistency.*
- Effort: medium | Risk: medium
- Rationale: Where a legitimate but undocumented domain transfer has taken place, the catalogue entry is the stale record and must be brought up to date rather than forcing the design document to revert to an obsolete state. An EXTEND action formalises the transfer in the catalogue with proper governance sign-off, preserving audit traceability. Risk is medium because the change affects the authoritative record and may have downstream impacts on domain-scoped access controls, cost allocation, and integration ownership.
- Draft catalogue entry:
  ```json
  {
    "object_type": "application",
    "version": "1.0",
    "id": "APP-0002",
    "name": "E-Commerce Platform",
    "alias": [
      "REQUIRED - TO BE CONFIRMED"
    ],
    "status": "live",
    "owner_domain": "Marketing",
    "technology_refs": [
      "REQUIRED - TO BE CONFIRMED"
    ],
    "data_entity_refs": [
      "REQUIRED - TO BE CONFIRMED"
    ],
    "integration_refs": [
      "REQUIRED - TO BE CONFIRMED"
    ],
    "lifecycle_end_date": null,
    "tags": [
      "domain-transfer",
      "ownership-updated"
    ],
    "description": "E-Commerce Platform \u2014 catalogue entry updated to reflect confirmed domain ownership transfer from 'Retail' to 'Marketing'. Previous owner_domain 'Retail' recorded for audit purposes. Transfer approved by EA governance board [APPROVAL REF - TO BE CONFIRMED]."
  }
  ```

**Option: EXCEPTION**
- *Where domain ownership is genuinely disputed or cannot be confirmed within the current sprint/release cycle, raise a time-boxed governed exception against the data integrity rule for APP-0002. The exception must document: (1) the two conflicting values ('Marketing' vs 'Retail'), (2) the business justification for deferral, (3) the named accountable owner responsible for resolution, and (4) an expiry date no greater than 60 days from approval. During the exception window, a formal domain ownership adjudication must be conducted (involving Marketing, Retail, and EA governance leads) with the outcome used to execute either the CONFORM or EXTEND option above. The exception must be recorded in the EA register and surfaced at the next architecture review board.*
- Effort: low | Risk: medium
- Rationale: In cases where the correct owner_domain cannot be determined immediately — for example, due to an ongoing organisational restructure or a disputed handover — forcing a premature correction risks enshrining the wrong value in either record. A short-lived, governed exception prevents a bad fix while ensuring the conflict is not simply abandoned. Risk is medium because the underlying data integrity violation remains live during the exception window and could propagate to dependent artefacts if not actively managed.

### Finding: Conflict: Analytics Dashboard vs APP-0004 — Owner domain mismatch. The design document records owner_domain as 'Marketing' for the Analytics Dashboard, but the catalogue entry APP-0004 records owner_domain as 'Data'. This may indicate an error in the design document or a catalogue entry that is out of date. The authoritative domain ownership must be confirmed and one record corrected.

*Type: conflict | Severity: medium*

### Finding: Gap: Loyalty Points Transaction — No matching catalogue entry exists. The design document explicitly states this is a new entity requiring a catalogue entry. It tracks individual earn, redeem, and expiry events per customer with a 7-year regulatory retention requirement and Confidential classification.

*Type: gap | Severity: high*

**Option: EXTEND**
- *Register 'Loyalty Points Transaction' as a new data entity in the EA catalogue using the refined draft entry below. Resolve the two open required fields before submission: (1) confirm the next available DE-XXXX identifier — DE-0004 is flagged as the likely candidate given the noted sequence gap, but must be verified against the current catalogue state; (2) confirm the owning application APP-ID for the Customer Loyalty Platform — if that application is not yet registered, an application catalogue entry must be created first to satisfy the ref:application constraint on owning_application. Once both values are confirmed, submit the entry for EA review and mark it 'active'. Back-link DE-0004 into the owning application's data_entity_refs array.*
- Effort: low | Risk: low
- Rationale: This is the architecturally correct and lowest-risk resolution for a gap finding. The entity is explicitly called out in the design document as new, has a clear regulatory retention requirement (7 years), a Confidential classification, and PII linkage — all of which make a formal catalogue entry mandatory rather than optional. The draft is already well-formed; only two field values require confirmation, making completion effort minimal. Formalising the entry ensures the entity is discoverable, governed, and correctly linked to its owning application before the solution goes live.
- Draft catalogue entry:
  ```json
  {
    "object_type": "data_entity",
    "version": "1.0",
    "id": "REQUIRED - TO BE CONFIRMED (expected: DE-0004 \u2014 verify next available identifier in catalogue before submission)",
    "name": "Loyalty Points Transaction",
    "status": "active",
    "owning_application": "REQUIRED - TO BE CONFIRMED (expected: APP-ID for Customer Loyalty Platform \u2014 owning application must be registered in catalogue before this entry can be submitted, to satisfy ref:application constraint)",
    "data_classification": "confidential",
    "owner_domain": "Marketing",
    "description": "Individual loyalty points earn, redeem, and expiry event record per customer. Captures points delta, transaction type, source event reference, ISO-8601 timestamp, and running balance after transaction. References DE-0001 Customer Profile via customer_id foreign key. Retained for 7 years per regulatory compliance requirement. Classified Confidential due to PII linkage.",
    "tags": [
      "loyalty",
      "transactional",
      "marketing",
      "pii"
    ]
  }
  ```

**Option: CONFORM**
- *Before creating a net-new catalogue entry, conduct a targeted review of existing data entities in the Marketing and Customer domains to determine whether any current entity — such as a generic 'Customer Transaction' or 'Loyalty Event' record — could be formally extended in scope to cover Loyalty Points Transactions without requiring a separate entry. If a suitable entity is identified: (1) raise a catalogue amendment request to update that entity's description, tags, and classification to encompass earn/redeem/expiry events; (2) validate that its owning application, retention policy, and data classification are compatible with the 7-year and Confidential requirements; (3) update the design document to reference the existing entity ID. If no suitable entity is found after review, fall through to the EXTEND option.*
- Effort: medium | Risk: medium
- Rationale: Catalogue sprawl is an EA risk in its own right. If a semantically compatible entity already exists but was not surfaced during the gap analysis (e.g. due to inconsistent naming or tagging), creating a duplicate entry would introduce redundancy and ambiguity. A short conformance review — timeboxed to avoid delaying delivery — is warranted before committing to net-new registration. However, the specificity of loyalty transaction data (points delta, balance, earn/redeem/expire lifecycle, regulatory retention) makes a true semantic match with a generic entity unlikely, so this option carries medium effort with a medium risk of inconclusive outcome. It should be pursued in parallel with, not instead of, preparing the EXTEND draft.

**Option: EXCEPTION**
- *If the owning application catalogue entry is not yet available and delivery timelines cannot accommodate the dependency resolution required for a full EXTEND submission, raise a governed EA exception to permit the Loyalty Points Transaction entity to operate without a confirmed catalogue entry for a strictly time-boxed period not to exceed 60 days. Exception conditions that must all be satisfied: (1) the draft catalogue entry (as produced in the EXTEND option) is attached to the exception request as the committed future state; (2) a named owner in the Marketing domain accepts accountability for the entity during the exception window; (3) the owning application APP-ID is confirmed and the full catalogue entry is submitted within 60 days — non-negotiable given high severity; (4) data classification controls (Confidential) and 7-year retention policy are enforced from day one regardless of catalogue status; (5) the exception is reviewed at 30 days and auto-escalated if not resolved by day 60.*
- Effort: medium | Risk: high
- Rationale: The gap is severity HIGH and involves a Confidential, PII-linked, regulatory-retention entity — conditions that make an open-ended exception unacceptable. However, a tightly governed, time-boxed exception is preferable to blocking delivery entirely if the only outstanding blocker is the owning application's own catalogue registration (an administrative dependency rather than a design deficiency). The high risk rating reflects the combination of data sensitivity, regulatory exposure, and the inherent risk of operating outside the catalogue. This option should only be selected if the EXTEND path is temporarily blocked by a resolvable dependency, and must never be used to defer governance indefinitely.

### Finding: Conflict: Customer Profile vs DE-0001 — Dual ownership violation. DE-0001 is currently owned exclusively by APP-0001 (CRM System) under the Sales domain. The design document proposes that the Customer Loyalty Platform will manage loyalty-specific fields on this entity (loyalty tier, opt-in status, communication preferences). This introduces a second owning application, which directly violates REL-002 (max_owners: 1). A resolution strategy must be agreed before implementation — options include: (a) sub-entity or extension pattern — create a new 'Customer Loyalty Profile' data entity owned by the Customer Loyalty Platform that references DE-0001 as its master; (b) delegated field ownership — formally document which fields are stearded by which application while retaining a single catalogue owner; (c) domain data ownership transfer — formally re-assign DE-0001 ownership to a cross-domain data steward.

*Type: conflict | Severity: high*

### Finding: Catalogue quality: DE-0012 — Entry status is 'deprecated' but no retirement date, successor entity, or migration deadline is recorded in any catalogue field. The description mentions ownership was migrated from a retired Supplier Portal, but no owning application transition or deprecation policy metadata is captured. Consumers of this entry have no machine-readable signal for when to stop using it.

*Type: catalogue_quality | Severity: medium*

### Finding: Catalogue quality: CATALOGUE-WIDE — ID sequence gap detected: DE-0004 is absent from the catalogue. IDs jump from DE-0003 to DE-0005. This may indicate a deleted or unpublished entry, an error in ID assignment, or an intentional retirement without a catalogue record. The gap is relevant because the draft entry for 'Loyalty Points Transaction' may be a candidate for DE-0004 if the sequence was reserved.

*Type: catalogue_quality | Severity: low*

**Option: CONFORM**
- *Conduct a targeted catalogue audit to determine the origin of DE-0004. Review version control history, catalogue change logs, and any EA governance records (e.g. review board minutes, intake registers) to establish whether DE-0004 was previously published, informally deleted, or incorrectly skipped during ID assignment. If the investigation confirms an assignment error (i.e. no entry ever existed under DE-0004 and the ID was never reserved), update the ID assignment register to formally document DE-0004 as 'skipped — assignment error' with a timestamp and approver. If the draft entry for 'Loyalty Points Transaction' was the intended occupant, confirm this by tracing its intake record. This option restores catalogue auditability without creating or retiring any entry, and is the recommended first action regardless of which subsequent option is chosen.*
- Effort: low | Risk: low
- Rationale: The audit is a prerequisite to all other options. Acting on the gap without understanding its cause risks either duplicating a previously retired concept or assigning an ID that was intentionally held. The effort is low (log and record review) and the risk is minimal — this is a catalogue hygiene action with no downstream system impact.

**Option: EXTEND**
- *Publish a new, schema-valid catalogue entry for 'Loyalty Points Transaction' using the reserved ID DE-0004, filling the sequence gap with a formally governed data entity. This should be preceded by the CONFORM audit (Option 1) to confirm DE-0004 is available and was the intended ID for this draft. The entry must be completed by the owning domain team and pass standard EA review before being set to 'active' status. All required fields in the data_entity schema must be confirmed prior to publication; placeholder values are marked below. Once published, the ID sequence gap is fully remediated and the draft entry is promoted to a governed catalogue record.*
- Effort: medium | Risk: low
- Rationale: The finding explicitly identifies 'Loyalty Points Transaction' as a candidate for DE-0004, suggesting the ID was likely reserved for this concept. Publishing the entry eliminates the gap, formalises a draft that is presumably already in use or under active development, and improves catalogue completeness. Effort is medium due to the EA review cycle required to confirm all mandatory field values before publication.
- Draft catalogue entry:
  ```json
  {
    "object_type": "data_entity",
    "version": "1.0",
    "id": "DE-0004",
    "name": "Loyalty Points Transaction",
    "status": "active",
    "owning_application": "REQUIRED - TO BE CONFIRMED",
    "data_classification": "REQUIRED - TO BE CONFIRMED",
    "owner_domain": "REQUIRED - TO BE CONFIRMED",
    "description": "Represents an individual transaction event that credits, debits, or adjusts loyalty points associated with a customer account. Captures the transaction type, point delta, reference entity (e.g. purchase or redemption), and timestamp. REQUIRED - TO BE CONFIRMED: full canonical definition to be validated by owning domain.",
    "tags": [
      "loyalty",
      "points",
      "transaction",
      "REQUIRED - TO BE CONFIRMED"
    ]
  }
  ```

**Option: EXCEPTION**
- *If investigation confirms that DE-0004 was intentionally skipped (e.g. due to a superseded naming decision, a merged concept, or a deliberate hold during a catalogue restructure) and there is no current entity to assign to it, raise a formal catalogue exception to document the gap as a known, accepted deviation from the sequential ID integrity convention. The exception record must capture: the confirmed reason for the gap, the date the gap was introduced, the approving authority, and a condition that DE-0004 must not be reassigned in future without explicit governance sign-off (to prevent ID reuse confusion). The exception should be reviewed at the next catalogue governance cycle. This option is only appropriate if the CONFORM audit (Option 1) conclusively rules out an error or an unrecorded retirement.*
- Effort: low | Risk: low
- Rationale: Sequential ID integrity is a convention, not a schema-enforced constraint. If the gap has a legitimate, documented origin and no entry is required to fill it, forcing an artificial entry would reduce catalogue quality rather than improve it. A formal exception preserves auditability, prevents future confusion about whether DE-0004 is 'missing' or 'intentionally absent', and satisfies governance without unnecessary churn. Risk is low given the finding's low severity rating.

**Option: RETIRE**
- *If the CONFORM audit (Option 1) reveals that an entry previously existed at DE-0004 but was informally deleted without a catalogue record, create a retrospective 'retired' status entry for DE-0004 to close the auditability gap. The entry should capture all recoverable metadata (name, owning domain, approximate active period, reason for retirement) and be set to status 'retired' with a backdated or estimated lifecycle_end_date. This ensures the catalogue sequence is continuous and that the historical record reflects what was once governed under that ID. If the original entry's metadata cannot be recovered, a minimal record with a description noting 'Entry retired — details unrecoverable; record created retrospectively to document sequence gap' is acceptable. This option is mutually exclusive with Option 2 (EXTEND) — both cannot occupy DE-0004.*
- Effort: low | Risk: low
- Rationale: Informal deletions without retirement records are a catalogue governance failure that undermines traceability. Registering a retrospective retired entry is a low-effort, low-risk corrective action that restores the audit trail, signals to catalogue consumers that the ID was used and closed rather than never assigned, and aligns with standard EA catalogue lifecycle management. This is only triggered if the audit confirms a prior entry existed.

### Finding: Catalogue quality: DE-0001 — The description ('Core customer record including contact details, preferences, and account history') does not reflect the expanded scope being introduced by the Customer Loyalty Platform (loyalty tier, opt-in status, communication preferences). If any ownership resolution results in DE-0001 retaining these fields, the description must be updated to remain accurate and authoritative.

*Type: catalogue_quality | Severity: low*

### Finding: Gap: MongoDB 7.0 — MongoDB is present in the catalogue (TECH-0005) but has status 'unapproved'. It is not a missing entry gap, but a BLOCKED technology gap — the design is attempting to use a prohibited technology. No EXTEND draft is appropriate here. The design must either (a) replace MongoDB with an approved alternative (PostgreSQL TECH-0002 for relational workloads, or Redis TECH-0006 for caching in eligible domains), or (b) submit a formal exception request with data governance justification to seek conditional approval.

*Type: gap | Severity: high*

### Finding: Conflict: MongoDB 7.0 — used by: Customer Loyalty Platform vs TECH-0005 — REL-003 VIOLATION: MongoDB has status 'unapproved'. Applications may only use technologies with status 'approved' or 'conditional'. The Customer Loyalty Platform's use of MongoDB is blocked. Catalogue guidance explicitly states: 'data governance requires relational or approved NoSQL stores only — use PostgreSQL or Redis instead'.

*Type: conflict | Severity: high*

### Finding: Catalogue quality: TECH-0005 — Field 'version_in_use' is null. While not strictly required by schema, this is inconsistent with all other database entries and reduces catalogue utility. The design document references v7.0 — this should be recorded to support future exception or approval tracking.

*Type: catalogue_quality | Severity: low*

**Option: CONFORM**
- *Populate the 'version_in_use' field on TECH-0005 with the value 'v7.0', as referenced in the associated design document. This is a direct data quality correction requiring no schema changes, no new catalogue entries, and no governance process. The update should be applied by the technology record owner and verified against the source design document before submission. Once corrected, TECH-0005 will be consistent with all other technology catalogue entries and the version will be available to support exception tracking, approval workflows, and lifecycle reporting.*
- Effort: low | Risk: low
- Rationale: The correct value (v7.0) is already known from the design document, making this a trivial data entry correction. The field is schema-valid and present on the technology object. This is the lowest-effort, lowest-risk path to full catalogue consistency and is the recommended default remediation for a low-severity catalogue quality finding of this type.

**Option: EXTEND**
- *In addition to populating 'version_in_use' on TECH-0005 (as per the CONFORM option), propose a schema amendment to promote 'version_in_use' from required: false to required: true on the technology object schema (v1.0 → v1.1). This formalises the de-facto standard already observed across all other catalogue entries, prevents recurrence of this finding class, and ensures version data is always available for lifecycle and exception tracking. The schema change must go through the EA governance board for approval. A migration task should be raised to audit all existing TECH-XXXX entries for compliance with the new constraint prior to the schema version being ratified.*
- Effort: medium | Risk: medium
- Rationale: The finding notes that a null 'version_in_use' is inconsistent with all other database entries, indicating an implicit community standard that the schema does not yet enforce. Formalising this as required removes the ambiguity, eliminates the need for future catalogue quality findings of this type, and strengthens the catalogue's utility for version-aware governance processes. The medium risk reflects the need for a backwards-compatibility audit of existing entries before the schema constraint is tightened.
- Draft catalogue entry:
  ```json
  {
    "object_type": "technology",
    "version": "1.1",
    "fields": {
      "id": {
        "type": "string",
        "required": true,
        "pattern": "TECH-[0-9]{4}"
      },
      "name": {
        "type": "string",
        "required": true
      },
      "category": {
        "type": "enum",
        "required": true,
        "values": [
          "language",
          "framework",
          "platform",
          "database",
          "cloud_service",
          "protocol",
          "tool"
        ]
      },
      "status": {
        "type": "enum",
        "required": true,
        "values": [
          "approved",
          "conditional",
          "unapproved",
          "retired"
        ]
      },
      "vendor": {
        "type": "string",
        "required": false
      },
      "version_in_use": {
        "type": "string",
        "required": true,
        "comment": "SCHEMA CHANGE FROM v1.0: Promoted from required: false to required: true. Reflects de-facto standard observed across all catalogue entries. Rationale: supports lifecycle tracking, exception approval workflows, and catalogue consistency."
      },
      "approved_domains": {
        "type": "array",
        "required": false,
        "items": "string",
        "comment": "If empty, approved for all domains"
      },
      "condition_notes": {
        "type": "string",
        "required": false,
        "comment": "Required if status is conditional"
      },
      "lifecycle_end_date": {
        "type": "date",
        "required": false
      },
      "description": {
        "type": "string",
        "required": true
      }
    }
  }
  ```

**Option: RETIRE**
- *Treat the null 'version_in_use' field as a signal that TECH-0005 may be stale or inadequately maintained, and trigger a formal EA review to determine whether the entry should be retired or superseded. The review should confirm: (1) whether v7.0 is still the active version in production; (2) whether a newer version has been adopted without a catalogue update; (3) whether TECH-0005 is still actively referenced by any application or integration catalogue entries. If the technology is no longer current, update the status field to 'retired', set a 'lifecycle_end_date', and raise successor entries as needed. If still active, fall back to the CONFORM option to populate 'version_in_use' and re-assess the entry's overall completeness.*
- Effort: medium | Risk: low
- Rationale: A missing version on a technology entry can indicate that the record has not been actively curated and may not reflect the current production reality. Given the finding already highlights a gap between the catalogue and the design document, a lightweight lifecycle review is prudent to ensure TECH-0005 is not masking a broader staleness issue. The effort is medium due to the need for stakeholder engagement to confirm production status, but the risk is low as no system changes are involved — only catalogue record governance.

### Finding: Catalogue quality: TECH-0007 — Field 'vendor' is present ('Oracle Corporation') but field 'version_in_use' is absent. More importantly, the entry has status 'retired' with a lifecycle_end_date of 2023-12-31. While not referenced in this design, the entry is valid but should carry a prominent warning comment or condition_notes field to guide consumers. 'condition_notes' is absent — recommended to document migration path explicitly.

*Type: catalogue_quality | Severity: low*

**Option: CONFORM**
- *Patch TECH-0007 in the EA catalogue to resolve both quality gaps in a single editorial update: (1) populate 'condition_notes' with an explicit decommission narrative — stating that Oracle Corporation technology reached end-of-life on 2023-12-31, identifying the approved successor technology, and linking to the relevant migration runbook or ADR; (2) populate 'version_in_use' with the last known version active at retirement (e.g. the version current as of lifecycle_end_date). No structural or schema changes are required; both fields already exist on the technology object. The entry remains status 'retired' — this is a documentation-only patch. Once merged, the entry will satisfy the catalogue quality rule and provide unambiguous guidance to any future consumer who encounters TECH-0007.*
- Effort: low | Risk: low
- Rationale: Both 'condition_notes' and 'version_in_use' are already defined optional fields on the technology schema (v1.0). Populating them requires no schema change, no tooling change, and no downstream impact. The entry is not currently referenced in any active design, so the patch carries zero integration risk. This is the preferred resolution: it fully closes the finding, improves catalogue trustworthiness, and sets a precedent for how retired entries should be documented going forward.

**Option: EXCEPTION**
- *Raise a time-boxed catalogue quality exception for TECH-0007, formally accepting the absence of 'condition_notes' and 'version_in_use' for a defined period (recommended: no longer than the next catalogue governance review cycle, typically 90 days). The exception record must document: (a) the specific fields absent and why the gap exists (e.g. original author no longer available, version data not retained); (b) the assessed consumer impact — currently nil, as the entry carries status 'retired' and is unreferenced in any active design; (c) a named owner responsible for resolving the gap before expiry; and (d) a condition that any new design referencing TECH-0007 is blocked until the exception is resolved or the entry is formally closed out. The exception is logged in the EA decision register and attached to TECH-0007 as a tagged annotation.*
- Effort: low | Risk: low
- Rationale: Because TECH-0007 is not referenced in any current design and carries an explicit 'retired' status with a past lifecycle_end_date, the immediate consumer risk of the missing fields is negligible. An exception is appropriate where the authoritative data (last-known version, migration target) requires investigation that cannot be completed immediately — for instance, if the owning team needs to be consulted or historical records retrieved. The exception provides a governed, auditable mechanism to acknowledge the gap without blocking other work, while preserving accountability for closure. It is a second-best option to CONFORM and should not be used simply to defer effort.

**Option: RETIRE**
- *Trigger a formal EA catalogue retirement review for TECH-0007 to determine whether the entry should be fully closed out and removed from active catalogue surfaces. The review should answer: (1) Is any system still running this Oracle Corporation technology in production beyond the 2023-12-31 lifecycle_end_date? (2) Are there any undocumented references (shadow IT, legacy integrations) that depend on this entry? (3) Should the entry be hard-deleted, archived to a read-only catalogue tier, or retained with a tombstone record? The review outcome must produce at minimum: a final 'condition_notes' value documenting the decommission outcome; confirmation or removal of the entry from all catalogue indexes and search surfaces; and an EA bulletin to registered consumers notifying them of the closure. If active dependencies are discovered during the review, escalate immediately to a medium-severity finding.*
- Effort: medium | Risk: low
- Rationale: TECH-0007 has been past its lifecycle_end_date since 2023-12-31. While the immediate finding severity is low, a retired entry that persists indefinitely without a formal closure process accumulates latent risk: teams may reference it in new designs without realising it is truly decommissioned, or legacy systems depending on it may go undetected. The RETIRE option goes beyond the minimum documentation fix (CONFORM) by triggering active governance to confirm no residual dependencies exist and to cleanly close out the entry's lifecycle. This is the highest-value option if there is any uncertainty about whether the technology has truly been fully decommissioned across the estate.

### Finding: Catalogue quality: TECH-0006 — Status is 'conditional' but no 'condition_notes' field is missing — this entry is COMPLIANT (condition_notes IS present). However, 'version_in_use' is recorded as '7.2' which should be validated as current given Redis's rapid release cadence.

*Type: catalogue_quality | Severity: low*

### Finding: Catalogue quality: TECH-0009 — Status is 'conditional' and condition_notes IS present — compliant. However, 'vendor' field value is 'Elastic NV' — the legal entity name changed to 'Elastic N.V.' (stylistic). Minor data quality issue for consistency.

*Type: catalogue_quality | Severity: low*

**Option: CONFORM**
- *Perform an immediate in-place correction of the 'vendor' field on TECH-0009: update the value from 'Elastic NV' to 'Elastic N.V.' to match the correct legal entity name. Additionally, conduct a one-time sweep of all other technology catalogue entries to identify and correct any similar vendor-name inconsistencies (e.g., missing punctuation, abbreviated legal suffixes). The correction requires no structural schema change — 'vendor' is an optional string field — and can be applied via a catalogue admin update with no downstream impact to references or status.*
- Effort: low | Risk: low
- Rationale: This is the preferred option. The fix is trivial, requires no schema changes, carries zero functional risk, and immediately restores data consistency. A concurrent catalogue-wide sweep ensures the issue is not repeated across other entries, maximising the return on the minimal effort required.

**Option: CONFORM**
- *Correct the 'vendor' field on TECH-0009 to 'Elastic N.V.' (as per Option 1), and additionally introduce a catalogue governance control to prevent recurrence: define a curated vendor name reference list (or a catalogue validation rule) that enforces approved legal entity name strings for known vendors. Integrate this as a linting check in the catalogue CI/CD pipeline or review workflow so that future submissions are validated against the reference list at entry time.*
- Effort: medium | Risk: low
- Rationale: Addresses the immediate finding and the underlying process gap simultaneously. While the one-time correction is low effort, without a preventive control the same stylistic inconsistency is likely to recur as new entries are added. The additional investment is proportionate if the catalogue is actively growing or maintained by multiple contributors. Recommended when catalogue hygiene is a standing EA priority.

**Option: EXCEPTION**
- *Formally accept the current vendor field value of 'Elastic NV' on TECH-0009 as a governed, time-bounded exception. Document the deviation in the catalogue entry's metadata (e.g., a 'known_issues' or 'exception_notes' annotation), stating: (1) the correct legal name is 'Elastic N.V.', (2) the discrepancy is cosmetic and carries no functional or compliance impact, and (3) the exception is valid until the next scheduled catalogue review cycle, at which point the value must be corrected. No operational or architectural decisions may be blocked on the basis of this deviation.*
- Effort: low | Risk: low
- Rationale: Acceptable only if catalogue edit access is currently restricted, a release freeze is in effect, or correction is deferred to a scheduled batch maintenance window. The exception must be time-bounded to prevent permanent acceptance of a known inaccuracy. This option is strictly lower priority than CONFORM Option 1 — the correction effort is comparable to or less than the exception documentation effort, so exception should not be chosen for convenience alone.

### Finding: Catalogue quality: TECH-0010 — Field 'vendor' is absent. While not required by schema, XML/SOAP is a protocol standard — the vendor field could reference 'W3C / OASIS' for traceability. Additionally, 'version_in_use' is absent — acceptable for a protocol, but noting for completeness.

*Type: catalogue_quality | Severity: low*

### Finding: Catalogue quality: TECH-0001 — Field 'approved_domains' is an empty array [], implying approval across all domains — this is correct per schema comment. However, the description states 'Primary backend programming language for all new RetailCo services' which confirms intent. No issue — informational only.

*Type: catalogue_quality | Severity: low*

### Finding: Catalogue quality: TECH-0008 — Field 'version_in_use' is absent. For a managed AWS cloud service this is expected and acceptable (AWS manages versioning). However, the schema does not exempt cloud_service entries from this field. Recommend adding a note such as 'managed-service — versioning abstracted by vendor' for clarity.

*Type: catalogue_quality | Severity: low*

### Finding: Gap: E-Commerce Platform → Customer Loyalty Platform — No catalogue entry exists for an integration from E-Commerce Platform to Customer Loyalty Platform. This async Kafka-based loyalty points earning flow is entirely absent from the EA catalogue and must be registered before implementation.

*Type: gap | Severity: high*

### Finding: Gap: Customer Loyalty Platform → Analytics Dashboard — No catalogue entry exists for an integration from Customer Loyalty Platform to Analytics Dashboard. Although INT-0002 covers E-Commerce → Analytics via Kafka, this is a distinct source application and data entity (Loyalty Points Transaction) and must be independently catalogued.

*Type: gap | Severity: high*

### Finding: Gap: Customer Loyalty Platform → CRM System — No catalogue entry exists for a database_link integration from Customer Loyalty Platform to CRM System. Direct database connections are a recognised anti-pattern in event-driven architectures and violate separation of concerns. The use of MongoDB as a cross-system database link raises significant data sovereignty, coupling, and security concerns that require Architecture Review Board (ARB) approval before proceeding.

*Type: gap | Severity: high*

### Finding: Gap: Customer Loyalty Platform → Legacy Promotions Engine — No catalogue entry exists for a sync_api integration from Customer Loyalty Platform to a Legacy Promotions Engine. The 'Legacy' designation suggests this may be a system not yet registered in the application catalogue. Additionally, FastAPI 0.104 must be validated against the approved technology register. The use of a synchronous call to a legacy system introduces availability and latency coupling risks.

*Type: gap | Severity: high*

### Finding: Gap: Loyalty API Gateway → Customer Loyalty Platform — No catalogue entry exists for a sync_api integration from Loyalty API Gateway to Customer Loyalty Platform. Neither 'Loyalty API Gateway' nor 'Customer Loyalty Platform' appear as registered applications in the catalogue. Both applications and this integration must be registered. Additionally, the combined technology stack (FastAPI 0.104 + AWS Lambda) requires technology reference validation. Two data entities (Loyalty Points Transaction and Customer Profile) are exchanged and both require DE-IDs.

*Type: gap | Severity: high*

### Finding: Conflict: Customer Loyalty Platform → CRM System vs INT-0001 — The design specifies a database_link (direct MongoDB connection) pattern for CRM data access. The only CRM-related integration in the catalogue (INT-0001) uses async_event via Kafka. Direct database links circumvent the established event-driven integration standard observed across the catalogue and represent an architectural pattern violation. This integration must be reviewed by the ARB; the recommended remediation is to replace the database_link with a sync_api call (e.g. mirroring INT-0010 Mobile App → CRM pattern) or an async_event subscription.

*Type: conflict | Severity: high*

### Finding: Conflict: Customer Loyalty Platform → Legacy Promotions Engine vs INT-0008 — INT-0008 establishes the approved pattern for Promotions interactions as E-Commerce Platform → Promotions Service (APP-0011) via sync_api/REST (TECH-0011). The design routes Customer Loyalty Platform → Legacy Promotions Engine using FastAPI 0.104, which is not the catalogued technology reference (TECH-0011). It is unclear whether 'Legacy Promotions Engine' is the same application as APP-0011 ('Promotions Service') under a different name, or a separate, unregistered legacy system. If the same system, the technology reference conflicts; if a different system, it is an unregistered application. Clarification is required.

*Type: conflict | Severity: medium*

### Finding: Catalogue quality: INT-0001 — The source_app value 'APP-0001' and target_app value 'APP-0002' are application reference IDs but the schema requires items to resolve to ref:application. No application register was provided for validation — these references cannot be confirmed as resolvable. Same concern applies to technology_ref 'TECH-0003' and data entity 'DE-0001'. This is a systemic issue across all catalogue entries.

*Type: catalogue_quality | Severity: medium*

### Finding: Catalogue quality: INT-0005 — Status is set to 'conditional' which is a valid enum value, but the description explicitly states this integration is 'to be decommissioned when IMS is fully retired'. If decommissioning has commenced or IMS retirement is in-flight, the status should be reviewed for transition to 'retired'. No retirement date or dependency tracking is recorded in the entry, creating a governance blind spot.

*Type: catalogue_quality | Severity: medium*

### Finding: Catalogue quality: INT-0002 — INT-0002 is superficially similar in target (Analytics Dashboard / APP-0004) and technology (TECH-0003 / Kafka) to the design entity 'Customer Loyalty Platform → Analytics Dashboard'. The catalogue entry name 'E-Commerce to Analytics Order Events' and its data entity (DE-0002 / Order Events) are sufficiently distinct, but the similarity creates a risk of future duplicate registration. Recommend adding a 'related_integrations' or 'notes' field at schema level to cross-reference related flows.

*Type: catalogue_quality | Severity: low*

### Finding: Catalogue quality: INT-0008 — The target application is recorded as APP-0011 with name 'Promotions Service'. The design document refers to a 'Legacy Promotions Engine' interacting with the Customer Loyalty Platform. It is ambiguous whether APP-0011 and the Legacy Promotions Engine are the same system. If they are, the catalogue entry name 'Promotions Service' does not reflect the legacy nature of the application, which has governance implications (legacy systems typically require additional review gates). The application catalogue entry for APP-0011 should clarify its legacy status.

*Type: catalogue_quality | Severity: medium*

### Finding: Catalogue quality: INT-0009 — INT-0009 uses pattern_type 'streaming' which is a valid schema enum value, but it is the only streaming entry in the catalogue and no streaming technology standard appears to be defined separately from the Kafka entries (TECH-0003). If TECH-0003 covers both async_event and streaming use cases, this creates an implicit dual-use technology reference without formal pattern differentiation. The schema does not enforce a mapping between pattern_type and technology_ref, which may lead to inconsistent future registrations.

*Type: catalogue_quality | Severity: low*

### Finding: Consistency issue: Integration target 'Legacy Promotions Engine' has status 'retired'. Only 'live' applications may be integration targets.

*Type: consistency | Severity: high*

### Finding: Consistency issue: Data entity 'Customer Profile' is owned by 'APP-0001' in the catalogue but the design claims ownership for 'CRM System'. A data entity may only have one owning application.

*Type: consistency | Severity: high*

### Finding: Consistency issue: Integration 'Customer Loyalty Platform' → 'CRM System' uses pattern 'database_link' which is not among approved patterns in the catalogue (async_event, batch_file, streaming, sync_api).

*Type: consistency | Severity: high*

**Option: CONFORM**
- *Re-architect the 'Customer Loyalty Platform' → 'CRM System' integration to replace the direct database link with an EA-approved integration pattern. The recommended replacement is 'sync_api' (e.g., a RESTful or GraphQL API exposed by the CRM System) for real-time loyalty data lookups, or 'async_event' (e.g., a message broker such as Kafka or RabbitMQ) if the data flow is event-driven and latency-tolerant. The integration record must be updated so that 'pattern_type' is set to one of the approved enum values: sync_api, async_event, batch_file, or streaming. The owning teams of both applications must co-design the new interface contract, update the integration catalogue entry, and retire the existing database_link connection.*
- Effort: high | Risk: medium
- Rationale: This is the preferred long-term path and the only option that fully resolves the REL-004 violation. Direct database links create tight coupling between applications, expose internal data schemas across domain boundaries, undermine data ownership principles (as modelled by the 'owning_application' field on data_entity), and make independent evolution of either system very difficult. Migrating to an approved pattern eliminates architectural debt, restores catalogue consistency, and reduces operational risk from uncontrolled cross-schema dependencies.

**Option: EXTEND**
- *Formally add 'database_link' as a conditional integration pattern to the EA catalogue, with clearly defined guardrails that restrict its use to narrowly scoped, time-bounded scenarios (e.g., same-domain read-only reporting integrations or legacy migration bridges). The pattern would carry a 'conditional' status, requiring explicit EA board approval for each new instance and mandating a migration plan to an approved pattern within an agreed timeframe. The integration record for 'Customer Loyalty Platform' → 'CRM System' must then be updated to status 'conditional' and linked to this new catalogue entry, with condition_notes documented on the associated technology reference.*
- Effort: medium | Risk: medium
- Rationale: While 'database_link' is present as a valid enum value in the integration schema's pattern_type field, it is currently absent from the EA-approved patterns catalogue, indicating it was intentionally excluded from governed use. If the architecture board determines there are legitimate, recurring use cases (e.g., legacy data migration, same-team co-owned systems) that cannot be served by existing patterns, formalising it as a conditional pattern with guardrails is preferable to allowing ungoverned usage. This avoids the precedent of silent non-compliance while acknowledging real-world constraints.
- Draft catalogue entry:
  ```json
  {
    "object_type": "integration",
    "version": "1.0",
    "id": "REQUIRED - TO BE CONFIRMED",
    "name": "Database Link Integration Pattern",
    "pattern_type": "database_link",
    "status": "conditional",
    "source_app": "REQUIRED - TO BE CONFIRMED",
    "target_app": "REQUIRED - TO BE CONFIRMED",
    "technology_ref": "REQUIRED - TO BE CONFIRMED",
    "data_entities_exchanged": [],
    "description": "A direct database-to-database link pattern permitting one application to read from or write to another application's database. This pattern is conditionally approved only where: (1) both applications share the same owner_domain, (2) the integration is read-only or strictly time-bounded as part of a migration effort, (3) a migration plan to an approved pattern (sync_api, async_event, batch_file, or streaming) is documented and approved by the EA board, and (4) condition_notes on the associated technology_ref explicitly state the approved scope, data classification constraints, and sunset date."
  }
  ```

**Option: EXCEPTION**
- *Raise a formal EA exception against rule REL-004 to permit the existing 'database_link' pattern between 'Customer Loyalty Platform' and 'CRM System' for a defined, time-limited period (recommended maximum: 12 months). The exception request must document: (1) the business justification for why re-architecting is not immediately feasible, (2) the data entities exchanged and their classification (per the data_entity schema), (3) compensating controls in place (e.g., read-only database user, network-level access restrictions, monitoring/alerting on cross-schema queries), and (4) a committed remediation date by which the integration will be migrated to a CONFORM-compliant pattern. The integration record must be updated to status 'conditional' with explicit condition_notes referencing the exception approval.*
- Effort: low | Risk: high
- Rationale: An exception is appropriate only as a short-term tactical measure where the cost or risk of immediate re-architecture outweighs the risk of continued non-compliance — for example, if a major CRM migration is already in flight. The risk level is rated high because database links bypass application-layer access controls, violate data domain ownership boundaries, and may expose confidential or restricted data entities to uncontrolled access. Compensating controls and a hard sunset date are mandatory conditions for exception approval. This option does not resolve the underlying violation and must not be used as a permanent state.

**Option: RETIRE**
- *Initiate a formal review of the 'Customer Loyalty Platform' → 'CRM System' integration itself, assessing whether this integration is still required or whether the business capability it serves has been superseded. If the integration is found to be redundant (e.g., the CRM System already exposes the required data via an approved sync_api or async_event feed that is not yet registered in the catalogue), the integration should be decommissioned and its catalogue entry updated to status 'retired' with a lifecycle_end_date populated. Both the source and target application records must have their 'integration_refs' updated to remove the retired entry.*
- Effort: medium | Risk: low
- Rationale: High-severity findings of this type sometimes surface integrations that were implemented historically and have since been partially or fully superseded by other data flows, but were never formally decommissioned. Before investing effort in re-architecting or governing a database link, it is worth validating that the integration is still actively needed. If the data exchange is already being served through an approved pattern elsewhere in the landscape, retiring this non-compliant integration is the lowest-risk and lowest-effort path to full compliance, and avoids creating duplicate data flows.

### Finding: Consistency issue: Proposed application 'Customer Loyalty Platform' does not reference any approved technology. At least one approved technology is required.

*Type: consistency | Severity: high*

**Option: CONFORM**
- *Update the 'Customer Loyalty Platform' application catalogue entry to populate the required 'technology_refs' field with at least one technology that already holds 'approved' status in the EA technology catalogue. The application owner should audit the platform's actual or intended technology stack, identify matching approved entries (e.g. an approved cloud platform, language, or framework), and add the corresponding TECH-XXXX reference(s) to the entry. This resolves the REL-005 violation with zero new catalogue changes.*
- Effort: low | Risk: low
- Rationale: If any component of the Customer Loyalty Platform's technology stack already exists in the EA catalogue with 'approved' status, this is the fastest and lowest-risk path. It enforces the architectural standard as intended, requires no governance approvals beyond normal catalogue editing rights, and leaves no outstanding compliance debt.

**Option: EXTEND**
- *If one or more technologies used by the 'Customer Loyalty Platform' are not yet present in the EA technology catalogue, create a new Technology catalogue entry for each missing technology and submit it for EA approval review. Once at least one new entry is approved (status set to 'approved'), reference it in the application's 'technology_refs' field to satisfy REL-005. The draft entry below should be completed by the application owner and reviewed by the EA board prior to publishing.*
- Effort: medium | Risk: medium
- Rationale: Where the platform legitimately uses a technology that has not yet been catalogued, the correct architectural response is to extend the catalogue rather than either force-fit an incorrect reference or grant a blanket exception. This path maintains catalogue integrity, creates a reusable approved entry for other teams, and resolves the compliance gap in a governed manner. Risk is medium because the approval outcome is not guaranteed and could require technology changes if the EA board rejects the submission.
- Draft catalogue entry:
  ```json
  {
    "object_type": "technology",
    "version": "1.0",
    "id": "REQUIRED - TO BE CONFIRMED",
    "name": "REQUIRED - TO BE CONFIRMED",
    "category": "REQUIRED - TO BE CONFIRMED",
    "status": "approved",
    "vendor": "REQUIRED - TO BE CONFIRMED",
    "version_in_use": "REQUIRED - TO BE CONFIRMED",
    "approved_domains": [
      "REQUIRED - TO BE CONFIRMED"
    ],
    "condition_notes": null,
    "lifecycle_end_date": null,
    "description": "REQUIRED - TO BE CONFIRMED"
  }
  ```

**Option: EXCEPTION**
- *Raise a time-boxed EA exception against rule REL-005 for the 'Customer Loyalty Platform', explicitly documenting the reason no approved technology reference can be provided at this time. The exception must be approved by the EA Governance Board, must state a specific expiry date (recommended maximum: 90 days), and must be accompanied by a committed remediation plan (either CONFORM or EXTEND) that will be executed before expiry. The application entry should be tagged with 'exception:REL-005' and linked to the exception record.*
- Effort: medium | Risk: high
- Rationale: An exception is only appropriate where the application is under active development and the technology stack is genuinely not yet finalised, or where an urgent delivery deadline prevents immediate catalogue alignment. It is classified as high risk because it leaves the application in a non-compliant state, creates governance debt, and may set an undesirable precedent if not tightly controlled. It must not be used as a substitute for CONFORM or EXTEND where those paths are viable.

**Option: RETIRE**
- *If investigation reveals that the 'Customer Loyalty Platform' proposal duplicates functionality already delivered by an existing live application in the catalogue — one that already carries approved technology references — initiate a formal retirement/cancellation review of the 'Customer Loyalty Platform' proposal. Update its status to 'retired', set a 'lifecycle_end_date', and redirect stakeholders to the existing compliant application. Document the duplication finding and the decision rationale in the catalogue entry before archiving.*
- Effort: high | Risk: medium
- Rationale: If the proposed application should not exist in its current form (e.g. it is a shadow-IT initiative or a duplicate of a governed platform), retiring the proposal is architecturally cleaner than forcing a technology reference onto an entry that will never progress to 'live' status. This option avoids catalogue pollution and steers investment toward compliant, already-approved solutions. Effort is high due to the stakeholder alignment and potential scope-change implications of cancelling an application proposal.

---

## Appendix A: Full Entity Match Table

| Catalogue Type | Design Entity | Catalogue Entry | Confidence |
|---|---|---|---|
| application | CRM System | `APP-0001` | 100% |
| application | E-Commerce Platform | `APP-0002` | 100% |
| application | Legacy Promotions Engine | `APP-0003` | 100% |
| application | Analytics Dashboard | `APP-0004` | 100% |
| data_entity | Customer Profile | `DE-0001` | 98% |
| data_entity | Loyalty Points Transaction | `DE-0009` | 12% |
| technology | Python 3.11 | `TECH-0001` | 100% |
| technology | Apache Kafka 3.5 | `TECH-0003` | 100% |
| technology | FastAPI 0.104 | `TECH-0011` | 100% |
| technology | AWS Lambda | `TECH-0008` | 98% |
| technology | MongoDB 7.0 | `TECH-0005` | 100% |
| integration | E-Commerce Platform → Customer Loyalty Platform | `INT-0002` | 20% |
| integration | Customer Loyalty Platform → Analytics Dashboard | `INT-0002` | 20% |
| integration | Customer Loyalty Platform → CRM System | `INT-0001` | 15% |
| integration | Customer Loyalty Platform → Legacy Promotions Engine | `INT-0008` | 20% |
| integration | Loyalty API Gateway → Customer Loyalty Platform | `INT-0004` | 15% |

## Appendix B: Schema Validation Results

**ea_catalogue_applications.json** — ✗ FAIL (1 error(s)) (12 entries)
  - [HIGH] `APP-0031` — description: Missing required field: description
**ea_catalogue_data_entities.json** — ✓ PASS (11 entries)
**ea_catalogue_technologies.json** — ✓ PASS (13 entries)
**ea_catalogue_integrations.json** — ✓ PASS (10 entries)
