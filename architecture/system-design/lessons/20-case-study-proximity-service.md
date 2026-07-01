---
id: system-design/20
subject: system-design
title: "Case Study: Proximity / Geo Service"
slug: case-study-proximity-service
status: drafted
mastery:
seniority: senior
source: "System Design Guide for Software Professionals (Sinha & Chopra), Chapter 10"
prerequisites: [system-design/16, ddia/10]
created: 2026-06-30
updated: 2026-06-30
---

# Case Study: Proximity / Geo Service

## TL;DR
Design a highly scalable geospatial service like Yelp or Uber to find nearby places or drivers. We replace inefficient multi-dimensional relational database scans with spatial indexing mechanisms like geohash and quadtrees. This system handles static points of interest and rapid driver coordinate updates, using region-based partitioning to scale horizontally.

## The idea
Traditional database indexes are one-dimensional, sorting data along a single linear scale. Finding places near a latitude and longitude requires a two-dimensional query. A relational database with standard indexes must perform two separate range scans and intersect the results, scanning millions of irrelevant records in the process.

Geospatial services solve this by projecting two-dimensional coordinates onto a one-dimensional space. By partitioning the globe into hierarchical grids, we can locate nearby items with simple string prefix matches or tree traversals. This case study explores how to design and partition these spatial data structures.

## How it works

### 1. Requirements
#### Functional Requirements
- Users can search for nearby points of interest within a given radius.
- Owners can add, update, or delete their business locations.
- Drivers can report their live location coordinates every few seconds for real-time tracking.

#### Non-Functional Requirements
- Sub-second search response times, targeting less than 100 milliseconds.
- High write throughput to handle frequent location updates from moving drivers.
- Seamless horizontal scaling as the number of places and users grows worldwide.

#### Consistency and Availability Trade-offs
Our system prioritizes availability and low latency over strict consistency, in line with PACELC theorem concepts from system-design/03. For search, a newly added business or a slightly outdated rating does not impact user experience. Eventual consistency is sufficient for live driver locations. A user requesting nearby drivers can tolerate a delay of a few seconds in coordinate synchronization, allowing us to perform fast, non-blocking reads from local Redis replica nodes.

### 2. Back of the Envelope Estimation
Let's evaluate the storage and query capacity required for a global service with 500 million points of interest (POIs) and 20 million active users.

#### Query Volume
Assume each active user searches for nearby places 5 times a day.
20,000,000 users * 5 searches = 100,000,000 daily queries.
Average QPS = 100,000,000 / 86,400 seconds = ~1,157 queries per second.
At peak, this can reach 10,000 QPS.

#### Storage Requirements (Worked Detail)
We store the primary POI data in a relational database, but keep a copy of the index in memory for fast retrieval.
- Each POI record contains:
  - POI ID: 8 bytes
  - Latitude: 8 bytes
  - Longitude: 8 bytes
  - Category and rating metadata: 16 bytes
- Total data per POI = 32 bytes.
- Total raw memory for 500 million POIs: 500,000,000 * 32 bytes = 16,000,000,000 bytes = 16 GB.
- Including tree overhead or hash map pointers, the primary geospatial index comfortably fits within 25 GB of RAM on a single modern server.

### 3. API Sketch
The service exposes clean endpoints for searching nearby places and updating dynamic positions.

#### Find Nearby Places
`GET /api/v1/search/nearby?lat=37.7749&lng=-122.4194&radius_km=2&category=restaurant`
Response:
```json
{
  "places": [
    {
      "id": "poi_8829",
      "name": "The Gourmet Grill",
      "lat": 37.7752,
      "lng": -122.4181,
      "distance_km": 0.12,
      "rating": 4.8,
      "review_count": 312,
      "price_level": "$$"
    }
  ]
}
```

#### Update Live Location
`POST /api/v1/drivers/location`
Request:
```json
{
  "driver_id": "drv_5512",
  "lat": 37.7749,
  "lng": -122.4194,
  "timestamp": 1782806400
}
```
Response:
```json
{
  "status": "acknowledged"
}
```

### 4. Data Model
We keep our business database highly optimized by splitting it into core tables. Metadata that changes infrequently is stored in PostgreSQL, which provides reliable transaction boundaries and relational joins. Real-time, fleeting driver locations are kept in Redis to avoid hitting disk write bottlenecks. This dual-storage design ensures that massive driver updates never impact catalog queries.

```
Table: Point_Of_Interest (PostgreSQL)
- id (BIGINT, Primary Key)
- name (VARCHAR)
- latitude (DOUBLE)
- longitude (DOUBLE)
- geohash (VARCHAR, Indexed)
- description (TEXT)

Table: Driver_Location (Redis Key-Value)
- Key: driver_id
- Value: { latitude, longitude, updated_at }
- Geospatial Index: Redis GEOADD (uses S2 cells under the hood)
```

### 5. High Level Architecture

