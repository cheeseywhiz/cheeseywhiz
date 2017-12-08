PDF:=pdflatex
PDF_FLAGS:=-halt-on-error

BROWSER:=chromium

all: 10solutions.pdf

open:
	$(BROWSER) 10solutions.pdf

clean:
	rm -f *.pdf *.aux *.log

%.pdf: %.tex
	$(PDF) $(PDF_FLAGS) $<

.PHONY: all
