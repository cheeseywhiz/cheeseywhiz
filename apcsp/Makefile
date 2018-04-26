TEX:=pdflatex
TEX_FLAGS:=-halt-on-error

BROWSER:=chromium

FILES:=graph2.pdf graph3.pdf

all: $(FILES)

open:
	$(BROWSER) $(FILES)

clean:
	rm -f *.aux *.log *.nav *.out *.snm *.toc *.vrb


%.pdf: %.tex graph.sty graph.py
	$(TEX) $(TEX_FLAGS) $<

.PHONY: all open clean
