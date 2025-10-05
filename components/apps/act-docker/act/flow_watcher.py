#!/usr/bin/env python3
"""
Flow File Watcher - Hot Reload System
Monitors flow file for changes and triggers automatic reload
"""

import os
import time
import threading
import logging
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class FlowWatcher:
    """
    Watches the flow file for changes and triggers reload callbacks.
    Features:
    - Debouncing (prevents multiple reloads for same change)
    - Change detection (only reload if content actually changed)
    - Thread-safe operation
    """

    def __init__(
        self,
        flow_path: str = "/app/flow",
        check_interval: float = 1.0,
        debounce_seconds: float = 0.5
    ):
        self.flow_path = Path(flow_path)
        self.check_interval = check_interval
        self.debounce_seconds = debounce_seconds

        self._last_mtime: Optional[float] = None
        self._last_content: Optional[str] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: list[Callable] = []
        self._lock = threading.Lock()

        logger.debug(f"FlowWatcher initialized for: {self.flow_path}")

    def register_callback(self, callback: Callable):
        """Register a callback to be called when flow file changes"""
        with self._lock:
            self._callbacks.append(callback)
            logger.debug(f"Registered callback: {callback.__name__}")

    def start(self):
        """Start watching the flow file"""
        if self._running:
            logger.warning("FlowWatcher already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
        logger.info(f"🔍 FlowWatcher started - monitoring {self.flow_path}")

    def stop(self):
        """Stop watching the flow file"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("🛑 FlowWatcher stopped")

    def _watch_loop(self):
        """Main watch loop - runs in separate thread"""
        while self._running:
            try:
                if self._check_for_changes():
                    # Debounce: wait a bit to ensure file write is complete
                    time.sleep(self.debounce_seconds)

                    # Check again after debounce
                    if self._check_for_changes():
                        self._trigger_callbacks()

                time.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"Error in watch loop: {e}", exc_info=True)
                time.sleep(self.check_interval)

    def _check_for_changes(self) -> bool:
        """Check if flow file has changed"""
        try:
            if not self.flow_path.exists():
                # File doesn't exist yet - check if it did before
                if self._last_mtime is not None:
                    logger.warning(f"Flow file disappeared: {self.flow_path}")
                    self._last_mtime = None
                    self._last_content = None
                    return True
                return False

            # Get file modification time
            mtime = self.flow_path.stat().st_mtime

            # First time checking or mtime changed
            if self._last_mtime is None or mtime != self._last_mtime:
                # Read content to verify actual change
                content = self.flow_path.read_text(encoding='utf-8')

                # Content actually changed?
                if content != self._last_content:
                    logger.debug(f"Flow file changed - mtime: {mtime}")
                    self._last_mtime = mtime
                    self._last_content = content
                    return True
                else:
                    # mtime changed but content same (e.g., touch command)
                    self._last_mtime = mtime
                    return False

            return False

        except Exception as e:
            logger.error(f"Error checking file changes: {e}")
            return False

    def _trigger_callbacks(self):
        """Trigger all registered callbacks"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"🔄 Flow file changed at {timestamp} - triggering reload...")

        with self._lock:
            for callback in self._callbacks:
                try:
                    logger.debug(f"Executing callback: {callback.__name__}")
                    callback()
                except Exception as e:
                    logger.error(f"Error in callback {callback.__name__}: {e}", exc_info=True)

    def force_reload(self):
        """Force a reload even if file hasn't changed"""
        logger.info("🔄 Force reload requested")
        self._trigger_callbacks()

    def get_flow_info(self) -> dict:
        """Get information about the current flow file"""
        try:
            if not self.flow_path.exists():
                return {
                    "exists": False,
                    "path": str(self.flow_path),
                    "size": 0,
                    "modified": None
                }

            stat = self.flow_path.stat()
            return {
                "exists": True,
                "path": str(self.flow_path),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "watching": self._running
            }
        except Exception as e:
            logger.error(f"Error getting flow info: {e}")
            return {"error": str(e)}


# Singleton instance
_watcher_instance: Optional[FlowWatcher] = None


def get_watcher(flow_path: str = "/app/flow") -> FlowWatcher:
    """Get or create the singleton FlowWatcher instance"""
    global _watcher_instance

    if _watcher_instance is None:
        _watcher_instance = FlowWatcher(flow_path)

    return _watcher_instance
