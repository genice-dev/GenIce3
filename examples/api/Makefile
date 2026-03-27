# examples/api から実行する想定:
#   cd examples/api && make
# プロジェクトルートから実行する場合:
#   make -C examples/api
#
# 実行時のカレントディレクトリは examples/api になるので、
# .sh / .yaml 内の相対パス（例: --file ../cif/MEP.cif）は examples/api 基準。
# genice3 は Poetry venv の Python で解決する（パッケージ未インストールでも可）。

ROOT     := ../..
# Resolve venv python at parse time (override: make PYTHON=/path/to/python)
PYTHON   ?= $(shell cd $(ROOT) && poetry env info --executable)
VENV_BIN := $(dir $(PYTHON))

# ---- .sh / .py / .yaml の三点セットがあるもの ----
TRIO_BASES := \
	basic/2_simple \
	cif_io/4_from_cif \
	cif_io/5_to_cif \
	doping/3_doped \
	doping/9_ion_group \
	doping/11_ion_group_unitcell \
	guest_occupancy/6_with_guests \
	guest_occupancy/8_cage_survey \
	polarization/7_polarized \
	unitcell_transform/10_extend_unitcell

# ---- .py のみのもの ----
PY_ONLY_BASES := \
	basic/1_reactive_properties \
	topological_defects/12_topological_defect \
	topological_defects/13_topological_defect2 \
	unitcell_transform/14_use_reshaped_unitcell

TRIO_OUTS  := $(foreach b,$(TRIO_BASES),$(b).sh.out $(b).py.out $(b).yaml.out)
PYONLY_OUTS := $(foreach b,$(PY_ONLY_BASES),$(b).py.out)
ALL_OUTS   := $(TRIO_OUTS) $(PYONLY_OUTS)

COMPARE_TARGETS := $(patsubst %,%.compare,$(TRIO_BASES))

all: api_outs $(COMPARE_TARGETS)
api_outs: $(ALL_OUTS)
	@:

compare: $(COMPARE_TARGETS)

%.compare: %.py.out %.yaml.out %.sh.out
	-diff $*.py.out $*.yaml.out
	-diff $*.py.out $*.sh.out
	-diff $*.py.log $*.yaml.log
	-diff $*.py.log $*.sh.log

.PHONY: all api_outs compare clean

# Prepend venv bin to PATH so that 'python3' inside .sh resolves to the venv python.
%.sh.out: %.sh Makefile
	PATH="$(VENV_BIN):$$PATH" sh $< > $@ 2> $<.log
%.py.out: %.py Makefile
	$(PYTHON) $< > $@ 2> $<.log
%.yaml.out: %.yaml Makefile
	$(PYTHON) -m genice3.cli.genice --config $< > $@ 2> $<.log

clean:
	rm -f $(foreach d,basic cif_io doping guest_occupancy polarization topological_defects unitcell_transform,$(d)/*.out $(d)/*.log)
