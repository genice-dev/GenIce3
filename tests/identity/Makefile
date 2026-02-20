NTHREADS=1
LIMIT=1000

# 想定フロー
# make discover LIMIT=1000           # discoveries.json を生成（時間かかる）
# make update-reference.discover     # reference/ を並列生成
# make test.discover                 # 回帰テスト


# 回帰テスト: 現在の出力を reference/ と比較
test: Makefile.rules
	$(MAKE) -f Makefile.rules -k test

# 参照出力を更新（意図した変更時のみ。更新後は git add reference/ してコミット）
update-reference: Makefile.rules
	$(MAKE) -f Makefile.rules update-reference

# 発見ベース: オプション組み合わせの選別 → discoveries.json（reference は作らない）
# make discover           # 全組み合わせ
# make discover LIMIT=100  # 成功100件まで
discover: option_sets.py
	python3 discover.py -o discoveries.json $(if $(LIMIT),--limit $(LIMIT))

# 発見ベース: discoveries.json から Makefile.rules.discover を生成
Makefile.rules.discover: discoveries.json
	python3 generate_rules.py discoveries.json -o Makefile.rules.discover

# 発見ベース: reference を生成（make -j で並列）
update-reference.discover: Makefile.rules.discover
	$(MAKE) -f Makefile.rules.discover -j$(NTHREADS) update-reference

# 発見ベース: 回帰テスト（reference が先に存在すること）
test.discover: Makefile.rules.discover
	$(MAKE) -f Makefile.rules.discover -k test

# 従来方式: mkmk.py から Makefile.rules を生成（固定オプション）
Makefile.rules: mkmk.py ../../genice3/plugin.py
	python3 mkmk.py > $@

clean:
	-rm -f *.diff
	-rm -f *.log

distclean: clean
	-rm reference/
	-rm Makefile.rules
