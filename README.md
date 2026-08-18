# Mohuddle LiveKit Lab

An isolated environment for proving Mohuddle video behavior before integrating it into the main product.

## Project layout

```text
liveKit-video-folder/
|-- liveKit-be/             NestJS token, room administration, and webhook API
|-- liveKit-video-fe/       Next-style Sites/Vinext web testing console
|-- liveKit-video-mobile/   Expo React Native LiveKit client
`-- liveKit-video-infra/    Local Docker and later OVH deployment configuration
```

## Subproject versions

`liveKit-be`, `liveKit-video-fe`, and `liveKit-video-mobile` are separate Git
repositories with their own remotes, so this repository does not contain their
code. `workspace.lock.json` records the commit of each one that forms a known
working set, and `liveKit-video-infra` is tracked here directly.

```powershell
npm run pin:check    # verify the three checkouts match the lock file
npm run pin:sync     # restore the pinned commits (refuses if a repo is dirty)
npm run pin:update   # record the current commits as the new working set
```

`npm run validate` runs `pin:check` first, so a mismatched set fails before the
build does.

## Local services

| Service | Address |
|---|---|
| Web test console | http://localhost:3200 |
| NestJS API | http://localhost:3101/api |
| LiveKit WebSocket | ws://localhost:7880 |
| LiveKit TCP fallback | localhost:7881 |
| Redis | localhost:6380 plus Docker-private `redis:6379` |
| PostgreSQL | Neon development database |

## Start locally

Prerequisites: Node.js 22+, npm, and Docker Desktop.

```powershell
cd C:\Users\kriss\liveKit-video-folder
npm install
npm run infra:up
npm run db:migrate
npm run db:seed
npm run contracts:update
npm run dev:api
```

In another terminal:

```powershell
cd C:\Users\kriss\liveKit-video-folder
npm run dev:web
```

Open http://localhost:3200, join `first-room`, then open a private browser window with the same room code to test a second participant.

The mobile app requires an Expo development build because Expo Go cannot load
LiveKit's native WebRTC module:

```powershell
Copy-Item liveKit-video-mobile/.env.example liveKit-video-mobile/.env
npm --prefix liveKit-video-mobile run android
# after installing the development build
npm run dev:mobile
```

On a physical phone, set `EXPO_PUBLIC_VIDEO_API_URL` to this computer's LAN
address, such as `http://192.168.1.50:3101/api/v1`.

For an iPhone development build with Expo SDK 54:

```powershell
cd C:\Users\kriss\liveKit-video-folder\liveKit-video-mobile
npx eas-cli login
npx eas-cli device:create
npx eas-cli build --profile development --platform ios
npm start
```

Install the EAS build from its link on the registered iPhone, then open the
installed Mohuddle app while Metro is running. Expo Go is not supported.

## Validate

```powershell
npm run build
npm run test
npm run validate
```

## Development security boundary

`ALLOW_TEST_IDENTITIES=true` and the `x-test-user-id` header are only for this local lab. The test console sends `local-test-user`, which has a seeded `development-pro` entitlement. Missing identities receive `401`; inactive, missing, or expired subscriptions receive `402`.

Before any public deployment, test identities must be disabled and replaced with verified Mohuddle authentication. The subscription check remains server-side. LiveKit and database secrets must never be included in web or mobile applications.

## Neon database

Keep the pooled Neon connection in the ignored `liveKit-be/.env` as `DATABASE_URL`. Prefer the unpooled Neon connection as `DIRECT_DATABASE_URL` when running production migrations. During development, the migration runner falls back to `DATABASE_URL` when the direct URL is not yet supplied.

```powershell
npm run db:generate
npm run db:migrate
npm run db:seed
```

The migrations create subscription entitlements, meeting lifecycle records, idempotent LiveKit webhook events and a transactional notification outbox. LiveKit signs every webhook, the API verifies the original raw bytes, and duplicate event IDs are ignored safely.

## Recording, playback and transcripts

LiveKit Egress runs as a separate worker and shares LiveKit's Redis and API
credentials. The API starts and stops room-composite MP4 or HLS jobs, persists
job/webhook state, enforces subscription storage quotas and retention, and
writes outputs directly to private S3-compatible storage. Clients receive only
short-lived signed playback/download URLs.

Web hosts can alternatively choose **This computer** or **Both** from the room
recording panel. The browser composites the visible meeting stage, mixes the
published meeting audio, and records MP4 when supported or WebM otherwise.
Chromium browsers can stream chunks directly to a user-selected file through
the File System Access API; other supported browsers retain timed chunks and
download the completed file when recording stops. Keep the meeting tab open
until the save confirmation appears. Local-only files never enter Mohuddle's
recording library, storage quota, transcription pipeline, or sharing system.
The backend still records the local lifecycle, consent and audit trail, and all
participants receive the distinct **Local REC** notice on web and mobile.

The product includes recording consent, visible web/mobile indicators,
automatic recording, a recording library, controlled/revocable sharing,
retention deletion, thumbnail output, transcript job callbacks, searchable
speaker segments, transcript editing and TXT/VTT/JSON downloads. Configure
`TRANSCRIPTION_PROVIDER_URL` and `TRANSCRIPTION_PROVIDER_TOKEN` to connect a
speech-to-text worker. Without that worker, recording works but requested
transcripts remain in processing until the signed callback is delivered.

Recordable meetings use LiveKit transport encryption. Strict E2EE is rejected
for this workflow because an Egress or transcription worker cannot process
media whose keys are available only to participants.

## Notification delivery

Meeting events are written transactionally to `outbox_events`, claimed by the
outbox publisher, and delivered through BullMQ. The worker fans events out to
the in-app inbox, Expo push and Resend email according to each user's
preferences. Deliveries are idempotent, retries use exponential backoff, and
exhausted jobs are persisted in `notification_dead_letters`.

Invitation reminders are scheduled 15 minutes before a meeting. Quiet hours
are evaluated in the recipient's configured IANA time zone, and email includes
a signed unsubscribe link.

## Current status

- Neon PostgreSQL connection and initial migration: complete for development
- Signed LiveKit webhook persistence and idempotency: complete
- Development subscription enforcement: complete
- Phase One API foundation, OpenAPI contracts, background jobs and CI: complete
- Mohuddle production authentication: pending until the lab is integrated
- Expo SDK 54 mobile client, notification inbox and recording consent: implemented; physical-device matrix validation pending
- Egress recording lifecycle, private S3 playback, retention and transcript APIs: implemented
- Production Egress worker and OVH Object Storage credentials: pending server provisioning
- OVH staging domains, TLS, TURN, monitoring, and backups: pending
