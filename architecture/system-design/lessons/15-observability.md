---
id: system-design/15
subject: system-design
title: "Observability: Logging, Metrics, and Tracing"
slug: observability
status: drafted
mastery: 
seniority: mid
source: "System Design Guide for Software Professionals (Sinha & Chopra), Chapter 8"
prerequisites: []
created: 2026-06-30
updated: 2026-06-30
---

# Observability: Logging, Metrics, and Tracing

## TL;DR
Observability lets engineers explain the internal state of a complex, distributed system by analyzing its external outputs. It combines structured logs, multi-dimensional metrics, and distributed traces to diagnose novel failures without redeploying code. This approach replaces static monitoring with active, interactive debugging.

## The idea
Traditional monitoring works well when we can predict how a system might fail. We configure dashboards to display CPU usage, database connection pools, or memory consumption. These static charts watch for known thresholds, but modern microservices systems fail in unpredictable, non-linear ways. A failure might only occur when a specific combination of user actions, database locks, and network latency interact.

Consider a modern e-commerce platform where a checkout request flows through twenty microservices. If checkouts start failing, a simple alert stating that "CPU usage is high on the Order Service" does not help. The high CPU usage might be a symptom of a slow database query inside the Inventory Service, or a retry storm from the Notification Service.

Observability solves this problem by collecting high-cardinality, high-dimensionality data. It allows us to ask new questions about our systems without knowing the questions in advance. When a system is observable, we do not just see that it is slow. We can pinpoint which specific database query, running inside which container, serving which particular user, is causing the delay.

This concept applies fundamental principles from Designing Data-Intensive Applications (DDIA). Specifically, it tackles the challenge of operating complex, unreliable hardware and software systems. By designing for observability, we accept that individual nodes and networks will fail. Instead of trying to prevent every failure, we focus on shortening our time to detect and resolve issues.

## How it works
Observability rests on three core telemetry sources: logs, metrics, and distributed tracing. It also includes systems for alerting on these sources while keeping human operators from burning out.

### Monitoring versus Observability
Monitoring is about tracking known failures. It answers the question, "Is my system working?" We set up dashboards and alarms for static thresholds, like a disk reaching 90 percent capacity. Monitoring is passive, watching for predefined symptoms that we have already seen in past outages.

Observability, on the other hand, is about debugging unknown failures. It answers the question, "Why is my system failing in this completely new way?" This requires rich, contextual telemetry that lets you slice and dice system behavior along any arbitrary dimension, like tenant, version, or request path. While monitoring tells you that your API success rate has dropped to 95 percent, observability allows you to ask: "Show me the logs for the 5 percent failed requests, grouped by database host and user subscription level."

### The First Pillar: Structured Logging
Logs record discrete events that happen inside an application. Older applications often wrote unstructured text files, which were incredibly hard for machines to parse. Modern systems use structured logging, which formats log messages as machine-readable JSON payloads.

Each log entry contains a standard set of key-value pairs. Standard fields include the timestamp, severity level, environment, and message. Teams also inject contextual metadata like user IDs, tenant IDs, and transaction IDs. Centralized log aggregation engines collect these files from hundreds of containers, index them using inverted indexes, and allow engineers to search millions of rows instantly.

```
Unstructured Log (Hard to parse):
[2026-06-30 10:15:30] WARN Order failed for user 9482 due to db timeout in 150ms

Structured Log (JSON, Easy to parse and query):
{
  "timestamp": "2026-06-30T10:15:30.123Z",
  "level": "WARN",
  "service": "order-service",
  "message": "Order processing failed",
  "user_id": "9482",
  "error": "database_timeout",
  "duration_ms": 150,
  "trace_id": "abc-123"
}
```

#### Log Aggregation Architecture
To collect and process these logs, applications send them to an ingestion pipeline. Tools like Fluentd, Logstash, or Vector collect logs from standard output, parse them, and forward them to storage backends. Typical storage engines include Elasticsearch, OpenSearch, or Grafana Loki. 

