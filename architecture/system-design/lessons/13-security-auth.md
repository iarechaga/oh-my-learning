---
id: system-design/13
subject: system-design
title: "Security: Authentication and Authorization"
slug: security-auth
status: drafted
mastery:
source: "System Design Guide for Software Professionals (Sinha & Chopra), Chapter 8"
prerequisites: []
created: 2026-06-30
updated: 2026-06-30
---

# Security: Authentication and Authorization

## TL;DR
Authentication verifies identity while authorization determines permissions. Secure system design relies on clear, decoupled validation mechanisms, using protocols like OAuth2, OpenID Connect, and mutual TLS to protect API endpoints and sensitive resources. Managing secrets securely and applying strong models like RBAC and ABAC protects systems from unauthorized access.

## The idea
Why do we separate authentication from authorization? Security in distributed systems is about establishing trust across untrusted networks. When a user requests data, the system needs to resolve two fundamental questions. First, who is making the request? Second, is that actor allowed to perform the specific action?

In monolithic systems, a local database query or an in-memory session check handles both. But in distributed systems, service-to-service requests cross physical and network boundaries. Relying on centralized checks on every request causes performance bottlenecks. Therefore, we use patterns that allow decentralized validation without compromising trust.

Understanding these patterns is essential. If we mix authentication and authorization, or use the wrong mechanisms, our services become vulnerable to lateral movement, token theft, and privilege escalation. We must design security boundaries that scale with the architecture.

## How it works

### Authentication vs Authorization
Authentication (AuthN) is the process of proving identity. It answers "who are you?" by validating credentials such as passwords, certificates, or tokens.
Authorization (AuthZ) is the process of enforcing permissions. It answers "what are you allowed to do?" by mapping the authenticated identity to specific resources and actions.

The table below contrasts these two phases:

| Dimension | Authentication (AuthN) | Authorization (AuthZ) |
| --- | --- | --- |
| Primary Question | Who are you? | What can you do? |
| Timing in Request | Happens first. | Happens second (after identity is known). |
| Data Checked | Passwords, OTPs, certificates, biometrics. | Roles, permissions, context, user attributes. |
| Typical Outcome | Identity context (user ID, tenant ID, scopes). | Access granted or denied (HTTP 403 Forbidden). |
| Example Protocol | OpenID Connect (OIDC), SAML, mTLS. | RBAC, ABAC, OAuth2 scopes. |

### Session-Based vs Token-Based Authentication
In session-based authentication, the server stores session state in memory or a database (like Redis) and returns a unique session ID to the client via a secure cookie. On subsequent requests, the client sends this cookie, and the server queries the store to retrieve user data.

In token-based authentication, the identity provider issues a self-contained token (like a JWT) to the client after a successful login. The client attaches this token to the Authorization header of every request. The resource server validates the token cryptographically without querying a central database.

The table below compares these two approaches:

| Feature | Session-Based (Stateful) | Token-Based (Stateless) |
| --- | --- | --- |
| State Location | Server-side (memory, database, or cache). | Client-side (stored in memory or storage). |
| Scalability | Challenging; requires distributed caches for sticky sessions. | High; servers validate cryptographically in a stateless way. |
| Revocation | Immediate; delete session from server-side store. | Complex; tokens are valid until expiry unless blacklisted. |
| CSRF Risk | High; cookies are sent automatically by browsers. | Low; Authorization headers are not sent automatically. |
| Network Overhead | Low; session ID is a small string. | High; JWT payload and signature increase header size. |

### JSON Web Tokens (JWT) in Depth
A JWT is a JSON object represented as three base64url-encoded parts separated by dots: `Header.Payload.Signature`.

1. **Header**: Contains metadata about the token, such as the algorithm used for signing (e.g., RS256 or HS256) and the token type (JWT).
2. **Payload**: Contains claims (statements about the user and metadata), such as issuer (`iss`), subject (`sub`), expiration time (`exp`), and audience (`aud`).
3. **Signature**: Formed by signing the encoded header and payload with a secret key (symmetric HS256) or a private key (asymmetric RS256).

Asymmetric signing (like RS256) is ideal for microservices. Only the auth server has the private key to issue tokens, while all downstream services use the public key to validate them. This maps directly to DDIA Chapter 9 concepts on consensus and centralized coordinators; the auth server acts as a single writer, while resource servers are read-only replicas of the public key.

