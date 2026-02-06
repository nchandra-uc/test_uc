#!/usr/bin/env python3
"""Tests for the CLI application."""

import io
import sys
import unittest
from unittest.mock import patch

from cli import create_parser, main, open_composer_picker, start_default_mode


class TestCreateParser(unittest.TestCase):
    """Tests for the argument parser."""

    def test_cloud_flag_short(self):
        parser = create_parser()
        args = parser.parse_args(["-c"])
        self.assertTrue(args.cloud)

    def test_cloud_flag_long(self):
        parser = create_parser()
        args = parser.parse_args(["--cloud"])
        self.assertTrue(args.cloud)

    def test_cloud_flag_default(self):
        parser = create_parser()
        args = parser.parse_args([])
        self.assertFalse(args.cloud)

    def test_verbose_flag_short(self):
        parser = create_parser()
        args = parser.parse_args(["-v"])
        self.assertTrue(args.verbose)

    def test_verbose_flag_long(self):
        parser = create_parser()
        args = parser.parse_args(["--verbose"])
        self.assertTrue(args.verbose)

    def test_verbose_flag_default(self):
        parser = create_parser()
        args = parser.parse_args([])
        self.assertFalse(args.verbose)

    def test_cloud_and_verbose_combined(self):
        parser = create_parser()
        args = parser.parse_args(["-c", "-v"])
        self.assertTrue(args.cloud)
        self.assertTrue(args.verbose)


class TestMain(unittest.TestCase):
    """Tests for the main function."""

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_default_mode(self, mock_stdout):
        result = main([])
        self.assertEqual(result, 0)
        output = mock_stdout.getvalue()
        self.assertIn("Use -c or --cloud to start in cloud mode", output)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_cloud_mode_short(self, mock_stdout):
        result = main(["-c"])
        self.assertEqual(result, 0)
        output = mock_stdout.getvalue()
        self.assertIn("composer picker", output.lower())

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_cloud_mode_long(self, mock_stdout):
        result = main(["--cloud"])
        self.assertEqual(result, 0)
        output = mock_stdout.getvalue()
        self.assertIn("composer picker", output.lower())

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_verbose_mode(self, mock_stdout):
        result = main(["-v"])
        self.assertEqual(result, 0)
        output = mock_stdout.getvalue()
        self.assertIn("Cloud mode: False", output)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_cloud_verbose(self, mock_stdout):
        result = main(["-c", "-v"])
        self.assertEqual(result, 0)
        output = mock_stdout.getvalue()
        self.assertIn("Cloud mode: True", output)
        self.assertIn("composer picker", output.lower())


class TestOpenComposerPicker(unittest.TestCase):
    """Tests for the composer picker function."""

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_composer_picker_output(self, mock_stdout):
        open_composer_picker()
        output = mock_stdout.getvalue()
        self.assertIn("Opening composer picker", output)
        self.assertIn("Cloud mode is active", output)
        self.assertIn("New Composer", output)
        self.assertIn("Recent Composers", output)
        self.assertIn("Browse Templates", output)


class TestStartDefaultMode(unittest.TestCase):
    """Tests for the default mode function."""

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_default_mode_output(self, mock_stdout):
        start_default_mode()
        output = mock_stdout.getvalue()
        self.assertIn("Use -c or --cloud to start in cloud mode", output)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_default_mode_verbose(self, mock_stdout):
        start_default_mode(verbose=True)
        output = mock_stdout.getvalue()
        self.assertIn("Starting in default (local) mode", output)


if __name__ == "__main__":
    unittest.main()
