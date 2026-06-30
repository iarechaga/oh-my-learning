---
id: system-design/12
subject: system-design
title: API Design and Communication
slug: api-design-communication
status: drafted
mastery:
source: System Design Guide for Software Professionals (Sinha & Chopra), Chapter 8
prerequisites: [ddia/06]
created: 2026-06-30
updated: 2026-06-30
---

# API Design and Communication

## TL;DR
Designing service APIs requires selecting the right communication protocol for the use case: REST for public-facing resource-based APIs, gRPC for high-performance internal microservices, and GraphQL for client-driven complex data graph queries. Robust APIs must handle distributed system realities like unreliable networks and schema evolution by implementing idempotency keys, cursor-based pagination, and backward-compatible schemas.

## The idea
In a distributed system, services are isolated islands. They cannot share memory or direct access to databases, so they must communicate over a network using clear, structured interfaces called APIs. An API acts as a strict contract between a service provider and its consumers.

If an API contract is poorly designed, it causes immediate friction. Teams become blocked by breaking changes, system performance drops due to excessive network overhead, and data becomes inconsistent because clients cannot safely retry failed requests. Designing good APIs means thinking deeply about how systems evolve over time. Since you cannot force all clients to upgrade at the exact same moment, your API design must accommodate change while maintaining service availability and operational simplicity.

## How it works
Different communication paradigms solve different problems in system design.

### REST (Representational State Transfer)
REST is an architectural style centered on resources, which are identified by URLs. REST uses standard HTTP verbs to perform actions on these resources:
- `GET`: Retrieve a resource. This must be safe and idempotent.
- `POST`: Create a new resource. This is neither safe nor idempotent.
- `PUT`: Replace an existing resource, or create it if it doesn't exist. This is idempotent.
- `DELETE`: Remove a resource. This is idempotent.
- `PATCH`: Partially modify a resource. This is not guaranteed to be idempotent.

REST enforces statelessness: each request must contain all the information necessary to process it. No client context is stored on the server between requests. Statelessness ensures that any application server instance can handle any incoming request. This facilitates horizontal scaling by simply placing a load balancer in front of a pool of stateless servers.

Furthermore, REST takes advantage of standard HTTP caching. By returning headers like `Cache-Control`, `ETag`, or `Last-Modified`, servers can instruct browsers or reverse proxies (like Cloudflare or Varnish) to cache responses locally. This drastically reduces the load on backend servers for frequently read data.
HATEOAS (Hypermedia As Only the Engine of Application State) is a REST constraint where the server returns links to other related actions in the response, allowing clients to navigate the API dynamically, though it is rarely implemented in practice.

### gRPC (Google Remote Procedure Call)
gRPC is a high-performance, open-source framework developed by Google. It operates on a schema-first approach, using Protocol Buffers (Protobuf) as its interface definition language and serialization format. This connects directly to schema evolution (DDIA Concept 06: Encoding and Evolution).

Key mechanisms:
- **HTTP/2 Transport**: Unlike REST, which typically uses HTTP/1.1, gRPC uses HTTP/2. This enables multiplexing (sending multiple requests and responses over a single TCP connection), binary framing (sending data as binary instead of text), and header compression.
- **Protocol Buffers**: Messages are encoded into a compact, binary format, making serialization and deserialization extremely fast compared to JSON. While JSON repeats field keys in every payload and processes them as raw strings, Protobuf strips keys completely, encoding fields as sequence tags. This reduces the size of payloads by up to 80 percent and dramatically speeds up parsing.
- **Streaming**: gRPC natively supports unary calls (single request, single response), client-streaming, server-streaming, and bidirectional streaming.
- **Schema Evolution**: Protobuf handles field additions and deletions smoothly. Each field has a unique tag number. As long as developers don't change existing tag numbers, old and new services can read each other's messages safely.

### GraphQL
GraphQL is a query language for APIs developed by Facebook. It shifts control from the server to the client. Instead of hitting multiple endpoints, a client sends a single POST request containing a query that describes exactly what data it needs.

