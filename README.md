# Tkinter Dashboard Sample

Tkinter を使用したダッシュボードアプリのサンプルです。

SQLite に保存された設備のアラーム履歴を読み込み、検索条件に応じて
**Matplotlib のグラフ**と **ttk.Treeview のテーブル**で可視化します。

このプロジェクトでは、1つの大きなファイルにすべての処理をまとめるのではなく、
各タブを独立した Python ファイルとして分離しています。

そのため、今後 Tkinter で設備データ、生産実績、稼働率、品質データなどを
可視化するダッシュボードを作成するときのテンプレートとして利用できます。

---

## 主な機能

- Tkinter / ttk を使用したデスクトップ GUI
- `ttk.Notebook` を使用したタブ形式の画面
- SQLite からのデータ検索
- 機械番号による絞り込み
- 開始日・終了日による期間指定
- Matplotlib グラフの Tkinter への埋め込み
- Treeview による検索結果一覧表示
- アラーム種類別の発生回数表示
- 日別のアラーム発生回数表示
- 日付にデータがない場合は `0` として補完
- 平日と土日で棒グラフの色を変更
- 共通 UI スタイルを `style.py` に分離
- 各タブを単体でも起動して確認可能

---

## 画面構成

アプリには次の2つのタブがあります。

### アラーム別

指定した機械番号・期間のアラーム履歴を取得し、
アラームコメントごとの発生回数を横棒グラフで表示します。

発生回数が多いアラームほど上側に表示されます。

グラフには各アラームの発生回数と、期間内の合計発生回数を表示します。

画面下部のテーブルには、対象期間のアラーム履歴を時系列で表示します。

### 日別

指定した機械番号・期間について、
1日ごとのアラーム発生回数を棒グラフで表示します。

アラームが1件も発生していない日も省略せず、`0` 件として表示します。

現在の設定では、

- 平日：pink
- 土日：gray

として表示します。

画面下部には、アラーム履歴を時系列で表示します。

---

## ファイル構成

```text
.
├─ app.py
├─ alarm_tab.py
├─ daily_tab.py
├─ style.py
└─ body_inspection_machine.db
```

### `app.py`

アプリ全体のエントリーポイントです。

主な役割は次のとおりです。

- メインウィンドウの作成
- 共通スタイルの適用
- `ttk.Notebook` の作成
- `AlarmTab` の登録
- `DailyTab` の登録
- アプリ終了時の Matplotlib Figure のクローズ

各タブ内部の検索処理やグラフ処理は `app.py` に持たせず、
それぞれのタブ側に分離しています。

### `alarm_tab.py`

「アラーム別」タブを担当します。

`AlarmTab(ttk.Frame)` として実装されており、主に次の処理を持ちます。

- 検索条件 UI
- SQLite から機械番号を取得
- アラームコメント別の発生回数を集計
- アラーム履歴を取得
- 横棒グラフを更新
- Treeview を更新
- 日付入力の増減

SQL では `alarm_comment` ごとに `COUNT(*)` して、
発生回数の多い順に取得します。

### `daily_tab.py`

「日別」タブを担当します。

`DailyTab(ttk.Frame)` として実装されており、基本構造は
`AlarmTab` とほぼ同じです。

主な違いはグラフ用データの作り方です。

SQLite から日別の件数を取得したあと、
`fill_missing_dates()` で検索期間内の欠落日を `0` 件として補完します。

また、`get_bar_colors()` で曜日を判定し、
平日と土日で棒グラフの色を変更しています。

### `style.py`

アプリ全体で使用する ttk ウィジェットの共通スタイルを設定します。

対象例：

- Label
- Entry
- Combobox
- Button
- Notebook Tab
- Treeview
- Treeview Heading

フォントや余白、Treeview の行高などを一か所で変更できます。

---

## 使用ライブラリ

標準ライブラリ：

- `tkinter`
- `sqlite3`
- `datetime`
- `pathlib`

追加ライブラリ：

- `matplotlib`

Matplotlib がインストールされていない場合は、次のコマンドでインストールします。

```bash
pip install matplotlib
```

Tkinter と SQLite は通常の Python for Windows では標準で利用できます。

---

## データベース

データベースファイル：

```text
body_inspection_machine.db
```

各タブは、Python ファイルと同じフォルダにある
`body_inspection_machine.db` を参照します。

使用するテーブルは次のとおりです。

```text
alarm_history
```

このアプリで使用している主な列は次の3つです。

```text
machine_no
datetime
alarm_comment
```

`machine_no` は機械番号、
`datetime` はアラーム発生日時、
`alarm_comment` はアラーム内容として使用します。

---

## 実行方法

必要なファイルを同じフォルダに配置します。

```text
app.py
alarm_tab.py
daily_tab.py
style.py
body_inspection_machine.db
```

その後、次のコマンドで起動します。

```bash
python app.py
```

---

## 操作方法

1. `Machine No` から対象設備を選択します。
2. `Start` に検索開始日を入力します。
3. `End` に検索終了日を入力します。
4. `Search` を押します。
5. グラフとテーブルが更新されます。

