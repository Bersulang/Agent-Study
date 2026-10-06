"""先定义事件边界、草稿校验和取消的可观测契约。"""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "examples" / "demo.py"
spec = importlib.util.spec_from_file_location("stream_demo", path)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)

class StreamTests(unittest.TestCase):
    def test_chunks_do_not_define_events(self):
        # UTF-8中文跨字节分块；CRLF与多行data共同参与边界解析。
        wire = ':心跳\r\ndata: 第一行\r\ndata: 第二行\r\n\r\n'.encode()
        chunks = [wire[index:index + 1] for index in range(len(wire))]
        self.assertEqual(list(demo.sse_events(chunks)), ["第一行\n第二行"])

    def test_unterminated_event_is_not_dispatched(self):
        self.assertEqual(list(demo.sse_events([b'data: unfinished'])), [])

    def test_cancel_does_not_commit_partial_json(self):
        chunks = [b'data: {"title":\n\n', b'data: "x"}\n\n']
        with self.assertRaises(demo.StreamCancelled):
            demo.collect_draft(chunks, cancelled=lambda: True)

    def test_schema_rejects_boolean_priority_and_extra_fields(self):
        for value in [{"title": "x", "priority": True}, {"title": "x", "priority": 3, "extra": 1}]:
            with self.assertRaises(ValueError):
                demo.validate_draft(value)

    def test_missing_done_is_incomplete(self):
        with self.assertRaises(ValueError):
            demo.collect_draft([b'data: {"title":"x","priority":3}\n\n'])

if __name__ == "__main__":
    unittest.main()
