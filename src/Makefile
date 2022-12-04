pysrc     := __init__.py _version.py draw_pitch.py util.py
distfiles := $(pysrc) icon_auto.png icon_manual.png ../LICENSE manifest.json \
             NOTE user_pitchdb.csv wadoku_pitchdb.csv
version   := `grep -Po "(?<=__version__ = ')\d+\.\d+\.\d+(?=')" _version.py`
distdir   := ./dist/$(version)/
basefn    := japanese_pitch_accent
tmpdir    := ./dist/$(version)/$(basefn)
ts        := $(shell /bin/date "+%s")
testdir   := ./test_$(ts)
testreqs  := aqt[qt6]

dist : $(distfiles)
	@mkdir -p $(tmpdir)
	@cp $(distfiles) $(tmpdir)
	@cd $(tmpdir) && zip -r ../$(basefn).ankiaddon *
	@rm -rf $(tmpdir)

.PHONY : test
test :
	# TODO: test for existing venv and test recency
	@mkdir -p $(testdir)
	@python3.9 -m venv $(testdir)/anki_venv_latest
	@. $(testdir)/anki_venv_latest/bin/activate;\
	pip install --upgrade pip;\
	pip install $(testreqs);\
	anki
	# TODO: setup custom addon path if possible and
	#       install addon from dist
