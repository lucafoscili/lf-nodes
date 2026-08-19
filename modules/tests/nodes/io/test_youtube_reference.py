import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import types
import unittest

from pathlib import Path
from unittest.mock import patch

server = types.ModuleType("server")
server.PromptServer = types.SimpleNamespace(instance=None)
sys.modules.setdefault("server", server)


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

folder_paths = sys.modules.setdefault("folder_paths", types.ModuleType("folder_paths"))
folder_paths.models_dir = "."
folder_paths.get_input_directory = lambda: "."
folder_paths.get_output_directory = lambda: "."
folder_paths.get_temp_directory = lambda: "."
folder_paths.get_user_directory = lambda: "."
folder_paths.get_filename_list = lambda _folder_type: []
folder_paths.get_save_image_path = lambda *args, **kwargs: (".", "output", 0, "", None)

# This node only needs the lightweight sync-event helper.  Keep direct pytest
# collection independent from Comfy's model/native stack, just like the
# subprocess custody probe below.
helpers = types.ModuleType("modules.utils.helpers")
helpers.__path__ = [str(REPO_ROOT / "modules" / "utils" / "helpers")]
sys.modules.setdefault("modules.utils.helpers", helpers)
comfy_helpers = types.ModuleType("modules.utils.helpers.comfy")
comfy_helpers.safe_send_sync = lambda *args, **kwargs: None
sys.modules.setdefault("modules.utils.helpers.comfy", comfy_helpers)

constants = types.ModuleType("modules.utils.constants")
constants.FUNCTION = "on_exec"
constants.Input = types.SimpleNamespace(STRING="STRING", LF_CODE="LF_CODE", JSON="JSON")
sys.modules.setdefault("modules.utils.constants", constants)

io_package = types.ModuleType("modules.nodes.io")
io_package.__path__ = [str(REPO_ROOT / "modules" / "nodes" / "io")]
io_package.CATEGORY = "LF Nodes/IO Operations"
sys.modules.setdefault("modules.nodes.io", io_package)

from modules.nodes.io import youtube_reference


VIDEO_ID = "ETPjddfrk_w"
URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"


_PROCESS_INGEST = r'''
import json
import os
import sys
import time
import types
from pathlib import Path

input_dir, call_log = sys.argv[1:]
server = types.ModuleType("server")
server.PromptServer = types.SimpleNamespace(instance=None)
sys.modules["server"] = server
# The subprocess only exercises youtube cache custody.  Provide the one
# helper it needs so importing the node does not pull every optional LF
# helper (SVG, detection, Comfy filters, and their native dependencies).
helpers = types.ModuleType("modules.utils.helpers")
helpers.__path__ = [str(Path.cwd() / "modules" / "utils" / "helpers")]
sys.modules["modules.utils.helpers"] = helpers
comfy_helpers = types.ModuleType("modules.utils.helpers.comfy")
comfy_helpers.safe_send_sync = lambda *args, **kwargs: None
sys.modules["modules.utils.helpers.comfy"] = comfy_helpers
constants = types.ModuleType("modules.utils.constants")
constants.FUNCTION = "on_exec"
constants.Input = types.SimpleNamespace(STRING="STRING", LF_CODE="LF_CODE", JSON="JSON")
sys.modules["modules.utils.constants"] = constants
io_package = types.ModuleType("modules.nodes.io")
io_package.__path__ = [str(Path.cwd() / "modules" / "nodes" / "io")]
io_package.CATEGORY = "LF Nodes/IO Operations"
sys.modules["modules.nodes.io"] = io_package
folder_paths = types.ModuleType("folder_paths")
folder_paths.models_dir = "."
folder_paths.get_input_directory = lambda: input_dir
folder_paths.get_output_directory = lambda: input_dir
folder_paths.get_temp_directory = lambda: input_dir
folder_paths.get_user_directory = lambda: input_dir
folder_paths.get_filename_list = lambda _folder_type: []
folder_paths.get_save_image_path = lambda *args, **kwargs: (input_dir, "output", 0, "", None)
sys.modules["folder_paths"] = folder_paths

from modules.nodes.io import youtube_reference

class ProcessYoutubeDL:
    def __init__(self, options):
        self.options = options
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def extract_info(self, url, download):
        with Path(call_log).open("ab") as handle:
            handle.write(b"download\n")
        time.sleep(0.2)
        Path(self.options["outtmpl"].replace("%(ext)s", "mp4")).write_bytes(b"process media")
        return {"id": "ETPjddfrk_w"}

def fake_remux(source, target):
    target.write_bytes(b"process m4a")

youtube_reference._remux_aac_to_m4a = fake_remux
os.environ["LF_YOUTUBE_INGEST_ENABLED"] = "1"
sys.modules["yt_dlp"] = types.SimpleNamespace(YoutubeDL=ProcessYoutubeDL)
print(json.dumps(youtube_reference.LF_YouTubeReference().on_exec(
    "https://www.youtube.com/watch?v=ETPjddfrk_w", "audio_m4a"
)))
'''


