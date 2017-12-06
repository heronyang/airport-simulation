.PHONY: clean
all: report.tex one-pager.tex
	pdflatex report.tex
	bibtex report.aux
	pdflatex report.tex
	pdflatex report.tex
	pdflatex one-pager.tex
	pdflatex one-pager.tex

clean:
	rm -rf *.pdf *.out *.aux *.log