Because log ingestion can spike dramatically during an outage, many architectures place a buffer like Apache Kafka between the collector and the storage engine. This prevents the log database from being overwhelmed. Once stored, logs are typically segregated into hot, warm, and cold tiers to optimize storage costs, with older logs archived to cheaper object storage.

To make logs useful across a distributed system, we must use correlation IDs. When a request enters our API gateway, the gateway generates a unique ID. It passes this ID down to every downstream service in the request headers. Every service includes this request ID in its logs, letting developers reconstruct the entire life cycle of a single transaction.

Security remains a major concern for logs. Teams must implement filters to scrub personally identifiable information (PII), passwords, and credit card numbers before they reach disk. Failure to do so violates regulatory compliance and introduces massive security vulnerabilities.

### The Second Pillar: Multi-Dimensional Metrics
Metrics represent aggregated numeric values that describe system behavior over time. They are cheap to store and incredibly fast to query. We divide metrics into three main types:
* **Counters:** Numeric values that only increase, like total requests received or total errors encountered.
* **Gauges:** Current instantaneous values that can go up and down, like CPU usage, memory consumption, or active worker threads.
* **Histograms:** Mathematical representations of the distribution of values, which are vital for tracking latency.

In DDIA, we learn that average latency is a deceptive metric. It hides the experiences of users who suffer from slow response times, which we call tail latency. The heaviest users, who often generate the most revenue, typically trigger tail latency because they have the most data stored in the system. Histograms let us calculate percentiles like the p95, p99, and p99.9. These numbers show the maximum latency that 95 percent, 99 percent, or 99.9 percent of our users experience.

#### The Math of Percentiles
Percentiles are difficult to aggregate mathematically. You cannot simply average the p99 latency across ten different servers, because a slow server with low traffic will distort the overall picture. To get accurate cluster-wide percentiles, metrics databases use advanced algorithms like t-digests or HDR Histograms to merge distributions.

Another major challenge with metrics is cardinality. Cardinality refers to the number of unique combinations of label values. If you add a `user_id` tag to a metric in a system with millions of users, you will create millions of unique time series. This can crash your Time Series Database (TSDB) by consuming all available memory. To save space, modern TSDBs use exponential bucket schemas to compress histogram data instead of linear buckets, allowing high precision without memory bloating.

#### Metric Collection Mechanics: Pull vs Push
Systems collect metrics using either pull or push architectures. Pull systems, like Prometheus, scrape metrics from a standard HTTP endpoint on each service. Push systems, like StatsD or Datadog, have applications actively send metrics to a collector daemon. Pull systems offer better control over traffic flow and prevent a failing service from DDOS-ing the monitoring backend. Push systems are easier to configure behind strict firewalls and work well for short-lived batch jobs.

For service health, teams use the **RED method**:
* **Rate:** The number of requests your service receives per second.
* **Errors:** The number of those requests that fail.
* **Duration:** The amount of time those requests take to complete.

For resource health, we use the **USE method**:
* **Utilization:** The percentage of time that a resource is busy, like a disk or CPU.
* **Saturation:** The queue of extra work waiting for the resource.
* **Errors:** The count of error events on that resource.

### The Third Pillar: Distributed Tracing
Distributed tracing tracks the path of a request as it flows through multiple services. While logs show what happened inside one service and metrics show aggregate health, traces show how services interact.

A trace consists of a tree of spans. A span represents a single unit of work, like a database query, an HTTP request, or an internal function call. Spans have a start time, a duration, and a parent span ID. They can also contain custom attributes, events, and status codes.

Trace context propagation makes this work. To link spans together, services must pass trace metadata along with every RPC or HTTP call. This metadata includes the Trace ID, the current Span ID, and sampling flags. Open standards like W3C Trace Context and B3 Propagation define standard HTTP headers for this data.

