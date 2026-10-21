NTHREADS=8
LIMIT=1000
CORPUS=corpus.json
OLD=
# 並列 NTHREADS 本を想定し、1 プロセスあたり 1 GiB
MEM_MB=1024
TIMEOUT=60

# 想定フロー
# make discover LIMIT=1000           # corpus.json を生成／拡張（時間かかる）
# make update-reference              # reference/ を並列生成（ローカルのみ）
# make test                          # 回帰テスト（各プロセス ≤ MEM_MB MiB）
# make compare OLD=/path/to/old/repo # 版間比較


# 回帰テスト: 現在の出力を reference/ と比較
test: Makefile.rules
	$(MAKE) -f Makefile.rules -k -j$(NTHREADS) test

# 参照出力を更新（意図した変更時のみ。reference/ は git 管理外）
# 失敗した実行は空ファイルを残さない（generate_rules の原子的書き込み）。
update-reference: Makefile.rules
	$(MAKE) -f Makefile.rules -j$(NTHREADS) update-reference

# 失敗で残った空の reference を削除（次回 update-reference で再生成される）
prune-empty-reference:
	@find reference -type f ! -name '*.log' -size 0 -print -delete 2>/dev/null | \
		(grep . >/dev/null && echo "removed empty reference files above" || echo "no empty reference files")

# ice-rule AssertionError（イオン近接など）で落ちたケースを corpus から除外し rules を再生成
# make prune-failed              # assertion のみ
# make prune-failed REASON=all   # reference 欠落＋ログありを全部
REASON=assertion
prune-failed: $(CORPUS)
	python3 prune_failed.py --corpus $(CORPUS) --reason $(REASON)
	$(MAKE) Makefile.rules

# 層化 discover → corpus.json（タイムアウト／OOM は成功に含めない）
# make discover           # 全組み合わせ（非常に重い）
# make discover LIMIT=100  # 成功 100 件まで
# make discover LIMIT=100 MERGE=1  # 既存にマージ
discover: option_sets.py
	python3 discover.py -o $(CORPUS) \
		--mem-mb $(MEM_MB) --timeout $(TIMEOUT) \
		$(if $(LIMIT),--limit $(LIMIT)) \
		$(if $(MERGE),--merge)

# corpus.json から Makefile.rules を生成（run_limited 経由）
Makefile.rules: $(CORPUS) generate_rules.py corpus_util.py run_limited.py
	python3 generate_rules.py $(CORPUS) -o Makefile.rules \
		--mem-mb $(MEM_MB) --timeout $(TIMEOUT)

# 個別ターゲットは Makefile.rules に委譲
# （この Makefile には test / update-reference しか無く、
#  make reference/FOO すると No rule で即終了してしまう）
reference/%: Makefile.rules
	$(MAKE) -f Makefile.rules $@

%.diff: Makefile.rules
	$(MAKE) -f Makefile.rules $@

# 旧 discoveries.json → corpus.json（初回・移行用）
migrate:
	python3 migrate_corpus.py --rename-reference

# 版間比較: 同じコーパスを OLD と現行で実行して diff
# make compare OLD=/path/to/old/GenIce3
# make compare OLD=/path/to/old/GenIce3 LIMIT=50
compare: $(CORPUS)
	@test -n "$(OLD)" || (echo "Usage: make compare OLD=/path/to/old/GenIce3"; exit 1)
	python3 compare_versions.py --corpus $(CORPUS) \
		--old-cwd $(OLD) \
		--mem-mb $(MEM_MB) --timeout $(TIMEOUT) \
		$(if $(LIMIT),--limit $(LIMIT))

clean:
	-rm -f *.diff
	-rm -f *.log

distclean: clean
	-rm -rf reference/
	-rm -f Makefile.rules
