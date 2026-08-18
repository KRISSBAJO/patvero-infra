# Production runbook

## Install at `/opt/patvero/transcriber`

1. Copy this directory to `/opt/patvero/transcriber` on the Patvero media host.
   Keep it as a separate Compose project from `/opt/patvero/livekit`.
2. Copy `.env.example` to `.env`, enter the LiveKit and OpenAI credentials, and
   set file mode `600`. Never put `.env` in source control or command output.
3. Keep `LIVEKIT_URL=ws://127.0.0.1:7880`. The standalone Compose project uses
   host networking to reach the existing local LiveKit process. Use an API
   key/secret scoped to this Patvero deployment, not another product.
4. Keep `LIVEKIT_AGENT_NAME=patvero-transcriber` and configure the API with
   `LIVEKIT_TRANSCRIPTION_AGENT_NAME=patvero-transcriber`.

Validate and start:

```sh
cd /opt/patvero/transcriber
docker compose config --quiet
docker compose build --pull transcriber
docker compose up -d transcriber
docker compose ps
docker compose logs --tail=100 transcriber
```

The container is healthy only after the LiveKit worker process exposes its
health endpoint on host port `8081`. Confirm UFW does not allow public access to
`8081`; the port is for local health checks only. A healthy container does not by itself prove OpenAI can
transcribe; run a private two-device meeting and verify that enabling Captions
returns `running` and text appears for both speakers.

## Routine checks

```sh
cd /opt/patvero/transcriber
docker compose ps
docker compose logs --since=15m transcriber
docker inspect --format '{{json .State.Health}}' patvero-transcriber-transcriber-1
```

Alert on container restarts, unhealthy state, LiveKit dispatches stuck in
`pending`, provider authentication/rate-limit errors, and missing transcription
events. Container logs rotate at 10 MB with five retained files.

## Upgrade

```sh
cd /opt/patvero/transcriber
docker compose build --pull transcriber
docker compose up -d --no-deps transcriber
docker compose ps
```

Schedule upgrades outside active meetings. The two-minute stop grace period lets
the worker drain active sessions, but a replacement worker does not preserve an
in-flight provider stream.

## Rollback

Retag or restore the previous image in `TRANSCRIPTION_AGENT_IMAGE`, then run:

```sh
cd /opt/patvero/transcriber
docker compose up -d --no-deps transcriber
docker compose ps
docker compose logs --tail=100 transcriber
```

If the worker must be disabled, run `docker compose stop transcriber`. The API
will return an unavailable/pending caption state instead of telling users that
captions are active. Existing audio/video meetings remain unaffected.

## Secret rotation

Rotate the LiveKit API key/secret and OpenAI key whenever access changes or the
service is transferred. Update `.env`, restart the container, and then revoke
the old credentials. Never reuse Patvero's credentials for a sold or separate
Mohuddle deployment.
