"""Network behaviours tested offline, without touching university services."""
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.robotparser
import urllib.error

from synesis.acquisition import AccessDenied, InvalidPDF, PoliteClient, _CheckedRedirect


class Response(io.BytesIO):
    def __init__(self, payload, url="https://example.org/file.pdf"):
        super().__init__(payload)
        self.headers = {"Content-Type": "application/pdf", "Content-Length": str(len(payload))}
        self.url = url

    def geturl(self):
        return self.url


class AcquisitionTests(unittest.TestCase):
    def test_robots_4xx_unavailable_does_not_imply_resource_denied(self):
        client = PoliteClient()
        error = urllib.error.HTTPError("https://example.org/robots.txt", 403, "Denied", {}, None)
        with patch.object(client, "_request", side_effect=error):
            parser, _ = client._policy("https://example.org")
        self.assertIsNone(parser)
        self.assertEqual(client.robots_observations["https://example.org"]["http_status"], 403)

    def test_resource_403_is_denied_even_when_robots_unavailable(self):
        client = PoliteClient()
        client._robots["https://example.org"] = None, 0
        error = urllib.error.HTTPError("https://example.org/file.pdf", 403, "Denied", {}, None)
        with patch.object(client, "_request", side_effect=error), patch.object(client, "_pause"):
            with self.assertRaises(AccessDenied):
                client.get_bytes("https://example.org/file.pdf")

    def test_disallowed_content_is_never_requested(self):
        parser = urllib.robotparser.RobotFileParser()
        parser.parse(["User-agent: *", "Disallow: /private"])
        client = PoliteClient()
        client._robots["https://example.org"] = parser, 3.0
        with patch.object(client, "_request") as request:
            with self.assertRaises(AccessDenied):
                client.get_bytes("https://example.org/private/file.pdf")
            request.assert_not_called()

    def test_pdf_signature_and_size_guard_prevent_html_artifacts(self):
        client = PoliteClient()
        client._robots["https://example.org"] = None, 0
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)/"file.pdf"
            with patch.object(client, "_open", return_value=Response(b"<html>Login required</html>")):
                with self.assertRaises(InvalidPDF):
                    client.download_pdf("https://example.org/file.pdf", destination)
            self.assertFalse(destination.exists())
            self.assertFalse(destination.with_suffix(".pdf.part").exists())

    def test_pdf_download_is_atomic_and_resume_needs_no_network(self):
        client = PoliteClient()
        client._robots["https://example.org"] = None, 0
        payload = b"%PDF-1.7\n"+b"x"*150+b"\n%%EOF"
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)/"file.pdf"
            with patch.object(client, "_open", return_value=Response(payload)):
                result = client.download_pdf("https://example.org/file.pdf", destination)
            self.assertEqual(destination.read_bytes(), payload)
            self.assertEqual(result["bytes"], len(payload))
            with patch.object(client, "_open") as opened:
                repeated = client.download_pdf("https://example.org/file.pdf", destination)
                opened.assert_not_called()
            self.assertTrue(repeated["cache_hit"])
            self.assertEqual(result["sha256"], repeated["sha256"])

    def test_redirect_to_disallowed_destination_is_rejected(self):
        parser = urllib.robotparser.RobotFileParser()
        parser.parse(["User-agent: *", "Disallow: /blocked"])
        client = PoliteClient()
        client._robots["https://example.org"] = parser, 0
        with self.assertRaises(AccessDenied):
            _CheckedRedirect(client).redirect_request(
                None, None, 302, "Moved", {}, "https://example.org/blocked/file.pdf")

    def test_size_limit_does_not_leave_partial_file(self):
        client = PoliteClient()
        client._robots["https://example.org"] = None, 0
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)/"file.pdf"
            with patch.object(client, "_open", return_value=Response(b"%PDF-1.7\n"+b"x"*150)):
                with self.assertRaises(ValueError):
                    client.download_pdf("https://example.org/file.pdf", destination, max_bytes=100)
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