日付形式は次の形式です。

```text
YYYY-MM-DD
```

例：

```text
2026-09-01
```

開始日・終了日の Entry では、上下キーでも日付を変更できます。

- `↑`：1日前
- `↓`：1日後
- `Enter`：検索実行

機械番号を Combobox から変更した場合も検索が実行されます。

初期表示では、

- Start：当月1日
- End：今日

が設定されます。

---

## プログラム構造

このサンプルで重視しているのは、
**タブごとの独立性を高く保つこと**です。

```text
app.py
  │
  ├─ AlarmTab
  │    ├─ Search UI
  │    ├─ SQLite
  │    ├─ Chart
  │    └─ Table
  │
  └─ DailyTab
       ├─ Search UI
       ├─ SQLite
       ├─ Chart
       └─ Table
```

`app.py` は各タブを配置する役割に集中し、
具体的な処理は各タブ自身が担当します。

この構成にすると、新しいタブを追加するときも既存タブへの影響を抑えられます。

---

## 新しいタブを追加する場合

例えば「機械別」「月別」「停止時間別」などのタブを追加したい場合は、
既存の `alarm_tab.py` または `daily_tab.py` をテンプレートとしてコピーできます。

例：

```text
machine_tab.py
```

```python
class MachineTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
```

その後、`app.py` に追加します。

```python
from machine_tab import MachineTab

machine_tab = MachineTab(notebook)

notebook.add(
    machine_tab,
    text="機械別",
)
```

各タブを独立させることで、タブごとに必要な変数名や処理を自由に記述できます。

---

## この構成の考え方

このサンプルでは、すべてを無理に共通化することはしていません。

`AlarmTab` と `DailyTab` には似たコードがありますが、
それぞれを独立したファイルとして保持しています。

これは意図的な設計です。

ダッシュボードでは、最初は似ていた画面でも、
後から個別の検索条件、グラフ、テーブル、ボタンなどが追加されることがあります。

過度に共通化すると、1つのタブを変更するために
共通クラスや設定値まで追いかける必要が生じ、
コードが読みにくくなる場合があります。

このサンプルでは、

> 共通化する部分は限定し、各タブの具体的な処理は各ファイルに残す

という方針を採用しています。

共通化している代表例が `style.py` です。

見た目の設定は共通化しても各タブの処理内容への影響が小さいため、
共通ファイルとして分離しています。

一方、SQL、グラフ更新、テーブル更新などは各タブに残しています。

---

## カスタマイズ

グラフの基本設定は各タブ上部の Settings セクションにあります。

例：

```python
CHART_TITLE = "Daily Alarm Count"
CHART_X_LABEL = "Date"
CHART_Y_LABEL = "Count"
CHART_COLOR = "special"
```

グラフ種類そのものを変更したい場合は `update_chart()` を変更します。

例えば、

```python
self.ax.bar(...)
self.ax.barh(...)
self.ax.plot(...)
self.ax.scatter(...)
```

などへ変更できます。

Treeview の列設定も `TABLE_COLUMNS` にまとめています。

```python
TABLE_COLUMNS = {
    "datetime": {
        "text": "Datetime",
        "width": 200,
        "anchor": tk.CENTER,
    },
}
```

そのため、列名・幅・配置の変更箇所を見つけやすい構成になっています。

---

## タブ単体での動作確認

`alarm_tab.py` と `daily_tab.py` には、それぞれ

```python
if __name__ == "__main__":
```

のテスト起動処理があります。

そのため、アプリ全体を起動しなくても、

```bash
python alarm_tab.py
```

または

```bash
python daily_tab.py
```

として、対象タブだけを起動して確認できます。

タブ単位で開発・修正・テストしやすいことも、この構成の特徴です。

---

## 想定用途

このサンプルはアラーム履歴を題材にしていますが、
基本構造はさまざまな工場向けダッシュボードに流用できます。

例えば、

- 生産実績
- 稼働時間
- 稼働率
- 不良数
- 品質データ
- 設備停止履歴
- センサーデータ
- モーター電流
- PLC 収集データ

などです。

SQLite の検索処理と `update_chart()` を変更することで、
同じ UI 構造を使いながら別のデータを可視化できます。

---

## 開発方針

このサンプルでは、次の考え方を重視しています。

**KISS (Keep It Simple, Stupid)**

必要以上に抽象化せず、
コードを開いたときに「このタブで何をしているのか」が
すぐ分かる構造を目指しています。

似たタブを追加するときは、
既存タブをテンプレートとしてコピーして必要な部分だけ変更する方法も
実用的な選択肢としています。

ダッシュボードの規模が大きくなった場合でも、

```text
1 tab = 1 Python file
```

を基本にすることで、各画面の独立性と可読性を保ちやすくなります。

---

## Summary

This is a sample dashboard application built with Tkinter.

It demonstrates a simple structure for building desktop dashboards with:

- Tkinter / ttk
- SQLite
- Matplotlib
- Treeview
- Notebook tabs
- Independent tab modules
- Shared UI styles

The project is intended to be used as a simple template for future dashboard applications.
