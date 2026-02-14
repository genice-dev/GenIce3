NTHREADS=8
LIMIT=1000
REFERENCE=1

# 回帰テスト: 現在の出力を reference/ と比較
test: Makefile.rules
	$(MAKE) -f Makefile.rules -k test

# 参照出力を更新（意図した変更時のみ。更新後は git add reference/ してコミット）
update-reference: Makefile.rules
	$(MAKE) -f Makefile.rules update-reference

# 発見ベース: genice3 を実行して成功した組み合わせを discoveries.json に記録
# make discover              # 全組み合わせ
# make discover LIMIT=100     # 成功100件まで
# make discover REFERENCE=1   # 成功時に reference/ へ出力を保存
discover: option_sets.py
	python3 discover.py -o discoveries.json \
		$(if $(LIMIT),--limit $(LIMIT)) \
		$(if $(REFERENCE),--reference)

# 発見ベース: discoveries.json から Makefile.rules を生成
Makefile.rules.discover: discoveries.json
	python3 generate_rules.py discoveries.json -o Makefile.rules.discover

# 従来方式: mkmk.py から Makefile.rules を生成（固定オプション）
Makefile.rules: mkmk.py ../../genice3/plugin.py
	python3 mkmk.py > $@

clean:
	-rm -f *.diff
	-rm -f *.log

distclean: clean
	-rm reference/
	-rm Makefile.rules
