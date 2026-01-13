# AegisX Real-World Signal Flow

## Overview

This document describes how security signals flow through AegisX in production environments, from scanner execution to remediation, with concrete examples.

---

## End-to-End Flow: From Scan to Fix

```
[1] Scanner Runs → [2] Webhook Fires → [3] AegisX Processes → [4] Team Notified → [5] Engineer Fixes → [6] Metrics Updated
```

---

## Scenario 1: Critical SQL Injection Found

### Timeline

**T+0min: CI Pipeline Executes**

```bash
# GitHub Actions workflow
- name: Run Semgrep Security Scan
  run: semgrep --config=auto --json -o results.json ./src
```

**Output:**
```json
{
  "results": [
    {
      "check_id": "javascript.express.security.audit.sql-injection",
      "path": "src/api/users.js",
      "start": {"line": 45, "col": 12},
      "end": {"line": 45, "col": 67},
      "extra": {
        "severity": "ERROR",
        "message": "Detected SQL query that depends on user input..."
      }
    }
  ]
}
```

---

**T+1min: Webhook Sent to AegisX**

```bash
curl -X POST https://aegisx.company.com/api/v1/ingest/sast \
  -H "Authorization: Bearer $AEGISX_API_KEY" \
  -H "X-Scan-ID: github-actions-run-12345" \
  -H "X-Repository: company/payment-api" \
  -d @results.json
```

---

**T+1min: AegisX Ingestion**

```python
# AegisX receives webhook
{
  "scanner": "semgrep",
  "repository": "company/payment-api",
  "commit": "abc123def456",
  "branch": "main",
  "findings": [...]
}

# Step 1: Normalize finding
finding = SemgrepAdapter().normalize(raw_finding)
# Output: Finding(
#   source="semgrep",
#   rule_id="javascript.express.security.audit.sql-injection",
#   vulnerability_type="sql_injection",
#   severity="HIGH",
#   file_path="src/api/users.js",
#   line_start=45,
#   ...
# )

# Step 2: Compute fingerprint
fingerprint = hash(
    "src/api/users.js",
    "45-45",
    "javascript.express.security.audit.sql-injection"
)
# Output: "7f3a8b9c2d1e..."

# Step 3: Check if seen before
existing = await db.get_finding_by_fingerprint(fingerprint)
if existing:
    # Update last_seen, increment recurrence_count
    existing.last_seen = datetime.now()
    existing.recurrence_count += 1
    await db.update(existing)
else:
    # New finding - create record
    await db.create(finding)
```

---

**T+2min: Context Enrichment**

```python
# Query Git for context
git_context = await git_service.get_metadata("src/api/users.js")
# Output: {
#   "last_author": "jane@company.com",
#   "last_modified": "2026-01-10",
#   "commit_frequency": 8  # commits/week in this file
# }

# Query service registry
service = await service_registry.get("payment-api")
# Output: {
#   "tier": "critical",
#   "data_classification": "pii",
#   "ownership": {
#     "team": "payments",
#     "oncall": "payments-oncall@pagerduty.com",
#     "slack_channel": "#payments-security"
#   },
#   "external_facing": true,
#   "deployment_frequency": "daily"
# }

# Fetch historical patterns
history = await history_service.get_patterns("sql_injection", "payment-api")
# Output: {
#   "false_positive_rate": 0.05,  # 5% of SQL injection findings are FP
#   "avg_remediation_time_days": 3,
#   "similar_findings_fixed": 15
# }

# Combine into EnrichedFinding
enriched_finding = EnrichedFinding(
    **finding.dict(),
    git_context=git_context,
    service=service,
    history=history
)
```

---

**T+3min: Risk Scoring**

```python
# Calculate exploitability
exploitability = calculate_exploitability(enriched_finding)
# Factors:
#   - SQL injection is well-understood attack (0.9)
#   - Service is external-facing (1.0)
#   - Authentication not required for endpoint (1.0)
#   - CVSS attack complexity: LOW (0.9)
# Result: 0.95

# Calculate business impact
impact = calculate_impact(enriched_finding)
# Factors:
#   - Service tier: CRITICAL (1.0)
#   - Data classification: PII (1.0)
# Result: 1.0

# Calculate urgency
urgency = calculate_urgency(enriched_finding)
# Factors:
#   - Finding is new (not recurring) (0.8)
#   - Service deploys daily (fix can go out quickly) (0.9)
# Result: 0.85

# Estimate remediation cost
remediation_cost = estimate_remediation_cost(enriched_finding)
# Factors:
#   - SQL injection avg fix time: 3 days (0.6)
#   - File has high commit frequency (maintained) (0.7)
# Result: 0.65

# Final risk score
risk_score = (
    exploitability * 0.4 +  # 0.95 * 0.4 = 0.38
    impact * 0.3 +          # 1.0 * 0.3 = 0.30
    urgency * 0.2 +         # 0.85 * 0.2 = 0.17
    remediation_cost * 0.1  # 0.65 * 0.1 = 0.065
)
# Result: 0.915 (CRITICAL)
```

