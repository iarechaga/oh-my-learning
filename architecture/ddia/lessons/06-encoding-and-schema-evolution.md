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
This section covers encoding categories, textual limitations, binary formats, schema resolution, compatibility definitions, and modes of dataflow.

### The Purpose of Encoding
Applications use two representations of data. In memory, data is kept in objects, structs, or pointers. These structures are optimized for CPU access and manipulation, but they cannot be written to disk or sent across a network directly. For storage or transmission, the data must be converted into a contiguous stream of bytes. 

The transition from in-memory structures to bytes is called encoding, serialization, or marshalling. The reverse process is decoding, deserialization, or unmarshalling.

### Language-Specific Formats and Their Hazards
Many programming languages include native serialization systems. Examples include Java Serialization, Python's `pickle`, or Ruby's `Marshal`. These systems are highly convenient because they require minimal setup, but they present three major hazards:

1. **Security Vulnerabilities**: Deserialization processes can instantiate arbitrary classes. Attackers can exploit this to run remote code inside your application process. For example, Python's `pickle` allows serializing objects that, upon deserialization, execute shell commands through custom state reconstruction methods. Accepting serialized bytes from untrusted clients is a massive security risk.
2. **Platform Lock-in**: If you serialize an object in Java, a service written in Python or Go cannot decode it. This binds your entire microservice architecture to a single language. It makes integrating new services written in modern languages extremely difficult.
3. **Weak Schema Evolution Support**: These formats lack precise compatibility rules. Modifying a class field frequently causes deserialization crashes when reading older objects. The system must maintain exact class definitions across all nodes, making zero-downtime rolling upgrades impossible.

### Textual Formats vs Binary JSON
Text-based formats like JSON, XML, and CSV are universal and human-readable, but they suffer from significant physical limitations:

1. **Ambiguity and Number Precision**: JSON does not distinguish between integers and floating-point numbers. This causes precision loss in languages like JavaScript when parsing large 64-bit integers. For example, Twitter had to change how it sent tweets because JSON could not parse large 64-bit tweet IDs without losing precision, forcing them to send tweet IDs as text strings instead of numbers.
2. **Binary String Handling**: These formats do not support binary strings natively. Developers must encode binary data as Base64 text, which inflates the payload size by approximately 33%.
3. **Optional Schemas**: XML has XSD schemas, but JSON typically lacks standardized schemas. JSON Schema exists, but it is not universally enforced or parsed by standard tools.
4. **CSV Ambiguity**: CSV is flat, lacks nested structures, has complex character escaping rules, and suffers from format ambiguity due to varying column delimiters.

Binary JSON formats like MessagePack or BSON reduce payload sizes by compressing standard JSON structures. They convert text values into binary markers to save space. However, because they are schema-less, they must still store the literal key names as strings in every single message. If you send a list of a million records, the key name "username" is repeated a million times in the bytes, which is highly inefficient.

### Field Tags and Binary Formats: Thrift and Protocol Buffers
To solve these limitations, Apache Thrift and Protocol Buffers (Protobuf) use schemas defined in an Interface Definition Language (IDL). A code generator compiles these schemas into classes across multiple programming languages. This prevents developers from manually writing parsing logic and ensures strict type checks across microservices.

Thrift and Protobuf achieve high performance by eliminating field names from the encoded bytes. Instead, the schema assigns a unique numeric field tag to each field. The binary payload contains only the numeric field tag and the encoded value. This makes it impossible to understand the binary stream without the compiled schema blueprint.

```protobuf
// Protobuf IDL Example
message User {
  required int32 id = 1;
  optional string name = 2;
}
```

#### Rules of Schema Evolution
To safely modify a schema over time, developers must follow strict rules:
* **Never change or reuse a field tag**: Each tag is the permanent identifier for that field in the binary stream. Renaming a field name in the IDL is perfectly safe because the tag remains identical on the wire.
* **New fields must be optional or have default values**: If you add a required field, old code cannot read new messages because the field is missing. This breaks forward compatibility instantly.
* **Can only remove optional fields**: You can never remove a required field, and you must make sure that its tag is retired so it is never reused in the future. If a retired tag is reused, old data parsed by new code would map to an entirely different field, causing silent data corruption.

