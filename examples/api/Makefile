# examples/api から実行する想定:
#   cd examples/api && make
# プロジェクトルートから実行する場合:
#   make -C examples/api
#
# 実行時のカレントディレクトリは examples/api になるので、
# .sh / .yaml 内の相対パス（例: --file ../cif/MEP.cif）は examples/api 基準。
# genice3 は PYTHONPATH=$(ROOT) で解決する（パッケージ未インストールでも可）。

ROOT := ..
export PYTHONPATH := $(ROOT)

API_BASES := 2_simple 3_doped 4_from_cif 5_to_cif 6_with_guests 7_polarized 8_cage_survey 9_ion_group 10_extend_unitcell 11_ion_group_unitcell
API_OUTS := $(foreach b,$(API_BASES),$(b).sh.out $(b).py.out $(b).yaml.out)

all: api_outs 3_doped.compare 4_from_cif.compare 5_to_cif.compare 6_with_guests.compare 7_polarized.compare 8_cage_survey.compare 9_ion_group.compare 10_extend_unitcell.compare 11_ion_group_unitcell.compare
api_outs: $(API_OUTS)
	@:

compare: 3_doped.compare 4_from_cif.compare 5_to_cif.compare 6_with_guests.compare 7_polarized.compare 8_cage_survey.compare 9_ion_group.compare 10_extend_unitcell.compare 11_ion_group_unitcell.compare

%.compare: %.py.out %.yaml.out %.sh.out
	-diff $*.py.out $*.yaml.out
	-diff $*.py.out $*.sh.out
	-diff $*.py.log $*.yaml.log
	-diff $*.py.log $*.sh.log

.PHONY: all api_outs yaml clean

%.sh.out: %.sh Makefile
	sh $< > $@ 2> $<.log
%.py.out: %.py Makefile
	python3 $< > $@ 2> $<.log
%.yaml.out: %.yaml Makefile
	python3 -m genice3.cli.genice --config $< > $@ 2> $<.log

clean:
	rm -f *.out *.log
