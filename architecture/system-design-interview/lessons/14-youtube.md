---
id: system-design-interview/14
subject: system-design-interview
title: "Design YouTube (Video Platform)"
slug: youtube
status: drafted
mastery: 
seniority: senior
source: "System Design Interview – An Insider's Guide, Vol. 1 (Alex Xu), Chapter 14"
prerequisites: [system-design-interview/01, system-design-interview/02, system-design-interview/03]
created: 2026-08-10
updated: 2026-08-10
---

# Design YouTube (Video Platform)

## TL;DR
A video platform's hardest problems are almost entirely on the upload/processing side,
not the read side: a raw uploaded video must be transcoded into multiple resolutions
and formats through a resilient, parallelizable pipeline, then served efficiently to a
global audience via a CDN using adaptive bitrate streaming. The interview deep dive
centers on the transcoding pipeline's architecture (chunking, parallelism,
DAG-based processing stages) and how adaptive bitrate streaming lets playback quality
adjust to each viewer's real-time network conditions.

## The idea
Serving a static video file is not the hard part of this system — a CDN can do that
efficiently once the file exists in the right formats. The hard part is getting from
"a user just uploaded a 4K, 2-hour raw video file" to "that video is available, quickly,
in multiple resolutions and formats suitable for phones on 3G, tablets on WiFi, and
smart TVs on gigabit fiber, without the upload pipeline falling over under the huge and
highly variable size/length of uploaded content." This asymmetry — an easy, well-solved
read path and a genuinely hard write/processing path — is what makes this a strong
senior-level design question.

## How it works

### Step 1: Clarify requirements
- **Core features.** Upload a video, transcode it into multiple resolutions, stream
  playback, basic metadata (title, description) and comments. (Assume: recommendation
  and search are explicitly out of scope, or noted as extensions, to keep the deep dive
  focused.)
- **Scale.** Assume 500 hours of video uploaded per minute, and a much larger, highly
  read-skewed viewing audience (billions of daily views).
- **Quality/format requirements.** Support multiple resolutions (e.g., 240p to 4K) and
  adaptive playback that adjusts to network conditions.
- **Latency tolerance for processing.** Upload-to-available doesn't need to be
  instantaneous (users tolerate a short "processing" delay), unlike, say, chat message
  delivery — a materially different latency budget than most other case studies in this
  subject, worth stating explicitly since it changes several design decisions
  downstream (e.g., justifying an asynchronous, queue-based processing pipeline).

### Step 2: Back-of-the-envelope
500 hours of video uploaded per minute ≈ `500 × 60 = 30,000 hours/day`. Assume average
raw upload bitrate of ~50 Mbps (a reasonably high-quality source before transcoding):
storage for raw uploads alone is roughly `30,000 hours × 3600 sec/hour × 50 Mbps / 8 =
~675,000,000 MB/day ≈ 675 TB/day` just for the raw, pre-transcoded originals — and each
video gets transcoded into several output resolutions/formats (each its own stored
file), multiplying total stored output considerably beyond the raw figure. This number
alone justifies why video storage lives in a dedicated, massively scalable object store
(e.g., S3-style blob storage), never in a relational database or even a general
key-value store — the storage and bandwidth profile is qualitatively different from
every other case study in this subject (compare to the ~90 GB/day of *text* in
`system-design-interview/02`'s tweet example — video storage is four to five orders of
magnitude larger per day).

### Step 3: High-level design
```
Upload/processing path:
[Client] --> [Upload Service] --> [Raw Storage] --> [Transcoding Pipeline] --> [Processed Storage] --> [CDN]

Playback path:
[Client] --> [CDN] --(miss)--> [Processed Storage]
                 |
          [Metadata Service] <--> [Database: video/user metadata]
```

- **Upload Service**: accepts the raw video file (often via chunked/resumable upload,
  given file sizes can be many GB), stores it in raw object storage, and enqueues a
  transcoding job.
- **Transcoding Pipeline**: the core deep-dive component (Step 4).
- **Processed Storage**: holds the transcoded outputs (multiple resolutions/formats),
  the files actually served to viewers.
- **CDN**: caches and serves the processed video files close to viewers, absorbing the
  overwhelming majority of playback bandwidth (recall: video's egress volume,
  driven by view count, dwarfs its ingress volume, exactly the pattern a CDN exists to
  handle — see `system-design-interview/02` and `system-design/06`).

