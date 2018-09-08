TEX:=pdflatex
TEX_FLAGS:=-halt-on-error

BROWSER:=chromium

FILES:=solutions.pdf

all: $(FILES)

open:
	$(BROWSER) $(FILES)

trim:
	rm -f *.aux *.log *.nav *.out *.snm *.toc *.vrb

clean: trim
	rm -f *.pdf


%.pdf: %.tex solutions.sty
	$(TEX) $(TEX_FLAGS) $<

.PHONY: all open clean trim
