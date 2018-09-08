PDF:=pdflatex
PDF_FLAGS:=-halt-on-error

BROWSER:=chromium

all: app_nerf_report.pdf

open:
	$(BROWSER) app_nerf_report.pdf

clean:
	rm -f *.pdf *.aux *.log

%.pdf: %.tex
	$(PDF) $(PDF_FLAGS) $<

.PHONY: all
