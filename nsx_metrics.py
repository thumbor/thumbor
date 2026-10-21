# NSXBet: statsd-over-TCP metrics backend.
# Same interface as thumbor.metrics.statsd_metrics but uses TCPStatsClient —
# UDP packets between containers are unreliable on Docker Desktop (macOS).
from statsd import TCPStatsClient

from thumbor.metrics import BaseMetrics


class Metrics(BaseMetrics):
    @classmethod
    def client(cls, config):
        if not hasattr(cls, "_client"):
            cls._client = TCPStatsClient(
                config.STATSD_HOST, config.STATSD_PORT, config.STATSD_PREFIX
            )
        return cls._client

    def incr(self, metricname, value=1):
        Metrics.client(self.config).incr(metricname, value)

    def timing(self, metricname, value):
        Metrics.client(self.config).timing(metricname, value)
