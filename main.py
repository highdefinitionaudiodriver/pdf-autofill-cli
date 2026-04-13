"""
PDF自動入力CLIツール
====================
ユーザープロフィール(JSON)の情報を、マッピング定義に従って
PDFテンプレートに書き込み、新しいPDFとして出力する。

対応する書き込み方式:
  - coordinate: 指定ページの(x, y)座標にテキストを描画
  - form_field: PDFフォームフィールド名を指定して値をセット
"""

import argparse
import json
import sys
from pathlib import Path

import fitz  # PyMuPDF


# ---------------------------------------------------------------------------
# JSON読み込み
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict:
    """JSONファイルを読み込んで辞書として返す。"""
    if not path.exists():
        print(f"[エラー] ファイルが見つかりません: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[エラー] JSONの解析に失敗しました: {path}\n  {e}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# 日本語フォント登録
# ---------------------------------------------------------------------------

def register_japanese_font() -> str:
    """
    日本語表示用のフォントを登録して、フォント名を返す。
    Windows環境のMSゴシック(msgothic.ttc)を優先し、
    見つからなければPyMuPDF組み込みの等幅フォントにフォールバックする。
    """
    # よく使われる日本語フォントのパス候補
    font_candidates = [
        Path("C:/Windows/Fonts/msgothic.ttc"),
        Path("C:/Windows/Fonts/meiryo.ttc"),
        Path("C:/Windows/Fonts/YuGothR.ttc"),
    ]
    for font_path in font_candidates:
        if font_path.exists():
            # カスタムフォントとして登録
            font_name = font_path.stem
            fitz.Font(fontname=font_name, fontfile=str(font_path))
            return str(font_path)

    # フォントが見つからない場合はNoneを返す (ASCII専用フォールバック)
    print("[警告] 日本語フォントが見つかりません。ASCII文字のみ対応します。", file=sys.stderr)
    return None


# ---------------------------------------------------------------------------
# 座標指定による書き込み
# ---------------------------------------------------------------------------

def write_by_coordinate(page: fitz.Page, text: str, x: float, y: float,
                        font_size: float, font_path: str | None) -> None:
    """ページの指定座標にテキストを描画する。"""
    insertion_point = fitz.Point(x, y)

    if font_path:
        # 日本語フォントを使ってテキストを挿入
        page.insert_text(
            insertion_point,
            text,
            fontsize=font_size,
            fontfile=font_path,
            fontname=Path(font_path).stem,
            color=(0, 0, 0),
        )
    else:
        # フォールバック: PyMuPDF組み込みフォント (日本語非対応)
        page.insert_text(
            insertion_point,
            text,
            fontsize=font_size,
            fontname="helv",
            color=(0, 0, 0),
        )


# ---------------------------------------------------------------------------
# フォームフィールドへの書き込み
# ---------------------------------------------------------------------------

def write_by_form_field(doc: fitz.Document, field_name: str, value: str) -> bool:
    """
    PDF内のフォームフィールド(AcroForm)に値をセットする。
    フィールドが見つかればTrue、なければFalseを返す。
    """
    found = False
    for page in doc:
        for widget in page.widgets():
            if widget.field_name == field_name:
                widget.field_value = value
                widget.update()
                found = True
                print(f"  [フォーム] '{field_name}' <- '{value}'")
    if not found:
        print(f"  [スキップ] フォームフィールド '{field_name}' が見つかりません")
    return found


# ---------------------------------------------------------------------------
# メイン処理
# ---------------------------------------------------------------------------

def fill_pdf(template_path: Path, output_path: Path,
             profile: dict, mappings: list[dict]) -> None:
    """マッピング定義に従い、PDFにテキストを書き込んで保存する。"""

    if not template_path.exists():
        print(f"[エラー] テンプレートPDFが見つかりません: {template_path}", file=sys.stderr)
        sys.exit(1)

    # PDFを開く
    doc = fitz.open(str(template_path))
    print(f"テンプレート読み込み: {template_path} ({len(doc)}ページ)")

    # 日本語フォントを登録
    font_path = register_japanese_font()

    # 各マッピングを処理
    for mapping in mappings:
        field_key = mapping.get("field_key", "")
        method = mapping.get("method", "coordinate")

        # プロフィールから値を取得
        value = profile.get(field_key)
        if value is None:
            print(f"  [スキップ] プロフィールにキー '{field_key}' がありません")
            continue

        value = str(value)

        if method == "coordinate":
            # --- 座標指定 ---
            page_num = mapping.get("page", 0)
            if page_num >= len(doc):
                print(f"  [スキップ] ページ {page_num} は存在しません (全{len(doc)}ページ)")
                continue
            x = mapping.get("x", 0)
            y = mapping.get("y", 0)
            font_size = mapping.get("font_size", 10)

            page = doc[page_num]
            write_by_coordinate(page, value, x, y, font_size, font_path)
            print(f"  [座標] p{page_num} ({x},{y}) <- '{value}'")

        elif method == "form_field":
            # --- フォームフィールド ---
            field_name = mapping.get("field_name", "")
            if not field_name:
                print("  [スキップ] field_name が未指定です")
                continue
            write_by_form_field(doc, field_name, value)

        else:
            print(f"  [スキップ] 不明なmethod: '{method}'")

    # 出力先ディレクトリを作成して保存
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    doc.close()
    print(f"\n出力完了: {output_path}")


# ---------------------------------------------------------------------------
# サンプルPDF生成 (テスト用)
# ---------------------------------------------------------------------------

def create_sample_template(output_path: Path) -> None:
    """テスト用の空白PDFテンプレートを生成する。"""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4サイズ

    # ラベルを描画 (フォームの見出し)
    labels = [
        (50, 200, "氏名:"),
        (50, 240, "郵便番号:"),
        (50, 270, "都道府県:"),
        (50, 300, "市区町村:"),
        (50, 330, "番地等:"),
        (50, 370, "電話番号:"),
        (50, 400, "メール:"),
    ]
    font_path = register_japanese_font()
    for x, y, label in labels:
        if font_path:
            page.insert_text(fitz.Point(x, y), label, fontsize=10,
                             fontfile=font_path, fontname=Path(font_path).stem)
        else:
            page.insert_text(fitz.Point(x, y), label, fontsize=10, fontname="helv")

    # タイトル
    title = "PDF自動入力テスト用テンプレート"
    if font_path:
        page.insert_text(fitz.Point(150, 100), title, fontsize=16,
                         fontfile=font_path, fontname=Path(font_path).stem)
    else:
        page.insert_text(fitz.Point(150, 100), "PDF Auto-Fill Template", fontsize=16,
                         fontname="helv")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    doc.close()
    print(f"サンプルテンプレート生成: {output_path}")


# ---------------------------------------------------------------------------
# CLI エントリポイント
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="PDF自動入力CLIツール - プロフィール情報をPDFに書き込む"
    )
    parser.add_argument(
        "template",
        nargs="?",
        default=None,
        help="テンプレートPDFのパス",
    )
    parser.add_argument(
        "-p", "--profile",
        default="config/user_profile.json",
        help="ユーザープロフィールJSONのパス (デフォルト: config/user_profile.json)",
    )
    parser.add_argument(
        "-m", "--mapping",
        default="config/mapping_config.json",
        help="マッピング定義JSONのパス (デフォルト: config/mapping_config.json)",
    )
    parser.add_argument(
        "-o", "--output",
        default="output/filled.pdf",
        help="出力先PDFのパス (デフォルト: output/filled.pdf)",
    )
    parser.add_argument(
        "--generate-template",
        action="store_true",
        help="テスト用のサンプルPDFテンプレートを生成する",
    )

    args = parser.parse_args()

    # サンプルテンプレート生成モード
    if args.generate_template:
        template_out = Path(args.template or "templates/sample_template.pdf")
        create_sample_template(template_out)
        return

    # 通常の入力モード: テンプレート必須
    if args.template is None:
        parser.error("テンプレートPDFのパスを指定してください (または --generate-template でサンプルを生成)")

    # 設定ファイルを読み込み
    profile = load_json(Path(args.profile))
    mapping_config = load_json(Path(args.mapping))
    mappings = mapping_config.get("mappings", [])

    if not mappings:
        print("[エラー] マッピング定義が空です。", file=sys.stderr)
        sys.exit(1)

    # PDF入力実行
    fill_pdf(
        template_path=Path(args.template),
        output_path=Path(args.output),
        profile=profile,
        mappings=mappings,
    )


if __name__ == "__main__":
    main()
