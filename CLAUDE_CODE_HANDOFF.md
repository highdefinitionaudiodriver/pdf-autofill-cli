# CLAUDE_CODE_HANDOFF

## 2026-05-27

Codexが `pdf-autofill-cli` にセットアップ診断CLIと回帰テストを追加しました。

- 追加: `tools/check_setup.py`
- 追加: `tests/test_check_setup.py`
- 更新: `README.md`
- 追加: `HANDOFF_FOR_CODEX.md`

診断CLIは、PyMuPDF、主要ファイル、サンプルJSON、医療費控除テンプレート用JSON、日本語フォント候補を確認します。マッピング定義では `field_key` とプロフィールJSONの整合、座標項目、フォームフィールド名を検証します。

検証:

```powershell
python -c "from pathlib import Path; files=['main.py','tools/check_setup.py','tests/test_check_setup.py']; [compile(Path(f).read_text(encoding='utf-8'), f, 'exec') for f in files]; print('syntax OK')"
python -m unittest discover -s tests
python tools\check_setup.py
```

この実行環境では PyMuPDF が未導入のため、診断CLIは期待どおり `NG missing Python package: PyMuPDF` を返しました。`py_compile` は既存 `__pycache__` への書き込み権限で失敗したため、`.pyc` を生成しない `compile()` で構文確認しています。

次に進めるなら、実PDF生成のスモークテスト、座標プレビュー/グリッドPDF生成、医療費控除テンプレートの年次更新手順整備が着手しやすいです。