---

**T+4min: Prioritization & Routing**

```python
# Add to priority queue
await priority_queue.push(enriched_finding)

# Determine routing based on risk score
if risk_score > 0.9:
    # CRITICAL - create incident
    await pagerduty.create_incident({
        "title": "CRITICAL: SQL Injection in payment-api",
        "service": "payment-api",
        "urgency": "high",
        "body": f"SQL injection found in {finding.file_path}:{finding.line_start}\n"
                f"Risk Score: {risk_score}\n"
                f"Assigned to: {service.ownership.oncall}"
    })

    # Also send Slack alert
    await slack.send_message({
        "channel": service.ownership.slack_channel,  # #payments-security
        "text": "🚨 CRITICAL Security Finding",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "SQL Injection Detected"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Service:* payment-api"},
                    {"type": "mrkdwn", "text": f"*Risk Score:* {risk_score:.2f}"},
                    {"type": "mrkdwn", "text": f"*File:* `src/api/users.js:45`"},
                    {"type": "mrkdwn", "text": f"*On-Call:* {service.ownership.oncall}"}
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View in AegisX"},
                        "url": f"https://aegisx.company.com/findings/{finding.id}"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Acknowledge"},
                        "value": str(finding.id),
                        "action_id": "ack_finding"
                    }
                ]
            }
        ]
    })

    # Create Jira ticket
    await jira.create_issue({
        "project": "SEC",
        "type": "Security Finding",
        "priority": "Highest",
        "summary": f"SQL Injection in payment-api (src/api/users.js)",
        "description": f"""
*Risk Score:* {risk_score:.2f}

*Finding Details:*
- Type: SQL Injection
- Location: src/api/users.js:45
- Severity: HIGH
- Exploitability: {exploitability:.2f}
- Impact: {impact:.2f}

*Remediation Guidance:*
Use parameterized queries instead of string concatenation:

{{code}}
// BAD
db.execute(f"SELECT * FROM users WHERE id = {user_input}")

// GOOD
db.execute("SELECT * FROM users WHERE id = $1", [user_input])
{{code}}

*AegisX Link:* https://aegisx.company.com/findings/{finding.id}
        """,
        "assignee": service.ownership.team_lead
    })
```

---

**T+4min: Engineer Notified**

**PagerDuty Incident:**
```
Title: CRITICAL: SQL Injection in payment-api
Assigned To: Jane Doe (payments-oncall)
Urgency: High
Status: Triggered
```

**Slack Message in #payments-security:**
```
🚨 CRITICAL Security Finding

SQL Injection Detected

Service: payment-api
Risk Score: 0.92
File: `src/api/users.js:45`
On-Call: payments-oncall

[View in AegisX] [Acknowledge]
```

**Jira Ticket SEC-1234:**
```
Summary: SQL Injection in payment-api (src/api/users.js)
Priority: Highest
Status: To Do
Assignee: Jane Doe
```

---

**T+10min: Engineer Acknowledges**

```python
# Jane clicks "Acknowledge" in Slack
@slack_app.action("ack_finding")
async def handle_ack(ack, body):
    finding_id = body["actions"][0]["value"]

    # Update finding status
    await db.update_finding(finding_id, status="IN_PROGRESS")

    # Acknowledge PagerDuty incident
    await pagerduty.acknowledge_incident(finding_id)

    # Reply in Slack
    ack({
        "text": f"<@{body['user']['id']}> acknowledged the finding. Starting remediation."
    })

    # Record in audit log
    await audit_log.record({
        "event": "finding_acknowledged",
        "finding_id": finding_id,
        "user": body["user"]["email"],
        "timestamp": datetime.now()
    })
```

---

**T+2 hours: Engineer Creates Fix**

```javascript
// Jane creates PR with fix
// BEFORE (vulnerable):
app.get('/users/:id', (req, res) => {
    const query = `SELECT * FROM users WHERE id = ${req.params.id}`;
    db.execute(query);
});

// AFTER (fixed):
app.get('/users/:id', (req, res) => {
    const query = 'SELECT * FROM users WHERE id = $1';
    db.execute(query, [req.params.id]);
});
```

