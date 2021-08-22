src = coupled.py lowpass.py __main__.py ness.py zverev.py

all: rftune README.md

rftune: ${src}
	zip rftune.zip ${src}
	echo '#!/usr/bin/python3' | cat - rftune.zip > rftune
	rm rftune.zip
	chmod 755 rftune

README.md: readme.py
	python3 readme.py > README.md

clean:
	rm -rf .ipynb_checkpoints *.dat *.lst rftune.* rftune README.md

############################################

repo = $(shell basename `pwd`)

zip: clean
	cd ..; zip -r -FS ~/apps/${repo} ${repo}

run: rftune
	./rftune -n 2 --cheb 0.01 -f 7.1e6 -b 200e3 --qu 800 --validate 

