

SRC:=src
OBJ:=src

UI:=$(shell find $(SRC)/ui/ -name *.ui)


PY_UI:=$(UI:$(SRC)/ui/%.ui=$(OBJ)/ui_py/%_ui.py)

PYUIC:=pyuic6

all: $(PY_UI)

run: all
	python3 src/employee_app.py

$(OBJ)/ui_py/%_ui.py: $(SRC)/ui/%.ui Makefile
	@mkdir -p $(@D)
	$(PYUIC) $< -o $@



