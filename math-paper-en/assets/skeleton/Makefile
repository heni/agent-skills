# Build and check. Building requires latexmk; `make check` is pure Python
# stdlib and needs no build. `make pages LIMIT=n` builds main.pdf and
# additionally needs poppler-utils (pdftotext, pdfinfo).
SKILL := ../..
# Hard page limit of the venue, bibliography included; empty means no limit.
LIMIT :=

.PHONY: all check check-all audit bib stats pages clean draft

all: main.pdf

main.pdf: main.tex macros.tex refs.bib $(wildcard sections/*.tex)
	latexmk -pdf -interaction=nonstopmode main.tex

# One section at a time while drafting: make draft SECTION=04-proofs
draft:
	latexmk -pdf -interaction=nonstopmode -usepretex='\includeonly{sections/$(SECTION)}' main.tex

check: audit bib stats

check-all: check pages

audit:
	python3 $(SKILL)/scripts/audit.py main.tex --bib refs.bib

bib:
	python3 $(SKILL)/scripts/bibcheck.py refs.bib

stats:
	python3 $(SKILL)/scripts/statcheck.py main.tex

# Measures the limit at the seam: the last allowed page must END with the
# bibliography. pagegate exits 1 over the limit and 2 when it could not check;
# make reports either as a failed target, which is the point. Kept out of
# `check` so that the lint pass stays independent of the build.
pages:
ifeq ($(strip $(LIMIT)),)
	@echo "pages: set LIMIT to the venue's page limit, e.g. make pages LIMIT=6"
else
	$(MAKE) main.pdf
	python3 $(SKILL)/scripts/pagegate.py main.pdf --limit $(LIMIT)
endif

clean:
	latexmk -C
	rm -f *.bbl *.blg
