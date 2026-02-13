# run them from the root dir with: poetry run make -f examples/api/Makefile

# .out を「明示的ターゲットの前提」にしておくと中間扱いされず消されない（GNU/BSD 両方で有効）
API_BASES := 3_doped 4_from_cif 5_to_cif 6_with_guests 7_polarized
API_OUTS := $(foreach b,$(API_BASES),examples/api/$(b)_flat.sh.out examples/api/$(b).py.out examples/api/$(b).yaml.out examples/api/$(b).sh.out)

all: api_outs examples/api/3_doped.compare examples/api/4_from_cif.compare examples/api/5_to_cif.compare examples/api/6_with_guests.compare examples/api/7_polarized.compare
api_outs: $(API_OUTS)
	@:

%.compare: %_flat.sh.out %.py.out %.yaml.out %.sh.out
	-diff $*.py.out $*.yaml.out
	-diff $*.py.out $*flat.sh.out
	-diff $*.py.out $*.sh.out
	-diff $*.py.log $*flat.sh.log
	-diff $*.py.log $*.yaml.log
	-diff $*.py.log $*.sh.log


%.sh.out: %.sh Makefile
	sh $< > $@ 2> $<.log
%.py.out: %.py Makefile
	python3 $< > $@ 2> $<.log
%.yaml.out: %.yaml Makefile
	python3 -m genice3.cli.genice --config $< > $@ 2> $<.log

clean:
	cd examples/api && \rm *.out *.log
