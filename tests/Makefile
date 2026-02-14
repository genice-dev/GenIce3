# rootで make testで呼びだされる。
all: test_unittest test_cli_ux




test_unittest:
	pytest unittest/ -v

test_cli_ux: test_cli_ux.py
	pytest test_cli_ux.py -v
