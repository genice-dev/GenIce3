# Benchmark（ベンチマーク）

tests/ から移動したベンチマーク用スクリプトです。テストスイートではなく、実行時間の計測・比較用です。

## ファイル

- **benchmark.sh** … 繰り返し実行して `bench.out` を生成する。`genice.x`（旧 GenIce の C バイナリ）を `../../genice.x` から呼び出す。`genice.x` が無い場合は利用できません。
- **bench.gp** … gnuplot 用。`bench.out` を分子数 vs 時間でプロットする。

## 使い方

```bash
cd examples/benchmark
./benchmark.sh    # genice.x がプロジェクト直下にある場合
gnuplot bench.gp # または gnuplot -p bench.gp
```

生成される `bench.out` と一時ファイル `@*` は `.gitignore` で除外されています。
