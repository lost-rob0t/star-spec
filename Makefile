.PHONY: all generate check test manifest

all: check test

generate:
	python3 tools/spec_pipeline.py build

check:
	python3 tools/spec_pipeline.py check

test:
	python3 -m unittest discover -s tests -v
	@if python3 -c 'import jsonschema' >/dev/null 2>&1; then python3 tools/validate_jsonschema.py; else echo 'jsonschema unavailable; CI runs the JSON Schema fixture gate'; fi

manifest:
	sbcl --script tools/compile_manifest.lisp spec/starintel-doc-v0.9.1.2.star
