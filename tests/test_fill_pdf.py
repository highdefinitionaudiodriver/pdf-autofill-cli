"""pdf-autofill-cli の入力処理 (main.fill_pdf) の統合テスト.

実際に PyMuPDF でサンプル PDF を生成 → プロフィールを流し込み → 出力 PDF の
テキストを抽出して、座標書き込み・キー欠落/ページ範囲外/未知メソッドの
スキップ・フォームフィールド書き込みを検証する。
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import main  # noqa: E402

fitz = pytest.importorskip("fitz")  # PyMuPDF 未導入ならスキップ


@pytest.fixture
def template(tmp_path):
    path = tmp_path / "template.pdf"
    main.create_sample_template(path)
    return path


def _extract_text(pdf_path: pathlib.Path) -> str:
    doc = fitz.open(str(pdf_path))
    try:
        return "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()


def test_coordinate_write_embeds_values(template, tmp_path):
    out = tmp_path / "out.pdf"
    profile = {"name": "山田太郎", "zip": "100-0001"}
    mappings = [
        {"field_key": "name", "method": "coordinate", "page": 0, "x": 150, "y": 200, "font_size": 10},
        {"field_key": "zip", "method": "coordinate", "page": 0, "x": 150, "y": 240, "font_size": 10},
    ]
    main.fill_pdf(template, out, profile, mappings)

    assert out.exists()
    text = _extract_text(out)
    assert "山田太郎" in text
    assert "100-0001" in text


def test_missing_profile_key_is_skipped(template, tmp_path):
    out = tmp_path / "out.pdf"
    profile = {"name": "佐藤花子"}
    mappings = [
        {"field_key": "name", "method": "coordinate", "page": 0, "x": 150, "y": 200},
        {"field_key": "does_not_exist", "method": "coordinate", "page": 0, "x": 150, "y": 240},
    ]
    # 欠落キーがあっても例外にならず、存在するキーは書き込まれる
    main.fill_pdf(template, out, profile, mappings)
    assert "佐藤花子" in _extract_text(out)


def test_out_of_range_page_is_skipped(template, tmp_path):
    out = tmp_path / "out.pdf"
    profile = {"name": "範囲外テスト"}
    mappings = [{"field_key": "name", "method": "coordinate", "page": 99, "x": 10, "y": 10}]
    # ページ範囲外でもクラッシュせず保存される
    main.fill_pdf(template, out, profile, mappings)
    assert out.exists()


def test_unknown_method_is_skipped(template, tmp_path):
    out = tmp_path / "out.pdf"
    profile = {"name": "x"}
    mappings = [{"field_key": "name", "method": "telepathy"}]
    main.fill_pdf(template, out, profile, mappings)
    assert out.exists()


def test_form_field_write_sets_value(tmp_path):
    # フォームフィールド(ウィジェット)を持つ PDF を生成
    src = tmp_path / "form.pdf"
    doc = fitz.open()
    page = doc.new_page(width=300, height=200)
    widget = fitz.Widget()
    widget.field_name = "name_field"
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.rect = fitz.Rect(50, 50, 250, 70)
    page.add_widget(widget)
    doc.save(str(src))
    doc.close()

    doc = fitz.open(str(src))
    try:
        assert main.write_by_form_field(doc, "name_field", "記入太郎") is True
        # 存在しないフィールドは False
        assert main.write_by_form_field(doc, "nope", "x") is False
    finally:
        doc.close()


def test_load_json_missing_file_exits(tmp_path):
    with pytest.raises(SystemExit):
        main.load_json(tmp_path / "nope.json")


def test_load_json_invalid_json_exits(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(SystemExit):
        main.load_json(bad)


def test_load_json_valid(tmp_path):
    good = tmp_path / "good.json"
    good.write_text(json.dumps({"a": 1}), encoding="utf-8")
    assert main.load_json(good) == {"a": 1}


def test_fill_pdf_missing_template_exits(tmp_path):
    with pytest.raises(SystemExit):
        main.fill_pdf(tmp_path / "nope.pdf", tmp_path / "o.pdf", {}, [])