```
                       [ Client App (User or Driver) ]
                                      |
                                      v
                                [ API Gateway ]
                                      |
                 +--------------------+--------------------+
                 |                                         |
                 v                                         v
     [ Nearby Search Service ]                 [ Location Update Service ]
                 |                                         |
                 +--------------------+                    v
                 |                    |          [ Message Queue (Kafka) ]
                 v                    v                    |
       [ Geospatial Cache ]     [ POI SQL DB ]             v
         (Quadtree/Geohash)                   [ Live Tracker Service ]
                                                           |
                                                           v
                                                [ Redis Geo cluster ]
```

#### Component Descriptions
- **Nearby Search Service**: A stateless service that processes read-only query requests by querying the Geospatial Cache or Postgres database.
- **Location Update Service**: A high-throughput ingest engine that receives periodic WebSocket or HTTPS coordinate ping requests from active driver devices.
- **Live Tracker Service**: A background consumer that processes driver location updates from Kafka and updates the memory-mapped Redis cluster.
- **Geospatial Cache**: An in-memory distributed store holding pre-built quadtrees and geohash indexes for static points of interest.

#### Nearby Search Query Path (Worked Detail)
When a user searches for restaurants within 2 km of their coordinates:
1. The client sends its latitude and longitude to the API Gateway.
2. Our gateway forwards the request to the Nearby Search Service.
3. This service maps the coordinates to a geohash representation.
4. To cover a 2 km search radius, the service selects a 5-character geohash string which covers a 4.9 km by 4.9 km square grid.
5. We retrieve the target geohash cell from the cache, along with the 8 neighboring cells to account for boundary edge cases.
6. The service filters the retrieved points, computing the precise Euclidean distance for each POI.
7. Sorted results are returned to the client in under 50 milliseconds.

### 6. How It Scales

#### Naive B-Tree Limitations
A naive SQL query tries to filter on latitude and longitude independently:
`SELECT * FROM POI WHERE lat BETWEEN 37.7 AND 37.8 AND lng BETWEEN -122.5 AND -122.4`
The database can use a B-tree to filter latitude quickly, but it must scan all resulting rows to filter longitude, causing high CPU load.

#### Geohash Indexing (Worked Detail)
A geohash converts a 2D coordinate into a base32 string.
- The algorithm divides the world into alternating latitude and longitude binary ranges.
- Let's trace how latitude 37.7749 is encoded:
  - Range [-90, 90] -> Midpoint 0. 37.7749 is in [0, 90], so the first bit is 1.
  - Dividing [0, 90] -> Midpoint 45. 37.7749 is in [0, 45], so the second bit is 0.
  - Refining [0, 45] -> Midpoint 22.5. 37.7749 is in [22.5, 45], so the third bit is 1.
  - Selecting [22.5, 45] -> Midpoint 33.75. 37.7749 is in [33.75, 45], so the fourth bit is 1.
- Combining alternating latitude and longitude bits yields a 2D grid cell. We group every 5 bits and map them to a character in a base32 alphabet (like "9bcdef...").
- Shared string prefixes guarantee spatial closeness, except at cell boundaries.
- To resolve this boundary problem, we calculate the coordinates of the target cell and shift by one cell width in all eight cardinal and ordinal directions.

```
       Geohash Grid Neighbor Search (9 Cells)
       +---------+---------+---------+
       |  g2p1r  |  g2p1s  |  g2p1u  |
       +---------+---------+---------+
       |  g2p1q  |  g2p1w  |  g2p1x  | <-- g2p1w is center
       +---------+---------+---------+
       |  g2p1m  |  g2p1t  |  g2p1y  |
       +---------+---------+---------+
```

#### Quadtree Indexing (Worked Detail)
A quadtree is an in-memory tree where each node has exactly four children, representing recursively subdivided quadrants.
- NW (North-West), NE (North-East), SW (South-West), and SE (South-East).
- Let's look at a quadtree subdivision example:
  - We have a quadrant representing San Francisco with a capacity limit of 100 POIs.
  - Initially, we have 90 POIs. They are stored in a single leaf node.
  - Adding 15 new restaurants brings the total to 105. This exceeds our limit of 100.
  - The node splits into 4 sub-quadrants: NW, NE, SW, SE.
  - Redistributing the 105 POIs is done based on their coordinates.
  - Sub-nodes become leaf nodes, and the original node becomes an internal node.
- This recursive subdivision allows dense urban areas to have deep trees, while rural deserts remain as large, undivided quadrants.

```
       Quadtree Recursive 2D Bounding Box
       +-------------------------+
       |            |            |
       |     NW     |     NE     |
       |            |            |
       |------------+------------|
       |            |     |      |
       |     SW     |--SE1+--SE2-|
       |            |     |      |
       |            |--SE3+--SE4-|
       +-------------------------+
```

