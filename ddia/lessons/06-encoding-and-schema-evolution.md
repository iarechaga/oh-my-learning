---
id: ddia/06
subject: ddia
title: "Encoding and Schema Evolution"
slug: encoding-and-schema-evolution
status: drafted
mastery:
source: "Designing Data-Intensive Applications (Martin Kleppmann), Chapter 4"
prerequisites: [ddia/02]
created: 2026-06-30
updated: 2026-06-30
---

# Encoding and Schema Evolution

## TL;DR
Applications must encode in-memory data structures into byte sequences for storage or network transmission. As applications grow, data schemas inevitably change, which requires formats that support rolling updates. Choosing schema-driven binary formats like Protocol Buffers, Thrift, or Avro allows systems to maintain backward and forward compatibility.

## The idea
Programs maintain data in memory using pointers, arrays, and objects optimized for CPU processing. To send this data over the network or write it to disk, we must translate these structures into a self-contained sequence of bytes. This translation process is called encoding or serialization. The core challenge is that software is never static. We frequently need to deploy new code with added or modified fields. If some servers are updated while others are still running older code, the old and new programs must be able to read each other's data. This requirement is schema evolution. Without reliable compatibility rules, rolling upgrades fail, causing application downtime and database corruption.

Before studying encoding formats, read about the different data models described in [Data Models](../lessons/02-data-models.md).

## How it works
This section covers encoding categories, schema compatibility rules, and modes of dataflow.

### Categories of Encoding Formats
Software systems use three main classes of encoding formats to transfer and store information:

1. **Language-Specific Formats**: Many programming languages build in their own serialization systems, such as Java Serialization, Python's `pickle`, or Ruby's `Marshal`. These formats are highly convenient because they require no setup. However, they bind your applications to a single programming language and present severe security risks. Attackers can exploit these formats to run arbitrary code on your servers during deserialization.
2. **Textual Formats**: JSON, XML, and CSV are universal, human-readable formats supported by almost every language. They are excellent for integration but have clear limits. They do not distinguish between integers and floating-point numbers cleanly, which leads to precision loss. They also lack native schema support and consume massive amounts of space because they include field names as text in every message.
3. **Binary Schema-Driven Formats**: Thrift, Protocol Buffers (Protobuf), and Avro use a schema definition language to describe data structures. A compiler generates code in different programming languages to read and write the binary format. These systems produce tiny, efficient payloads because they do not transmit field names.

### Schema Evolution Compatibility Rules
To support zero-downtime rolling upgrades, an encoding system must support two forms of compatibility:

* **Backward Compatibility**: New code can read data written by old code. This is necessary because older records may still exist in databases or logs.
* **Forward Compatibility**: Old code can read data written by new code. This is necessary because during rolling deployments, some nodes run older code while others send new messages.

Protocol Buffers and Thrift achieve this compatibility using **field tags**. Instead of storing a string like `"username"`, the schema assigns a unique number to that field: `required string username = 2`. The binary payload only contains tag number `2` and its value.

To add a new field, you must assign it a new tag and make it optional or give it a default value. When old code encounters a message from new code containing the new tag, it simply skips the unknown tag, maintaining forward compatibility. When new code reads old data, it notices the tag is missing and uses the default value, maintaining backward compatibility.

### Avro: Writer vs Reader Schema
Avro takes a different approach to schema evolution. It does not use field tags. Instead, it relies on two schemas: the **writer's schema** (the schema used when the data was encoded) and the **reader's schema** (the schema expected by the decoding application).

When reading data, Avro resolves the differences between the two schemas by matching fields by name. To maintain compatibility, you can only add or remove fields that have a default value defined. The writer's schema must be made available to the reader, which is achieved by sending it at the start of a network connection, embedding it in a file container, or looking it up from a central schema registry using an ID.

### Modes of Dataflow
Data flows between processes in three primary ways:

1. **Through Databases**: One process writes to a database, and another process reads from it. The database behaves like a time machine where the reader and writer exist at different points in time. A record written years ago by old code must still be readable by new code today, requiring strict long-term backward compatibility.
2. **Through Services (REST and RPC)**: Processes communicate over network APIs. REST APIs typically use JSON over HTTP. RPC frameworks like gRPC use Protocol Buffers over HTTP/2, generating client and server code to ensure structured contracts.
3. **Through Asynchronous Message Passing**: Systems use message brokers like Kafka or RabbitMQ to decouple senders from receivers. The sender encodes a message and publishes it to a topic, and consumers decode and process the message.

### Concrete Encoding Example
Suppose we have a user object in memory:
`User { id: 12345, name: "Alice", email: "alice@example.com" }`

In JSON, this is written as a plain text string:
`{"id":12345,"name":"Alice","email":"alice@example.com"}` (54 bytes)

In Protocol Buffers, we define the schema:
```protobuf
message User {
  required int32 id = 1;
  required string name = 2;
  optional string email = 3;
}
```
The protobuf compiler translates the user object into a binary sequence:
`08 39 30 12 05 41 6c 69 63 65 1a 11 61 6c 69 63 ...` (only 31 bytes)

The engine reads this binary with the compiled schema:
* `08` indicates tag `1` (the `id` field) with a variable-length integer type. The next bytes decode to `12345`.
* `12` indicates tag `2` (the `name` field) with a string type. The next byte `05` indicates a length of 5 bytes, followed by the ASCII bytes for `"Alice"`.
* `1a` indicates tag `3` (the `email` field). This keeps the payload extremely compact and highly performant.

## Pros
- Binary schema-driven formats reduce network payload sizes and storage footprints compared to verbose JSON or XML.
- Numeric field tags and Avro schemas allow seamless backward and forward compatibility during rolling deployments.
- Schema definitions act as a single source of truth and can generate client-side code in multiple languages automatically.
- Strict data typing prevents malformed inputs from reaching core application logic.

## Cons
- Binary encodings are not human-readable, which requires specialized tools to inspect or debug payloads.
- Schema management introduces operational complexity because teams must coordinate schema registries and code generation steps.
- Language-specific serialization formats create severe security vulnerabilities and lock applications into a single platform.
- Schema changes require careful planning because renaming fields or changing field tags can break compatibility instantly.

## Alternatives
- **Dynamic schema-less binary formats**: Formats like MessagePack or BSON encode field names as strings alongside values, offering some size reduction without requiring schemas.
- **Flat text formats**: CSV remains a popular alternative for bulk file transfers when schema evolution is managed manually and structured hierarchy is unnecessary.

## When to use it
Choose schema-driven binary formats like Protocol Buffers or Avro when building high-throughput microservices, managing large-scale message queues, or storing massive datasets. Use textual formats like JSON or XML for public-facing web APIs where ease of integration and human readability are more important than byte efficiency.

## When NOT to use it
Do not use language-specific formats like Java Serialization or Python pickle for long-term storage or inter-service communication. Reach for JSON or Protocol Buffers instead. Do not use complex binary schemas for simple scripts or public API integrations where third-party developers expect standard, plain text payloads. Reach for JSON instead.

## Key takeaways / mental model
Think of JSON or XML as sending a package wrapped in wrapping paper that has detailed labels listing every ingredient and part name. It is easy for anyone to open and read, but it is heavy and bulky. Think of Protocol Buffers or Thrift as sending a sealed box containing only raw materials in a precise layout, with small numbers written on each piece. To open the box, you must have the original blueprint that maps number 1 to "id" and number 2 to "name". Without that blueprint, the box is just a meaningless stream of bytes.

## Self-check questions
1. Why are language-specific serialization formats like Java Serialization considered dangerous for security?
2. What is the difference between forward and backward compatibility, and why must both hold to allow zero-downtime rolling upgrades?
3. How does Avro resolve schemas when the reader's schema has fields in a different order than the writer's schema?
4. Why is a database considered a "dataflow through time", and how does this affect how we evolve database schemas?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 4: Encoding and Evolution.
- Prerequisites: [02-data-models.md](../lessons/02-data-models.md)