Key properties:
- **Solves Over-fetching and Under-fetching**: Over-fetching occurs when a REST endpoint returns more fields than the client needs, wasting bandwidth. Under-fetching occurs when an endpoint doesn't return enough data, forcing the client to make multiple sequential network calls. GraphQL retrieves exactly the requested fields in a single round-trip.
- **The Schema and Types**: GraphQL APIs are defined by a strict schema written in Schema Definition Language (SDL). This schema contains Object Types, Fields, and Operations like Queries (reads), Mutations (writes), and Subscriptions (real-time stream connections).
- **Mutations and Schema Definition**: In addition to queries, GraphQL supports Mutations for writing or updating data on the server. Mutations are defined similarly to queries but are executed sequentially by the server to prevent race conditions during updates. The schema clearly defines mutations, their parameters, and their return types, providing a solid, type-safe API contract.
- **Resolvers**: Additionally, GraphQL resolver functions are executed by the server to fetch the data for each requested field. A resolver can fetch from a database, a cache, another HTTP service, or a gRPC microservice, making GraphQL an excellent API gateway pattern.
- **The N+1 Query Risk**: Because clients can request arbitrary nested data, a naive GraphQL resolver might query the database once for a list of items, and then query the database again for each individual item's nested relations. This is called the N+1 problem. Developers solve this using batching and caching patterns, such as Facebook's DataLoader utility, which aggregates individual queries into a single batch database call.

### Idempotency Keys for Safe Retries
In distributed systems, networks drop requests. If a client sends a payment request and gets a network timeout, they don't know if the server processed the payment before the connection broke. Retrying the request blindly can result in duplicate charges.

To solve this, clients must include a unique Idempotency Key (usually a UUID) in the request header.
1. The server receives the request and checks Redis or its database to see if the key has been processed.
2. If the key exists, the server returns the cached response of the previous run without executing the transaction again.
3. If the key does not exist, the server acquires a distributed lock on the key.
4. If a duplicate request arrives while the first request is still in-progress, the server rejects it with a `409 Conflict` status or blocks until the lock is released, protecting the database from concurrent processing. Once processing completes, the server stores the final response in Redis with a TTL (e.g., 24 hours), releases the lock, and returns the response to the client.

### Pagination: Offset-Based vs. Cursor-Based
When returning large datasets, APIs must paginate. Two main approaches exist:
- **Offset-Based Pagination**: Uses `limit` and `offset` query parameters. In SQL, this translates to `LIMIT 10 OFFSET 50`.
  - *Pros*: Simple to implement; allows users to jump directly to page 10.
  - *Cons*: Poor performance on deep pages because the database must read and discard all previous rows. It is also prone to skipped or duplicated items if rows are inserted or deleted while a user is paginating.
- **Cursor-Based Pagination**: Uses a unique, sequential pointer (a cursor, like an encoded ID or timestamp) to fetch the next batch.
  - *Pros*: Constant time database lookups using `WHERE id > cursor LIMIT 10`. It is immune to insertion anomalies, making it ideal for infinite scroll feeds.
  - *Cons*: Doesn't allow jumping to arbitrary pages; more complex to implement.

### API Versioning
To evolve APIs without breaking existing integrations, you must version them:
- **URL Versioning**: `/api/v1/orders` (simple and clear, but breaks the concept of permanent URLs).
- **Header Versioning**: `Accept: application/vnd.company.v1+json` (keeps URLs clean, but harder to test in browsers).
- **Query Parameter Versioning**: `/orders?version=1` (less common, but highly flexible).

Regardless of the strategy chosen (URLs, headers, or query parameters), versioning must be handled defensively. Breaking changes should be kept to a minimum, and older API versions must be deprecated gracefully. Providing deprecation headers like `Sunset` and `Deprecation` informs clients of the timeline before older versions are permanently shut down.

### Rate-Limiting and Error Conventions
APIs must protect themselves from abuse using rate-limiting. When a client exceeds their limit, the server should respond with HTTP Status `429 Too Many Requests` and include standard headers:
- `X-RateLimit-Limit`: The maximum number of requests allowed in a window.
- `X-RateLimit-Remaining`: The remaining requests in the current window.
- `Retry-After`: The number of seconds to wait before retrying.

Consistent error handling is crucial. Error payloads should have a predictable structure, combining a machine-readable error code with a human-readable explanation.