**Revocation Challenges**: Because JWTs are stateless, revoking them before their expiration time is difficult. If a user logs out or is deactivated, their token remains valid until the `exp` claim passes.
Defenses against this include:
- **Short Expiry Times**: Set token lifespan to 5 to 15 minutes, paired with a stateful refresh token to request new JWTs.
- **Revocation Lists (Blacklisting)**: Store revoked token IDs (`jti`) in a high-speed cache like Redis with a Time-To-Live (TTL) equal to the remaining token lifespan. Services check this cache during validation.
- **Database Synchronization**: Downstream services query user status periodically or listen to deactivation events via a message broker (a concept discussed in DDIA Chapter 11 on Stream Processing).

### OAuth2 and OpenID Connect
OAuth2 is an authorization framework, not an authentication protocol. It lets a third-party application obtain limited access to an HTTP service on behalf of a resource owner.

OpenID Connect (OIDC) is an identity layer built on top of OAuth2. It introduces the ID token (a JWT containing user profile info) alongside the OAuth2 access token to provide standardized authentication.

Key grant types in OAuth2:
- **Authorization Code Grant (with PKCE)**: Used for web and mobile apps. The client obtains an authorization code via a browser redirect, then exchanges this code for tokens. PKCE (Proof Key for Code Exchange) protects public clients from authorization code interception attacks.
- **Client Credentials Grant**: Used for machine-to-machine integration. The service requests an access token directly using its client ID and secret.

### API Keys and Mutual TLS (mTLS)
- **API Keys**: Simple strings passed in headers. Easy to use but vulnerable. They lack cryptographic signatures and expiration. If intercepted, an attacker can use them indefinitely until they are rotated.
- **Mutual TLS (mTLS)**: Used for service-to-service communication. Unlike standard TLS, where only the client validates the server certificate, mTLS requires both client and server to present and validate certificates. This establishes cryptographic identity at the transport layer, preventing man-in-the-middle attacks and providing strong authentication.

### TLS Basics: Handshake and Certificates
Transport Layer Security (TLS) secures communication over network links. It combines asymmetric cryptography for the initial handshake and symmetric cryptography for fast data encryption.

1. **The Handshake**:
   - **Client Hello**: Client sends supported TLS versions, cipher suites, and a random number.
   - **Server Hello & Certificate**: Server sends its selected cipher suite, another random number, and its digital certificate.
   - **Verification**: The client validates the server certificate against trusted Certificate Authorities (CAs).
   - **Key Exchange**: The client encrypts a pre-master secret using the server's public key (or uses Diffie-Hellman) to establish a shared session key.
   - **Symmetric Encryption**: Both parties use the shared session key to encrypt all subsequent communication.

2. **Certificates**: Digital files binding a public key to an identity, signed by a trusted CA. If the signature is valid and the domain matches, trust is established.

### Authorization Models: RBAC vs ABAC
- **Role-Based Access Control (RBAC)**: Groups permissions into roles (e.g., `Admin`, `Editor`, `Viewer`), then assigns roles to users. It is simple but inflexible for fine-grained scenarios.
- **Attribute-Based Access Control (ABAC)**: Evaluates policies based on attributes of the user (e.g., department, location), resource (e.g., classification, owner), and environment (e.g., time of day, IP address). It is highly flexible but more complex to implement and evaluate.

### API Security Threats and Defenses
1. **Broken Object Level Authorization (BOLA / IDOR)**: Occurs when an API endpoint exposes an identifier (e.g., `/api/orders/501`) and does not verify if the logged-in user owns that resource.
   - *Defense*: Verify resource ownership on every database query. Use unguessable UUIDs instead of sequential integers.
2. **Injection (SQLi, NoSQLi)**: Occurs when untrusted input is passed directly to an interpreter without sanitization.
   - *Defense*: Use parameterized queries, prepared statements, and strict input validation.
3. **Excessive Data Exposure**: Occurs when an API returns a full database record to the client, relying on the frontend to filter the UI.
   - *Defense*: Define strict Data Transfer Objects (DTOs) and serialize only the required fields.

### Secrets Management
Hardcoding database credentials, API keys, or private signing keys in source code is a major security risk. Secrets management systems (like HashiCorp Vault, AWS Secrets Manager, or Google Secret Manager) solve this:
- **Centralization**: Secrets are stored in an encrypted database, separated from code.
- **Dynamic Secrets**: The system generates short-lived credentials on demand and revokes them automatically.
- **Audit Logging**: Every access request is logged, enabling tracking of who accessed which secret and when.
- **Rotation**: Automated secret rotation reduces the window of vulnerability if a credential is leaked.

---

### Worked Example 1: OAuth2 Authorization-Code Flow Sequence

The diagram below shows how an application securely obtains an access token on behalf of a user using PKCE:

