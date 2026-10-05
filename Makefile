# Skript (docu.pdf), Folien (slides.pdf) und Handouts (handouts.pdf) bauen.
# Benoetigt TeX Live mit latexmk, lualatex und biber.
# Die RWU-Schrift Barlow Semi Condensed liegt in fonts/ und braucht lualatex;
# "make PDFTEX=1" baut mit pdflatex und Latin Modern.

ifdef PDFTEX
LATEXMK = latexmk -pdf -interaction=nonstopmode -halt-on-error
else
LATEXMK = latexmk -lualatex -interaction=nonstopmode -halt-on-error
endif

.PHONY: all script slides handouts publish clean

all: script slides handouts

script:
	$(LATEXMK) docu.tex

slides:
	$(LATEXMK) slides.tex

handouts:
	$(LATEXMK) handouts.tex

# Kopiert die PDFs nach pdf/ (versionierte Fassungen, verlinkt in README.md)
publish: all
	cp docu.pdf pdf/WuZ_WissArbeiten_Skript.pdf
	cp slides.pdf pdf/WuZ_WissArbeiten_Folien.pdf
	cp handouts.pdf pdf/WuZ_WissArbeiten_Handouts.pdf

clean:
	latexmk -c docu.tex slides.tex handouts.tex