### Avro: The Dynamic Schema Resolution Engine
Apache Avro takes a different approach to schema evolution. It does not use field tags. Instead, the raw values are written to the binary payload in the exact order they appear in the schema.

To decode the bytes, the reader must have access to both the writer's schema and the reader's schema.

#### Schema Resolution
During decoding, the Avro engine compares the writer's schema and the reader's schema. It maps fields from the writer's schema to the reader's schema by matching their names. 
* If the reader encounters a field that is present in the reader's schema but missing in the writer's schema, it fills it with the default value.
* If the reader encounters a field that is present in the writer's schema but missing in the reader's schema, it simply skips those bytes.

#### Why Avro Suits Hadoop and Big Data
Avro is highly optimized for large-scale data processing workloads like Hadoop.
* **Dynamically Generated Schemas**: Because Avro schemas are represented in standard JSON, engines can generate them dynamically from SQL database tables without code compilation.
* **Self-Contained Files**: In a large file containing millions of records, the writer's schema is simply written at the very beginning of the file container. The subsequent records are written without any tags or schemas, keeping overhead minimal.
* **Schema Registries**: In message passing systems, the sender registers the schema in a central database and attaches a 4-byte schema ID to each message. The receiver reads the ID, fetches the schema from the registry, and decodes the payload.

### Definitions of Compatibility
To support zero-downtime rolling upgrades, an encoding system must maintain two forms of compatibility:

* **Backward Compatibility**: New code can read data written by old code. This is necessary because older database records or archived logs must still be readable by updated application versions.
* **Forward Compatibility**: Old code can read data written by new code. This is necessary because during rolling deployments, some nodes run older code while others send new messages.

The following table summarizes the compatibility actions across formats:

| Schema Action | Thrift/Protobuf Evolution Rule | Avro Evolution Rule |
| :--- | :--- | :--- |
| **Add New Field** | Must be optional or have a default value. Assign a new tag. | Must define a default value in the schema. |
| **Remove Field** | Can only remove optional fields. Never reuse the tag. | Can only remove fields that had a default value. |
| **Rename Field** | Can rename fields as long as the tag remains the same. | Can rename fields using schema aliases to map schemas. |

### Evolution in Action: A Rolling Deployment Scenario
To see why we need both compatibility directions, imagine a cluster of three servers (Server A, Server B, and Server C) running version 1 of your application. These nodes communicate by passing serialized messages to each other. You want to deploy version 2 of your application, which adds a new optional field `profile_picture_url`. Let's look at the step-by-step timeline of this rolling deployment:

1. **Initial State**: All three servers run version 1 and understand version 1 messages.
2. **Server A Upgraded**: You deploy version 2 to Server A. It is now able to write messages containing the `profile_picture_url` field.
3. **New Message Sent**: Server A sends a version 2 message to Server B, which is still running version 1.
4. **Forward Compatibility Check**: Server B parses the message. Because it runs version 1, it does not know what `profile_picture_url` is. However, because you are using a schema-driven format with optional fields, Server B simply ignores the unknown tag and processes the rest of the message successfully. This is **forward compatibility** in action. If this check failed, Server B would crash, causing service downtime.
5. **Data Written to Database**: Server A writes a version 2 record to a shared database.
6. **Server C Upgraded**: You deploy version 2 to Server C.
7. **Old Record Read**: Server C reads an older version 1 record from the database.
8. **Backward Compatibility Check**: Server C looks for the `profile_picture_url` field in the record and notices it is missing. Because the field is marked as optional with a default of `null`, Server C sets the field to `null` and continues processing without errors. This is **backward compatibility** in action.
9. **Final State**: You upgrade Server B to complete the rolling deployment. All servers now run version 2 and can fully utilize the new field.

### Modes of Dataflow
Data flows between processes in three primary ways:

