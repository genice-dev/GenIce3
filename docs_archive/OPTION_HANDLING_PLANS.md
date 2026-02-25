# 現在の記法

```shell
python3 -m genice3.cli.genice "A15[shift=(0.1,0.1,0.1), anion.15=Cl, cation.21=Na, density=0.8]" \
  --rep 2 2 2 \
  --exporter "gromacs[guest.A12=me, guest.A14=et, spot_guest.0=4site, water_model=4site[type=ice]]" \
  --seed 42 \
  --depol_loop 2000 \
  --spot_anion 1=Cl \
  --spot_cation 5=Na
```

## 問題点

- コマンドラインのオプション(genice3 のグローバルオプション)と、プラグインのオプション([]で囲み、コンマで区切り)で書き方が違う。
- shift オプションで使っているコンマ区切りと、プラグインオプションのコンマ区切りが衝突する。

# genice2 風の記法

```shell
python3 -m genice3.cli.genice "A15[shift=0.1,0.1,0.1:density=0.8]" \
 --rep 2 2 2 \
 --exporter "gromacs[water_model=4site:opt=False]" \
 --seed 42 \
 --depol_loop 2000 \
 --spot_anion 1=Cl \
 --spot_cation 5=Na
```

## 問題点

- コマンドラインのオプション(genice3 のグローバルオプション)と、プラグインのオプション([]で囲み、コンマで区切り)で書き方が違う。
- プラグインのオプションは階層構造に対応していない。
- プラグインオプションには空白が使えない

# 階層のあるコマンドラインオプション

```shell
python3 -m genice3.cli.genice A15 --A15.shift=(0.1,0.1,0.1) \
 --A15.anion.15=Cl --A15.cation.21=Na --A15.density=0.8 \
 --rep 2 2 2 \
 --exporter gromacs--gromacs.guest.A12=me --gromacs.guest.A14=et \
 --gromacs.spot_guest.0=4site --gromacs.water_model=4site \
 --gromacs.4site.type=ice" \
 --seed 42 \
 --depol_loop 2000 \
 --spot_anion 1=Cl \
 --spot_cation 5=Na
```

## 問題点

- 全部同じように option の記法で書けるのはいい
- しかしものすごく冗長な上に階層構造もわからない。

# JSON

```json
{
  "unitcell": {
    "name": "A15",
    "options": {
      "shift": [0.1, 0.1, 0.1],
      "anion": {
        "15": "Cl"
      },
      "cation": {
        "21": "Na"
      },
      "density": 0.8
    }
  },
  "replication_factors": [2, 2, 2],
  "exporter": {
    "name": "gromacs",
    "options": {
      "guest": {
        "A12": "me",
        "A14": "et"
      },
      "spot_guest": {
        "0": "4site"
      },
      "water_model": {
        "name": "4site",
        "options": {
          "type": "ice"
        }
      }
    }
  },
  "seed": 42,
  "depol_loop": 2000,
  "spot_anion": {
    "1": "Cl"
  },
  "spot_cation": {
    "5": "Na"
  }
}
```

または、より簡潔な形式（インライン）:

```json
{
  "unitcell": {
    "name": "A15",
    "options": {
      "shift": [0.1, 0.1, 0.1],
      "anion": { "15": "Cl" },
      "cation": { "21": "Na" },
      "density": 0.8
    }
  },
  "replication_factors": [2, 2, 2],
  "exporter": {
    "name": "gromacs",
    "options": {
      "guest": { "A12": "me", "A14": "et" },
      "spot_guest": { "0": "4site" },
      "water_model": { "name": "4site", "options": { "type": "ice" } }
    }
  },
  "seed": 42,
  "depol_loop": 2000,
  "spot_anion": { "1": "Cl" },
  "spot_cation": { "5": "Na" }
}
```

## 利点

- 階層構造が明確
- 配列、オブジェクト、文字列など、すべての型を適切に表現できる
- プラグインオプションのネストも自然に表現できる

## 問題点

- コマンドラインに JSON を書くのはかなり抵抗がある（エスケープが面倒）
- シェルで使う際に引用符の処理が複雑

# HOCON

```hocon
unitcell { name = A15, options { shift = [0.1, 0.1, 0.1], anion { 15 = Cl }, cation { 21 = Na }, density = 0.8 } }, replication_factors = [2, 2, 2], exporter { name = gromacs, options { guest { A12 = me, A14 = et }, spot_guest { 0 = 4site }, water_model { name = 4site, options { type = ice } } } }, seed = 42, depol_loop = 2000, spot_anion { 1 = Cl }, spot_cation { 5 = Na }
```

- これもいわゆるコマンドラインの書きかたではまず見かけない書き方だなあ。

# コマンドラインのオプション記法を、むりやりプラグインにも使うスタイル

```shell
python3 -m genice3.cli.genice "A15 --shift 0.1 0.1 0.1 \
  --anion 15=Cl --cation 21=Na --density 0.8" \
  --rep 2 2 2 \
  --exporter "gromacs --guest A12=me --guest A14=et \
  --spot_guest 0=4site --water_model '4site --type ice'" \
  --seed 42 \
  --depol_loop 2000 \
  --spot_anion 1=Cl \
  --spot_cation 5=Na
```

- 一貫性はある。
- 読みやすいかというと微妙。
- クオーテーションに頼ると、階層は 2 層まで。そこだけカッコに変えるといいかも。
- おそらく click はこれをうまく分割できない?

# コマンドラインのオプション記法を、むりやりプラグインにも使うスタイル 2

