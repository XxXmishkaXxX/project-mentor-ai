.PHONY: mypy lint fix style api upgrade downgrade revision test test-unit test-integration test-cov

package?=app tests

args = `arg="$(filter-out $@,$(MAKECMDGOALS))" && echo $${arg:-${1}}`


mypy:
	python -m mypy --enable-error-code ignore-without-code $(package)

lint:
	python -m ruff check $(package)

fix:
	python -m ruff check $(package) --fix

style:
	python -m ruff format $(package)

api:
	python -m app api

upgrade:
	python -m app migrate upgrade head

downgrade:
	python -m app migrate downgrade $(call args,-1)

revision:
	python -m app migrate revision --autogenerate -m $(call args,autogen)

test:
	python -m pytest tests/ -v

test-unit:
	python -m pytest tests/unit/ -v

test-integration:
	python -m pytest tests/integration/ -v

test-cov:
	python -m pytest tests/ -v --cov=app --cov-report=term-missing

