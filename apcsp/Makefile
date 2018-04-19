PDF:=pdflatex
PDF_FLAGS:=-halt-on-error

BROWSER:=chromium

FILES:=graph2.pdf graph3.pdf

all: $(FILES)

open:
	$(BROWSER) $(FILES)

trim:
	rm -f *.aux *.log *.nav *.out *.snm *.toc *.vrb

clean: trim
	rm -f *.pdf

%.pdf: %.tex
	$(PDF) $(PDF_FLAGS) $<
	$(PDF) $(PDF_FLAGS) $<

.PHONY: all open trim clean