---

### Comparison: REST vs. gRPC vs. GraphQL
| Feature | REST | gRPC | GraphQL |
| :--- | :--- | :--- | :--- |
| Protocol / Transport | HTTP/1.1 or HTTP/2 | HTTP/2 | Typically HTTP/1.1 |
| Payload Format | JSON or XML | Protocol Buffers (Binary) | JSON |
| Contract Definition | OpenAPI / Swagger (Optional) | Proto Schema (Mandatory) | GraphQL Schema (Mandatory) |
| Client Control | Low (Fixed endpoints) | Low (Fixed procedures) | High (Client-specified query) |
| Streaming Support | Limited (SSE) | Native bidirectional | Limited (Subscriptions) |

---

### Worked Example 1: REST Order Resource Design
We design a REST endpoint to manage an order resource, illustrating standard verbs and HTTP status codes.

```
Client                             REST Server (API Gateway)
  |                                            |
  |  POST /v1/orders                           |
  |  Idempotency-Key: id-123                   |
  |  Payload: {"item_id": 45}                  |
  |------------------------------------------->|
  |                                            |  Processes transaction...
  |  HTTP 201 Created                          |  Saves resource...
  |  Location: /v1/orders/991                  |
  |<-------------------------------------------|
  |                                            |
  |  GET /v1/orders/991                        |
  |------------------------------------------->|
  |  HTTP 200 OK                               |
  |  Payload: {"id": 991, "status": "pending"} |
  |<-------------------------------------------|
```

Endpoint structure:
- `POST /v1/orders` : Creates an order. Returns `201 Created` with a `Location` header pointing to the new resource.
- `GET /v1/orders/{id}` : Retrieves an order. Returns `200 OK` if found, or `404 Not Found` if missing.
- `PUT /v1/orders/{id}` : Replaces an order completely. Returns `200 OK` or `204 No Content`.
- `DELETE /v1/orders/{id}` : Cancels/deletes an order. Returns `200 OK` or `204 No Content`.

### Worked Example 2: Same Operation as a gRPC Protobuf Schema
This Protocol Buffers schema defines the same order creation contract. Notice the schema-first nature and the use of field tags for backward compatibility.

```protobuf
syntax = "proto3";

package billing;

service OrderService {
  rpc CreateOrder (CreateOrderRequest) returns (CreateOrderResponse);
  rpc GetOrder (GetOrderRequest) returns (GetOrderResponse);
}

message CreateOrderRequest {
  string idempotency_key = 1;
  string customer_id = 2;
  repeated OrderItem items = 3;
}

message OrderItem {
  string sku = 1;
  int32 quantity = 2;
  double price_cents = 3;
}

message CreateOrderResponse {
  string order_id = 1;
  string status = 2;
  int64 created_at = 3;
}

message GetOrderRequest {
  string order_id = 1;
}

message GetOrderResponse {
  string order_id = 1;
  string status = 2;
  repeated OrderItem items = 3;
}
```

How this schema evolves:
If we need to add a shipping address in the future, we simply append:
`string shipping_address = 4;`
to the `CreateOrderRequest`. Old services that receive this new message will ignore field tag 4, and new services will read it. This is backward-compatible schema evolution.

### Worked Example 3: GraphQL Query to Avoid Over-Fetching
In our e-commerce dashboard, we only want to display the user's name and the IDs of their active orders. A REST endpoint would return a massive JSON file with profile details, transaction history, and address blocks. GraphQL lets us request exactly what we need.

Query:
```graphql
query GetDashboardInfo($userId: ID!) {
  user(id: $userId) {
    name
    orders(status: "active") {
      id
      totalPrice
    }
  }
}
```

Response (JSON format):
```json
{
  "data": {
    "user": {
      "name": "Jane Doe",
      "orders": [
        {
          "id": "ORD-9912",
          "totalPrice": 150.00
        }
      ]
    }
  }
}
```

The payload size is minimized, saving battery, bandwidth, and processing power on mobile clients.