#### S2 Cells and R-Trees
Google S2 projects the Earth onto a cube and subdivides each face into hierarchical cells using a Hilbert space-filling curve. This curve preserves spatial locality extremely well. It maps two-dimensional coordinates to a one-dimensional coordinate. By following a continuous loop that twists through every cell, the index ensures that nearby points on the globe remain nearby on the 1D line. This avoids the severe cell-width distortions found near the Earth's poles in geohashes. R-trees group bounding boxes of geometries into larger bounding boxes, which is the standard indexing approach for disk-based geospatial databases like PostGIS. These trees allow for arbitrary polygon queries but require more complex tree traversal logic during searches.

#### Sharding and Partitioning
To scale horizontally, we must partition the geospatial database across multiple nodes. This ties directly to the partitioning designs in DDIA Chapter 10 (ddia/10).
- POI ID Sharding: This distributes writes evenly across shards but requires searching every single partition for a nearby query, creating high scatter-gather latency.
- Region-Based Partitioning (Geohash Prefix): We shard data based on the geohash prefix of the location. This groups nearby POIs onto the same shard, allowing queries to target a single node.
- Handling Hotspots: Dense regions like Manhattan or Tokyo will contain far more POIs than entire states. We mitigate this by dynamic splitting, where a hot geohash partition is split into smaller prefixes and distributed across multiple nodes.

#### Managing Moving Objects
Static POI databases are read-heavy, but driver tracking services are write-heavy. We separate these paths completely. Drivers stream coordinates to Apache Kafka via WebSocket connections (system-design/16). A live tracker service processes these streams and writes directly to an in-memory Redis cluster. We use Redis Sorted Sets (GEOADD) to maintain active driver locations, bypassing disk writes entirely during active sessions. Redis represents locations as 52-bit geohashes inside a sorted set, sorting them by their geohash value. When a client queries nearby drivers, the service calls GEORADIUS, which efficiently decodes the target area and returns active drivers in parallel. This high-performance memory-first approach handles over 100,000 coordinate updates per second with microsecond latency.

### 7. Bottlenecks and Edge Cases
- **Grid Boundary Distortions**: Geohash grid boundaries can separate points that are only meters apart. We solve this by always querying the target cell and its eight adjacent neighbors.
- **Dynamic Quadtree Rebalancing**: Rebuilding an in-memory quadtree while thousands of drivers move is CPU intensive. We use the quadtree strictly for static POIs and rely on Redis for rapidly moving drivers.
- **Sparse vs Dense Radius Expansion**: A user in a desert might find zero restaurants within 2 km, while a user in Manhattan finds thousands. We implement an adaptive radius algorithm that dynamically expands the query range if the initial geohash lookup returns too few results.

## Pros
- Geohashes permit fast, direct database index lookups using simple string prefix matching.
- Quadtrees optimize memory usage by dynamically subdividing only the dense urban regions.
- Decoupling static places from moving drivers prevents slow disk writes from bottlenecking live tracking updates.

## Cons
- Geohash grids distort near the poles, where cells shrink dramatically in width.
- Quadtrees must be stored entirely in memory, introducing data loss risks if a server crashes without a replication backup.
- Region sharding can lead to unbalanced load distribution, requiring complex dynamic shard rebalancing logic.

## Alternatives
- **Google S2 Library**: Using S2 cells instead of geohashes. This minimizes geographic cell distortion near the poles and provides better prefix-to-location mapping, though S2 library integration is more complex.
- **PostGIS R-Tree Indexing**: Storing and querying coordinate shapes directly on disk. This is highly accurate and supports complex polygons, but it is much slower than in-memory quadtrees.

## When to use it
This architecture is ideal for applications requiring low-latency location lookups over millions of geographical points. It is standard for ride-hailing networks, restaurant directories, and localized social feeds.

## When NOT to use it
Avoid this complex spatial setup for basic applications with small, static datasets. If your app only lists a hundred store locations, calculating distances in memory on the client side or using a simple SQL table scan is far more cost-effective.

## Key takeaways / mental model
Standard indexes can only sort data in one dimension. To perform fast 2D proximity searches, we must translate coordinates into a single string prefix or recursively subdivide the map. Geohash maps coordinates to linear strings, while quadtrees recursively subdivide the globe based on density. By keeping these structures in memory and sharding by region, we can find nearby items in milliseconds.

## Self-check questions
1. Why are standard relational B-tree indexes inefficient when executing two-dimensional range queries?
2. How does a geohash encode a two-dimensional coordinate into a single base32 string?
3. What is the boundary problem in geohashing, and how does the neighbor-search algorithm resolve it?
4. How does a quadtree structure adapt its depth to handle the difference in density between Manhattan and the Sahara Desert?
5. What are the trade-offs of partitioning geospatial data by POI ID compared to partitioning by region?
6. Why do we decouple the search path for static places from the update path for dynamic drivers?

## References
- System Design Guide for Software Professionals, Chapter 10
- Designing Data-Intensive Applications, Chapter 10 (Partitioning)
- Sibling Lesson: Distributed Messaging (system-design/16)
