# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of PSyACC and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.

# You can set these variables from the command line, and also from the environment for
# the first two.
SPHINXOPTS	?=
SPHINXAPIDOC	= sphinx-apidoc
SPHINXBUILD	= sphinx-build
SOURCEDIR	= source
BUILDDIR	= build
PSYACC		= ../psyacc

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: apidoc help Makefile

copy_demos:
	install -d $(SOURCEDIR)/demos
	cp -r ../demos/*.py $(SOURCEDIR)/demos
	for f in $(SOURCEDIR)/demos/*.py; do pylit -c $$f; mv $$f.txt $$f.rst; done
	install -d $(BUILDDIR)/html/demos
	cp source/demos/*.py $(BUILDDIR)/html/demos

# Catch-all target: route all unknown targets to Sphinx using the new "make mode"
# option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile copy_demos
	@$(SPHINXAPIDOC) -o "$(SOURCEDIR)" "$(PSYACC)"
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	rm -rf $(BUILDDIR)
	rm -rf $(SOURCEDIR)/demos
