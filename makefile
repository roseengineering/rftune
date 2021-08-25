src = coupled.py lowpass.py __main__.py ness.py zverev.py

all: rftune README.md

rftune: ${src}
	python -m zipfile -c rftune.zip ${src}
	echo '#!/usr/bin/python3' | cat - rftune.zip > rftune
	rm rftune.zip
	chmod 755 rftune

README.md: readme.py
	make readme

readme:
	python3 readme.py > README.md
	
install:
	sudo cp rftune /usr/local/bin

clean:
	rm -rf */.ipynb_checkpoints/ .ipynb_checkpoints/ *.dat *.lst rftune.*

distclean:
	rm -f rftune README.md

############################################

repo = $(shell basename `pwd`)

zip: clean
	cd ..; zip -r -FS ~/apps/${repo} ${repo}

push: clean
	test "$(shell git push 2>&1)" = "Everything up-to-date" || git gc

run: rftune
	./rftune -n 2 --but -f 2.3e9 -b 26.9e6
	./rftune -n 2 --cheb 0.01 -f 7.1e6 -b 200e3 --qu 800 --validate 
	./rftune -f 7.36e6 --max-swr 1.039 --lowpass -n 7