1. **Through Databases**: One process writes to a database, and another process reads from it. The database behaves like a time machine where the reader and writer exist at different points in time. Data outlives code, which requires long-term backward compatibility. When the database schema evolves, we must often run migration scripts to update existing records, or design our application code to handle multiple schema versions simultaneously.
2. **Through Services (REST and RPC)**: Processes communicate over network APIs. REST APIs typically use JSON over HTTP. RPC frameworks like gRPC use Protocol Buffers over HTTP/2, generating client and server code to ensure structured contracts. RPC introduces distinct challenges compared to local function calls, including network latency, packet loss, timeouts, and retry overhead. If a service interface changes, developers must version their APIs (using headers or URL paths) to avoid breaking older clients that have not been redeployed.
3. **Asynchronous Message Passing**: Systems use message brokers like Kafka or RabbitMQ to decouple senders from receivers. Senders publish messages, which are buffered, redelivered, and processed asynchronously. This provides durability and decouples processing speeds. The sender does not need to wait for the consumer to finish processing, but we must ensure that consumers can parse newly formatted messages if the producer is upgraded first.
4. **The Actor Model**: This is a concurrency model where independent actors pass asynchronous encoded messages to communicate, even across different physical nodes. Since actors can be upgraded in a rolling fashion, messages sent between them must conform to strict backward and forward compatibility rules.

### Three Concrete Worked Examples

#### Example 1: Protocol Buffers Encoded-Bytes Walk-Through
Suppose we have a Protobuf schema:
```protobuf
message User {
  required int32 id = 1;
  optional string name = 2;
}
```

We encode this record: `User { id: 150, name: "Bob" }`.

The compiled encoder produces these 8 bytes (shown in hexadecimal):
`08 96 01 12 03 42 6f 62`

Let's walk through these bytes step-by-step:
* **Byte `08`**: Indicates the field tag and wire type. In Protobuf, this is calculated as `(tag << 3) | wire_type`. Here, tag is `1` (for `id`), and the wire type for varints is `0`. So `(1 << 3) | 0 = 8` (hex `08`).
* **Bytes `96 01`**: Represent the value `150` encoded as a variable-length integer (varint). In varints, the most significant bit (MSB) of each byte is a flag indicating if there are more bytes.
  - Value 150 in binary is `10010110`.
  - The lower 7 bits are `010110` (decimal 22). We set the MSB of the first byte to `1` to indicate more bytes follow: `10010110` (hex `96`).
  - The remaining bit is `1` (decimal 1). We set the MSB to `0` because no more bytes follow: `00000001` (hex `01`).
  - Combined, `96 01` decodes back to 150.
* **Byte `12`**: Represents tag `2` (for `name`) with wire type `2` (length-delimited). `(2 << 3) | 2 = 16 | 2 = 18` (hex `12`).
* **Byte `03`**: Indicates the length of the string, which is `3` bytes.
* **Bytes `42 6f 62`**: Represent the ASCII characters for `"Bob"` (`42` is 'B', `6f` is 'o', `62` is 'b').

The final payload size is only 8 bytes.

#### Example 2: JSON vs MessagePack (Binary JSON) Cost Analysis
Suppose we have a user record:
`{"id":150,"name":"Bob"}`

In UTF-8 text, this is exactly 21 bytes.

Let's see how MessagePack encodes the same map:
`82 a2 69 64 cd 00 96 a4 6e 61 6d 65 a3 42 6f 62`

Let's analyze this 17-byte stream:
* **`82`**: Indicates a map with 2 key-value pairs (high bits specify a map type, lower bits specify the size 2).
* **`a2`**: Indicates a string of length 2 (the key `"id"`).
* **`69 64`**: ASCII characters for `"id"`.
* **`cd 00 96`**: 16-bit unsigned integer containing `150` (`cd` is the type marker, `00 96` is the value).
* **`a4`**: Indicates a string of length 4 (the key `"name"`).
* **`6e 61 6d 65`**: ASCII characters for `"name"`.
* **`a3`**: Indicates a string of length 3 (the value `"Bob"`).
* **`42 6f 62`**: ASCII characters for `"Bob"`.

While MessagePack is smaller than raw JSON (17 bytes vs 21 bytes), it is still much larger than Protocol Buffers (8 bytes) because MessagePack must store the literal key names `"id"` and `"name"` as strings.

#### Example 3: Schema Resolution in Avro with Reader and Writer Schema Discrepancy
Suppose the writer uses this schema:
```json
{
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "id", "type": "int"},
    {"name": "name", "type": "string"}
  ]
}
```

The writer serializes: `User { id: 150, name: "Bob" }`.

Because Avro does not use tags or field names in the data payload, it simply writes the raw values in order:
* `150` as a varint (bytes `96 01`).
* `"Bob"` as a length-delimited string (length `06` (in Avro zigzag varint representation for strings), followed by `42 6f 62`).