**PR Description:**
```
Fix SQL injection vulnerability (SEC-1234)

- Use parameterized query instead of string interpolation
- Addresses AegisX finding: aegisx-7f3a8b9c2d1e

Closes SEC-1234
```

---

**T+2.5 hours: PR Merged, Fix Deployed**

```bash
# CI runs again
- name: Run Semgrep
  run: semgrep --config=auto --json -o results.json ./src

# No SQL injection finding in output

# Deploy to production
- name: Deploy
  run: kubectl rollout restart deployment/payment-api
```

**Webhook sent to AegisX:**
```json
{
  "scanner": "semgrep",
  "repository": "company/payment-api",
  "commit": "xyz789abc012",  # New commit with fix
  "findings": []  # SQL injection no longer present
}
```

---

**T+2.5 hours: AegisX Resolves Finding**

```python
# AegisX processes new scan
# Finding fingerprint not present in new results

# Auto-resolve finding
finding = await db.get_finding_by_fingerprint("7f3a8b9c2d1e...")
finding.status = "RESOLVED"
finding.resolved_at = datetime.now()
finding.resolution_method = "auto_scan"
await db.update(finding)

# Calculate MTTR
mttr = finding.resolved_at - finding.first_seen
# Result: 2.5 hours

# Close PagerDuty incident
await pagerduty.resolve_incident(finding.id, resolution_note="Fixed in production")

# Update Jira ticket
await jira.transition_issue("SEC-1234", "Done")
await jira.add_comment("SEC-1234", f"Fixed and deployed. MTTR: {mttr}")

# Send Slack notification
await slack.send_message({
    "channel": "#payments-security",
    "text": f"✅ SQL Injection finding resolved (MTTR: {mttr})"
})

# Update metrics
await metrics.record({
    "metric": "finding_resolved",
    "service": "payment-api",
    "severity": "HIGH",
    "mttr_hours": mttr.total_seconds() / 3600,
    "risk_score": 0.92
})
```

---

## Scenario 2: Low-Priority Dependency Vulnerability

### Timeline

**T+0: Snyk Scan Finds Outdated Library**

```bash
# Snyk scan in CI
snyk test --json > snyk-results.json
```

**Finding:**
```json
{
  "vulnerabilities": [
    {
      "id": "SNYK-JS-LODASH-567746",
      "title": "Prototype Pollution",
      "package": "lodash",
      "version": "4.17.15",
      "severity": "low",
      "cvssScore": 3.7,
      "isUpgradable": true,
      "upgradePath": ["lodash@4.17.21"]
    }
  ]
}
```

---

**T+1min: AegisX Processes**

```python
# Risk scoring
exploitability = 0.2  # Requires specific conditions
impact = 0.4  # Internal service, no PII
urgency = 0.3  # Known since 2020, patch available
remediation_cost = 0.9  # Easy upgrade

risk_score = 0.35  # MEDIUM-LOW
```

---

**T+1min: Routing Decision**

```python
if risk_score < 0.5:
    # MEDIUM/LOW - add to weekly digest, don't page
    await digest_queue.add(finding, team="platform")

    # No Jira ticket (yet)
    # No PagerDuty incident
    # No immediate Slack alert
```

---

**Monday 9am: Weekly Digest Sent**

```python
# Aggregate findings from past week
digest = await generate_weekly_digest(team="platform")

await email.send({
    "to": "platform-team@company.com",
    "subject": "Security Digest: Week of Jan 13",
    "body": f"""
    Platform Team Weekly Security Digest

    New Findings: 12
    Fixed Last Week: 8
    Open High-Priority: 2

    ## Action Required
    1. [MEDIUM] Prototype Pollution in lodash (payment-api, user-service)
       - Affects 2 services
       - Easy fix: upgrade to 4.17.21
       - AegisX: https://aegisx.company.com/findings/bulk-xyz

    2. [LOW] Outdated Express.js (internal-dashboard)
       - Low risk (internal only)
       - Suggested fix: ...

    View full report: https://aegisx.company.com/digest/2026-w03
    """
})
```

---

## Scenario 3: False Positive Dismissal

**Engineer reviews finding, determines it's a false positive:**

```python
POST /api/v1/findings/abc-123/dismiss

{
  "reason": "false_positive",
  "justification": "This endpoint requires admin authentication which mitigates the risk. The scanner doesn't detect our auth middleware."
}
```

**AegisX learns from dismissal:**

```python
# Record pattern
await ml_service.record_false_positive({
    "rule_id": finding.rule_id,
    "file_pattern": "*/admin/*",
    "code_pattern": has_auth_middleware(finding.code_snippet),
    "dismissal_reason": "auth_middleware_present"
})

# Future findings with similar pattern get lower priority
if has_auth_middleware(new_finding.code_snippet):
    risk_score *= 0.5  # Reduce by 50%
```

