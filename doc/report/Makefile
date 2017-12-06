.PHONY: clean
all: report.tex
	pdflatex report.tex
	bibtex report.aux
	pdflatex report.tex
	pdflatex report.tex

clean:
	rm -rf *.pdf *.out *.aux *.log
