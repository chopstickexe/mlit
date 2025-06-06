"""
Tests for Foreign Exchange Law compliance functionality
"""

import pytest
from mlit.compliance import ComplianceChecker, ComplianceStatus, validate_export_compliance


def test_mlit_data_compliance():
    """MLIT公開データの該非判定テスト"""
    checker = ComplianceChecker()
    result = checker.check_data_compliance(
        data_source="https://renrakuda.mlit.go.jp/renrakuda/",
        data_type="自動車不具合情報"
    )
    
    assert result["status"] == ComplianceStatus.NON_APPLICABLE
    assert "公開されている自動車安全情報" in result["reason"]
    assert "外為法第48条" in result["legal_basis"]


def test_unknown_data_requires_review():
    """未知のデータソースは要確認となることをテスト"""
    checker = ComplianceChecker()
    result = checker.check_data_compliance(
        data_source="https://unknown-source.com/",
        data_type="unknown_data"
    )
    
    assert result["status"] == ComplianceStatus.REQUIRES_REVIEW
    assert "手動での該非判定が必要" in result["reason"]


def test_domestic_export_compliance():
    """国内利用の輸出コンプライアンステスト"""
    assert validate_export_compliance(target_country=None) is True


def test_international_export_compliance():
    """国際輸出のコンプライアンステスト"""
    # 一般的な国への輸出は許可されるべき（公開情報のため）
    assert validate_export_compliance(target_country="US") is True
    assert validate_export_compliance(target_country="EU") is True


def test_compliance_report_generation():
    """コンプライアンス報告書生成テスト"""
    checker = ComplianceChecker()
    sources = [
        "https://renrakuda.mlit.go.jp/renrakuda/",
        "https://another-mlit-source.mlit.go.jp/"
    ]
    
    report = checker.generate_compliance_report(sources)
    
    assert report["total_sources"] == 2
    assert len(report["determinations"]) == 2
    assert "report_date" in report