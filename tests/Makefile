# rootで make testで呼びだされる。
all: test_unittest test_cli_ux test_doc_commands test_genice3

PYTEST = python -m pytest

test_unittest:
	$(PYTEST) unittest/ -v

test_cli_ux: test_cli_ux.py
	$(PYTEST) test_cli_ux.py -v

# AI 向け文書（docs/for-ai-assistants.md, temp_skill/SKILL.md）のコマンド例が実行できるか
test_doc_commands: test_doc_commands.py
	$(PYTEST) test_doc_commands.py -v

# genice3 テストスイート（test_validation, test_core, test_integration 等）
test_genice3:
	$(PYTEST) test_validation.py test_core.py test_integration.py test_optionparser_integration.py test_gromacs_parse_options.py -v
