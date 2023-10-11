APP_DIR=ecoscope

lint-pylint:
	#  pylint
	@ poetry run pylint --rcfile=setup.cfg --output-format=colorized --jobs=4 --recursive=y . $$PYLINT_ARGS;

lint-ruff:
	#  ruff
	@ poetry run ruff check .

lint-mypy:
	#  mypy
	@ poetry run mypy --show-column-numbers --show-absolute-path .;

LINTS := $(patsubst %,lint-%, ruff mypy pylint)
lint: $(LINTS)

git-new-and-modified:
	@ git diff ${BASE_BRANCH} --diff-filter=ACMR --name-only | (grep -E '.py$$' || true) | tr '\n' ' '

tidy:
	@ ( \
		export MODIFIED_FILES="$$(BASE_BRANCH=origin/main $(MAKE) -s git-new-and-modified)" && \
		if [ -z "$${MODIFIED_FILES}" ]; then echo "No files changed, not tidying"; exit; fi && \
		echo -e "Tidying python files:\n\n$${MODIFIED_FILES}\n" && \
		$(MAKE) tidy-all \
	)

tidy-pyupgrade:
	echo $${MODIFIED_FILES:-$$(find . -name "*.py")} | xargs poetry run pyupgrade --py310-plus --exit-zero-even-if-changed

tidy-sh:
	poetry run beautysh --indent-size=2 --force-function-style=fnpar $$(find . -name '*.sh')

tidy-json:
	find . -type d \( -path ./.git -o -path ./.vscode -o -path ./node_modules -o -path ./.mypy_cache -o -path ./.pytest_cache \) -prune -false -o -name '*.json' | xargs -I {} poetry run python -m json.tool --indent 4 {} {}

tidy-all: tidy-pyupgrade  ## Tidy all files tidy-sh tidy-json
	poetry run autoflake --expand-star-imports --remove-unused-variables --remove-all-unused-imports -r --in-place $${MODIFIED_FILES:-.}
	poetry run isort --quiet $${MODIFIED_FILES:-. -rc}
	poetry run docformatter --wrap-summaries 119 --wrap-descriptions 119 --in-place $${MODIFIED_FILES:-. -r}
	poetry run black --quiet --target-version py310 --line-length 120 $${MODIFIED_FILES:-.}


install:
	poetry install

tests:
	# running unit tests...
	ENV="development" TEST_MODE=1 poetry run pytest -v test/
