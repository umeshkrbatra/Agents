import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends.redis import RedisBackend

REDIS_URL = "redis://localhost:6379/0"

broker = RedisBroker(url=REDIS_URL)

dramatiq.set_broker(broker)

result_backend = RedisBackend(url=REDIS_URL)
broker.add_middleware(Results(backend=result_backend))

dramatiq.set_broker(broker)