```shell
python3 -m genice3.cli.genice A15[--shift 0.1 0.1 0.1 \
  --anion 15=Cl --cation 21=Na --density 0.8] \
  --rep 2 2 2 \
  --exporter gromacs[--guest A12=me --guest A14=et \
  --spot_guest 0=4site --water_model 4site[--type ice]] \
  --seed 42 \
  --depol_loop 2000 \
  --spot_anion 1=Cl \
  --spot_cation 5=Na
```

- 一貫性はある。
- たぶん、click はそのままでは処理できない。

# コマンドラインのオプション記法を、むりやりプラグインにも使うスタイル 2

```shell
python3 -m genice3.cli.genice [A15 --shift 0.1 0.1 0.1 \
  --anion 15=Cl --cation 21=Na --density 0.8] \
  --rep 2 2 2 \
  --exporter [gromacs --guest A12=me --guest A14=et \
  --spot_guest 0=4site --water_model [4site --type ice]] \
  --seed 42 \
  --depol_loop 2000 \
  --spot_anion 1=Cl \
  --spot_cation 5=Na
```

- 一貫性はある。
- 複数の記法を理解する必要がない点では一番簡潔。
- ただし、click はそのままでは処理できない。
- click に渡す前の処理を加えればいいかも。

## 実装方法について

click の`Command.main()`メソッドは`args`パラメータでカスタム引数リストを受け取れる:

```python
# 現在の実装
if __name__ == "__main__":
    main()  # sys.argvを自動的に使用

# カスタム引数リストを渡す場合
if __name__ == "__main__":
    import sys
    # プリプロセッサで [A15 --shift ...] 形式を解析し、
    # 通常の形式に変換してからclickに渡す
    processed_args = preprocess_args(sys.argv[1:])
    main.main(args=processed_args)  # カスタム引数リストを渡す
```

したがって、`[A15 --shift 0.1 0.1 0.1 --density 0.8]`のような形式をパースして、`"A15[shift=(0.1,0.1,0.1),density=0.8]"`のような既存の形式に変換するプリプロセッサを実装すれば、click にそのまま渡せる。

## この記法の利点（理解しやすさの観点）

- **既存知識の再利用**: `--オプション 値`という標準的な CLI 記法をそのまま使えるため、新しい記法を覚える必要がない
- **視覚的な明確さ**: `[プラグイン名 --オプション ...]`という形式で、どこからどこまでがプラグインの範囲かが一目瞭然
- **階層の表現が直感的**: `[プラグイン [ネストされたプラグイン]]`という入れ子構造で、階層関係が自然に理解できる
- **統一性**: グローバルオプション（`--rep`, `--seed`など）とプラグインオプション（`--shift`, `--guest`など）が同じ`--`記法で統一されている
- **学習コストが低い**: `plugin[options]`や`plugin[key=value,key=value]`などの特殊記法を覚える必要がない

この記法は、ユーザーが既に知っている CLI の知識だけで理解できるため、**理解までのハードルが最も低い**と言える。

## さらにユーザーの学習コストが低い方法

プラグインのオプションが、基底レベルで指定された場合で、基底レベルで処理されなかった場合には、プラグインに順次処理が渡されるようにする。

```shell
python3 -m genice3.cli.genice A15  \
  --rep 2 2 2 \
  --exporter gromacs \
  --seed 42 \
  --depol_loop 2000 \
  --spot_anion 1=Cl \
  --spot_cation 5=Na \
  --shift 0.1 0.1 0.1 \
  --anion 15=Cl --cation 21=Na --density 0.8 \
  --guest A12=me --guest A14=et \
  --spot_guest 0=4site --water_model 4site --type ice"
```

と書くことができる。

- 基底レベル(genice3)のオプションパーザーが知らない、shift や anion や guest は unitcell plugin の A15 にまず全部渡される。
- それでも parse されなかったものは exporter プラグインの gromacs に渡される。
- このように、オプション値のプールを genice3→ プラグインの順に渡していき、プラグインで処理させる。
- `[plugin --option]`でプラグインを指定する書き方も可能にしておく。
- 最後まで処理されなかったオプションは最後にエラーを返す。

## オプションの値の種類

オプションの値には以下のバリエーションが考えられる（コマンドライン引数として与えられる形式）。

1. 値なし(フラグ)

   - 例: `--debug`, `--assess_cages`
   - フラグとして機能し、指定されたかどうかの真偽値として扱われる

2. 文字列(プラグイン名、数値文字列、ブール値文字列など)

   - 例: `--exporter gromacs`, `--seed 42`, `--density 0.8`, `--water_model foursite`, `--type ice`
   - 単一の文字列値として扱われる

3. `[`からはじまる文字列。プラグインのオプションを含む生の文字列。

   - 例: `[A15 --shift 0.1 0.1 0.1]`, `[gromacs --guest A12=me]`
   - プラグイン名とそのオプションをまとめて指定する形式

4. リストまたはタプル(ベクトルなど) 中身は文字列。個数はあらかじめ指定されている。

   - 例: `--rep 2 2 2`, `--shift 0.1 0.1 0.1`
   - 複数の値をスペース区切りで指定し、タプルとして扱われる（値が 1 つの場合はそのまま文字列）

5. "a=b"タイプの文字列。"a"だけの場合もある。parser レベルではただの文字列として扱い、解釈はしない。複数指定される可能性があるので、リストを返す。
   - 例: `--anion 15=Cl`, `--guest A12=me --guest A14=et`, `--spot_guest 0=foursite`
   - キーと値を`=`で区切った文字列。同じオプションが複数回指定された場合はリストとして扱われる

注意: YAML ファイルから読み込まれた場合や、プラグインの処理結果として、辞書形式（ネストされた構造）が生成される場合もある（例：`water_model: {"name": "foursite", "options": {"type": "ice"}}`）。ただし、これはコマンドラインから直接与えられる形式ではない。