```
+--------+             +--------------+             +---------------+             +---------------+
|  User  |             | Client (App) |             | Auth Server   |             |Resource Server|
+--------+             +--------------+             +---------------+             +---------------+
    |                         |                             |                             |
    | 1. Click "Login"        |                             |                             |
    |------------------------>|                             |                             |
    |                         | 2. Redirect to Auth Page    |                             |
    |                         |    (with code_challenge)    |                             |
    |                         |---------------------------->|                             |
    | 3. Authenticate & Grant |                             |                             |
    |<======================================================|                             |
    |                         |                             |                             |
    |                         | 4. Redirect with Auth Code  |                             |
    |                         |<----------------------------|                             |
    |                         |                             |                             |
    |                         | 5. POST /token              |                             |
    |                         |    (code + code_verifier)   |                             |
    |                         |---------------------------->|                             |
    |                         |                             |                             |
    |                         | 6. Validate & Return Tokens |                             |
    |                         |<----------------------------|                             |
    |                         |    (Access + ID Token)      |                             |
    |                         |                             |                             |
    |                         | 7. Request Resource         |                             |
    |                         |    (with Access Token)      |                             |
    |                         |---------------------------------------------------------->|
    |                         |                             |                             |
    |                         | 8. Validate cryptographically & Return Data               |
    |                         |<----------------------------------------------------------|
```

1. **Initiation**: The user clicks login in the client application.
2. **Challenge Creation**: The client generates a random string (`code_verifier`), hashes it with SHA-256 (`code_challenge`), and redirects the browser to the authorization server with the challenge.
3. **Consent**: The user logs in at the authorization server and consents to the requested permissions.
4. **Auth Code**: The authorization server redirects back to the client application redirect URI with a short-lived authorization code.
5. **Token Exchange**: The client sends the authorization code and the raw `code_verifier` to the token endpoint of the authorization server.
6. **Verification**: The authorization server hashes the verifier and compares it with the stored challenge. If they match, it issues an access token and an ID token.
7. **Resource Request**: The client requests secure data from the API gateway or resource server.
8. **Stateless Access**: The resource server validates the signature and returns the requested data.

---

### Worked Example 2: Distributed JWT Verification Logic

In this scenario, we have a gateway that forwards requests to downstream microservices. Downstream services do not call the auth server. They validate the signature locally.

```
+------------------+         +------------------+         +------------------+
|      Client      | ------> |   API Gateway    | ------> | Payment Service  |
+------------------+         +------------------+         +------------------+
                             (Fetches JWKS once,          (Parses claims from
                              adds context headers)        headers locally)
```

The validation algorithm executed by a resource service on receiving a request:

1. **Extraction**: Retrieve the token from the `Authorization` header:
   `Authorization: Bearer <JWT_STRING>`
2. **Parsing**: Split the token by `.` into Header, Payload, and Signature. Decode the Header to find the key ID (`kid`) and signing algorithm (`alg`).
3. **Public Key Retrieval**: Look up the public key for `kid` in the local cache. If missing, fetch the JSON Web Key Set (JWKS) from the authorization server's well-known endpoint, cache it, and select the matching key.
4. **Signature Validation**: Use the public key and the algorithm specified (e.g., RS256) to verify the signature against the decoded Header and Payload bytes. If the signature is invalid, reject with HTTP 401.
5. **Claims Verification**:
   - Check `exp` (expiration): Assert that current system time is less than `exp`.
   - Check `nbf` (not before): Assert that current system time is greater than `nbf`.
   - Check `iss` (issuer) and `aud` (audience): Assert that they match expected service configuration values.
6. **Context Propagation**: Once verified, convert the token payload into local user context, such as extracting the user ID or role, and proceed with processing.

---

### Worked Example 3: RBAC vs ABAC in a Multi-Tenant Document System

Consider a medical records application. We must manage access to patients' medical history.

**Scenario**: A user wants to edit a document with ID `doc_902`.

- **RBAC Implementation**:
  1. The database maps user `Dr. Alice` to the role `Doctor`.
  2. The system has a policy: "Users with role `Doctor` have permission `edit_records`."
  3. Since `Dr. Alice` has the `Doctor` role, she is allowed to edit any document that requires `edit_records`.
  4. *Limitation*: Under pure RBAC, `Dr. Alice` can edit records for patients she does not treat, or records owned by a different clinic, unless custom backend checks are added.