The payload is just `96 01 06 42 6f 62` (6 bytes).

Now suppose the reader has a newer schema where a new optional field `email` is added with a default of `null`, and the fields are in a different order:
```json
{
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "name", "type": "string"},
    {"name": "email", "type": ["null", "string"], "default": null},
    {"name": "id", "type": "int"}
  ]
}
```

When reading the data, the Avro engine resolved the discrepancy:
1. It reads the reader's schema and matches field names with the writer's schema.
2. For the reader's first field `name`: the engine looks up `name` in the writer's schema, sees it is the second field, and decodes the string `"Bob"`.
3. For the reader's second field `email`: the engine sees `email` is missing in the writer's schema, looks up its default value, and sets it to `null`.
4. For the reader's third field `id`: the engine looks up `id` in the writer's schema, sees it is the first field, and decodes the integer `150`.

This demonstrates how Avro resolves schemas dynamically at read-time, keeping payloads tiny and allowing schema evolution without tags.

## Pros
- Schema-driven binary formats produce tiny payloads because they omit field names from the encoded bytes.
- Interface Definition Languages act as a single source of truth and generate client libraries in multiple languages.
- Strict data typing prevents malformed inputs from reaching core application logic.
- Field tags and schema registries allow seamless backward and forward compatibility during rolling deployments.
- Code generation tools automatically compile schemas into typed classes across diverse programming languages.

## Cons
- Binary encodings are not human-readable, which requires specialized tools to inspect or debug payloads.
- Managing schema registries and code generation processes introduces operational complexity.
- Language-specific serialization formats create severe security vulnerabilities and lock applications into a single platform.
- Schema changes require careful planning because renaming fields or changing field tags can break compatibility instantly.
- Build toolchains must integrate code compilation steps, which increases setup friction for small projects.

## Alternatives
- **Dynamic schema-less binary formats**: Formats like MessagePack or BSON encode field names as strings alongside values, offering some size reduction without requiring schemas.
- **Flat text formats**: CSV remains a popular alternative for bulk file transfers when schema evolution is managed manually and structured hierarchy is unnecessary.
- **Strict schema-driven text formats**: XML schemas (XSD) provide typing and structure, but they consume massive amounts of bandwidth compared to binary alternatives.

## When to use it
Use schema-driven binary formats like Protocol Buffers or Avro when building high-throughput microservices, managing large-scale message queues, or storing massive datasets. Use textual formats like JSON or XML for public-facing web APIs where ease of integration and human readability are more important than byte efficiency.

## When NOT to use it
Do not use language-specific formats like Java Serialization or Python pickle for long-term storage or inter-service communication. Reach for JSON or Protocol Buffers instead. Do not use complex binary schemas for simple scripts or public API integrations where third-party developers expect standard, plain text payloads. Reach for JSON instead.

## Key takeaways / mental model
Think of JSON or XML as sending a package wrapped in wrapping paper that has detailed labels listing every ingredient and part name. It is easy for anyone to open and read, but it is heavy and bulky. Think of Protocol Buffers or Thrift as sending a sealed box containing only raw materials in a precise layout, with small numbers written on each piece. To open the box, you must have the original blueprint that maps number 1 to "id" and number 2 to "name". Without that blueprint, the box is just a meaningless stream of bytes.

## Self-check questions
1. Why are language-specific serialization formats like Java Serialization considered dangerous for security?
2. What is the difference between forward and backward compatibility, and why must both hold to allow zero-downtime rolling upgrades?
3. How does Avro resolve schemas when the reader's schema has fields in a different order than the writer's schema?
4. Why is a database considered a "dataflow through time", and how does this affect how we evolve database schemas?
5. How do field tags in Protocol Buffers replace field names in JSON, and what is the wire-type formula used to decode them?
6. Suppose a service receives a binary message that contains a field tag not defined in its compiled schema. How should the service handle this field to maintain forward compatibility?
7. Why are remote procedure calls (RPC) inherently more fragile than local function calls, and what network concerns must an engineer handle when using RPC?
8. What is the schema evolution difference between Protocol Buffers and Apache Avro, and why does Avro not need field tags?

## References
- Designing Data-Intensive Applications (Martin Kleppmann), Chapter 4: Encoding and Evolution.
- Prerequisites: [02-data-models.md](../lessons/02-data-models.md)