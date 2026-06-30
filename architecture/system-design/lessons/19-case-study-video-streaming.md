---
id: system-design/19
subject: system-design
title: "Case Study: Video Streaming (Netflix)"
slug: case-study-video-streaming
status: drafted
mastery:
source: "System Design Guide for Software Professionals (Sinha & Chopra), Chapter 14"
prerequisites: [system-design/16, system-design/10]
created: 2026-06-30
updated: 2026-06-30
---

# Case Study: Video Streaming (Netflix)

## TL;DR
Design a highly available video streaming system that serves millions of concurrent users globally with minimal buffering. We build a decoupled architecture that separates video ingestion from real-time playback. This system transcodes master files into multiple codecs and bitrates via parallel batch jobs, storing the resulting chunks in object storage and distributing them to edge caches.

## The idea
Video streaming platforms face two competing pressures. They must ingest massive, high-quality source files from creators, and they must deliver smooth playback to clients with highly variable network speeds and diverse hardware. A single static video file cannot satisfy both. High-resolution files buffer constantly on mobile connections, while low-resolution files look terrible on large 4K TVs.

The core solution is to break videos into small temporal chunks, transcode each chunk into various resolutions, and serve them using adaptive bitrate protocols. By caching these static chunks near users, we reduce latency and protect core data centers. This case study shows how to build this pipeline at global scale.

## How it works

### 1. Requirements
#### Functional Requirements
- Creators can upload high-quality raw video files.
- Viewers can stream videos smoothly in real time without manual quality selection.
- The system must support metadata search, video recommendations, and digital rights management.

#### Non-Functional Requirements
- High availability for the playback path, targeting 99.99% uptime.
- Low latency start times with minimal playback buffering.
- Global scalability to support millions of concurrent viewers and massive egress traffic.

### 2. Back of the Envelope Estimation
Let's calculate the system storage and bandwidth demands for a platform with 100 million active users.

#### Peak Concurrent Streams
Assume 10% of our active users stream videos at peak times.
100,000,000 active users * 10% = 10,000,000 peak concurrent streams.

#### Storage per Movie across Renditions (Worked Detail)
When a raw 2-hour movie is uploaded, we transcode it into multiple formats.
- Average movie duration: 2 hours (7,200 seconds).
- Raw master upload: High-quality ProRes file, averaging 100 GB.
- We support three codecs: H.264 (for legacy compatibility), HEVC (for modern high-efficiency streaming), and AV1 (to save egress bandwidth on supported devices).
- For each codec, we generate five resolutions with different bitrates:
  - 360p at 500 kbps (0.5 Mbps)
  - 480p at 1 Mbps
  - 720p at 2.5 Mbps
  - 1080p at 5 Mbps
  - 4K at 15 Mbps
- Sum of bitrates for one codec: 0.5 + 1.0 + 2.5 + 5.0 + 15.0 = 24 Mbps.
- Total size for one codec's renditions: 24 Mbps * 7,200 seconds = 172,800 Mb = 21,600 MB = 21.6 GB.
- This results in 64.8 GB of transcoded storage across all three codecs.
- Adding the raw master file (100 GB) yields approximately 165 GB of total storage per movie.
- For a catalog of 50,000 titles, the total storage required is: 50,000 * 165 GB = 8.25 PB (Petabytes).

#### Peak Egress Bandwidth
With 10 million concurrent viewers streaming at an average bitrate of 3 Mbps, the peak bandwidth is:
10,000,000 concurrent viewers * 3 Mbps = 30,000,000 Mbps = 30 Tbps (Terabits per second).
In terms of data egress, this equals 3.75 TB (Terabytes) of video delivered per second.

### 3. API Sketch
The service exposes separate APIs for playback, ingestion, and catalog management.

#### Playback Session
`POST /api/v1/playback/session`
Request:
```json
{
  "video_id": "vid_98765",
  "device_type": "smart_tv",
  "supported_codecs": ["HEVC", "H264"]
}
```
Response:
```json
{
  "session_id": "sess_12345",
  "manifest_url": "https://manifest.netflix.com/vid_98765/manifest.m3u8",
  "drm_license_server": "https://drm.netflix.com/license",
  "initial_segment_duration_seconds": 5
}
```

