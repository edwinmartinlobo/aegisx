# Threat Model

## AegisX Security Analysis

### 1. System Overview
AegisX is a planning API that accepts user input and generates structured task plans. The system stores data in a local SQLite database and exposes HTTP endpoints.

### 2. Assets
1. **User Data**: Planning context, goals, and generated tasks
2. **Database**: SQLite database containing historical plans
3. **API Service**: FastAPI application and business logic
4. **Prompt Templates**: AI prompt configurations

### 3. Trust Boundaries
```
┌─────────────────────────────────────────┐
│         Untrusted Zone                  │
│  - API Clients                          │
│  - User Input                           │
└──────────────┬──────────────────────────┘
               │
        ┌──────▼───────┐
        │  API Layer   │
        │  (FastAPI)   │
        └──────┬───────┘
               │
┌──────────────▼──────────────────────────┐
│        Trusted Zone                     │
│  - Business Logic                       │
│  - Database                             │
│  - File System                          │
└─────────────────────────────────────────┘
```

### 4. Threat Categories (STRIDE)

#### 4.1 Spoofing
**Threat**: Attackers impersonating legitimate users
- **Current Risk**: LOW (no authentication in v1.0)
- **Mitigation**:
  - Add API key authentication for production
  - Implement rate limiting per client
- **Future**: OAuth 2.0 / JWT authentication

#### 4.2 Tampering
**Threat**: Malicious modification of data in transit or at rest
- **Current Risk**: MEDIUM
- **Mitigations**:
  - Use HTTPS/TLS for all API communication
  - Input validation via Pydantic models
  - SQL parameterization (SQLite library handles this)
- **Recommendations**:
  - Deploy behind HTTPS reverse proxy
  - Implement request signing

#### 4.3 Repudiation
**Threat**: Users denying actions they performed
- **Current Risk**: LOW
- **Mitigations**:
  - Structured logging of all API requests
  - Timestamp all database records
- **Future**: Audit logging with user attribution

#### 4.4 Information Disclosure
**Threat**: Unauthorized access to sensitive data
- **Current Risk**: MEDIUM
- **Mitigations**:
  - No sensitive data in error responses
  - Database file permissions (600)
  - No API keys or secrets in code
- **Recommendations**:
  - Encrypt database at rest
  - Implement field-level encryption for sensitive data
  - Add authentication before production deployment

#### 4.5 Denial of Service
**Threat**: Service unavailability through resource exhaustion
- **Current Risk**: MEDIUM
- **Mitigations**:
  - Request size limits (Pydantic field constraints)
  - Database query timeouts
- **Recommendations**:
  - Implement rate limiting (e.g., 100 req/min per IP)
  - Add request throttling
  - Deploy with resource limits (Docker/K8s)
  - Add health check monitoring

#### 4.6 Elevation of Privilege
**Threat**: Attackers gaining unauthorized access
- **Current Risk**: LOW (no privilege levels in v1.0)
- **Mitigations**:
  - No system-level operations
  - Principle of least privilege for file access
- **Future**: Role-based access control (RBAC)

### 5. Attack Vectors

#### 5.1 Input Validation Attacks
- **SQL Injection**: ✅ Mitigated (parameterized queries)
- **XSS**: ⚠️ N/A (no HTML rendering, but validate output)
- **Command Injection**: ✅ Mitigated (no shell commands)
- **Path Traversal**: ✅ Mitigated (fixed paths, no user-supplied paths)

#### 5.2 Business Logic Attacks
- **Resource Exhaustion**: ⚠️ Moderate risk (add rate limiting)
- **Mass Assignment**: ✅ Mitigated (explicit Pydantic models)
- **Logic Bombs**: ✅ Mitigated (code review required)

#### 5.3 Infrastructure Attacks
- **MITM**: ⚠️ Requires HTTPS deployment
- **DDoS**: ⚠️ Requires upstream protection
- **Brute Force**: ⚠️ Add rate limiting

### 6. Security Controls

#### Implemented
- ✅ Input validation (Pydantic)
- ✅ Parameterized SQL queries
- ✅ Error handling (no stack traces to clients)
- ✅ Structured logging
- ✅ CORS configuration
- ✅ Request size limits

#### Recommended for Production
- ⚠️ Authentication (API keys or OAuth)
- ⚠️ Rate limiting
- ⚠️ HTTPS/TLS termination
- ⚠️ Database encryption at rest
- ⚠️ Secret management (no .env in version control)
- ⚠️ Security headers (CSP, HSTS, etc.)
- ⚠️ WAF (Web Application Firewall)

### 7. Security Checklist

#### Pre-Production
- [ ] Enable HTTPS/TLS
- [ ] Implement authentication
- [ ] Add rate limiting
- [ ] Set up monitoring and alerting
- [ ] Security scan (SAST/DAST)
- [ ] Dependency vulnerability scan
- [ ] Set secure file permissions (database: 600)
- [ ] Remove debug mode
- [ ] Configure CORS properly (no wildcards)
- [ ] Set up backup and recovery

#### Ongoing
- [ ] Regular dependency updates
- [ ] Security patch monitoring
- [ ] Log review and monitoring
- [ ] Penetration testing (annual)
- [ ] Incident response plan

### 8. Data Privacy

#### Personal Data Handling
- User context and goals may contain personal information
- No PII validation in v1.0
- **Recommendation**: Add data classification and handling policies

#### Compliance Considerations
- GDPR: Right to deletion, data export
- CCPA: Privacy policy, opt-out mechanisms
- **Action**: Implement data retention and deletion policies

### 9. Incident Response

#### Detection
- Monitor error rates in logs
- Set up alerts for unusual patterns
- Health check monitoring

#### Response
1. Isolate affected systems
2. Analyze logs for root cause
3. Apply fixes and patches
4. Document incident
5. Post-mortem and improvements

### 10. Risk Summary

| Risk Category | Severity | Likelihood | Priority |
|---------------|----------|------------|----------|
| No Authentication | HIGH | HIGH | P0 |
| No Rate Limiting | MEDIUM | MEDIUM | P1 |
| No HTTPS Enforcement | HIGH | MEDIUM | P0 |
| SQL Injection | LOW | LOW | P3 |
| DoS Attacks | MEDIUM | MEDIUM | P1 |
| Data Exposure | MEDIUM | LOW | P2 |

### 11. Security Roadmap

#### Phase 1 (MVP)
- Add API key authentication
- Implement rate limiting
- Deploy with HTTPS

#### Phase 2 (Production)
- OAuth 2.0 integration
- Database encryption
- WAF deployment
- Security monitoring

#### Phase 3 (Enterprise)
- SOC 2 compliance
- Advanced threat detection
- Zero-trust architecture
