"""Portable adapter/CLI regression tests; never access a real credential store."""
import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'api-guardian/scripts/api_guard.py'
spec = importlib.util.spec_from_file_location('api_guard', SCRIPT)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class CredentialAdapterTests(unittest.TestCase):
    def run_delete(self, platform, result, name='synthetic-test'):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(guard.platform, 'system', return_value=platform), \
             patch.object(guard.shutil, 'which', return_value='/synthetic/secret-tool'), \
             patch.object(guard.subprocess, 'run', return_value=result) as run, \
             contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = guard.main(['delete', name])
        return code, out.getvalue(), err.getvalue(), run

    def test_failed_deletion_never_reports_success(self):
        # Include missing-item-like, access-denied, and termination statuses.
        # Ambiguous/nonzero statuses fail closed rather than asserting deletion.
        for platform in ('Darwin', 'Linux'):
            for status in (1, 44, 128, -15):
                for stderr in ('Permission denied', ''):
                    with self.subTest(platform=platform, status=status, stderr=stderr):
                        result = subprocess.CompletedProcess([], status, '', stderr)
                        code, out, err, run = self.run_delete(platform, result)
                        self.assertEqual(code, 1)
                        self.assertEqual(out, '')
                        self.assertIn('did not confirm credential deletion', err)
                        self.assertEqual(run.call_count, 1)

    def test_successful_delete_is_scoped_to_named_item(self):
        for platform in ('Darwin', 'Linux'):
            with self.subTest(platform=platform):
                code, out, err, run = self.run_delete(platform, subprocess.CompletedProcess([], 0, '', ''))
                self.assertEqual(code, 0)
                self.assertIn("Deleted 'synthetic-test'", out)
                self.assertEqual(err, '')
                argv = run.call_args.args[0]
                self.assertEqual(run.call_count, 1)
                self.assertFalse(run.call_args.kwargs.get('shell', False))
                if platform == 'Darwin':
                    self.assertEqual(argv[1], 'delete-generic-password')
                    self.assertEqual(argv[argv.index('-s') + 1], guard.target_name('synthetic-test'))
                    self.assertIn('-a', argv)
                else:
                    self.assertEqual(argv, ['secret-tool', 'clear', 'service', guard.SERVICE_PREFIX, 'name', 'synthetic-test'])

    def test_invalid_delete_name_never_calls_backend(self):
        for platform in ('Darwin', 'Linux'):
            code, out, err, run = self.run_delete(platform, subprocess.CompletedProcess([], 0, '', ''), '../invalid')
            self.assertEqual(code, 1)
            self.assertEqual(out, '')
            run.assert_not_called()

    def test_linux_store_has_required_label_and_stdin_only_secret(self):
        with patch.object(guard.shutil, 'which', return_value='/synthetic/secret-tool'), \
             patch.object(guard.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '', '')) as run:
            guard.LinuxSecretToolStore().store('synthetic-test', 'SYNTHETIC-NOT-A-REAL-CREDENTIAL')
        argv = run.call_args.args[0]
        self.assertEqual(argv[:2], ['secret-tool', 'store'])
        self.assertEqual(argv[argv.index('--label') + 1], guard.target_name('synthetic-test'))
        self.assertNotIn('SYNTHETIC-NOT-A-REAL-CREDENTIAL', argv)
        self.assertEqual(run.call_args.kwargs['input'], 'SYNTHETIC-NOT-A-REAL-CREDENTIAL')
        self.assertEqual(argv[-4:], ['service', guard.SERVICE_PREFIX, 'name', 'synthetic-test'])

    def test_linux_store_failure_is_not_suppressed(self):
        with patch.object(guard.shutil, 'which', return_value='/synthetic/secret-tool'), \
             patch.object(guard.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1, '', 'synthetic failure')):
            with self.assertRaises(guard.StoreError):
                guard.LinuxSecretToolStore().store('synthetic-test', 'SYNTHETIC-NOT-A-REAL-CREDENTIAL')


if __name__ == '__main__':
    unittest.main()