#### Upload Initialization
`POST /api/v1/ingest/upload`
Request:
```json
{
  "title": "New Release",
  "duration_seconds": 7200,
  "file_size_bytes": 107374182400
}
```
Response:
```json
{
  "upload_id": "up_55443",
  "signed_url": "https://ingest-bucket.s3.amazonaws.com/raw/up_55443.mov"
}
```

### 4. Data Model
Metadata is kept in a relational database like PostgreSQL for ACID compliance on catalog updates, while playback state lives in a fast key-value store.

```
Table: Video
- id (UUID, Primary Key)
- title (VARCHAR)
- description (TEXT)
- duration_seconds (INT)
- created_at (TIMESTAMP)

Table: Video_Rendition
- id (UUID, Primary Key)
- video_id (UUID, Foreign Key)
- codec (VARCHAR)
- resolution (VARCHAR)
- bitrate_bps (INT)
- manifest_url (VARCHAR)

Table: Playback_Session (Redis Key-Value)
- Key: session_id
- Value: { user_id, video_id, last_offset_seconds, ip_address }
```

### 5. High Level Architecture

```
                                  [ Raw Video Upload ]
                                           |
                                           v
                            [ Asset Ingestion Service ]
                                           |
                                           v
                            [ Raw Object Storage S3 ]
                                           |
                                           v
                       +-------------------+-------------------+
                       |                                       |
                       v                                       v
               [ Chunker Service ]                   [ Catalog Metadata DB ]
                       |                                       |
                       v                                       v
          [ Message Queue (Kafka) ]                     [ API Gateway ]
                       |                                       |
                       v                                       |
          [ Transcoding Workers ] (DDIA Batch)                 |
                       |                                       |
                       v                                       |
         [ Rendition Object Storage ]                          |
                       |                                       |
                       +-------------------+-------------------+
                                           |
                                           v
                                   [ CDN Edge POPs ]
                                      ^         ^
                      Request segment |         | Request manifest
                                      |         v
                           [ Client Media Player ]
```

#### The Playback Flow (Worked Detail)
The player initiates playback by requesting a streaming manifest.
1. The client calls `POST /api/v1/playback/session` via the API Gateway.
2. Manifest services query catalog metadata and DRM services to build a customized manifest file (such as HLS or DASH).
3. Our server returns the manifest to the client. This file acts as an index, listing URLs for every 5-second video segment across all available bitrates and codecs.
4. A client media player parses the manifest, requesting the first 5-second segment in a conservative low-bitrate format from the nearest CDN.
5. While decoding and playing this segment, the player measures the actual download speed.
6. If the network throughput is high, the player requests the next segment at a higher resolution (e.g. 1080p).
7. When congestion occurs, the client automatically requests a lower-bitrate segment (e.g. 480p) to prevent buffering.

#### Sample Manifest Structure
The master HLS manifest (`manifest.m3u8`) coordinates the playback choices:
```
#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=640x360,CODECS="avc1.42c00d"
360p/manifest.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=5000000,RESOLUTION=1920x1080,CODECS="hev1.1.6.L120.90"
1080p/manifest.m3u8
```

The individual media playlist (`1080p/manifest.m3u8`) indexes the segments:
```
#EXTM3U
#EXT-X-TARGETDURATION=5
#EXTINF:5.0,
segment_001.ts
#EXTINF:5.0,
segment_002.ts
```

### 6. How It Scales

#### The Transcoding Pipeline (Worked Detail)
Raw master video uploads are too large for a single machine to process efficiently. We apply batch processing design patterns from DDIA Chapter 10 (ddia/10) to execute this work deterministically.
1. When the upload completes, the Chunker Service reads the raw master file from S3. It splits the video into exact 5-second temporal segments without decoding them.
2. The chunker writes metadata tasks to a high-throughput message queue like Apache Kafka (matching system-design/16 patterns).
3. Transcoding workers consume these tasks in parallel. Each task instructs a worker to download a specific 5-second raw segment, decode it, and encode it into target resolutions (360p up to 4K) and codecs (AVC, HEVC, AV1).
4. Workers output these transcoded fragments back to object storage.
5. Once all segments are processed, a coordinator task runs to generate the master manifest files indexing the fragments.