## Pros
- **Decoupled Development**: Teams can work on frontend and backend services in parallel once they agree on the API contract.
- **Enforced Security Boundaries**: Standardizing communication through APIs makes it easier to enforce rate-limiting, authentication, and logging at the API Gateway.
- **Technology Agnostic**: Services written in Python can call gRPC services written in Go or REST services in Node.js, allowing teams to pick the best language for the task.
- **Optimized Bandwidth**: Frameworks like gRPC compress headers and use binary payloads to drastically reduce payload sizes over the network.
- **Flexible Data Aggregation**: Technologies like GraphQL allow client developers to stitch together multiple backends into a single clean query, reducing front-end complexity.

## Cons
- **Contract Rigidness**: Changing a published contract requires deprecation periods, backward-compatible designs, and parallel version maintenance, slowing down changes.
- **Network Overhead**: Moving from single-process calls to network-based API calls introduces latency, serialization costs, and network failure modes.
- **Performance Risks**: Complex GraphQL schemas make it easy for clients to write terrible queries that cause severe database load (N+1 queries).
- **Debugging Difficulty**: When an RPC call fails, finding the root cause across nested microservice calls requires trace logs and diagnostic correlation.
- **Schema Management Overhead**: Maintaining clean OpenAPI specs, Protobuf files, or GraphQL schemas requires build pipelines and contract testing tools.

## Alternatives
- **SOAP (Simple Object Access Protocol)**: An XML-based messaging protocol. Pick this only when integrating with legacy enterprise systems that require strict XML security and built-in transaction protocols.
- **tRPC**: A framework that lets you build strongly typed APIs between TypeScript backends and frontends without schemas. Pick this for small or mid-sized pure TypeScript monorepos to move fast without code generation overhead.
- **WebSockets / Server-Sent Events (SSE)**: Persistent connections for real-time bidirectional messaging. Pick this when building chat systems, live dashboards, or collaborative editors that require push updates instead of request-response polling.
- **Database Sharing**: Letting multiple services write to the same database. Pick this only for simple applications or during rapid prototyping, as it breaks encapsulation and prevents independent scaling.

## When to use it
- **Public-facing integrations**: Use REST because it is highly compatible, widely understood, and easy for third-party developers to adopt.
- **Internal microservice communication**: Use gRPC for its low latency, high throughput, and strict schema contracts.
- **Complex frontend dashboards**: Use GraphQL when building mobile or web apps that display diverse data blocks from multiple microservices in a single view.

## When NOT to use it
- **Within a single process**: Don't use network-based APIs like HTTP or gRPC between components in a monolith. Use local function calls instead to avoid network and serialization overhead.
- **For continuous high-frequency real-time updates**: Avoid request-response REST or GraphQL for live multiplayer gaming or real-time trading. Use WebSockets or dedicated TCP connections.
- **Bulk data replication**: Don't use REST or GraphQL to transfer gigabytes of database records. Use batch processing, database dumps, or stream processing frameworks instead.

## Key takeaways / mental model
An API is a binding legal contract. Once published, you cannot change it without coordinating with your clients.
REST uses standard HTTP to treat everything as a resource. gRPC uses Protobuf and HTTP/2 to treat remote interactions like local function calls. GraphQL gives clients a query language to pull exactly what they need, moving aggregation to the backend.
Always protect your APIs with rate-limiting, secure authentication, and idempotency keys to ensure they remain highly available and consistent in an unreliable distributed world.

## Self-check questions
1. Explain how gRPC Protobuf tag numbers facilitate seamless backward and forward schema compatibility.
2. What is the N+1 query problem in GraphQL, and how does the DataLoader pattern mitigate it?
3. Contrast offset-based and cursor-based pagination. Under what circumstances will offset-based pagination cause database performance issues?
4. Walk through the step-by-step lifecycle of an API call using an idempotency key. What must the server do when a client retries a transaction that is still in progress?
5. Why does gRPC offer better performance than REST over JSON? Explain the roles of both HTTP/2 and Protocol Buffers.
6. A service must support three active client applications (web, iOS, Android) that display different quantities of user information. Compare how you would address this using REST versus GraphQL.

## References
- System Design Guide for Software Professionals (Sinha & Chopra), Chapter 8
- Designing Data-Intensive Applications (Kleppmann), Chapter 4: Encoding and Evolution (DDIA/06)