```
W3C Traceparent Header Format:
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
             │  └─────────────┬────────────────┘ └───────┬──────┘ └─┬┘
             │            Trace ID                    Span ID     Flags
         Version (00)                                           (01 = Sampled)
```

#### Trace Baggage Propagation
We can also propagate non-tracing metadata alongside the trace context, which is called baggage propagation. Baggage allows you to pass key-value pairs, like user subscription tiers, down the entire call stack. Downstream services use this baggage to make real-time decisions, like prioritizing database queries for premium users or applying custom rate limits.

#### Tracing Storage and Sampling
Because tracing every request produces massive amounts of data, tracing systems use sampling. Head-based sampling decides whether to trace a request at the API gateway, based on a fixed rate. Tail-based sampling makes this decision after the request completes, ensuring that we capture rare errors or unusually slow requests. Storing trace data requires highly scalable databases like Cassandra, ClickHouse, or Jaeger's memory-backed storage, with retention configured for short periods, usually 7 to 14 days.

### The OpenTelemetry Standard
Historically, distributed tracing suffered from fragmentation. Every vendor maintained their own agents and APIs, which locked customers into specific monitoring platforms. OpenTelemetry (OTel) solved this issue by creating a unified vendor-neutral framework under the Cloud Native Computing Foundation (CNCF).

OpenTelemetry provides a standard set of APIs, SDKs, and tooling to generate and export telemetry. The central component is the OTel Collector, which runs as a proxy alongside applications. It receives data in multiple formats, processes it (filtering PII, performing tail-based sampling, and batching), and exports it to backends like Datadog, Honeycomb, or Jaeger. This architecture decouples instrumentation from storage, giving teams complete control over their telemetry pipelines.

### Alerting, Service Level Objectives (SLOs), and Error Budgets
Uncontrolled alerts cause alert fatigue, which leads to engineers ignoring real outages. To prevent this, we should alert on symptoms rather than causes. For example, do not page an engineer because a single container is at 90 percent CPU. Page them because the system's error rate is spiking.

We organize alerting around Service Level Objectives (SLOs):
* **Service Level Indicator (SLI):** A quantitative measure of service performance, like the percentage of HTTP requests that return success in under 200 milliseconds.
* **Service Level Objective (SLO):** A target value for an SLI that the team agrees to meet, like 99.9 percent success over a 30-day window.
* **Error Budget:** The allowable room for failure, which is 100 percent minus your SLO. For a 99.9 percent SLO, the error budget is 0.1 percent.

#### Multi-Window Multi-Burn-Rate Alerts
If a team consumes their error budget too quickly, alerts fire. Modern teams use burn rate alerting, which triggers alerts based on how fast the error budget is being consumed. For instance, consuming 2 percent of your monthly error budget in a single hour indicates a severe outage that requires an immediate page. Consuming 5 percent over 6 hours represents a slower burn that might trigger a ticket instead of waking up an engineer in the middle of the night. This approach minimizes false alarms while guaranteeing that critical outages are detected immediately.

Furthermore, teams enforce strict policies around error budgets. If a service completely exhausts its monthly error budget, product teams must halt all new feature deployments. They must pivot 100 percent of their engineering capacity to addressing reliability issues until the error budget is restored.

#### On-Call and Blameless Retrospectives
Operating high-reliability systems requires a strong on-call culture. When an engineer is paged, they must have clear, automated runbooks to guide their mitigation. After resolving the incident, SRE teams host a blameless retrospective. SRE on-call engineers also write detailed handover notes at the end of each shift to ensure seamless transitions between incoming and outgoing on-call rotations.

#### The 5-Whys Methodology in Practice
To perform a blameless post-mortem, teams use the 5-Whys methodology. For example:
1. Why did the checkout fail? Because the Order database rejected queries.
2. Why did the database reject queries? Because the connection pool was exhausted.
3. Why was the pool exhausted? Because the Payment Service was hanging on third-party calls.
4. Why was the Payment Service hanging? Because it did not have a timeout configured.
5. Why did it not have a timeout? Because timeouts were not enforced in our API design standard.

