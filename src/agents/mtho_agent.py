# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Ghost Agent: Kurzlebige Sub-Instanz fuer Intent-Verarbeitung (Signal-Vektor 2).

Lebenszyklus:
1. Spawn: Bei Intent-Erkennung (Takt 2)
2. Execute: Verarbeitet den spezifischen Intent
3. Report: Liefert Ergebnis an Pool
4. Die: Selbstterminierung nach Erfuellung

Architektur:
- GhostAgent: Einzelne Instanz mit TTL
- GhostAgentPool: Verwaltet aktive Ghosts, Garbage Collection

Integration:
- Hoeren: scout_direct_handler.process_text() spawnt Ghost bei deep_reasoning
- Sehen: vision_daemon spawnt Ghost bei Symmetriebruch-Events
- Sprechen: Ghost kann TTS triggern
"""
from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine
from loguru import logger


class GhostIntent(Enum):
    """Intent-Typen fuer Ghost Agents (Signal-Vektor 2)."""
    COMMAND = "command"
    DEEP_REASONING = "deep_reasoning"
    VISION_ANALYSIS = "vision_analysis"
    TTS_DISPATCH = "tts_dispatch"
    FAILOVER = "failover"


@dataclass
class GhostResult:
    """Ergebnis eines Ghost Agent Tasks."""
    success: bool
    intent: GhostIntent
    payload: Any = None
    error: str | None = None
    duration_ms: float = 0.0


@dataclass
class GhostAgent:
    """
    Kurzlebige Sub-Instanz fuer Intent-Verarbeitung.
    Stirbt nach TTL oder nach Erfuellung.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    intent: GhostIntent = GhostIntent.COMMAND
    payload: dict = field(default_factory=dict)
    ttl_seconds: float = 30.0
    created_at: float = field(default_factory=time.time)
    completed: bool = False
    result: GhostResult | None = None

    @property
    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.ttl_seconds

    @property
    def age_ms(self) -> float:
        return (time.time() - self.created_at) * 1000

    async def execute(self, handler: Callable[..., Coroutine[Any, Any, Any]]) -> GhostResult:
        """
        Fuehrt den Intent-Handler aus und terminiert.
        """
        start = time.time()
        try:
            logger.debug(f"[GHOST-{self.id}] Spawn: {self.intent.value}")
            result_payload = await handler(self.payload)
            duration = (time.time() - start) * 1000
            self.result = GhostResult(
                success=True,
                intent=self.intent,
                payload=result_payload,
                duration_ms=duration
            )
            logger.debug(f"[GHOST-{self.id}] Complete: {duration:.1f}ms")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self.result = GhostResult(
                success=False,
                intent=self.intent,
                error=str(e),
                duration_ms=duration
            )
            logger.warning(f"[GHOST-{self.id}] Failed: {e}")
        finally:
            self.completed = True
        return self.result


class GhostAgentPool:
    """
    Pool fuer Ghost Agents mit automatischer Garbage Collection.
    """
    def __init__(self, max_concurrent: int = 10, gc_interval: float = 5.0):
        self._agents: dict[str, GhostAgent] = {}
        self._max_concurrent = max_concurrent
        self._gc_task: asyncio.Task | None = None
        self._gc_interval = gc_interval
        self._handlers: dict[GhostIntent, Callable] = {}

    def register_handler(self, intent: GhostIntent, handler: Callable):
        """Registriert einen Handler fuer einen Intent-Typ."""
        self._handlers[intent] = handler
        logger.info(f"[GHOST-POOL] Handler registriert: {intent.value}")

    async def spawn(
        self,
        intent: GhostIntent,
        payload: dict,
        ttl: float = 30.0
    ) -> GhostAgent:
        """
        Spawnt einen neuen Ghost Agent.
        Wirft Exception wenn Pool voll.
        """
        self._gc_sync()
        
        if len(self._agents) >= self._max_concurrent:
            raise RuntimeError(f"Ghost Pool erschoepft ({self._max_concurrent} max)")

        ghost = GhostAgent(intent=intent, payload=payload, ttl_seconds=ttl)
        self._agents[ghost.id] = ghost
        logger.debug(f"[GHOST-POOL] Spawned {ghost.id} ({len(self._agents)} aktiv)")
        return ghost

    async def execute(self, ghost: GhostAgent) -> GhostResult:
        """
        Fuehrt einen Ghost Agent aus (sucht passenden Handler).
        """
        handler = self._handlers.get(ghost.intent)
        if not handler:
            ghost.completed = True
            ghost.result = GhostResult(
                success=False,
                intent=ghost.intent,
                error=f"Kein Handler fuer Intent: {ghost.intent.value}"
            )
            return ghost.result
        return await ghost.execute(handler)

    async def spawn_and_execute(
        self,
        intent: GhostIntent,
        payload: dict,
        ttl: float = 30.0
    ) -> GhostResult:
        """
        Convenience: Spawnt und fuehrt Ghost in einem Schritt aus.
        """
        ghost = await self.spawn(intent, payload, ttl)
        return await self.execute(ghost)

    def _gc_sync(self):
        """Synchrone Garbage Collection: Entfernt abgelaufene/erledigte Ghosts."""
        to_remove = [
            gid for gid, g in self._agents.items()
            if g.completed or g.is_expired
        ]
        for gid in to_remove:
            del self._agents[gid]
        if to_remove:
            logger.debug(f"[GHOST-POOL] GC: {len(to_remove)} Ghosts entfernt")

    async def start_gc_loop(self):
        """Startet den Garbage Collection Loop (fuer Daemon-Betrieb)."""
        async def _gc_loop():
            while True:
                await asyncio.sleep(self._gc_interval)
                self._gc_sync()
        self._gc_task = asyncio.create_task(_gc_loop())

    async def stop(self):
        """Stoppt den GC Loop und alle Ghosts."""
        if self._gc_task:
            self._gc_task.cancel()
        self._agents.clear()

    @property
    def active_count(self) -> int:
        return len([g for g in self._agents.values() if not g.completed])

    @property
    def stats(self) -> dict:
        return {
            "active": self.active_count,
            "total": len(self._agents),
            "max": self._max_concurrent,
            "handlers": list(self._handlers.keys())
        }


# Singleton Pool fuer globale Nutzung
_global_pool: GhostAgentPool | None = None


def get_ghost_pool() -> GhostAgentPool:
    """Liefert den globalen Ghost Agent Pool (Singleton)."""
    global _global_pool
    if _global_pool is None:
        _global_pool = GhostAgentPool()
    return _global_pool
