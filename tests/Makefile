# rootで make testで呼びだされる。
all: test_unittest test_cli_ux test_genice3

PYTEST = python -m pytest

test_unittest:
	$(PYTEST) unittest/ -v

test_cli_ux: test_cli_ux.py
	$(PYTEST) test_cli_ux.py -v

# genice3 テストスイート（test_validation, test_core, test_integration 等）
test_genice3:
	$(PYTEST) test_validation.py test_core.py test_integration.py test_optionparser_integration.py test_gromacs_parse_options.py -v
