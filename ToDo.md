## ToDo

### Polarized Ice の生成

- [x] 検証のためのプラグインを準備。
- [x] target_pol を与えるために引数を追加。
- [ ] 動作検証コードを作成。

- [ ] temp_README の作表の部分を改良。(生成側で header も作る)

### Polarized Ice の生成

- [x] 検証のためのプラグインを準備。
- [x] target_pol を与えるために引数を追加。
- [ ] 動作検証コードを作成。

- [ ] temp_README の作表の部分を改良。(生成側で header も作る)

- [x] reactive なデータ生成。無駄がなくていい。
- [x] spot anion & cation
- 目玉機能。この 2 つが完成するまでは公表できない。
  - [ ] group!
    - [ ] API呼び出しでgroupを指定する方法を文書化する。
    - [ ] カチオンのサブオプションとしてgroupを指定する。例: `--cation 0=[N --group 1=methyl 2=butyl 4=hexyl 12=methyl]`（階層記法）。flat記法も検討。
    - [ ] インタラクティブCLI: `--group 水分子番号` で隣接4ケージのメニューを表示し、各ケージに配置するgroupを選択させる（questionary使用）。
  - [ ] topological defects
    - 指定方法を真剣に考える。本来なら、edge を指定する必要がある。まあそれでいいか。-D 0 2 -L 4 5
    - GenIce3 CLI に登録する必要はないと思う。API で簡単に書ければ十分。
- [x] Loader (CIF, mdanalysis)
- [x] API レベルでの mdanalysis との連携方法。gro ファイルを経由するのが手っ取り早いのか。
- [ ] Exporter を増やす。
  - [x] svg 細かいチェックはできてない。
  - [x] png 細かいチェックはできてない。
  - [x] py3dmol
  - [x] mdanalysis これも py3dmol 方式で、一旦 gromacs を経由すれば簡単。コマンドラインで呼ぶ場合(dump)は、オプションには出力ファイル名を掻く。API で呼ぶ場合(universe())には、`Universe`オブジェクトを返す。
  - [x] \_KG まだおかしい。
- [x] 速度改善 → GenIce2 よりは早そう。
- [ ] Jupyter sample. xFAU はひとまず回避しよう。
- [ ] xFAU なぜうまくつながらないのか謎。
- [x] オプション内の Plugin の扱いの統一。コマンドラインではやむを得ないが、API から呼ぶ場合は loader を省略しないほうが良い。(オプションを指定する場合とで書式が変わってししまうのは結局親切といえない)
  - [x] 階層的オプションを扱うためのデータ形式の再検討。JSON5? HOCON?
  - [x] 深く再検討する。svg ですでにリスト型オプションのセパレータに`,`を使っていることに留意。
- [x] seed の設定は reactive か?
- [ ] Plugin を実行すると usage が表示されるように。
- [ ] help の充実。

## Bug

- poetry はシンボリックリンクをパッケージに含めない。そのため、いくつかのモジュールが使えなくなる。
  - .genice2/を一時的に作成して symlink をコピーに変換し、そこから wheel を生成するようにした。
