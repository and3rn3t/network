"""
Scheduler for periodic data collection.

Runs the data collector at specified intervals.
"""

import logging
import signal
import time
from datetime import datetime
from threading import Event as ThreadEvent
from typing import Callable, Optional

from .config import CollectorConfig
from .data_collector import DataCollector

logger = logging.getLogger(__name__)


class CollectionScheduler:
    """
    Scheduler for periodic data collection.

    Runs data collector at configured intervals with graceful shutdown support.
    """

    def __init__(self, collector: DataCollector):
        """
        Initialize scheduler.

        Args:
            collector: DataCollector instance to run
        """
        self.collector = collector
        self.config = collector.config
        self._stop_event = ThreadEvent()
        self._running = False

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("CollectionScheduler initialized")

    def _signal_handler(self, signum, frame):
        """
        Handle shutdown signals.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.stop()

    def start(self, immediate: bool = True) -> None:
        """
        Start the scheduler.

        Args:
            immediate: If True, run first collection immediately
        """
        if self._running:
            logger.warning("Scheduler already running")
            return

        self._running = True
        self._stop_event.clear()

        logger.info(
            f"Starting scheduler with {self.config.collection_interval}s interval"
        )

        # Run immediately if requested
        if immediate:
            logger.info("Running immediate collection")
            try:
                self.collector.collect()
            except Exception as e:
                logger.error(f"Initial collection failed: {e}", exc_info=True)

        # Main collection loop
        while not self._stop_event.is_set():
            try:
                # Wait for next collection interval
                next_run = time.time() + self.config.collection_interval
                logger.info(
                    f"Next collection in {self.config.collection_interval}s "
                    f"at {datetime.fromtimestamp(next_run).strftime('%H:%M:%S')}"
                )

                # Use wait() with timeout for interruptible sleep
                if self._stop_event.wait(timeout=self.config.collection_interval):
                    # Stop event was set
                    break

                # Run collection
                logger.info("Running scheduled collection")
                self.collector.collect()

            except Exception as e:
                logger.error(f"Collection error: {e}", exc_info=True)
                # Continue running despite errors

        self._running = False
        logger.info("Scheduler stopped")

    def stop(self) -> None:
        """Stop the scheduler gracefully."""
        if not self._running:
            logger.warning("Scheduler not running")
            return

        logger.info("Stopping scheduler...")
        self._stop_event.set()

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running

    def run_once(self) -> None:
        """Run a single collection cycle immediately."""
        logger.info("Running single collection cycle")
        self.collector.collect()


def run_collector(
    config: CollectorConfig, daemon: bool = False, immediate: bool = True
) -> CollectionScheduler:
    """
    Run the data collector.

    Args:
        config: Collector configuration
        daemon: If True, run as daemon (continuous)
        immediate: If True, run first collection immediately

    Returns:
        CollectionScheduler instance
    """
    # Create collector
    collector = DataCollector(config)

    # Create scheduler
    scheduler = CollectionScheduler(collector)

    if daemon:
        # Run continuously
        logger.info("Starting collector in daemon mode")
        scheduler.start(immediate=immediate)
    else:
        # Run once
        logger.info("Running collector once")
        scheduler.run_once()

    return scheduler
