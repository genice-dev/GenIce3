PIPNAME=genice3
GITNAME=GenIce

all: README.md
	echo Hello.

# docs/references.md is generated from citations.json by "make docs" (replacer --docs)
README.md: temp_README.md Utilities/replacer.py genice3/__init__.py genice3/plugin.py citations.json pyproject.toml
	python3 -m Utilities.replacer < temp_README.md > README.md

# Generate docs/*.md from temp_docs/*.md (same Jinja2 context as README).
# Depends on unitcell/molecule plugins so that ref/desc changes are reflected.
docs: temp_docs/cli.md temp_docs/getting-started.md temp_docs/output-formats.md temp_docs/ice-structures.md temp_docs/water-models.md temp_docs/guest-molecules.md temp_docs/plugins.md EXTRA.yaml Utilities/replacer.py genice3/__init__.py genice3/plugin.py citations.json pyproject.toml $(wildcard genice3/unitcell/*.py) $(wildcard genice3/molecule/*.py)
	python3 -m Utilities.replacer --docs

%: temp_% Utilities/replacer.py genice3/__init__.py genice3/plugin.py citations.json pyproject.toml
	python3 -m Utilities.replacer < $< > $@


update-citations:
	cp citations.json old.citations.json
	python3 Utilities/citation.py < old.citations.json > citations.json
	-diff old.citations.json citations.json

unitcell-test: $(patsubst genice3/unitcell/%.py, %.unitcell-test, $(wildcard genice3/unitcell/[0-9A-Za-z]*.py))

%.unitcell-test:
	python3 -m genice3.unitcell._test.lattice_vs_unitcell $*
	touch $@


# prepare step is not needed for genice3 (no symlink conversion)
prepare:
	@echo "No preparation needed for genice3"


test:
	make -C tests all

test-deploy: clean prepare build
	python3 -m twine upload --repository testpypi dist/*
test-install:
	pip3 install --index-url https://test.pypi.org/simple/ $(PIPNAME)
uninstall:
	-pip3 uninstall -y $(PIPNAME)
build: README.md $(wildcard genice3/*.py)
	python3 -m build --wheel
deploy: clean prepare build
	python3 -m twine upload dist/*
check:
	python3 -m build --check


clone-myself-from-github:
	git clone -b genice-core https://github.com/vitroid/GenIce.git ../GenIce3.clone


%.png: %.pov
	povray +I$< +W1000 +H1000 +D +FN +O$@
clean:
	-rm -rf build dist
distclean:
	-rm *.scad *.yap *.unitcell-test *.gro *.cif @*
	-rm -rf build dist
	-rm -rf *.egg-info
	-rm .DS_Store
	find . -name __pycache__ | xargs rm -rf
	find . -name \*.pyc      | xargs rm -rf
	find . -name \*~         | xargs rm -rf
