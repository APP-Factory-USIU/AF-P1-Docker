import unittest
from unittest.mock import patch

import redis

from app.app import app


class CounterTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch("app.app.store")
    def test_page_reads_without_incrementing(self, store):
        store.get.return_value = "12"
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b">12</p>", response.data)
        store.incr.assert_not_called()

    @patch("app.app.store")
    def test_empty_counter_and_post(self, store):
        store.get.return_value = None
        self.assertIn(b">0</p>", self.client.get("/").data)
        response = self.client.post("/count")
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["Location"], "/")
        store.incr.assert_called_once_with("visits")

    @patch("app.app.store")
    def test_health_and_redis_failure(self, store):
        self.assertEqual(self.client.get("/health").json, {"status": "ok"})
        store.ping.side_effect = redis.ConnectionError("offline")
        self.assertEqual(self.client.get("/health").status_code, 503)
        store.get.side_effect = redis.ConnectionError("offline")
        self.assertEqual(self.client.get("/").status_code, 503)
        store.incr.side_effect = redis.ConnectionError("offline")
        self.assertEqual(self.client.post("/count").status_code, 503)


if __name__ == "__main__":
    unittest.main()
