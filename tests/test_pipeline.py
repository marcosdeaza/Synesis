"""Behavioural checks for public exports, temporal evidence and bounded harvesting."""
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
from xml.sax.saxutils import escape

from synesis.core import curate, mention_features, metadata_date, period, validate_record, wilson
from synesis.harvest import check_robots, harvest, parse_page


def row(**updates):
    value = {"id": "fixture", "institution_id": "fixture", "title": "Study of ChatGPT",
             "year": 2023, "date_precision": "year", "degree_level": "master",
             "source_url": "https://example.org/1", "record_identifier": "fixture:1",
             "retrieved_at": "2026-10-16", "evidence_kind": "metadata", "abstract": None, "subjects": []}
    value.update(updates)
    return value


def dc_page(degree="masterThesis", date="2024", token=None):
    token_xml = "" if token is None else "<resumptionToken>" + escape(token) + "</resumptionToken>"
    return ('''<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:dc="http://purl.org/dc/elements/1.1/">
<ListRecords><record><header><identifier>oai:x:1</identifier></header><metadata><x>
<dc:title>A</dc:title><dc:type>''' + escape(degree) + '''</dc:type><dc:date>''' + escape(date) + '''</dc:date>
<dc:identifier>https://example.org/1</dc:identifier></x></metadata></record>''' + token_xml + '''</ListRecords></OAI-PMH>''').encode()


def dim_page():
    return b'''<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:dim="http://www.dspace.org/xmlns/dspace/dim">
<ListRecords><record><header><identifier>oai:x:2</identifier></header><metadata><dim:dim>
<dim:field mdschema="dc" element="title">Qualified dates</dim:field>
<dim:field mdschema="dc" element="title" qualifier="alternative">Translation</dim:field>
<dim:field mdschema="dc" element="type">TFM</dim:field>
<dim:field mdschema="dc" element="date" qualifier="accessioned">2026-10-10T12:00:00Z</dim:field>
<dim:field mdschema="dc" element="date" qualifier="created">2021-05-20</dim:field>
<dim:field mdschema="dc" element="date" qualifier="issued">2021-06</dim:field>
<dim:field mdschema="dc" element="identifier" qualifier="citation">Citation containing author fields</dim:field>
<dim:field mdschema="dc" element="identifier" qualifier="uri">https://example.org/2</dim:field>
<dim:field mdschema="dc" element="description" qualifier="abstract">Not exported</dim:field>
<dim:field mdschema="dc" element="contributor" qualifier="author">Not exported</dim:field>
<dim:field mdschema="dc" element="subject">Topic</dim:field>
<dim:field mdschema="dc" element="subject">Topic</dim:field>
<dim:field mdschema="dc" element="rights" qualifier="accessRights">openAccess</dim:field>
</dim:dim></metadata></record></ListRecords></OAI-PMH>'''


