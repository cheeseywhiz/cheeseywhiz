TEX:=pdflatex
TEX_FLAGS:=-halt-on-error

BROWSER:=chromium

FILES:=expl.pdf

all: $(FILES)

open: $(FILES)
	$(BROWSER) $^

trim:
	rm -f *.aux *.log *.nav *.out *.snm *.toc *.vrb

clean: trim
	rm -rf expl.pdf


%.pdf: %.tex graph.sty
	$(TEX) $(TEX_FLAGS) $<

.PHONY: all open clean
