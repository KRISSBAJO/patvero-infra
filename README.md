# Patvero

A meeting and professional-services platform: scheduled and instant video
meetings on LiveKit, plus the booking, document, records and administration
systems built around them.

The video stack is the foundation rather than the whole product. Alongside
meetings the API carries a full booking and scheduling engine, a compliance-grade
professional records system, document lifecycle and e-signature workflows,
project and task tracking, messaging, workspaces and an operator control plane.

## Platform at a glance

| | |
|---|---|
| API | 28 feature modules, 34 controllers, 744 route handlers |
| Data | 318 PostgreSQL tables, 59 Drizzle migrations |
| Web | 126 pages (Next.js App Router) |
| Mobile | 61 screens (Expo Router) |
| Tests | 57 backend suites |

Principal domains:

- **Meetings** — scheduling, templates, recurrence, waiting room, breakout
  rooms, moderation, live captions, AI recap and meeting memory
- **Bookings** — event types, availability, calendar sync, routing forms,
  waitlists, resources, storefronts, commerce and invoicing
- **Records** — professional cases, encounters, entries, attestations and
  amendments, with legal holds, break-glass access, retention policies,
  disclosure authorizations and deletion certificates
- **Documents** — lifecycle workflows, signature fields, client file requests
- **Collaboration** — messaging, notes, projects and tasks, pulse, office
- **Administration** — feature flags, incidents, audit, finance, queue and
  webhook operations, trust and safety cases
- **Platform** — subscriptions and entitlements, notifications, recordings and
  transcripts, universal search, resumable uploads, workspaces

Pilot operations for the gated Patvero Church commercial launch are documented
in [the Winners Chapel Phase 5 runbook](docs/phase5-winners-chapel-pilot-runbook.md).

## Project layout

```text
liveKit-video-folder/
|-- liveKit-be/             NestJS API: meetings, bookings, records, admin, LiveKit
|-- liveKit-video-fe/       Next.js 15 web application
|-- liveKit-video-mobile/   Expo SDK 54 React Native application
`-- liveKit-video-infra/    Docker LiveKit/Egress/Redis and the transcription agent
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
| Web application | http://localhost:3200 |
| NestJS API | http://localhost:3101/api |
| Metro bundler | http://localhost:8087 |
| LiveKit WebSocket | ws://localhost:7880 |
| LiveKit TCP fallback | localhost:7881 |
| Redis | localhost:6380 plus Docker-private `redis:6379` |
| PostgreSQL | Neon development database |

Routes are versioned in the URI behind the `api` prefix, so endpoints are served
at `/api/v1/...`.

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

`npm run db:seed` creates the plan catalog, the `local-test-user` identity with a
`development-pro` entitlement, and a development administrator from `ADMIN_EMAIL`
and `ADMIN_PASSWORD` with an enterprise entitlement.

Open http://localhost:3200 and sign in or create an account. To test a second
participant, start a meeting, copy its join link, and open that link in a private
browser window.

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
installed Patvero app while Metro is running. Expo Go is not supported.

## API contracts

The backend is the single source of truth for client types. `npm run
contracts:update` regenerates `liveKit-be/openapi/video-api.json` from the Nest
decorators, then regenerates the typed client in the web application. The mobile
app reads the same schema through `npm --prefix liveKit-video-mobile run
contracts:generate`.

Both clients check the generated file into source control, and their `ci`
scripts fail when it drifts from the schema. Regenerate both after changing any
controller signature or DTO.

## Authentication model

The API resolves four kinds of principal, selected by the token it receives:

| Principal | Token | Source |
|---|---|---|
| First-party member | `mhu_` prefix | Patvero accounts, email and password |
| Guest | `mhg_` prefix | redeemed meeting invitation |
| Mohuddle member | signed JWT | the external Mohuddle identity provider |
| Development | `x-test-user-id` header | local only, see below |

Tokens arrive as a `Bearer` header or the `mh_access` cookie; the web client
refreshes expired sessions automatically. Administration is a separate plane with
its own guard, session TTL, IP allowlist, and TOTP or WebAuthn second factor.

"Mohuddle" throughout the auth code refers to that external identity provider,
verified through `MOHUDDLE_JWT_ISSUER`, `MOHUDDLE_JWT_AUDIENCE` and
`MOHUDDLE_JWKS_URL`. It is not the product name.

## Validate

```powershell
npm run build
npm run test
npm run validate
```

## Development security boundary

`ALLOW_TEST_IDENTITIES=true` and the `x-test-user-id` header are only for local
development. The seeded `local-test-user` carries a `development-pro`
entitlement. Missing identities receive `401`; inactive, missing, or expired
subscriptions receive `402`.

Before any public deployment, test identities must be disabled and replaced with
verified Mohuddle authentication. The subscription check remains server-side.
LiveKit and database secrets must never be included in web or mobile
applications.

## Neon database

Keep the pooled Neon connection in the ignored `liveKit-be/.env` as
`DATABASE_URL`. Prefer the unpooled Neon connection as `DIRECT_DATABASE_URL` when
running production migrations. During development, the migration runner falls
back to `DATABASE_URL` when the direct URL is not yet supplied.

```powershell
npm run db:generate
npm run db:migrate
npm run db:seed
```

The schema covers subscription entitlements, meeting lifecycle records,
idempotent LiveKit webhook events, a transactional notification outbox, and the
booking, records, document and administration domains. LiveKit signs every
webhook, the API verifies the original raw bytes, and duplicate event IDs are
ignored safely.

Migrations under `liveKit-be/drizzle/` and their `meta/` snapshots are applied
history. Never edit them; add a new migration instead.

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
until the save confirmation appears. Local-only files never enter Patvero's
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

Implemented:

- Meeting lifecycle, scheduling, moderation, captions and meeting memory
- Booking engine through commerce and enterprise routing
- Professional records with governance, retention and disclosure controls
- Document lifecycle and signature workflows
- Administration control plane, audit and observability
- Subscriptions, entitlements and plan gating
- Egress recording lifecycle, private S3 playback, retention and transcript APIs
- Notification outbox, BullMQ delivery, in-app inbox, Expo push and email
- OpenAPI contracts, background jobs and CI across all three applications

Pending:

- Mohuddle production authentication, until the platform is integrated
- Physical-device validation matrix for the mobile client
- Production Egress worker and OVH Object Storage credentials
- OVH staging domains, TLS, TURN, monitoring and backups
- Completing the Mohuddle to Patvero rename beyond user-facing copy: internal
  symbols, client storage keys, package names and the EAS slug still use the
  former name
