# Patvero live transcription agent

This isolated service registers the explicitly named `patvero-transcriber`
LiveKit agent and publishes final and interim `lk.transcription` streams. The
web application consumes those streams through `useTranscriptions()`.

The service is intentionally independent from `/opt/patvero/livekit`, but runs
on the same media host with host networking so it can reach LiveKit at
`ws://127.0.0.1:7880`. Its health listener therefore binds host port `8081`;
that port must remain blocked by the host firewall and must not be publicly
exposed. The worker also needs outbound HTTPS access to OpenAI.

Required configuration is documented in `.env.example`. `LIVEKIT_AGENT_NAME`
must exactly match the API's `LIVEKIT_TRANSCRIPTION_AGENT_NAME`; otherwise a
dispatch remains pending and the UI reports captions as unavailable.

See [RUNBOOK.md](./RUNBOOK.md) for the production installation, validation,
upgrade, and rollback procedure.
