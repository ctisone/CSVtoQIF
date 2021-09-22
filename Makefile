#*********
# Tools
#*********
PYTHON := python3.9

#***************
# Directories
#***************
TEST_DIR := ${CURDIR}/Tests
SOURCE_DIR := ${CURDIR}/Source
BUILD_DIR := ${CURDIR}/dist
DEPLOY_DIR := /usr/local/bin

#*********
# Files
#*********
TEST_FILES := $(wildcard ${TEST_DIR}/*.py)
MAIN_TEST_FILE := ${TEST_DIR}/UnitTestMain.py

SOURCE_FILES := $(wildcard ${SOURCE_DIR}/*.py)
MAIN_SOURCE_FILE := ${SOURCE_DIR}/CSVtoQIF.py

TARGET_FILE_BASE_NAME := CSVtoQIF
OUTPUT_FILE := ${BUILD_DIR}/${TARGET_FILE_BASE_NAME}
DEPLOYED_FILE := ${DEPLOY_DIR}/${TARGET_FILE_BASE_NAME}

#***********
# Targets
#***********
.PHONY: all variables install uninstall installdirs clean check

all: ${OUTPUT_FILE}

variables:
	@echo
	@echo Makefile variables
	@echo
	@echo PYTHON: ${PYTHON}
	@echo TEST_DIR: ${TEST_DIR}
	@echo SOURCE_DIR: ${SOURCE_DIR}
	@echo BUILD_DIR: ${BUILD_DIR}
	@echo DEPLOY_DIR: ${DEPLOY_DIR}

	@echo TEST_FILES: ${TEST_FILES}
	@echo MAIN_TEST_FILE: ${MAIN_TEST_FILE}
	@echo SOURCE_FILES: ${SOURCE_FILES}

	@echo OUTPUT_FILE: ${OUTPUT_FILE}
	@echo DEPLOYED_FILE: ${DEPLOYED_FILE}

	@echo MAIN_SOURCE_FILE: ${MAIN_SOURCE_FILE}
	@echo

install: all | installdirs
	@echo
	@echo Copying final package to ${DEPLOY_DIR}...
	@echo
	@sudo cp ${OUTPUT_FILE} ${DEPLOY_DIR}
	@sudo chmod u=rwx,g=rx,o=rx ${DEPLOYED_FILE}

uninstall:
	@echo
	@echo Removing final package from ${DEPLOY_DIR}...
	@echo
	@sudo rm -f ${DEPLOYED_FILE}

installdirs:
	@echo
	@echo Creating ${DEPLOY_DIR}...
	@echo
	@sudo mkdir -p ${DEPLOY_DIR}

clean:
	@echo
	@echo Cleaning build related directories...
	@echo
	@rm -rf build/*
	@rm -rf dist/*
	@rm -f ${TARGET_FILE_BASE_NAME}.spec

check:
	@echo
	@echo Running unit tests...
	@echo
	@${PYTHON} ${MAIN_TEST_FILE}

# Self contained executable as built by PyInstaller and contained in local directory
${OUTPUT_FILE}: ${SOURCE_FILES} ${TEST_FILES} | check
	@echo
	@echo Testing and building final package...
	@echo
	@${PYTHON} -m PyInstaller ${MAIN_SOURCE_FILE} --onefile

