import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("publish_next", os.path.join(HERE, "..", "ops", "publish_next.py"))
pn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pn)


class FakeGit:
    """pn.sh 와 push 의 subprocess 호출을 가짜로 바꾼다. 호출 기록을 남기고, push 결과를 정할 수 있다."""

    def __init__(self, push_result="ok"):
        self.calls = []        # sh(...) 호출
        self.pushes = []       # push subprocess.run 호출 (args, kwargs)
        self.push_result = push_result

    def sh(self, *cmd):
        self.calls.append(cmd)
        if cmd[:3] == ("git", "rev-parse", "--abbrev-ref"):
            return "main"
        if cmd[:3] == ("git", "status", "--porcelain"):
            return ""
        return ""

    def run(self, args, **kwargs):
        self.pushes.append((args, kwargs))
        if self.push_result == "fail":
            raise subprocess.CalledProcessError(1, args, output="", stderr="fatal: unable to access remote")
        if self.push_result == "timeout":
            raise subprocess.TimeoutExpired(args, kwargs.get("timeout"))
        return subprocess.CompletedProcess(args, 0, "", "")


class PublishNextTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        self.queue = os.path.join(self.root, "queue")
        os.makedirs(os.path.join(self.queue, "01-hello-world"))
        for lang in ("en", "ko"):
            with open(os.path.join(self.queue, "01-hello-world", lang + ".md"), "w", encoding="utf-8") as f:
                f.write('---\ntitle: "Hello"\n---\nbody\n')
        self.git = FakeGit()
        self.patches = [
            mock.patch.object(pn, "REPO", self.root),
            mock.patch.object(pn, "sh", side_effect=self.git.sh),
            mock.patch.object(pn.subprocess, "run", side_effect=self.git.run),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self._tmp.cleanup()

    def publish(self, env):
        argv = ["publish_next.py", "--date", "2026-11-19", "--time", "15:00", "--queue", self.queue]
        with mock.patch.object(sys, "argv", argv), mock.patch.dict(os.environ, env, clear=True):
            return pn.main()

    def commit_calls(self):
        return [c for c in self.git.calls if c[:2] == ("git", "commit")]

    def reset_calls(self):
        return [c for c in self.git.calls if c[:3] == ("git", "reset", "--hard")]

    def moved(self):
        return (not os.path.isdir(os.path.join(self.queue, "01-hello-world"))
                and os.path.isdir(os.path.join(self.queue, ".published", "01-hello-world")))

    def test_push_failure_still_publishes_and_moves_queue(self):
        self.git.push_result = "fail"
        with mock.patch.object(pn, "sh", side_effect=self.git.sh):
            rc = self.publish({"DUSK_PUSH": "1"})
        self.assertEqual(rc, 0)
        self.assertTrue(self.moved(), "push 실패해도 큐는 .published/ 로 옮겨야 한다")
        self.assertEqual(len(self.git.pushes), 1)

    def test_push_failure_keeps_commit(self):
        self.git.push_result = "fail"
        rc = self.publish({"DUSK_PUSH": "1"})
        self.assertEqual(rc, 0)
        self.assertEqual(len(self.commit_calls()), 1, "커밋은 한 번 만들어져야 한다")
        self.assertEqual(self.reset_calls(), [], "push 실패 뒤 reset --hard 로 커밋을 버리면 안 된다")

    def test_push_timeout_still_publishes(self):
        self.git.push_result = "timeout"
        rc = self.publish({"DUSK_PUSH": "1"})
        self.assertEqual(rc, 0)
        self.assertTrue(self.moved())
        self.assertEqual(self.reset_calls(), [])

    def test_no_push_when_dusk_push_unset(self):
        rc = self.publish({})
        self.assertEqual(rc, 0)
        self.assertEqual(self.git.pushes, [], "DUSK_PUSH 미설정이면 push 를 부르면 안 된다")
        self.assertTrue(self.moved())
        self.assertEqual(len(self.commit_calls()), 1)

    def test_no_push_when_dusk_push_is_not_one(self):
        rc = self.publish({"DUSK_PUSH": "0"})
        self.assertEqual(rc, 0)
        self.assertEqual(self.git.pushes, [])

    def test_push_success_path(self):
        rc = self.publish({"DUSK_PUSH": "1"})
        self.assertEqual(rc, 0)
        self.assertEqual(len(self.git.pushes), 1)
        args, kwargs = self.git.pushes[0]
        self.assertEqual(args, ["git", "push", "origin", "main"])
        self.assertEqual(kwargs.get("timeout"), pn.PUSH_TIMEOUT)
        self.assertEqual(kwargs.get("env", {}).get("GIT_TERMINAL_PROMPT"), "0")
        self.assertTrue(self.moved())
        self.assertEqual(self.reset_calls(), [])

    def test_push_runs_after_commit(self):
        order = []
        real_sh = self.git.sh

        def sh(*cmd):
            if cmd[:2] == ("git", "commit"):
                order.append("commit")
            return real_sh(*cmd)

        def run(args, **kwargs):
            order.append("push")
            return subprocess.CompletedProcess(args, 0, "", "")

        with mock.patch.object(pn, "sh", side_effect=sh), mock.patch.object(pn.subprocess, "run", side_effect=run):
            rc = self.publish({"DUSK_PUSH": "1"})
        self.assertEqual(rc, 0)
        self.assertEqual(order, ["commit", "push"])


if __name__ == "__main__":
    unittest.main()
