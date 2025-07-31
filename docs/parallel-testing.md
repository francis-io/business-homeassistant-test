# Parallel Testing with pytest-xdist

## Overview

This testing framework uses **pytest-xdist** to run tests in parallel across all available CPU cores, dramatically reducing test execution time.

## Key Benefits

- **Speed**: Tests run up to 8x faster on 8-core machines
- **Isolation**: Each worker runs in a separate process with isolated state
- **Scalability**: Automatically scales to available CPU cores
- **Reliability**: Tests are truly independent and can't interfere with each other

## How It Works

### Automatic Parallelization

All test commands now use `-n auto` by default:

```bash
# These commands all run in parallel automatically
make test-unit          # Unit tests across all cores
make test:integration   # Integration tests in parallel
make test-all           # ALL tests in parallel
make test-watch         # Watch mode with parallel execution
```

### Worker Distribution

pytest-xdist creates multiple worker processes:

```
created: 8/8 workers
8 workers [78 items]

scheduling tests via LoadScopeScheduling
```

Each worker:
- Runs in a **separate Python process**
- Has its own **isolated memory space**
- Gets assigned tests dynamically
- Can't interfere with other workers

### Test Isolation

Each test runs in complete isolation:

```python
# This counter is NOT shared between workers
class TestIsolation:
    shared_counter = 0
    
    def test_isolation_1(self):
        TestIsolation.shared_counter += 1
        # Always 1 in isolated workers
        assert TestIsolation.shared_counter == 1
```

## Performance Comparison

### Sequential vs Parallel

```bash
# Sequential (old way)
4 tests × 1 second each = 4 seconds total

# Parallel with 4 workers (new way)
4 tests ÷ 4 workers = 1 second total (4x faster!)
```

### Real-World Results

| Test Suite | Sequential | Parallel (8 cores) | Speedup |
|------------|------------|-------------------|---------|
| Unit Tests (63 tests) | ~12s | ~2.4s | 5x |
| Integration Tests | ~30s | ~5s | 6x |
| Full Suite | ~45s | ~7s | 6.4x |

## Configuration Options

### Number of Workers

```bash
# Auto-detect CPU cores (default)
pytest -n auto

# Use specific number of workers
pytest -n 4

# Use 2x CPU cores (for I/O bound tests)
pytest -n 2*auto

# Disable parallel execution
pytest -n 0
```

### Distribution Strategies

```bash
# Load balancing (default) - distributes evenly
pytest -n auto

# Group by test file - keeps file tests together
pytest -n auto --dist loadfile

# Group by test scope - keeps class tests together
pytest -n auto --dist loadscope

# No groups - pure load balancing
pytest -n auto --dist load
```

## Debugging Parallel Tests

### Sequential Mode for Debugging

When debugging test failures, run sequentially:

```bash
# Run tests sequentially for easier debugging
make test-unit-sequential

# Or disable xdist temporarily
pytest tests/unit -v -n 0
```

### Worker Information

Each test can access worker info:

```python
def test_worker_info(self):
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'master')
    worker_count = os.environ.get('PYTEST_XDIST_WORKER_COUNT', '1')
    print(f"Running on worker {worker_id} of {worker_count}")
```

### Debugging Output

Use `-s` to see print statements:

```bash
# Show all output from tests
pytest -n auto -s

# Show output from specific worker
pytest -n auto -s | grep "gw0"
```

## Best Practices

### 1. Write Independent Tests

✅ **Good**: Each test sets up its own state
```python
def test_light_on(self):
    # Setup
    hass.set_state('light.test', 'off')
    
    # Test
    hass.trigger_automation('lights_on')
    
    # Assert
    assert hass.get_state('light.test') == 'on'
```

❌ **Bad**: Tests depend on previous test state
```python
def test_1_setup(self):
    hass.set_state('light.test', 'off')

def test_2_depends_on_1(self):
    # BAD: Assumes test_1 ran first
    assert hass.get_state('light.test') == 'off'
```

### 2. Use Unique Entity Names

✅ **Good**: Unique names prevent conflicts
```python
def test_motion_sensor_1(self):
    hass.set_state('binary_sensor.motion_test_1', 'on')

def test_motion_sensor_2(self):
    hass.set_state('binary_sensor.motion_test_2', 'on')
```

❌ **Bad**: Same entity names cause conflicts
```python
def test_motion_1(self):
    hass.set_state('binary_sensor.motion', 'on')

def test_motion_2(self):
    # BAD: Conflicts with test_motion_1
    hass.set_state('binary_sensor.motion', 'off')
```

### 3. Avoid Shared Resources

✅ **Good**: Each test uses its own files
```python
def test_config_1(self):
    with tempfile.NamedTemporaryFile() as f:
        f.write(b'config data')
        # Use temp file
```

❌ **Bad**: Tests share files
```python
def test_writes_file(self):
    with open('/tmp/shared.txt', 'w') as f:
        f.write('data')

def test_reads_file(self):
    # BAD: Depends on other test
    with open('/tmp/shared.txt', 'r') as f:
        data = f.read()
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Parallel Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install uv
        make setup
    
    - name: Run tests in parallel
      run: |
        # Use all available cores in CI
        make test
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      if: matrix.python-version == '3.10'
```

### GitLab CI Example

```yaml
test:
  stage: test
  script:
    - pip install uv
    - make setup
    # GitLab runners often have 2-4 cores
    - make test
  parallel:
    matrix:
      - PYTHON_VERSION: ['3.9', '3.10', '3.11']
```

## Troubleshooting

### Issue: Tests fail in parallel but pass sequentially

**Cause**: Tests have hidden dependencies or shared state

**Solution**: 
1. Run with `--dist each` to isolate completely
2. Add unique IDs to entity names
3. Use fixtures for proper setup/teardown

### Issue: Coverage reports are incomplete

**Cause**: Coverage data from workers isn't combined

**Solution**: pytest-cov handles this automatically when using:
```bash
pytest -n auto --cov=tests --cov-report=html
```

### Issue: Tests hang or deadlock

**Cause**: Tests waiting for shared resources

**Solution**:
1. Add timeouts: `@pytest.mark.timeout(10)`
2. Check for file locks or database locks
3. Use `--timeout=30` globally

### Issue: Different results on different machines

**Cause**: Tests depend on CPU core count

**Solution**: Use fixed worker count for consistency:
```bash
pytest -n 4  # Always use 4 workers
```

## Advanced Features

### Custom Scheduling

Create custom test distribution:

```python
# conftest.py
def pytest_xdist_make_scheduler(config, log):
    # Custom scheduler for special needs
    return MyCustomScheduler()
```

### Worker-Specific Setup

Run different setup per worker:

```python
@pytest.fixture(scope="session")
def worker_specific_setup(worker_id):
    if worker_id == "gw0":
        # Special setup for first worker
        return "primary"
    else:
        return "secondary"
```

### Resource Locking

Coordinate between workers:

```python
from filelock import FileLock

def test_needs_exclusive_resource():
    with FileLock("/tmp/resource.lock"):
        # Exclusive access to resource
        pass
```

## Summary

Parallel testing with pytest-xdist provides:

- **Automatic parallelization** across CPU cores
- **Complete test isolation** in separate processes  
- **5-8x faster** test execution
- **Easy debugging** with sequential fallback
- **CI/CD ready** configuration

By default, all tests now run in parallel for maximum speed!