The goal of this retrospective is to uncover these root systemic causes rather than pointing fingers at individuals. Once identified, teams write concrete action items to prevent recurrence.

### Logs, Metrics, and Traces: A Comparison

| Feature | Logs | Metrics | Traces |
| :--- | :--- | :--- | :--- |
| **Data Type** | Structured text / JSON | Aggregate numbers | Graphs of spans |
| **Cost** | High | Low | Medium to High |
| **Storage Growth** | Linear with request volume | Constant with service scale | Linear with sampled volume |
| **Primary Use Case** | Detailed context on failures | Alerting and high-level health | Finding cross-service bottlenecks |

### Worked Examples

#### Example 1: Trace Propagation across Services
This diagram shows how a single request travels from an API Gateway to an Order Service, which then calls both a Database and an Inventory Service. The Trace ID remains constant, while Span IDs establish parent-child relationships.

```
Request enters API Gateway
  [Span A: Gateway Request] (Trace ID: abc-123, Span ID: 001, Parent: None)
   |
   +--> Calls Order Service (Injects HTTP header: traceparent: 00-abc-123-001-01)
          [Span B: Process Order] (Trace ID: abc-123, Span ID: 002, Parent: 001)
           |
           +--> Query Database
           |      [Span C: Write Order] (Trace ID: abc-123, Span ID: 003, Parent: 002)
           |
           +--> RPC Call Inventory
                  [Span D: Reserve Item] (Trace ID: abc-123, Span ID: 004, Parent: 002)
```

In this model, the API Gateway creates Span A and injects the HTTP header. The Order Service parses this header, sets Span A as its parent, and creates Span B. This chain continues down the call stack, preserving the path of execution.

#### Example 2: Computing SLO and Error Budget
Let us design an SLO for a payment processing API.

* **Metric (SLI):** The percentage of successful API requests. We define success as any HTTP response code other than 5xx, completed in under 500 milliseconds.
* **Target (SLO):** 99.9 percent success over a rolling 30-day window.

To calculate our error budget, we first count our total monthly requests. Suppose the API receives 10,000,000 requests per month.

Our allowed failed requests count equals:
```
Total Requests * (100% - SLO%)
10,000,000 * 0.001 = 10,000 requests
```

If we experience an outage that fails 8,000 requests, we consume 80 percent of our monthly error budget. The team must now prioritize reliability fixes over new features to avoid violating the target.

#### Example 3: RED Metrics Selection for a User API
Let us design the RED metrics dashboard for a billing service.

```
Billing Service RED Dashboard
====================================================================
1. Rate (Requests per second)
   [ 124 rps ]  -----> Query: sum(rate(http_requests_total[1m]))

2. Errors (Failed requests per second)
   [ 0.05 rps ] -----> Query: sum(rate(http_requests_total{status=~"5.."}[1m]))

3. Duration (Response time percentiles)
   [ p50: 45ms ] [ p95: 120ms ] [ p99: 350ms ]
   -----> Query: histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
====================================================================
```

By watching these three metrics, an on-call engineer can immediately tell if the billing service is failing, running slow, or facing an unusual spike in traffic.

## Pros
- **Fast Troubleshooting:** Teams can correlate logs, metrics, and traces to locate the source of an issue in minutes instead of hours.
- **Deep Tail Latency Insights:** Percentile metrics expose the exact delay that frustrated users experience, highlighting system bottlenecks.
- **Improved Team Autonomy:** Distributed tracing helps developers understand how their service behaves in production without needing deep knowledge of downstream systems.
- **Data-Driven Engineering Decisions:** Error budgets provide clear guidelines for balancing feature velocity with system stability.