### Step 4: Deep dive — the transcoding pipeline
Transcoding — converting the raw upload into multiple output resolutions/bitrates/codecs
— is CPU-intensive, can take significantly longer than the video's own runtime for
high resolutions, and must not block the upload response (the user shouldn't wait
minutes/hours staring at an upload spinner).

**Asynchronous processing via a queue.** The upload service enqueues a transcoding job
and returns success to the user immediately (the video shows as "processing"); a fleet
of transcoding workers consumes the queue — the same decoupling pattern used
throughout this subject (`system-design-interview/03`, `system-design-interview/10`),
here justified by processing time that can run into hours for long/high-resolution
source content, an even more extreme case than a slow third-party API call.

**Chunking for parallelism.** A 2-hour video transcoded as one single serial job would
take a very long time even on powerful hardware. Instead, split the source video into
smaller chunks (e.g., by GOP — Group of Pictures, a natural encoding boundary — or
fixed time segments), transcode chunks in parallel across many workers, then
reassemble/concatenate the transcoded chunks into the final output files per
resolution.

*Worked example:* a 2-hour video split into 120 one-minute chunks. Instead of one
worker processing the video serially (say, at 2x realtime speed, taking ~1 hour for a
2-hour video), 120 workers each process one ~1-minute chunk in parallel (each taking
~30 seconds at the same 2x-realtime rate) — the wall-clock time for the whole video
drops from roughly an hour to roughly 30 seconds plus a reassembly step, a large
practical improvement that directly reduces upload-to-available latency for the user.

