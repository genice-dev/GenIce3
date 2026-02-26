PIPNAME=genice3
GITNAME=GenIce
# Use Poetry venv Python so it works on any machine (override with make PYTHON=...)
PYTHON ?= poetry run python

all: README.md
	echo Hello.

# docs/references.md is generated from citations.yaml by "make docs" (replacer --docs)
README.md: temp_README.md Utilities/replacer.py genice3/__init__.py genice3/plugin.py citations.yaml pyproject.toml
	$(PYTHON) -m Utilities.replacer < temp_README.md > README.md

# Generate docs/*.md from temp_docs/*.md (same Jinja2 context as README).
# Then embed examples/api (py/sh/yaml) into docs/api-examples/*.md.
# Depends on unitcell/molecule plugins so that ref/desc changes are reflected.
docs: temp_docs/cli.md temp_docs/getting-started.md temp_docs/output-formats.md temp_docs/unitcells.md temp_docs/water-models.md temp_docs/guest-molecules.md temp_docs/plugins.md EXTRA.yaml Utilities/replacer.py genice3/__init__.py genice3/plugin.py citations.yaml pyproject.toml $(wildcard genice3/unitcell/*.py) $(wildcard genice3/molecule/*.py)
	$(PYTHON) -m Utilities.replacer --docs
	$(PYTHON) scripts/build_api_docs.py

%: temp_% Utilities/replacer.py genice3/__init__.py genice3/plugin.py citations.yaml pyproject.toml
	$(PYTHON) -m Utilities.replacer < $< > $@


# Regenerate API.ipynb from examples/api (READMEs + .py interleaved)
api-notebook: scripts/build_api_notebook.py $(wildcard examples/api/*/*.py) $(wildcard examples/api/*/README.md)
	$(PYTHON) scripts/build_api_notebook.py

# Run all examples/api/*/*.py from project root (some may fail occasionally due to randomness)
run-api-examples: scripts/run_api_examples.py
	$(PYTHON) scripts/run_api_examples.py --all

update-citations:
	cp citations.yaml old.citations.yaml
	$(PYTHON) Utilities/citation.py < old.citations.yaml > citations.yaml
	-diff old.citations.yaml citations.yaml

unitcell-test: $(patsubst genice3/unitcell/%.py, %.unitcell-test, $(wildcard genice3/unitcell/[0-9A-Za-z]*.py))

%.unitcell-test:
	$(PYTHON) -m genice3.unitcell._test.lattice_vs_unitcell $*
	touch $@


# prepare step is not needed for genice3 (no symlink conversion)
prepare:
	@echo "No preparation needed for genice3"

# docs/ や mkdocs.yml の変更で自動リビルド・ブラウザリロード（watchdog 入りで監視が安定）
serve:
	mkdocs serve

# mkdocs serve 起動中に、キー一発でブラウザをリロードしたいとき用。
# docs/ 内を touch すると livereload が検知してブラウザが更新される。
# 自動監視が効かない環境（Dropbox等）では、編集後に make docs && make reload または
# Cursor のキーバインドで「make reload」を実行するとよい。
reload:
	@touch docs/index.md && echo "Touched docs/index.md — livereload should refresh the browser."

test:
	make -C tests all

# Test PyPI へアップロード（事前に poetry config repositories.testpypi https://test.pypi.org/legacy/ を実行）
test-deploy: clean prepare build
	poetry publish -r testpypi
test-install:
	pip3 install --index-url https://test.pypi.org/simple/ $(PIPNAME)
uninstall:
	-pip3 uninstall -y $(PIPNAME)
build: README.md $(wildcard genice3/*.py)
	poetry build
deploy: clean prepare build
	poetry publish
check:
	poetry build


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
