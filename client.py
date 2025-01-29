import aiohttp
import asyncio
import random
import time
import logging
from datetime import datetime
import json

SERVER_URLS = [
    "http://localhost:8000/message",
    "http://localhost:8001/message",
]
USER_NAMES = [
    "Alice", "Bob", "Charlie", "David", "Eve",
    "Frank", "Grace", "Hank", "Ivy", "Jack"
]
WORKERS_COUNT = 50
REQUESTS_PER_WORKER = 100

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def send_request(session: aiohttp.ClientSession, url: str, sender: str) -> tuple:
    text = f"Message from {sender} at {datetime.utcnow().isoformat()}"
    payload = {"sender": sender, "text": text}
    
    start_time = time.perf_counter()
    try:
        async with session.post(url, json=payload) as response:
            response_json = await response.json()
            if response.status != 200:
                return -1, None
            return time.perf_counter() - start_time, response_json
    except Exception:
        return -1, None

async def worker(session: aiohttp.ClientSession, worker_id: int) -> list[tuple]:
    timings = []
    for _ in range(REQUESTS_PER_WORKER):
        url = random.choice(SERVER_URLS)
        user = random.choice(USER_NAMES)
        elapsed, response_json = await send_request(session, url, user)
        if elapsed > 0:
            timings.append((url, user, elapsed, response_json))
    return timings

async def main():
    start_time = time.perf_counter()
    
    async with aiohttp.ClientSession() as session:
        tasks = [worker(session, i) for i in range(WORKERS_COUNT)]
        results = await asyncio.gather(*tasks)

    total_time = time.perf_counter() - start_time
    all_timings = [t for sublist in results for t in sublist]
    
    successful = len(all_timings)
    total_expected = WORKERS_COUNT * REQUESTS_PER_WORKER
    loss_percent = (total_expected - successful) / total_expected * 100
    
    logger.info(f"Total time: {total_time:.2f} s")
    logger.info(f"Successful requests: {successful}/{total_expected} ({loss_percent:.1f}% loss)")
    logger.info(f"Throughput: {successful/total_time:.2f} req/s")
    if successful:
        logger.info(f"Average latency: {sum(t[2] for t in all_timings)/successful*1000:.2f} ms")
        random_success = random.choice(all_timings)
        logger.info("Random successful request:")
        logger.info(f"  User: {random_success[1]}")
        logger.info(f"  Latency: {random_success[2]*1000:.2f} ms")
        logger.info(f"  Response: {json.dumps(random_success[3], indent=2)}")
    else:
        logger.info("No successful requests")

if __name__ == "__main__":
    asyncio.run(main())