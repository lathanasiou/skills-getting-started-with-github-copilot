"""
Unit tests for business logic functions
Tests the validation functions directly without going through the API
"""
import sys
from pathlib import Path

import pytest

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import validate_email, is_activity_full


class TestValidateEmail:
    """Tests for email validation function"""

    def test_valid_email(self):
        """Test that valid email format is accepted"""
        assert validate_email("student@mergington.edu") is True

    def test_valid_email_with_numbers(self):
        """Test valid email with numbers"""
        assert validate_email("student123@example.com") is True

    def test_valid_email_with_underscore(self):
        """Test valid email with underscore"""
        assert validate_email("student_name@example.com") is True

    def test_valid_email_with_hyphen(self):
        """Test valid email with hyphen"""
        assert validate_email("student-name@example.com") is True

    def test_valid_email_with_multiple_subdomains(self):
        """Test valid email with multiple domain levels"""
        assert validate_email("student@mail.example.co.uk") is True

    def test_invalid_email_no_at_symbol(self):
        """Test that email without @ is rejected"""
        assert validate_email("studentmergington.edu") is False

    def test_invalid_email_no_domain(self):
        """Test that email without domain is rejected"""
        assert validate_email("student@") is False

    def test_invalid_email_no_local_part(self):
        """Test that email without local part is rejected"""
        assert validate_email("@mergington.edu") is False

    def test_invalid_email_no_tld(self):
        """Test that email without top-level domain is rejected"""
        assert validate_email("student@mergington") is False

    def test_invalid_email_multiple_at_symbols(self):
        """Test that email with multiple @ symbols is rejected"""
        assert validate_email("student@@mergington.edu") is False

    def test_invalid_email_whitespace(self):
        """Test that email with whitespace is rejected"""
        assert validate_email("student @mergington.edu") is False

    def test_invalid_email_empty_string(self):
        """Test that empty string is rejected"""
        assert validate_email("") is False

    def test_valid_email_plus_addressing(self):
        """Test email with plus sign (Gmail-style)"""
        assert validate_email("student+label@mergington.edu") is True

    def test_invalid_email_special_characters(self):
        """Test that email with invalid special characters is rejected"""
        assert validate_email("student!name@mergington.edu") is False


class TestIsActivityFull:
    """Tests for activity capacity check function"""

    def test_activity_not_full_empty(self):
        """Test that empty activity is not full"""
        activity = {
            "max_participants": 10,
            "participants": []
        }
        assert is_activity_full(activity) is False

    def test_activity_not_full_with_space(self):
        """Test that activity with available space is not full"""
        activity = {
            "max_participants": 10,
            "participants": ["user1@example.com", "user2@example.com"]
        }
        assert is_activity_full(activity) is False

    def test_activity_exactly_full(self):
        """Test that activity is full when at max capacity"""
        activity = {
            "max_participants": 3,
            "participants": ["user1@example.com", "user2@example.com", "user3@example.com"]
        }
        assert is_activity_full(activity) is True

    def test_activity_one_below_capacity(self):
        """Test that activity with one spot left is not full"""
        activity = {
            "max_participants": 10,
            "participants": ["user1@example.com"] * 9
        }
        assert is_activity_full(activity) is False

    def test_activity_one_above_capacity(self):
        """Test that activity exceeding max is considered full"""
        activity = {
            "max_participants": 10,
            "participants": ["user@example.com"] * 11
        }
        assert is_activity_full(activity) is True

    def test_activity_large_capacity(self):
        """Test activity with large capacity"""
        activity = {
            "max_participants": 100,
            "participants": ["user@example.com"] * 99
        }
        assert is_activity_full(activity) is False

    def test_activity_large_capacity_full(self):
        """Test activity with large capacity that is full"""
        activity = {
            "max_participants": 100,
            "participants": ["user@example.com"] * 100
        }
        assert is_activity_full(activity) is True

    def test_activity_single_spot(self):
        """Test activity with single spot"""
        activity = {
            "max_participants": 1,
            "participants": []
        }
        assert is_activity_full(activity) is False

    def test_activity_single_spot_full(self):
        """Test activity with single spot that is full"""
        activity = {
            "max_participants": 1,
            "participants": ["user@example.com"]
        }
        assert is_activity_full(activity) is True
