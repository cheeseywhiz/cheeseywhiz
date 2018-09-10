TEX:=pdflatex
TEX_FLAGS:=-halt-on-error
BROWSER:=chromium

FILES:=sea_monkey_report.pdf

all: files trim

files: $(FILES)

open:
	$(BROWSER) $(FILES)

trim:
	rm -f *.aux *.log *.nav *.out *.snm *.toc *.vrb

clean: trim
	rm -f *.pdf


.PHONY: all files open clean trim

%.pdf: %.tex sea_monkey_report.sty
	$(TEX) $(TEX_FLAGS) $<
