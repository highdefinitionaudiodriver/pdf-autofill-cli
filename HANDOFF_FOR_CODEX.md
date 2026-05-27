# HANDOFF_FOR_CODEX

## 2026-05-27 Codex 作業メモ

対象: `pdf-autofill-cli`

### セットアップ診断CLIを追加

PDF生成前に、ローカル環境と設定JSONが最低限そろっているか確認できる `tools/check_setup.py` を追加しました。

確認内容:

- 主要ファイル構成
  - `main.py`
  - `requirements.txt`
  - `config/user_profile.json`
  - `config/mapping_config.json`
  - `templates/sample_template.pdf`
  - `templates/iryouhi_meisai/user_profile.iryouhi.json`
  - `templates/iryouhi_meisai/mapping_config.iryouhi.json`
- Python依存
  - `PyMuPDF` (`fitz`)
- 日本語フォント候補
  - `C:/Windows/Fonts/msgothic.ttc`
  - `C:/Windows/Fonts/meiryo.ttc`
  - `C:/Windows/Fonts/YuGothR.ttc`
- 設定JSON
  - `mappings` が空でないこと
  - `field_key` がプロフィールJSONに存在すること
  - `coordinate` の `page` / `x` / `y` が数値であること
  - `form_field` の `field_name` が指定されていること

### 回帰テストを追加

`tests/test_check_setup.py` を追加し、診断CLIのマッピング検証ロジックを依存パッケージなしで確認できるようにしました。

### README更新

READMEに `python tools/check_setup.py` の手順を追記し、末尾の現状サマリを今回の状態に更新しました。

### 検証

```powershell
& 'C:\Users\highd\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -c "from pathlib import Path; files=['main.py','tools/check_setup.py','tests/test_check_setup.py']; [compile(Path(f).read_text(encoding='utf-8'), f, 'exec') for f in files]; print('syntax OK')"
& 'C:\Users\highd\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests
& 'C:\Users\highd\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\check_setup.py
```

この実行環境では PyMuPDF が未導入のため、診断CLIは期待どおり `NG missing Python package: PyMuPDF` を返しました。`py_compile` は既存 `__pycache__` への書き込み権限で失敗したため、`.pyc` を生成しない `compile()` で構文確認しています。

### 次に着手しやすいこと

- `--generate-template` から生成したPDFに対して、実際に `fill_pdf()` するスモークテストを追加する
- 座標調整を支援するプレビュー/グリッドPDF生成オプションを追加する
- 医療費控除明細書テンプレートの年次更新手順を `templates/iryouhi_meisai/README.md` に追記する