#### Distributed Caching with CDNs
Static video segments are highly cacheable. Instead of serving files from origin object storage, we deploy a distributed caching network (system-design/10).
- Edge POPs (Points of Presence) are located near metropolitan areas.
- We use a hybrid Push-Pull cache model. Popular new releases are pushed to CDNs in advance (pre-positioning). Older or niche content is pulled to the edge on demand when a user first requests it.
- This strategy maintains a cache hit ratio over 98%, dramatically reducing the cost and load on our central storage infrastructure.

#### DRM and Security
We secure high-value content using Digital Rights Management systems (like Widevine, FairPlay, or PlayReady). The client must request an encryption key from our DRM license server before playing any segment. This key is stored securely in the hardware of the playback device.

#### The Recommendation Pipeline
Recommendations are split into an offline precomputation phase and an online serving phase.
- Offline: Batch processing jobs run daily on historical view logs. These jobs compute movie similarity scores and precompute candidate recommendations for every user, storing them in a fast NoSQL database.
- Online: When a user visits the homepage, the online serving layer fetches the precomputed candidate list, filters out already watched titles, and runs a lightweight real-time model to rank the final suggestions.

### 7. Bottlenecks and Edge Cases
- **Transcoding Cold Start Latency**: New uploads might experience long queues during peak times. We mitigate this by prioritizing popular creators and splitting transcoding into dynamic worker groups.
- **CDN Cache Stampede**: When a highly anticipated show drops, millions of users request the exact same video segment at the same second. If the segment is not yet cached at the edge, all requests cascade to the origin storage. We resolve this by using locking caches at the CDN level, where only the first request is passed to origin, and subsequent requests wait to share the cached result.
- **Client Bandwidth Fluctuations**: Rapid switching between cellular and Wi-Fi networks can cause the player to oscillate bitrates too quickly. We implement a smoothing algorithm in the player client that uses exponential moving averages of bandwidth, preventing jarring resolution jumps.

## Pros
- Decoupling ingestion from playback ensures that slow video uploads never block streaming traffic.
- Using standardized 5-second chunks enables massive parallelization of transcoding tasks, reducing process time from hours to minutes.
- Distributing cached content through CDN edge nodes reduces origin egress costs and minimizes start latency.

## Cons
- Storage requirements multiply rapidly due to the combinations of codecs, resolutions, and bitrates required for diverse client devices.
- Manifest parsing and frequent segment switching increase client-side player logic complexity and resource usage.
- Orchestrating a parallel chunk-based transcoding workflow introduces significant tracking overhead and potential synchronization bugs.

## Alternatives
- **Dynamic On-The-Fly Transcoding**: Transcoding videos on demand when a user requests a specific resolution. This saves vast amounts of storage but introduces huge CPU latency and cost during playback, making it impractical for massive audiences.
- **Monolithic File Streaming**: Serving a single progressive MP4 file instead of chunked adaptive streaming. While simple to implement and manage, this approach fails on slow networks where users must wait for massive downloads before playback begins.

## When to use it
This architecture is ideal for large-scale video-on-demand platforms that serve global audiences with diverse devices. It is the gold standard when low-latency playback and reliable performance under varying network conditions are top business priorities.

## When NOT to use it
Avoid this design for simple internal applications or small websites hosting only a handful of videos. The engineering overhead, storage costs, and CDN configuration are unnecessary when progressive MP4 streaming from a single server can satisfy the user base.

## Key takeaways / mental model
The secret to global video streaming is to divide and conquer. Divide massive video files into tiny, immutable segments. Conquer playback latency by precomputing every rendition in parallel batch jobs and caching those segments at the network edge. The client acts as the intelligent controller, dynamically choosing which rendition to pull based on live network speeds.

## Self-check questions
1. Why do we divide video files into exact temporal chunks before transcoding, instead of processing the entire file as a single unit?
2. How does the client media player interact with the streaming manifest to achieve adaptive bitrate streaming?
3. What are the trade-offs of caching video content via a push strategy compared to a pull strategy on CDN edge nodes?
4. How do we prevent origin server crashes when a highly anticipated show causes a CDN cache stampede?
5. Why are legacy codecs like H.264 still generated alongside modern formats like HEVC and AV1?
6. In what ways does the chunked transcoding pipeline mirror the batch processing models described in DDIA Chapter 10?

## References
- System Design Guide for Software Professionals, Chapter 14
- Designing Data-Intensive Applications, Chapter 10 (Batch Processing)
- Sibling Lesson: Distributed Caching (system-design/10)
- Sibling Lesson: Distributed Messaging (system-design/16)
