# The binary to build (just the basename).
MODULE := wiktionary2dict

init:
	pip install -r requirements.txt

test:
	py.test tests

run:
	@python -m $(MODULE)

PHONY: init test