.PHONY: usage install uninstall
usage:
	@echo "Usage: make <target>, where target is one of:\n"
	@echo "python-readme: generate library/README.rst from README.md"
	@echo "python-wheels: build python .whl files for distribution"
	@echo "python-sdist:  build python source distribution"
	@echo "python-clean:  clean python build and dist directories"
	@echo "python-dist:   build all python distribution files" 
	@echo "python-test:   run tests and QA with tox"

python-readme: library/README.rst

python-license: library/LICENSE.txt

library/README.rst: README.md
	pandoc --from=markdown --to=rst -o library/README.rst README.md

library/LICENSE.txt: LICENSE
	cp LICENSE library/LICENSE.txt

python-wheels: python-readme python-license
	cd library; python3 setup.py bdist_wheel
	cd library; python setup.py bdist_wheel

python-sdist: python-readme python-license
	cd library; python setup.py sdist

python-clean:
	-rm -r library/dist
	-rm -r library/build
	-rm -r library/*.egg-info

python-dist: python-clean python-wheels python-sdist
	ls library/dist

python-deploy: python-dist
	twine upload library/dist/*

python-test:
	cd library; tox