## Cons
- **High Storage Costs:** Retaining large amounts of high-cardinality logs and traces requires significant database storage and compute resources.
- **Performance Overhead:** Generating and propagating trace contexts adds memory and CPU strain to high-throughput applications.
- **Complex Implementation:** Configuring trace headers, logging libraries, and metric collectors across heterogeneous codebases takes substantial engineering time.
- **Vendor Lock-In Risk:** Relying on proprietary agent libraries can make it incredibly expensive to switch monitoring platforms later.

## Alternatives
- **Monolithic APM Agents:** These heavy agents instrument runtime environments automatically. While easy to set up, they offer less flexibility than open standards like OpenTelemetry.
- **SaaS Platform Monitoring:** These out-of-the-box dashboards are provided by cloud hosts. They are simple to use but often lack the deep distributed tracing needed for complex, multi-cloud microservices.
- **Local Application Profiling:** This approach runs profilers like flame graphs in production. While powerful for analyzing a single node, it cannot trace requests across network boundaries.
- **Synthetics and Black-Box Testing:** This technique polls the system from the outside to verify availability. It tells you when the system is down but provides no visibility into why it is failing internally.
- **eBPF Kernel-Level Monitoring:** Extended Berkeley Packet Filter (eBPF) lets you monitor system-level network traffic and system calls directly from the Linux kernel. It is zero-overhead and requires zero modification to application code. It compiles highly sandboxed bytecode which runs at specific hook points in the kernel space. However, it is hard to configure and lacks rich application-level context.
- **Continuous Profiling Tools:** Continuous profilers like Pyroscope or Parca run constantly in production to record CPU and memory allocations per line of code. They are highly powerful for analyzing memory leaks and CPU bottlenecks across a cluster. However, they add slight runtime overhead and do not capture end-to-end request-response network flows.

## When to use it
- **Distributed Microservices:** When single requests flow through multiple network boundaries, tracing is necessary to find bugs.
- **High-Velocity Environments:** When teams deploy code multiple times a day, real-time metrics and SLO alerts are needed to catch regressions early.
- **Multi-Tenant Software:** When you must isolate performance bugs that only affect specific customers using high-cardinality metadata tags.

## When NOT to use it
- **Simple Monoliths:** A single application with a direct database connection does not need complex distributed tracing. Standard application logs and server metrics are perfectly fine.
- **Batch Processing Systems:** High-throughput offline pipelines care about total throughput and job completion rather than request-response latency, making RED service metrics useless. Use custom job-tracking metrics instead.
- **Strictly Budget-Constrained Projects:** If the cost of storing telemetry data starts to approach the cost of running the actual application, stick to basic host metrics and sampled error logging.

## Key takeaways / mental model
Think of metrics as your system's check-engine light, logs as the mechanic's detailed inspection report, and distributed tracing as a map showing exactly how parts interact. Do not watch individual servers. Focus on the journeys of requests and the health of error budgets to keep your systems stable and your engineers sane.

## Self-check questions
1. Why is average latency a poor metric for evaluating user experience in a web service, and what should we use instead?
2. Explain how a trace context is propagated when Service A makes a REST call to Service B. What specific information must cross the network?
3. If your service has a 99.5 percent SLO for request success and receives 2,000,000 requests weekly, what is your weekly error budget in total failed requests?
4. How do you distinguish between monitoring and observability? Give an example of a question only observability can answer.
5. What is the difference between head-based and tail-based sampling in distributed tracing, and why would you choose one over the other?
6. Explain the concept of cardinality in the context of metrics. Why does high cardinality pose a major risk to a Time Series Database, and how can we mitigate it?
7. In a microservices system, how does trace baggage propagation differ from standard trace context propagation? Provide a scenario where you would use baggage.

## References
- Sinha, S., & Chopra, A. (2024). *System Design Guide for Software Professionals*, Chapter 8. Packt.
- Kleppmann, M. (2017). *Designing Data-Intensive Applications*, Chapter 1 (Tail Latency and SLOs). O'Reilly.
