# Skript (docu.pdf), Folien (slides.pdf) und Handouts (handouts.pdf) bauen.
# Benoetigt TeX Live mit latexmk, lualatex und biber.
# Die RWU-Schrift Barlow Semi Condensed liegt in fonts/ und braucht lualatex;
# "make PDFTEX=1" baut mit pdflatex und Latin Modern.

ifdef PDFTEX
LATEXMK = latexmk -pdf -interaction=nonstopmode -halt-on-error
else
LATEXMK = latexmk -lualatex -interaction=nonstopmode -halt-on-error
endif

.PHONY: all script slides handouts einzeln english publish clean

all: script slides handouts

script:
	$(LATEXMK) docu.tex

slides:
	$(LATEXMK) slides.tex

handouts:
	$(LATEXMK) handouts.tex

# Getrennte PDFs aus handouts.tex: Uebungsblatt Teil A zum Austeilen zu
# Stundenbeginn, Teil B nach dem Staunmoment, Zusammenfassung (Handout) fuer
# danach. Je Lehreinheit eine Datei plus je eine Sammeldatei mit allen 13. Parallel bauen mit "make -j8 einzeln".
LES     = 01 02 03 04 05 06 07 08 09 10 11 12 13
UEB     = $(patsubst %,pdf/Uebungsblaetter/LE%_Uebungsblatt_A.pdf,$(LES)) \
          $(patsubst %,pdf/Uebungsblaetter/LE%_Uebungsblatt_B.pdf,$(LES))
ZUS     = $(patsubst %,pdf/Zusammenfassungen/LE%_Zusammenfassung.pdf,$(LES))
SAMMEL  = pdf/WuZ_WissArbeiten_Uebungsblaetter_A.pdf pdf/WuZ_WissArbeiten_Uebungsblaetter_B.pdf \
          pdf/WuZ_WissArbeiten_Zusammenfassungen.pdf
HDEPS   = handouts.tex preamble.tex wuzmacros.tex refs.bib refs_extra.bib
# $(call teil,jobname,LE-Nummer oder leer,uebunga|uebungb|handout,Ziel)
teil = $(LATEXMK) -outdir=build -jobname=$(1) \
	-usepretex='\def\wuzle{$(2)}\def\wuzteil{$(3)}$(5)' handouts.tex && \
	mkdir -p $(dir $(4)) && cp build/$(1).pdf $(4)

einzeln: $(UEB) $(ZUS) $(SAMMEL)

pdf/Uebungsblaetter/LE%_Uebungsblatt_A.pdf: handouts/LE%.tex $(HDEPS)
	$(call teil,LE$*_Uebungsblatt_A,$(patsubst 0%,%,$*),uebunga,$@)

pdf/Uebungsblaetter/LE%_Uebungsblatt_B.pdf: handouts/LE%.tex $(HDEPS)
	$(call teil,LE$*_Uebungsblatt_B,$(patsubst 0%,%,$*),uebungb,$@)

pdf/Zusammenfassungen/LE%_Zusammenfassung.pdf: handouts/LE%.tex $(HDEPS)
	$(call teil,LE$*_Zusammenfassung,$(patsubst 0%,%,$*),handout,$@)

pdf/WuZ_WissArbeiten_Uebungsblaetter_A.pdf: handouts/*.tex $(HDEPS)
	$(call teil,Uebungsblaetter_A,,uebunga,$@)

pdf/WuZ_WissArbeiten_Uebungsblaetter_B.pdf: handouts/*.tex $(HDEPS)
	$(call teil,Uebungsblaetter_B,,uebungb,$@)

pdf/WuZ_WissArbeiten_Zusammenfassungen.pdf: handouts/*.tex $(HDEPS)
	$(call teil,Zusammenfassungen,,handout,$@)

# Englische Uebungsblaetter (Worksheets) aus handouts/en/, bisher LE 1-4
LES_EN  = 01 02 03 04
UEB_EN  = $(patsubst %,pdf/Worksheets_EN/LE%_Worksheet_A.pdf,$(LES_EN)) \
          $(patsubst %,pdf/Worksheets_EN/LE%_Worksheet_B.pdf,$(LES_EN))

english: $(UEB_EN)

pdf/Worksheets_EN/LE%_Worksheet_A.pdf: handouts/en/LE%.tex $(HDEPS)
	$(call teil,LE$*_Worksheet_A,$(patsubst 0%,%,$*),uebunga,$@,\def\wuzsprache{en})

pdf/Worksheets_EN/LE%_Worksheet_B.pdf: handouts/en/LE%.tex $(HDEPS)
	$(call teil,LE$*_Worksheet_B,$(patsubst 0%,%,$*),uebungb,$@,\def\wuzsprache{en})

# Kopiert die PDFs nach pdf/ (versionierte Fassungen, verlinkt in README.md)
publish: all einzeln english
	cp docu.pdf pdf/WuZ_WissArbeiten_Skript.pdf
	cp slides.pdf pdf/WuZ_WissArbeiten_Folien.pdf
	cp handouts.pdf pdf/WuZ_WissArbeiten_Handouts.pdf

clean:
	latexmk -c docu.tex slides.tex handouts.tex
	rm -rf build