---

## Signal Sources in Production

### 1. SAST (Static Application Security Testing)

**Tools:** Semgrep, CodeQL, Checkmarx, Snyk Code

**Integration:**
```yaml
# .github/workflows/security.yml
- name: Run Semgrep
  run: |
    semgrep --config=auto --json -o results.json
    curl -X POST $AEGISX_URL/api/v1/ingest/sast \
      -H "Authorization: Bearer $AEGISX_KEY" \
      -d @results.json
```

**Findings:** Code vulnerabilities (SQL injection, XSS, etc.)

---

### 2. SCA (Software Composition Analysis)

**Tools:** Snyk, Dependabot, OWASP Dependency-Check

**Integration:**
```bash
# Dependabot webhook
POST /api/v1/webhooks/dependabot
{
  "alert": {
    "number": 42,
    "state": "open",
    "dependency": "lodash",
    "security_vulnerability": {
      "package": {"name": "lodash"},
      "severity": "moderate",
      "identifiers": [{"type": "CVE", "value": "CVE-2021-23337"}]
    }
  }
}
```

**Findings:** Vulnerable dependencies, outdated libraries

---

### 3. IaC (Infrastructure as Code)

**Tools:** Checkov, tfsec, Terrascan

**Integration:**
```bash
# Run Checkov on Terraform
checkov -d ./terraform --output json > checkov-results.json

# Send to AegisX
curl -X POST $AEGISX_URL/api/v1/ingest/iac \
  -H "Authorization: Bearer $AEGISX_KEY" \
  -d @checkov-results.json
```

**Findings:** Misconfigured cloud resources, insecure defaults

---

### 4. DAST (Dynamic Application Security Testing)

**Tools:** OWASP ZAP, Burp Suite

**Integration:**
```bash
# Run ZAP scan
zap-cli quick-scan --self-contained \
  https://staging.payment-api.company.com \
  -o zap-report.json

# Send to AegisX
curl -X POST $AEGISX_URL/api/v1/ingest/dast \
  -H "Authorization: Bearer $AEGISX_KEY" \
  -d @zap-report.json
```

**Findings:** Runtime vulnerabilities, configuration issues

---

## Metrics Collection & Observability

### Dashboard Queries

```python
# Security Posture by Service
GET /api/v1/services/{id}/posture
{
  "service_id": "payment-api",
  "findings": {
    "critical": 0,
    "high": 2,
    "medium": 5,
    "low": 12
  },
  "trend": {
    "7d": "+2",
    "30d": "-5"
  },
  "mttr_days": 3.2
}

# Organization-Wide Metrics
GET /api/v1/metrics/overview
{
  "total_findings": 1247,
  "open_critical": 3,
  "mttr_days": 8.5,
  "false_positive_rate": 0.12,
  "top_vulnerability_types": [
    {"type": "outdated_dependency", "count": 487},
    {"type": "sql_injection", "count": 34},
    {"type": "xss", "count": 28}
  ]
}
```

---

## System Evolution Over Time

### Week 1: High Noise

```
Findings ingested: 10,000
False positive rate: 40%
Engineer complaints: "Too many alerts!"
```

**AegisX learns:**
- Identifies noisy rules (low value findings)
- Learns organizational false positive patterns
- Adjusts risk weights based on feedback

### Week 12: Reduced Noise

```
Findings ingested: 8,500 (deduplicated)
False positive rate: 15%
Engineer feedback: "Alerts are actionable now"
MTTR: 14 days → 7 days
```

**Model improvements:**
- Auto-dismisses known false positives
- Better exploitability assessment
- Org-specific risk calibration

### Month 6: Predictive Intelligence

```
Findings ingested: 7,200
False positive rate: 8%
Proactive alerts: "This PR introduces SQL injection risk"
MTTR: 7 days → 3 days
```

**Advanced capabilities:**
- Pre-commit scanning integration
- Predictive risk modeling
- Automated remediation suggestions

---

## Key Outcomes

**For Security Teams:**
- 70% reduction in triage time (40h/week → 12h/week)
- Focus on high-impact work instead of noise
- Data-driven security posture reporting

**For Engineering Teams:**
- Clear, actionable findings (not overwhelming alerts)
- Remediation guidance reduces fix time
- Security findings feel helpful, not punitive

**For Leadership:**
- Measurable security improvements (MTTR, coverage)
- Audit trail for compliance
- Risk quantification for investment decisions

