# Infrastructure mapping

The local stack mirrors a portable staging environment without requiring server purchases during account validation. It can be deployed to DigitalOcean first and moved to OVHcloud later without changing application code.

| Local service | Initial staging destination |
|---|---|
| LiveKit | OVH `c3-8` media server |
| Live transcription agent | Dedicated OVH application/agent worker |
| Redis | OVH `b3-8` private-network application server |
| NestJS API | OVH `b3-8` application server |
| PostgreSQL | Neon |
| Recordings and backups | OVH S3-compatible Object Storage |
| Web test console | Sites |

Redis is available to the host-only backend at `127.0.0.1:6380` and to LiveKit inside Docker at `redis:6379`.

The local stack also runs a dedicated LiveKit Egress `v1.12.0` worker. Room
composite recording is CPU intensive, so production Egress belongs on a
separate worker with at least 4 vCPUs and 4 GB RAM. Port `7979` exposes its
host-only health endpoint and `7978` exposes Prometheus metrics. The Egress
worker and LiveKit must use the same Redis instance and API credentials.

Live captions use the named `patvero-transcriber` LiveKit Agents worker in
`transcription-agent/`. The API dispatches it only when a meeting has
`transcriptionEnabled=true`; the worker then creates one STT session for each
remote participant and publishes `lk.transcription` text streams that the web
client already consumes. The worker uses OpenAI's realtime transcription API
directly with server-side voice activity detection, so it needs its own
`OPENAI_API_KEY` and outbound HTTPS/WebSocket access but does not download a
browser or local language model and needs no public inbound port. Use the same agent name in the worker's
`LIVEKIT_AGENT_NAME` and the API's `LIVEKIT_TRANSCRIPTION_AGENT_NAME` if either
is changed from the default.

For production, run the agent pool separately from the media and Egress nodes,
use a protected secret store, monitor the worker health endpoint and job errors,
and keep the 15-minute-or-longer graceful shutdown window so rolling restarts do
not immediately cut off active captions.

Recording objects remain private. The API supplies storage credentials to the
Egress job and later returns short-lived signed playback URLs. Apply
`storage-lifecycle.example.json` to the production bucket after matching its
transition storage class to the selected provider. Application retention jobs
delete the logical recording; bucket lifecycle rules provide a second safety
net for incomplete uploads and archival.

The local LiveKit image is pinned to `v1.13.5`. Production will use separate protected secrets, public TLS/TURN domains, the documented WebRTC firewall ports, and OVH private networking between LiveKit and Redis.

## Embedded Chat and phone-grade call signaling

Chat audio calls reuse the existing NestJS API and LiveKit deployment;
they do not add a public service or media port. The public API reverse proxy must
preserve the HTTP/1.1 WebSocket upgrade for
`/api/v1/messaging/calls/socket`. Caddy's standard `reverse_proxy` transport
does this automatically, but any replacement load balancer must forward
`Upgrade` and `Connection` and retain the existing TLS origin checks.

Call socket events are fanned out through the existing private Redis service,
with local delivery retained as a safe single-instance fallback. Every API
replica must use the same `REDIS_URL`; sticky sessions are not required. Ringing
expiry is a BullMQ delayed job on that same Redis deployment, with a database
sweeper retained for recovery after queue downtime.

Lock-screen mobile ringing also requires native provider credentials on the API:
`APNS_TEAM_ID`, `APNS_KEY_ID`, `APNS_BUNDLE_ID`, `APNS_PRIVATE_KEY` and
`FCM_SERVICE_ACCOUNT_JSON`. Keep these in the production secret store, not in
Compose files or the repository. APNs uses the `.voip` topic; Android uses
high-priority FCM data messages and the app's ConnectionService/foreground
microphone service. Build the mobile app as a native development or store build;
Expo Go cannot load CallKit or ConnectionService modules.

Call media still travels directly through LiveKit;
camera, screen-share, data publication, room administration, and recording are
disabled in the server-issued Chat-call token. Recording and transcription can
only be started by the call host after every active participant explicitly
consents through the call API.
