"""The Korean detector that guards the English build (``robotics_curriculum.i18n.scan``)."""

from __future__ import annotations

import pytest

from robotics_curriculum.i18n.scan import (
    find_hangul,
    has_hangul,
    html_text,
    iter_json_strings,
    scan_json,
    scan_text,
)


@pytest.mark.parametrize(
    "text",
    ["기초", "ROS 2 개념", "ㄱㄴㄷ", "가", "Modern Robotics 위키"],
)
def test_korean_text_is_detected(text: str) -> None:
    assert has_hangul(text)


@pytest.mark.parametrize(
    "text",
    ["", "Vectors and matrices", "ROS 2", "$\\theta = 0^\\circ$", "日本語", "naïve café"],
)
def test_other_scripts_are_not_korean(text: str) -> None:
    assert not has_hangul(text)
    assert find_hangul(text) == []


def test_find_hangul_returns_each_run() -> None:
    assert find_hangul("a 기초 b 고급") == ["기초", "고급"]


def test_scan_text_reports_the_run_and_its_context() -> None:
    (finding,) = scan_text("the stage is 기초 for now", "line 1")
    assert finding.where == "line 1"
    assert finding.text == "기초"
    assert "the stage is 기초 for now" in finding.context
    assert str(finding).startswith("line 1: ")


def test_iter_json_strings_walks_values_and_korean_keys() -> None:
    data = {"a": ["x", {"b": "y"}], "단계": "z"}
    assert dict(iter_json_strings(data)) == {
        "/a/0": "x",
        "/a/1/b": "y",
        "/단계 (key)": "단계",
        "/단계": "z",
    }


def test_scan_json_points_at_the_offending_field() -> None:
    findings = scan_json({"stages": [{"level": "기초"}, {"level": "advanced"}]}, "GET /courses ")
    assert [f.where for f in findings] == ["GET /courses /stages/0/level"]


def test_scan_json_ignores_numbers_and_nulls() -> None:
    assert scan_json({"n": 1, "ok": True, "none": None, "f": 1.5}) == []


def test_html_text_drops_scripts_styles_comments_and_tags() -> None:
    html = (
        '<html><head><style>body{content:"기초"}</style>'
        '<script>var s = "중급"</script></head>'
        "<body><!-- 고급 --><p>Stage: <b>Foundation</b></p></body></html>"
    )
    text = html_text(html)
    assert not has_hangul(text)
    assert "Foundation" in text


def test_html_text_keeps_visible_korean() -> None:
    assert has_hangul(html_text("<p>기초</p>"))


def test_html_entities_do_not_hide_text() -> None:
    assert "&amp;" not in html_text("<p>a &amp; b</p>")