class Invariants(unittest.TestCase):
    def test_mentions_never_label_authorship(self):
        accepted, _ = curate([row()])
        self.assertTrue(accepted[0]["any_ai_cue"])
        self.assertEqual(accepted[0]["ai_use_status"], "not_assessed")

    def test_homonyms_and_classical_agents_are_not_generative_cues(self):
        for title in ["Claude Monet: colour and light", "Gemini Observatory galaxies",
                      "Autonomous agents in a 2015 traffic simulator"]:
            with self.subTest(title=title):
                self.assertFalse(mention_features(row(title=title))["any_ai_cue"])
        for title in ["GPT-4o for document retrieval", "Working with Claude Code",
                      "Claude for generative AI", "LLM autonomous agents"]:
            with self.subTest(title=title):
                self.assertTrue(mention_features(row(title=title))["any_ai_cue"])

    def test_preserve_unknown_level_and_transition(self):
        accepted, _ = curate([row(degree_level="unknown")])
        self.assertFalse(accepted[0]["eligible_level"])
        self.assertEqual(period(2022), "transition_2022_2023")
        self.assertEqual(period(None), "undated")

    def test_duplicate_identity_and_public_id_are_separate_invariants(self):
        accepted, issues = curate([row(), row(id="different"), row(record_identifier="fixture:2")])
        self.assertEqual(len(accepted), 1)
        self.assertIn("duplicate_identifier", issues[0]["issues"])
        self.assertIn("duplicate_id", issues[1]["issues"])
        # Sharing only a title is not sufficient evidence to delete a real thesis.
        accepted, issues = curate([row(), row(id="different", record_identifier="fixture:2")])
        self.assertEqual(len(accepted), 2)
        self.assertEqual(issues, [])

    def test_unreviewed_fields_and_contact_data_cannot_be_exported(self):
        for updates in [{"authors": ["Private"]}, {"contributors": ["Private"]},
                        {"dc_creator": "Private"}, {"private_email": "private@example.org"},
                        {"subjects": ["Contact private@example.org"]}]:
            with self.subTest(updates=updates):
                accepted, issues = curate([row(**updates)])
                self.assertEqual(accepted, [])
                self.assertTrue(issues)
        accepted, issues = curate([row(id="private@example.org")])
        self.assertEqual(accepted, [])
        self.assertIsNone(issues[0]["id"])
        self.assertNotIn("private@example.org", json.dumps(issues))

    def test_omitted_abstract_is_rejected_and_never_analyzed(self):
        source = row(title="Ordinary study", abstract="ChatGPT", abstract_available=True,
                     abstract_omitted_by_policy=True)
        values = mention_features(source)
        self.assertTrue(values["abstract_available"])
        self.assertFalse(values["abstract_text_analyzed"])
        self.assertFalse(values["any_ai_cue"])
        accepted, issues = curate([source])
        self.assertEqual(accepted, [])
        self.assertIn("abstract_present_despite_omission_policy", issues[0]["issues"])

    def test_schema_rejects_malformed_records_without_crashing(self):
        candidates = [None, [], "text", row(id=None), row(record_identifier=[]), row(subjects="ChatGPT"),
                      row(source_url="https:missing-host"), row(abstract_available="yes"),
                      row(retrieved_at="yesterday"), row(year=True), row(year=2027),
                      row(year=None, date_precision="day")]
        for candidate in candidates:
            with self.subTest(candidate=candidate):
                accepted, issues = curate([candidate])
                self.assertEqual(accepted, [])
                self.assertEqual(len(issues), 1)
        self.assertEqual(validate_record(row(metadata_license="CC0-1.0", academic_date_verified=False,
                                           rights_reference_url="https://example.org/rights")), [])

    def test_wilson_has_finite_zero_and_all_success_intervals(self):
        self.assertIsNone(wilson(0, 0))
        self.assertAlmostEqual(wilson(0, 10)[0], 0)
        self.assertAlmostEqual(wilson(10, 10)[1], 1)

    def test_dates_require_complete_valid_calendar_values(self):
        for text in ["2024-13-99", "2024-02-30", "2024garbage", "2024-01-01garbage", "2027", "No consta"]:
            with self.subTest(date=text):
                self.assertEqual(metadata_date(text), (None, "unknown"))
                rows, _ = parse_page(dc_page(date=text), "x", "2026-10-16")
                self.assertIsNone(rows[0]["year"])
                self.assertEqual(rows[0]["issued_raw"], text)
                self.assertEqual(rows[0]["date_precision"], "unknown")
        self.assertEqual(metadata_date("2024-02-29"), (2024, "day"))
        self.assertEqual(metadata_date("2023/06"), (2023, "month"))
        self.assertEqual(metadata_date("2024-02-29T12:00:00Z"), (2024, "day"))

    def test_explicit_degree_aliases_and_non_degree_words(self):
        for kind, expected in [("TFG", "bachelor"), ("TFM", "master"),
                               ("info:eu-repo/semantics/bachelorThesis", "bachelor"),
                               ("masterThesis", "master"), ("Posgrado", "unknown"),
                               ("Tesis", "unknown")]:
            with self.subTest(kind=kind):
                rows, _ = parse_page(dc_page(degree=kind), "x", "2026-10-16")
                self.assertEqual(rows[0]["degree_level"], expected)
        for kind in ["doctoralThesis", "PhD Thesis", "Doctor of Philosophy", "doutorado"]:
            with self.subTest(kind=kind):
                rows, _ = parse_page(dc_page(degree=kind), "x", "2026-10-16")
                self.assertEqual(rows, [])

    def test_oai_preserves_ambiguous_date_and_token(self):
        rows, token = parse_page(dc_page(token="next&page"), "x", "2026-10-16")
        self.assertEqual(rows[0]["date_semantics"], "dc_date_unqualified")
        self.assertEqual(rows[0]["date_candidates_raw"], ["2024"])
        self.assertEqual(token, "next&page")
        self.assertEqual(validate_record(rows[0]), [])

    def test_dim_preserves_qualified_dates_without_deposit_fallback(self):
        rows, _ = parse_page(dim_page(), "x", "2026-10-16")
        source = rows[0]
        self.assertEqual((source["year"], source["date_precision"]), (2021, "month"))
        self.assertEqual(source["issued_raw"], "2021-06")
        self.assertEqual(source["created_raw"], "2021-05-20")
        self.assertEqual(source["accessioned_raw"], "2026-10-10T12:00:00Z")
        self.assertEqual(source["date_semantics"], "dc_date_issued")
        self.assertEqual(source["title"], "Qualified dates")
        self.assertEqual(source["source_url"], "https://example.org/2")
        self.assertEqual(source["degree_level"], "master")
        self.assertEqual(source["subjects"], ["Topic"])
        self.assertTrue(source["abstract_available"])
        self.assertIsNone(source["abstract"])
        self.assertNotIn("contributor", json.dumps(source))
        self.assertNotIn("Not exported", json.dumps(source))
        self.assertEqual(validate_record(source), [])
        payload = dim_page().replace(b'<dim:field mdschema="dc" element="date" qualifier="issued">2021-06</dim:field>', b'')
        source = parse_page(payload, "x", "2026-10-16")[0][0]
        self.assertIsNone(source["year"])
        self.assertIsNone(source["issued_raw"])
        self.assertEqual(source["date_semantics"], "unknown")

    def test_wrong_xml_response_cannot_be_a_successful_empty_harvest(self):
        for payload in [b"<html><body>Blocked</body></html>",
                        b'<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"><Identify/></OAI-PMH>']:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                parse_page(payload, "x", "2026-10-16")

    def test_existing_public_pilot_remains_valid_and_minimized(self):
        root = Path(__file__).resolve().parents[1]
        rows = [json.loads(line) for path in sorted((root / "data/pilot").glob("*.jsonl"))
                for line in path.read_text().splitlines() if line.strip()]
        accepted, issues = curate(rows)
        self.assertEqual(issues, [])
        public_manifest = root / "PUBLIC_EXPORT_MANIFEST.json"
        expected = json.loads(public_manifest.read_text())["distributed_records"] if public_manifest.exists() else 225
        self.assertEqual(len(accepted), expected)
        self.assertTrue(all(r.get("abstract") is None for r in accepted))
        self.assertTrue(all(r["ai_use_status"] == "not_assessed" for r in accepted))