class FakeYoutubeDL:
    calls = 0
    delay = 0
    fail = False
    lock = threading.Lock()

    def __init__(self, options):
        self.options = options

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def extract_info(self, url, download):
        with self.lock:
            type(self).calls += 1
        if type(self).delay:
            time.sleep(type(self).delay)
        target = Path(self.options["outtmpl"].replace("%(ext)s", "mp4"))
        target.write_bytes(b"mock media")
        if type(self).fail:
            raise RuntimeError("mock download failure")
        return {"id": VIDEO_ID}


class TestYouTubeReference(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.input_dir = Path(self.temp.name) / "input"
        self.input_dir.mkdir()
        self.node = youtube_reference.LF_YouTubeReference()
        self.downloader = types.SimpleNamespace(YoutubeDL=FakeYoutubeDL)
        self.yt_patch = patch.dict(sys.modules, {"yt_dlp": self.downloader})
        self.yt_patch.start()
        self.remux_patch = patch.object(youtube_reference, "_remux_aac_to_m4a", side_effect=self._fake_remux)
        self.remux_patch.start()
        self.input_patch = patch.object(youtube_reference.folder_paths, "get_input_directory", return_value=str(self.input_dir))
        self.input_patch.start()
        self.env_patch = patch.dict(os.environ, {"LF_YOUTUBE_INGEST_ENABLED": "1"})
        self.env_patch.start()
        FakeYoutubeDL.calls = 0
        FakeYoutubeDL.delay = 0
        FakeYoutubeDL.fail = False

    def tearDown(self):
        self.env_patch.stop()
        self.input_patch.stop()
        self.yt_patch.stop()
        if self.remux_patch is not None:
            self.remux_patch.stop()
        self.temp.cleanup()

    @staticmethod
    def _fake_remux(source_path, target_path):
        target_path.write_bytes(b"mock m4a")

    def test_gate_is_disabled_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "disabled"):
                self.node.on_exec(URL, "audio_m4a")
        self.assertEqual(FakeYoutubeDL.calls, 0)

    def test_rejects_non_exact_video_urls(self):
        rejected = (
            f"http://www.youtube.com/watch?v={VIDEO_ID}",
            f"https://www.youtube.com/watch?v={VIDEO_ID}&list=playlist",
            f"https://www.youtube.com/watch?v={VIDEO_ID}&t=30",
            f"https://www.youtube.com/watch?v={VIDEO_ID}&si=",
            f"https://user@www.youtube.com/watch?v={VIDEO_ID}",
            f"https://www.youtube.com:443/watch?v={VIDEO_ID}",
            f"https://www.youtube.com/shorts/{VIDEO_ID}",
            f"https://youtu.be/{VIDEO_ID}?si=not%2Fsafe",
            "https://example.com/watch?v=ETPjddfrk_w",
        )
        for url in rejected:
            with self.subTest(url=url), self.assertRaises(ValueError):
                self.node.on_exec(url, "audio_m4a")
        self.assertEqual(FakeYoutubeDL.calls, 0)

    def test_share_urls_are_canonicalized_before_download(self):
        first = self.node.on_exec(f"https://youtu.be/{VIDEO_ID}?si=tracking_token", "audio_m4a")
        second = self.node.on_exec(f"https://m.youtube.com/watch?si=another_token&v={VIDEO_ID}", "audio_m4a")

        self.assertEqual(first, second)
        self.assertEqual(FakeYoutubeDL.calls, 1)
        self.assertEqual(first[2]["source_url"], URL)

    def test_cache_hit_returns_portable_reference_without_second_download(self):
        first = self.node.on_exec(URL, "audio_m4a")
        second = self.node.on_exec(f"https://youtu.be/{VIDEO_ID}", "audio_m4a")
        self.assertEqual(first, second)
        self.assertEqual(FakeYoutubeDL.calls, 1)
        self.assertEqual(first[0], f"lf-workflow-runner/youtube/{VIDEO_ID}/audio_m4a/reference.m4a")
        self.assertEqual(first[1], VIDEO_ID)
        self.assertEqual(first[2]["schema"], "lf.youtube-reference.v1")

    def test_success_updates_the_receipt_widget(self):
        with patch.object(youtube_reference, "safe_send_sync") as send:
            result = self.node.on_exec(URL, "audio_m4a", node_id="youtube-node")

        send.assert_called_once()
        event, payload, node_id = send.call_args.args
        self.assertEqual(event, "youtubereference")
        self.assertEqual(node_id, "youtube-node")
        self.assertIn("downloaded and verified", payload["value"])
        self.assertIn(result[2]["sha256"], payload["value"])

    def test_input_contract_exposes_the_lf_receipt_widget(self):
        inputs = self.node.INPUT_TYPES()

        self.assertEqual(inputs["optional"]["ui_widget"][0], "LF_CODE")
        self.assertEqual(inputs["hidden"]["node_id"], "UNIQUE_ID")

    def test_concurrent_requests_share_one_download(self):
        FakeYoutubeDL.delay = 0.08
        barrier = threading.Barrier(2)
        results = []
        errors = []

        def run():
            try:
                barrier.wait(timeout=2)
                results.append(self.node.on_exec(URL, "audio_m4a"))
            except Exception as error:
                errors.append((error, traceback.format_exc()))

        threads = [threading.Thread(target=run), threading.Thread(target=run)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], results[1])
        self.assertEqual(FakeYoutubeDL.calls, 1)
        profile_dir = self.input_dir / "lf-workflow-runner" / "youtube" / VIDEO_ID / "audio_m4a"
        self.assertTrue((profile_dir / "reference.m4a").is_file())
        self.assertTrue((profile_dir / "receipt.json").is_file())
        self.assertEqual(list(profile_dir.parent.glob("*.staging")), [])

    def test_cross_process_cache_recheck_prevents_a_second_download(self):
        call_log = self.input_dir / "downloads.log"
        command = [sys.executable, "-c", _PROCESS_INGEST, str(self.input_dir), str(call_log)]
        first = subprocess.Popen(command, cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(0.05)
        second = subprocess.Popen(command, cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        first_stdout, first_stderr = first.communicate(timeout=10)
        second_stdout, second_stderr = second.communicate(timeout=10)

        self.assertEqual(first.returncode, 0, first_stderr)
        self.assertEqual(second.returncode, 0, second_stderr)
        process_results = [json.loads(first_stdout), json.loads(second_stdout)]
        self.assertEqual(call_log.read_bytes().splitlines(), [b"download"])
        self.assertEqual(process_results[0], process_results[1])

    def test_download_failure_never_publishes_partial_cache(self):
        FakeYoutubeDL.fail = True
        with self.assertRaisesRegex(RuntimeError, "mock download failure"):
            self.node.on_exec(URL, "audio_m4a")
        video_dir = self.input_dir / "lf-workflow-runner" / "youtube" / VIDEO_ID
        self.assertFalse((video_dir / "audio_m4a").exists())
        self.assertEqual(list(video_dir.glob("*.staging")), [])

    def test_corrupt_cache_fails_closed_without_redownload(self):
        self.node.on_exec(URL, "audio_m4a")
        media = self.input_dir / "lf-workflow-runner" / "youtube" / VIDEO_ID / "audio_m4a" / "reference.m4a"
        media.write_bytes(b"corrupted")
        with self.assertRaisesRegex(ValueError, "integrity"):
            self.node.on_exec(URL, "audio_m4a")
        self.assertEqual(FakeYoutubeDL.calls, 1)

    def test_tampered_receipt_relative_path_fails_closed(self):
        self.node.on_exec(URL, "audio_m4a")
        receipt_path = self.input_dir / "lf-workflow-runner" / "youtube" / VIDEO_ID / "audio_m4a" / "receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["relative_input_path"] = "elsewhere/reference.m4a"
        receipt["receipt_sha256"] = hashlib.sha256(
            youtube_reference._canonical_json({key: value for key, value in receipt.items() if key != "receipt_sha256"}).encode("utf-8")
        ).hexdigest()
        receipt_path.write_text(youtube_reference._canonical_json(receipt), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "integrity"):
            self.node.on_exec(URL, "audio_m4a")
        self.assertEqual(FakeYoutubeDL.calls, 1)

    def test_downloader_options_prohibit_postprocessing_and_partial_files(self):
        captured = {}

        class CapturingYoutubeDL(FakeYoutubeDL):
            def __init__(self, options):
                captured.update(options)
                super().__init__(options)

        with patch.dict(sys.modules, {"yt_dlp": types.SimpleNamespace(YoutubeDL=CapturingYoutubeDL)}):
            self.node.on_exec(URL, "video_mp4")
        self.assertEqual(captured["postprocessors"], [])
        self.assertTrue(captured["nopart"])
        self.assertTrue(captured["ignoreconfig"])
        self.assertEqual(captured["js_runtimes"], {"node": {}})
        self.assertEqual(captured["format"], "18")
        self.assertEqual(captured["extractor_args"], {"youtube": {"player_client": ["android"]}})
        self.assertNotIn("ffmpeg", repr(captured).lower())

    def test_pyav_losslessly_remuxes_aac_to_audio_only_m4a(self):
        self.remux_patch.stop()
        self.remux_patch = None
        import av

        source_path = self.input_dir / "source.mp4"
        target_path = self.input_dir / "target.m4a"
        with av.open(str(source_path), mode="w") as output:
            video_stream = output.add_stream("mpeg4", rate=24)
            video_stream.width = 16
            video_stream.height = 16
            video_stream.pix_fmt = "yuv420p"
            audio_stream = output.add_stream("aac", rate=44100)
            audio_stream.layout = "mono"

            video_frame = av.VideoFrame(16, 16, "yuv420p")
            for plane in video_frame.planes:
                plane.update(bytes(plane.buffer_size))
            for packet in video_stream.encode(video_frame):
                output.mux(packet)

            audio_frame = av.AudioFrame(format="fltp", layout="mono", samples=1024)
            audio_frame.sample_rate = 44100
            audio_frame.planes[0].update(bytes(audio_frame.planes[0].buffer_size))
            for packet in audio_stream.encode(audio_frame):
                output.mux(packet)
            for packet in video_stream.encode():
                output.mux(packet)
            for packet in audio_stream.encode():
                output.mux(packet)

        def audio_packets(path):
            with av.open(str(path), mode="r") as container:
                audio_stream = next(stream for stream in container.streams if stream.type == "audio")
                return [bytes(packet) for packet in container.demux(audio_stream) if packet.dts is not None]

        source_packets = audio_packets(source_path)
        youtube_reference._remux_aac_to_m4a(source_path, target_path)
        with av.open(str(target_path), mode="r") as target:
            self.assertEqual([(stream.type, stream.codec_context.name) for stream in target.streams], [("audio", "aac")])
        self.assertEqual(audio_packets(target_path), source_packets)

    def test_containment_guard_rejects_a_path_outside_input(self):
        with self.assertRaisesRegex(ValueError, "escapes"):
            youtube_reference._contained(self.input_dir, self.input_dir.parent / "outside")

    @unittest.skipUnless(os.name == "nt", "Windows extended paths only")
    def test_containment_accepts_equivalent_extended_windows_path(self):
        ordinary = self.input_dir / "nested" / "reference.m4a"
        extended = Path("\\\\?\\" + os.fspath(ordinary))
        youtube_reference._contained(self.input_dir, extended)

    def test_cache_symlink_cannot_escape_input(self):
        external = Path(self.temp.name) / "outside-cache"
        external.mkdir()
        cache_parent = self.input_dir / "lf-workflow-runner"
        cache_parent.mkdir()
        cache_link = cache_parent / "youtube"
        try:
            cache_link.symlink_to(external, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"Directory symlinks unavailable on this host: {error}")

        with self.assertRaisesRegex(ValueError, "escapes"):
            self.node.on_exec(URL, "audio_m4a")
        self.assertEqual(FakeYoutubeDL.calls, 0)

    def test_node_mappings_expose_opt_in_reference_node(self):
        self.assertIs(
            youtube_reference.NODE_CLASS_MAPPINGS["LF_YouTubeReference"],
            youtube_reference.LF_YouTubeReference,
        )
        self.assertEqual(
            youtube_reference.NODE_DISPLAY_NAME_MAPPINGS["LF_YouTubeReference"],
            "YouTube Reference (opt-in)",
        )


if __name__ == "__main__":
    unittest.main()
