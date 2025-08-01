# Makefile - Dynamic wrapper for Just commands
# This forwards all commands to Just

# Check if just is installed
JUST := $(shell command -v just 2> /dev/null)

ifndef JUST
$(error "just is not installed. Please install it: https://github.com/casey/just")
endif

# Default target
.DEFAULT_GOAL := help

# Always run these targets
.PHONY: help

# Default help
help:
	@$(JUST)

# Forward all commands directly to just
# 'make test::unit' will work
%:
	@$(JUST) $@
