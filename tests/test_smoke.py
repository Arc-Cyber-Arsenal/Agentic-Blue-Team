import importlib
import json
import os
import uuid
from pathlib import Path

from django.core.cache import cache
from django.test import TestCase

from PLUGINS.Redis.redis_client import RedisClient
from PLUGINS.Redis.redis_stream_api import RedisStreamAPI

REPO_ROOT = Path(__file__).resolve().parent.parent


class RedisStreamTest(TestCase):
    def test_stream_roundtrip(self):
        api = RedisStreamAPI()
        stream = f"abt-test-{uuid.uuid4().hex[:8]}"
        try:
            msg_id = api.send_message(stream, {"alert": "smoke", "n": 1})
            self.assertIsNotNone(msg_id)
            client = RedisClient.get_stream_connection()
            self.assertGreaterEqual(client.xlen(stream), 1)
            entries = client.xrange(stream)
            payload = json.loads(entries[0][1]["data"])
            self.assertEqual(payload["alert"], "smoke")
        finally:
            RedisClient.get_stream_connection().delete(stream)


class DjangoInfrastructureTest(TestCase):
    def test_cache_backend_is_live_redis(self):
        token = f"abt-cache-{uuid.uuid4().hex[:8]}"
        cache.set(token, {"ok": True}, timeout=30)
        try:
            self.assertEqual(cache.get(token), {"ok": True})
        finally:
            cache.delete(token)

    def test_api_root_responds(self):
        response = self.client.get("/api/")
        self.assertLess(response.status_code, 500)


class DiscoveryTest(TestCase):
    def test_all_modules_import(self):
        modules_dir = REPO_ROOT / "MODULES"
        files = [p for p in modules_dir.glob("*.py") if not p.name.startswith("_")]
        self.assertGreaterEqual(len(files), 3)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ABT.settings")
        for path in files:
            spec = importlib.util.spec_from_file_location(path.stem, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self.assertTrue(hasattr(mod, "Module"), f"{path.name} missing Module class")

    def test_playbooks_have_playbook_class(self):
        from Lib.playbookloader import PlaybookLoader
        found = 0
        for path in (REPO_ROOT / "PLAYBOOKS").rglob("*.py"):
            rel = path.relative_to(REPO_ROOT / "PLAYBOOKS").with_suffix("")
            parts = [p for p in rel.parts if p not in ("__init__", "__pycache__")]
            if not parts:
                continue
            pkg = ".".join(["PLAYBOOKS"] + list(parts[:-1]))
            cls = PlaybookLoader._load_playbook_class(parts[-1], pkg)
            if cls is not None:
                found += 1
        self.assertGreaterEqual(found, 3)
