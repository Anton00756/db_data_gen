# ------ code style ------

check_pylint:
	pylint src/ --fail-under=9.0

check_format:
	ruff format --check src/

check_all: check_pylint check_format