- **ABAC Implementation**:
  1. The system retrieves attributes for the user, resource, and environment:
     - **User Attributes**: `{ id: "dr_alice", role: "Doctor", department: "Oncology", clinic_id: "clinic_east" }`
     - **Resource Attributes**: `{ id: "doc_902", patient_id: "patient_bob", primary_doctor: "dr_alice", clinic_id: "clinic_east", status: "active" }`
     - **Environment Attributes**: `{ current_time: "14:30:00", request_ip: "10.0.4.15" (internal network) }`
  2. The policy engine evaluates a structured rule:
     ```json
     allow if:
       user.role == "Doctor" AND
       user.clinic_id == resource.clinic_id AND
       (user.id == resource.primary_doctor OR resource.status == "emergency") AND
       environment.request_ip.starts_with("10.0.")
     ```
  3. The engine evaluates this to `true`. Access is granted. If Dr. Alice tries to access a record at `clinic_west`, or if she is not the primary doctor, access is denied unless an emergency status applies.

This shows how ABAC provides contextual security where RBAC falls short.

---

## Pros
- **Decoupled Identity Management**: Using modern identity protocols lets engineering teams delegate login flows to dedicated identity providers, keeping resource services lightweight.
- **Improved Performance**: Token-based authentication eliminates database lookups on every request, reducing API latency and database load across the fleet.
- **Cryptographic Trust**: Mutual TLS and public-key signatures provide mathematical proof of identity, protecting against packet capture and spoofing.
- **Precise Access Policies**: ABAC models allow systems to enforce dynamic, contextual security rules, minimizing risk in highly regulated environments.

## Cons
- **Key Rotation Complexity**: Managing public-private key pairs for token signing and certificates for mTLS requires automated PKI pipelines, which are hard to build and maintain.
- **Token Revocation Lag**: Stateless tokens are hard to invalidate immediately, exposing a temporary window of vulnerability if a client credential is stolen.
- **Increased Header Payload**: JWTs containing rich attributes increase HTTP header size, raising network overhead for high-frequency microservice calls.
- **Policy Evaluation Latency**: Evaluating complex ABAC policies on every API request can introduce processing overhead compared to simple role checks.

## Alternatives
- **Stateful Gateway with Stateless Services**: The API gateway validates a stateful session ID against a Redis cache, then translates it into a short-lived stateless JWT for internal services. This combines immediate session revocation with fast internal token validation.
- **Centralized Authorization Service**: Instead of evaluating RBAC or ABAC locally, services call a high-performance authorization service (e.g., Google Zanzibar or Open Policy Agent) via gRPC. This keeps policy logic consistent across different codebases.
- **Opaque Access Tokens**: The authorization server issues random, unique strings (opaque tokens). The resource server must send these tokens back to the auth server to validate them (introspection). This is highly secure but slower due to network calls.

## When to use it
- **SaaS Platforms**: Use OIDC and token-based OAuth2 to secure multi-tenant APIs, permitting seamless integration with third-party developer apps.
- **Highly Regulated Environments**: Use ABAC and mutual TLS in healthcare or finance to meet strict compliance requirements regarding data access and network isolation.
- **Service-to-Service Architecture**: Use mTLS for zero-trust microservice networks, ensuring that every service validates both the identity and transport layer of its peers.

## When NOT to use it
- **Monolithic Internal Applications**: Don't use OAuth2 or complex ABAC for small, single-database apps. A simple session cookie with basic RBAC in the database is easier to maintain and secure.
- **Extremely High-Frequency, Low-Latency Internal APIs**: Avoid passing large, complex JWTs on every internal call. Use lightweight opaque tokens, or offload authentication to a service mesh (such as Istio) that handles mTLS transparently.

## Key takeaways / mental model
Think of authentication as a passport check: it verifies your identity and country of origin. Think of authorization as the badge you wear inside a high-security facility: it determines which rooms you can enter based on your clearance level. 

Do not trust network boundaries. In modern systems, security must be enforced at both the transport layer (using mTLS) and the application layer (using cryptographically signed tokens). Keep tokens short-lived, automate key rotation, and enforce authorization checks directly on the database query level to prevent access leaks.

---

## Self-check questions
1. Explain why an application using pure RBAC is highly vulnerable to Broken Object Level Authorization (BOLA). How does ABAC resolve this?
2. A client has stolen a stateless JWT that is valid for another 4 hours. What specific architecture patterns can you implement to mitigate or prevent this risk?
3. Describe the exact differences between an OAuth2 Access Token and an OIDC ID Token. Why should you never use an Access Token for authentication?
4. Walk through the TLS handshake. At what point does symmetric encryption begin, and how do the client and server agree on the shared key?
5. Why is PKCE critical for the OAuth2 Authorization Code flow on public clients like single-page applications or mobile apps?

## References
- *System Design Guide for Software Professionals* (Sinha & Chopra), Chapter 8
- *Designing Data-Intensive Applications* (Martin Kleppmann), Chapter 9 (Consistency and Consensus) and Chapter 11 (Stream Processing)
