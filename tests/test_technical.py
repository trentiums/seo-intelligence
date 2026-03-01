"""Unit tests for technical SEO audit module."""

import pytest

from technical import (
    format_technical_audit,
)
from models import (
    PageAnalysis,
    TechnicalCheckResult,
    TechnicalAuditResult,
)


# ─── TechnicalCheckResult Tests ─────────────────────────────────────────────


class TestTechnicalCheckResult:
    """Test technical check result data model."""

    def test_pass_result(self):
        result = TechnicalCheckResult(
            check="Sitemap",
            status="pass",
            details="Valid sitemap found.",
        )
        assert result.status == "pass"
        assert result.recommendation == ""

    def test_fail_result_with_recommendation(self):
        result = TechnicalCheckResult(
            check="Sitemap",
            status="fail",
            details="No sitemap found.",
            recommendation="Create a sitemap.xml",
        )
        assert result.status == "fail"
        assert "sitemap" in result.recommendation.lower()

    def test_warn_result(self):
        result = TechnicalCheckResult(
            check="Robots.txt",
            status="warn",
            details="Missing sitemap reference.",
        )
        assert result.status == "warn"


# ─── TechnicalAuditResult Tests ─────────────────────────────────────────────


class TestTechnicalAuditResult:
    """Test technical audit result aggregation."""

    def test_healthy_status(self):
        result = TechnicalAuditResult(
            url="https://example.com",
            checks=[
                TechnicalCheckResult(check="Sitemap", status="pass"),
                TechnicalCheckResult(check="Robots.txt", status="pass"),
                TechnicalCheckResult(check="SSL", status="pass"),
            ],
            passed=3,
            warnings=0,
            failed=0,
            overall_status="Healthy",
        )
        assert result.overall_status == "Healthy"
        assert result.passed == 3

    def test_needs_attention_status(self):
        result = TechnicalAuditResult(
            url="https://example.com",
            checks=[
                TechnicalCheckResult(check="Sitemap", status="fail"),
                TechnicalCheckResult(check="Robots.txt", status="pass"),
                TechnicalCheckResult(check="SSL", status="pass"),
            ],
            passed=2,
            warnings=0,
            failed=1,
            overall_status="Needs Attention",
        )
        assert result.overall_status == "Needs Attention"
        assert result.failed == 1

    def test_critical_status(self):
        result = TechnicalAuditResult(
            url="https://example.com",
            checks=[
                TechnicalCheckResult(check="Sitemap", status="fail"),
                TechnicalCheckResult(check="SSL", status="fail"),
                TechnicalCheckResult(check="Redirects", status="warn"),
            ],
            passed=0,
            warnings=1,
            failed=2,
            overall_status="Critical",
        )
        assert result.overall_status == "Critical"
        assert result.failed == 2

    def test_error_state(self):
        result = TechnicalAuditResult(
            url="https://example.com",
            error="Connection timeout",
        )
        assert result.error == "Connection timeout"
        assert len(result.checks) == 0


# ─── Formatter Tests ─────────────────────────────────────────────────────────


class TestFormatTechnicalAudit:
    """Test the technical audit formatter."""

    def test_format_healthy_audit(self):
        result = TechnicalAuditResult(
            url="https://example.com",
            checks=[
                TechnicalCheckResult(check="Sitemap", status="pass", details="Found"),
                TechnicalCheckResult(check="SSL", status="pass", details="HTTPS OK"),
            ],
            passed=2,
            warnings=0,
            failed=0,
            overall_status="Healthy",
        )
        output = format_technical_audit(result)
        assert "Healthy" in output
        assert "✅" in output
        assert "example.com" in output

    def test_format_with_failures(self):
        result = TechnicalAuditResult(
            url="https://example.com",
            checks=[
                TechnicalCheckResult(
                    check="Sitemap",
                    status="fail",
                    details="Missing",
                    recommendation="Create sitemap.xml",
                ),
            ],
            passed=0,
            warnings=0,
            failed=1,
            overall_status="Critical",
        )
        output = format_technical_audit(result)
        assert "❌" in output
        assert "Critical" in output
        assert "Create sitemap.xml" in output

    def test_format_error(self):
        result = TechnicalAuditResult(
            url="https://example.com",
            error="Connection failed",
        )
        output = format_technical_audit(result)
        assert "Connection failed" in output
        assert "❌" in output

    def test_format_warnings(self):
        result = TechnicalAuditResult(
            url="https://example.com",
            checks=[
                TechnicalCheckResult(
                    check="Robots.txt",
                    status="warn",
                    details="No sitemap reference",
                ),
            ],
            passed=0,
            warnings=1,
            failed=0,
            overall_status="Needs Attention",
        )
        output = format_technical_audit(result)
        assert "⚠️" in output
        assert "Needs Attention" in output
