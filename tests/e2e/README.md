# End-to-End (E2E) Tests

This directory is for future end-to-end tests that will test the full Home Assistant UI using browser automation tools like Playwright or Selenium.

## Status

⚠️ **Not Yet Implemented**: E2E tests are planned for future development.

## Requirements

To run E2E tests (when implemented), install the dependencies:

```bash
make setup-e2e
```

This will install:
- Base test dependencies from `tests/requirements.txt`
- Browser automation tools from `tests/e2e/requirements.txt`

## Planned Features

- Test complete user workflows through the UI
- Verify automation creation through the UI
- Test dashboard interactions
- Validate real-time state updates
- Cross-browser testing

## Technology Choice

The `requirements.txt` file includes placeholders for:
- **Playwright** (recommended) - Modern, fast, reliable cross-browser testing
- **Selenium** (alternative) - Traditional, widely supported option

Uncomment your preferred tool in `requirements.txt` before running `make setup-e2e`.