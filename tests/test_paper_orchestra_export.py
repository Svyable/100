import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from scripts.paper_orchestra_export import export, verify


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Test')
        (self.root/'data').mkdir()
        self.record = {'work_id':'X-TEST', 'scope_sha256':'a'*64, 'author':'a',
                       'outcome':'merged_pending_review', 'claimed_on':'2026-11-25',
                       'closed_on':'2026-11-25', 'resources':{'agent_hours':0}}
        (self.root/'proof.txt').write_text('original proof\n')
        (self.root/'link').symlink_to('proof.txt')
        self.commit = self.save()

    def git(self, *a):
        return subprocess.check_output(['git','-C',str(self.root),*a]).decode().strip()

    def save(self):
        (self.root/'data/outcomes.json').write_text(json.dumps({'version':1, 'resource_unit':'agent_hour', 'outcomes':[self.record]}))
        self.git('add','data','proof.txt','link')
        self.git('commit','-qm','fixture')
        return self.git('rev-parse','HEAD')

    def run_export(self, name='out', paths=None, draft=True, commit=None):
        return export(self.root, commit or self.commit, 'X-TEST', paths or ['proof.txt'], self.root/name, draft)

    def test_pinned_and_deterministic(self):
        (self.root/'proof.txt').write_text('dirty change')
        self.run_export('one')
        self.run_export('two')
        for p in (self.root/'one').iterdir():
            self.assertEqual(p.read_bytes(), (self.root/'two'/p.name).read_bytes())
        self.assertIn('original proof', (self.root/'one/experimental_log.md').read_text())
        self.assertNotIn('dirty change', (self.root/'one/experimental_log.md').read_text())

    def test_draft_opt_in(self):
        with self.assertRaises(ValueError): self.run_export(draft=False)

    def test_paths(self):
        for p in ['../proof.txt','link','proof.txt/','/proof.txt']:
            with self.subTest(p=p), self.assertRaises(ValueError): self.run_export(paths=[p])

    def test_forged_self_review(self):
        self.record.update(outcome='accepted_independent', reviewer='a', review_url='https://example.invalid/review', accepted_on='2026-11-25')
        c=self.save()
        with self.assertRaises(ValueError): self.run_export(commit=c, draft=False)

    def test_reviewed_still_draft(self):
        self.record.update(outcome='accepted_independent', reviewer='b', review_url='https://example.invalid/review', accepted_on='2026-11-25')
        m=self.run_export(commit=self.save(), draft=False)
        self.assertEqual(m['disposition'],'draft_only')

    def test_no_overwrite(self):
        self.run_export()
        with self.assertRaises(FileExistsError): self.run_export()

    def test_reject_branch_ref(self):
        with self.assertRaises(ValueError): self.run_export(commit='HEAD')

    def test_casefolded_self_review(self):
        self.record.update(outcome='accepted_independent', reviewer=' A ', review_url='https://example.invalid/review', accepted_on='2026-11-25')
        with self.assertRaises(ValueError): self.run_export(commit=self.save(), draft=False)

    def test_invalid_review_date(self):
        self.record.update(outcome='accepted_independent', reviewer='b', review_url='https://example.invalid/review', accepted_on='not-a-date')
        with self.assertRaises(ValueError): self.run_export(commit=self.save(), draft=False)

    def test_novelty_without_review(self):
        self.record.update(novelty='new_restricted_result')
        with self.assertRaises(ValueError): self.run_export(commit=self.save())

    def test_verify_packet_and_tampering(self):
        m = self.run_export()
        def check():
            return verify(self.root, self.commit, 'X-TEST', ['proof.txt'], self.root/'out', True)
        self.assertEqual(m, check())
        for name in ('idea_sparse.md', 'experimental_log.md', 'manifest.json'):
            p = self.root/'out'/name
            original = p.read_bytes()
            p.write_bytes(original + b' altered')
            with self.subTest(name=name), self.assertRaises(ValueError):
                check()
            p.write_bytes(original)
        (self.root/'out'/'extra').touch()
        with self.assertRaises(ValueError): check()
        (self.root/'out'/'extra').unlink()
        p = self.root/'out'/'manifest.json'
        original = p.read_bytes()
        p.unlink()
        with self.assertRaises(ValueError): check()
        (self.root/'replacement').write_bytes(original)
        p.symlink_to(self.root/'replacement')
        with self.assertRaises(ValueError): check()
