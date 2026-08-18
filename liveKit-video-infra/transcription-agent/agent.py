import asyncio
import logging
import os

from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    AutoSubscribe,
    JobContext,
    StopResponse,
    cli,
    llm,
    room_io,
    utils,
)
from livekit.plugins import openai

from transcription_config import language_from_job_metadata


logger = logging.getLogger("patvero-transcriber")
AGENT_NAME = os.getenv("LIVEKIT_AGENT_NAME", "patvero-transcriber").strip()


class Transcriber(Agent):
    def __init__(self, *, participant_identity: str, language: str):
        super().__init__(
            instructions="Transcribe the selected participant without replying.",
            stt=openai.STT(
                model=os.getenv(
                    "OPENAI_TRANSCRIPTION_MODEL",
                    "gpt-4o-mini-transcribe",
                ),
                language=language,
                use_realtime=True,
            ),
        )
        self.participant_identity = participant_identity

    async def on_user_turn_completed(
        self,
        chat_ctx: llm.ChatContext,
        new_message: llm.ChatMessage,
    ) -> None:
        # AgentSession has already forwarded the transcript to lk.transcription.
        # Stop here so an STT-only session never attempts an LLM response.
        del chat_ctx, new_message
        raise StopResponse()


class MultiUserTranscriber:
    def __init__(self, ctx: JobContext, *, language: str):
        self.ctx = ctx
        self.language = language
        self._sessions: dict[str, AgentSession] = {}
        self._starting: dict[str, asyncio.Task[AgentSession]] = {}
        self._closing: set[asyncio.Task[None]] = set()

    def start(self) -> None:
        self.ctx.room.on("participant_connected", self.on_participant_connected)
        self.ctx.room.on("participant_disconnected", self.on_participant_disconnected)

    async def aclose(self) -> None:
        self.ctx.room.off("participant_connected", self.on_participant_connected)
        self.ctx.room.off("participant_disconnected", self.on_participant_disconnected)

        starting = list(self._starting.values())
        self._starting.clear()
        for task in starting:
            task.cancel()
        await utils.aio.cancel_and_wait(*starting)

        sessions = list(self._sessions.values())
        self._sessions.clear()
        await asyncio.gather(
            *(self._close_session(session) for session in sessions),
            return_exceptions=True,
        )

        closing = list(self._closing)
        self._closing.clear()
        if closing:
            await asyncio.gather(*closing, return_exceptions=True)

    def on_participant_connected(self, participant: rtc.RemoteParticipant) -> None:
        identity = participant.identity
        if identity in self._sessions or identity in self._starting:
            return

        logger.info("Starting transcription for participant %s", identity)
        task = asyncio.create_task(self._start_session(participant))
        self._starting[identity] = task
        task.add_done_callback(
            lambda completed, participant_identity=identity: self._session_started(
                participant_identity,
                completed,
            ),
        )

    def on_participant_disconnected(self, participant: rtc.RemoteParticipant) -> None:
        identity = participant.identity
        starting = self._starting.pop(identity, None)
        if starting is not None:
            starting.cancel()

        session = self._sessions.pop(identity, None)
        if session is not None:
            logger.info("Stopping transcription for participant %s", identity)
            self._track_close(self._close_session(session))

    def _session_started(
        self,
        identity: str,
        task: asyncio.Task[AgentSession],
    ) -> None:
        self._starting.pop(identity, None)
        if task.cancelled():
            return

        try:
            session = task.result()
        except Exception:
            logger.exception("Could not start transcription for participant %s", identity)
            return

        if identity not in self.ctx.room.remote_participants:
            self._track_close(self._close_session(session))
            return

        self._sessions[identity] = session

    def _track_close(self, coroutine) -> None:
        task = asyncio.create_task(coroutine)
        self._closing.add(task)
        task.add_done_callback(self._close_finished)

    def _close_finished(self, task: asyncio.Task[None]) -> None:
        self._closing.discard(task)
        if task.cancelled():
            return
        try:
            task.result()
        except Exception:
            logger.exception("Could not close a participant transcription session")

    async def _start_session(
        self,
        participant: rtc.RemoteParticipant,
    ) -> AgentSession:
        session = AgentSession()
        await session.start(
            agent=Transcriber(
                participant_identity=participant.identity,
                language=self.language,
            ),
            room=self.ctx.room,
            room_options=room_io.RoomOptions(
                audio_input=True,
                audio_output=False,
                text_input=False,
                text_output=True,
                participant_identity=participant.identity,
            ),
        )
        return session

    @staticmethod
    async def _close_session(session: AgentSession) -> None:
        try:
            await session.drain()
        finally:
            await session.aclose()


# Realtime STT setup is lightweight and external; one warm process avoids the
# SDK's CPU-count-sized default pool competing with the media host.
server = AgentServer(num_idle_processes=1)


@server.rtc_session(agent_name=AGENT_NAME)
async def entrypoint(ctx: JobContext) -> None:
    language = language_from_job_metadata(ctx.job.metadata)
    transcriber = MultiUserTranscriber(ctx, language=language)
    transcriber.start()

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    for participant in ctx.room.remote_participants.values():
        transcriber.on_participant_connected(participant)

    ctx.add_shutdown_callback(transcriber.aclose)


def validate_environment() -> None:
    required = (
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "OPENAI_API_KEY",
    )
    missing = [name for name in required if not os.getenv(name, "").strip()]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing),
        )
    if not AGENT_NAME:
        raise RuntimeError("LIVEKIT_AGENT_NAME must not be blank")


if __name__ == "__main__":
    validate_environment()
    cli.run_app(server)