**DAG-based pipeline stages.** Beyond simple parallel chunking, the book models the
pipeline as a directed acyclic graph (DAG) of stages: e.g., video segmentation → parallel
per-chunk transcoding (into each target resolution) → chunk reassembly → thumbnail
generation → DRM/watermarking (if required) → quality check → publish to processed
storage → CDN distribution. Modeling this explicitly as a DAG (rather than one
monolithic "transcode" step) lets independent stages run in parallel where they don't
depend on each other (e.g., thumbnail generation doesn't need to wait for every
resolution's transcode to finish) and lets a failure in one stage be retried without
re-running the entire pipeline from scratch.

**Handling failures mid-pipeline.** A worker can crash mid-chunk, or a specific
resolution's transcode can fail (e.g., a corrupt source segment). The pipeline needs
per-stage retry logic and idempotent stage outputs (retrying a chunk's transcode should
overwrite/replace its prior output cleanly, not create duplicates) — the same
idempotency discipline seen in `system-design-interview/10` and
`system-design-interview/12`, applied here at the level of pipeline stages rather than
individual messages.

### Step 5: Deep dive — adaptive bitrate streaming (the playback side)
Rather than serving one fixed-quality file, modern video platforms encode each video
into multiple resolution/bitrate variants (e.g., 240p/400kbps, 480p/1Mbps,
720p/2.5Mbps, 1080p/5Mbps, 4K/20Mbps) and split each variant into short segments
(typically a few seconds each), described by a manifest file (e.g., HLS or MPEG-DASH
format) that lists all available variants and their segment URLs.

**How the client adapts.** The video player continuously measures its actual download
throughput as it fetches segments, and for each upcoming segment, picks the
highest-quality variant it estimates it can fetch without stalling playback — switching
seamlessly between variants segment-by-segment as network conditions change, without an
interruption or full restart.

*Worked example:* a user starts watching on a strong WiFi connection; the player
selects 1080p segments. The user then walks outside onto a cellular connection with
degraded throughput; the player detects the drop in achieved download speed on the next
segment fetch and switches to fetching 480p segments for subsequent chunks — the video
continues playing smoothly at a lower visual quality rather than buffering/stalling.
This is the mechanism the transcoding pipeline in Step 4 exists to feed: without
multiple pre-encoded resolution variants sitting ready in storage, adaptive streaming
would have nothing to switch between.

### Step 6: Deep dive — CDN and caching strategy
Given the extreme read-skew (a small fraction of uploaded videos account for a large
share of total views — a long-tail popularity distribution typical of user-generated
content platforms), a CDN caching strategy that keeps popular content at edge locations
(reducing both latency and origin load) while falling back to origin (processed
storage) for the long tail of rarely-viewed content is the right default — this mirrors
the general cache/CDN reasoning from `system-design-interview/03`, but the popularity
skew here is typically even more extreme than in a social feed, because video content
has a much longer effective "shelf life" that a text post rarely does (a popular video
can be watched for years; a social post is mostly read within hours/days of posting).

### Step 7: Wrap-up — what to mention if pushed further
Content moderation (automated + human review pipelines), recommendation systems (a
large topic of its own, explicitly scoped out in Step 1), DRM for licensed content, and
live streaming (a fundamentally different latency budget than the on-demand upload
pipeline described here — live streaming can't tolerate the "processing delay" this
design assumes is acceptable) are all reasonable extensions to name explicitly as
out-of-scope, showing awareness without diluting the core deep dive.

## Pros
- Chunked, parallel, DAG-based transcoding turns an otherwise very slow serial
  operation into one that completes in a small fraction of the video's own runtime.
- Adaptive bitrate streaming means playback degrades gracefully under poor network
  conditions instead of stalling, directly improving the viewer experience.
- Decoupling upload (fast, synchronous) from transcoding (slow, asynchronous) keeps the
  user-facing upload experience responsive regardless of processing complexity.

## Cons
- The transcoding pipeline is a genuinely complex, resource-intensive piece of
  infrastructure (CPU/GPU-intensive workers, careful failure/retry handling, storage
  for many redundant resolution variants of the same content).
- Storing multiple resolution variants multiplies total storage several-fold over
  storing just the original — a real, ongoing storage cost trade-off against the
  playback-quality benefit.
- Upload-to-available latency, even optimized via chunked parallel processing, is
  fundamentally higher than most other systems in this subject — not a fit for any
  use case needing near-instant availability of user-generated video content.

## Alternatives
- **Serial, single-worker transcoding** — much simpler to implement and reason about,
  but processing time scales linearly with video length and resolution count, which is
  unacceptable at the scale and user-experience expectations assumed here; reasonable
  only for a very low-volume or non-time-sensitive use case.
- **A managed video processing/streaming platform** (e.g., a cloud provider's
  transcoding and streaming service) — in most real products, not worth building the
  full pipeline in-house; use a managed service unless video processing itself is the
  core product differentiator, similar to the "build vs. buy" note in
  `system-design-interview/09`'s crawler lesson.
- **Fixed single-resolution playback (no adaptive bitrate)** — much simpler client and
  server logic, but produces a materially worse experience under variable network
  conditions (stalling instead of smooth quality degradation); acceptable only if the
  target audience has uniformly strong, stable connectivity.

## When to use it
Any platform serving user-generated or licensed video content at meaningful scale where
playback quality across heterogeneous devices/networks matters: video-sharing
platforms, streaming services (with additional catalog/licensing concerns), e-learning
platforms with video lessons.

## When NOT to use it
For a small internal tool that occasionally needs to serve a handful of pre-recorded
videos (e.g., a company's internal training videos), the full chunked-parallel
transcoding pipeline and adaptive-bitrate infrastructure is significant
over-engineering — a single transcode step (even done serially) plus a CDN or even
direct object-storage serving of one or two fixed resolutions is more than sufficient.

## Key takeaways / mental model
Split the system's mental model cleanly in two: an asynchronous, throughput-oriented
"factory" (the transcoding pipeline — optimized for parallelism and resilience, not
latency, because users tolerate a short processing delay) that produces several
resolution variants of every video, and a synchronous, latency-oriented "storefront"
(the CDN-backed playback path) that serves those pre-built variants and lets each
individual viewer's client pick the best one for their current network conditions in
real time. Almost every hard design decision in this system falls out of optimizing one
side or the other of that split.

## Self-check questions
1. Why does the transcoding pipeline run asynchronously via a queue rather than
   synchronously within the upload request, and what latency-tolerance assumption from
   Step 1 justifies that choice?
2. Walk through why chunking a video into parallel segments for transcoding reduces
   wall-clock processing time, and what has to happen after the chunks are individually
   transcoded.
3. What specific problem does adaptive bitrate streaming solve for a viewer whose
   network conditions degrade mid-playback, and what does the transcoding pipeline need
   to have produced in advance for this to work?
4. Why does this system's storage/bandwidth profile (per Step 2's back-of-the-envelope)
   differ by orders of magnitude from, say, the tweet-storage example in
   `system-design-interview/02`, and what design decision does that difference justify?
5. A stakeholder asks whether this design could be reused as-is for a live-streaming
   feature. What specific assumption from Step 1 breaks, and why?

## References
- *System Design Interview – An Insider's Guide, Vol. 1* (Alex Xu), Chapter 14