class HarvestBounds(unittest.TestCase):
    def test_robots_returns_stricter_delay_and_rate(self):
        for text, expected in [(b"User-agent: *\nCrawl-delay: 10\nRequest-rate: 2/30\n", 15.0),
                               (b"User-agent: *\nCrawl-delay: 10\n", 10.0)]:
            with self.subTest(expected=expected), patch("synesis.harvest.urllib.request.urlopen", return_value=io.BytesIO(text)):
                self.assertEqual(check_robots("https://example.org/oai", "SynesisResearch"), expected)
        with patch("synesis.harvest.urllib.request.urlopen", return_value=io.BytesIO(b"User-agent: *\nDisallow: /oai\n")):
            with self.assertRaises(PermissionError):
                check_robots("https://example.org/oai", "SynesisResearch")

    def test_harvest_applies_delay_and_dim_prefix_without_network(self):
        with tempfile.TemporaryDirectory() as temp, \
             patch("synesis.harvest.check_robots", return_value=10.0), \
             patch("synesis.harvest.fetch", side_effect=[dc_page(token="next&page"), dim_page()]) as fetched, \
             patch("synesis.harvest.time.sleep") as sleep:
            destination = Path(temp) / "snapshot"
            manifest = harvest("https://example.org/oai", "x", "collection", destination,
                               "https://example.org/project", pages=2, metadata_prefix="dim")
            first = parse_qs(urlsplit(fetched.call_args_list[0].args[0]).query)
            second = parse_qs(urlsplit(fetched.call_args_list[1].args[0]).query)
            self.assertEqual(first["metadataPrefix"], ["dim"])
            self.assertEqual(second, {"verb": ["ListRecords"], "resumptionToken": ["next&page"]})
            self.assertEqual([call.args[0] for call in sleep.call_args_list], [10.0, 10.0])
            self.assertTrue(all(call.kwargs["min_interval"] == 10.0 for call in fetched.call_args_list))
            self.assertEqual(manifest["metadata_prefix"], "dim")
            self.assertEqual(manifest["effective_delay_seconds"], 10.0)
            self.assertEqual(manifest["records"], 2)
            self.assertTrue(manifest["exhausted"])
            self.assertTrue((destination / "page-001.xml").exists())
            self.assertEqual(len((destination / "metadata.jsonl").read_text().splitlines()), 2)


if __name__ == "__main__":
    unittest.main()
