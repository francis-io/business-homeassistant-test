# Pre-commit Configuration Recommendations for HA Test Framework

## Executive Summary

After deep analysis of this Home Assistant testing framework, I recommend a comprehensive pre-commit configuration with **20 specific checks** organized in 4 phases. The configuration addresses the unique challenges of:

1. **Multi-level testing architecture** (logic/mock/integration)
2. **AI code generation quality**
3. **Home Assistant specific requirements**
4. **Security and performance concerns**

## Key Insights from Analysis

### Repository-Specific Challenges

1. **Test Level Separation**: This repo's innovative approach of separating pure logic tests from mock/integration tests requires custom validators to maintain architectural integrity.

2. **Home Assistant Compatibility**: HA's frequent updates and specific async patterns require strict type checking and interface validation.

3. **AI Generation Risks**: AI tools often:
   - Mix test levels (putting integration code in unit tests)
   - Create incorrect mocks that don't match HA behavior
   - Forget async/await patterns
   - Generate duplicate helper functions

4. **Security Concerns**: Test configurations might accidentally include real tokens, API keys, or personal data.

## Recommended Checks (By Priority)

### Phase 1: Critical Security & Test Integrity (Week 1)

#### 1. **detect-secrets** (CRITICAL)
- Prevents accidental credential commits
- Especially important for HA configs that might contain real tokens
- Baseline file allows whitelisting known safe patterns

#### 2. **gitleaks** (CRITICAL)
- Additional layer of secret scanning
- Catches patterns detect-secrets might miss
- Fast and reliable

#### 3. **pytest --collect-only** (CRITICAL)
- Validates all tests are discoverable
- Catches import errors immediately
- Prevents broken test suites from being committed

#### 4. **mypy --strict** (CRITICAL)
- Essential for HA compatibility
- Catches async/await issues
- Validates mock interfaces match HA

### Phase 2: Code Quality & Structure (Week 1-2)

#### 5-7. **black, isort, flake8** (HIGH)
- Already in use via Makefile
- Ensures consistent formatting
- flake8 plugins add pytest-style and async checks

#### 8. **bandit** (HIGH)
- Security-focused Python linting
- Catches common vulnerabilities
- Important for test code that might handle sensitive data

### Phase 3: HA-Specific & Architecture (Week 2)

#### 9. **yamllint** (HIGH)
- Critical for HA configuration files
- Custom rules for HA's YAML style
- Prevents config parsing errors

#### 10. **test-structure-validator** (CUSTOM, HIGH)
- Enforces logic/mock/integration separation
- Prevents logic tests from importing HA components
- Maintains architectural integrity

#### 11. **automation-logic-enforcer** (CUSTOM, HIGH)
- Ensures business logic stays in `automation_logic.py`
- Prevents complex logic in test files
- Maintains testability

#### 12. **ha-mock-validator** (CUSTOM, MEDIUM)
- Validates mocks implement required HA interfaces
- Ensures consistency with HA API changes
- Prevents incorrect mock usage

### Phase 4: Performance & Quality (Week 3)

#### 13. **vulture** (MEDIUM)
- Finds dead code
- Keeps test suite lean
- Helps identify obsolete tests

#### 14. **pydocstyle** (MEDIUM)
- Enforces documentation standards
- Especially important for helper functions
- Google style for consistency

#### 15. **pyupgrade** (MEDIUM)
- Ensures modern Python 3.11+ syntax
- Keeps code current with Python best practices
- Helps AI generate modern code

### General Repository Health

#### 16-20. **Standard hooks** (MEDIUM)
- File formatting (trailing whitespace, EOF)
- Large file prevention
- JSON/YAML validation
- Markdown formatting
- Commit message standards

## Custom Validators Explained

### test-structure-validator
```python
# Enforces:
# - Logic tests cannot import HA components
# - Mock tests must use ha_mocks
# - Integration tests should use fast_ha_test
```

### automation-logic-enforcer
```python
# Detects:
# - Complex conditions (>3 logical operators)
# - Time/date calculations
# - State determination logic
# Suggests extraction to automation_logic.py
```

### ha-mock-validator
```python
# Validates:
# - Mock classes implement required interfaces
# - No direct HA imports in mock tests
# - Mock consistency with HA API
```

## Implementation Strategy

### Week 1: Foundation
1. Install pre-commit: `pip install pre-commit`
2. Add Phase 1 checks (security & test integrity)
3. Run on existing code to establish baseline
4. Fix critical issues

### Week 2: Structure
1. Add Phase 2 & 3 checks
2. Implement custom validators
3. Update CLAUDE.md with pre-commit requirements
4. Team training on new checks

### Week 3: Polish
1. Add Phase 4 checks
2. Fine-tune configurations
3. Integrate with CI/CD
4. Document bypass procedures

### Week 4: Optimization
1. Measure performance impact
2. Optimize slow checks
3. Consider lint-staged for large files
4. Establish maintenance process

## Configuration Decisions

### Why These Specific Tools?

1. **Security First**: Two secret scanners because HA tests often contain real-looking data
2. **Type Safety**: Strict mypy because HA's async patterns are error-prone
3. **Custom Validators**: This repo's unique architecture requires custom enforcement
4. **Incremental Adoption**: Phased rollout prevents disruption

### Why NOT These Tools?

1. **NOT pylint**: Too opinionated, overlaps with flake8
2. **NOT coverage in pre-commit**: Better in CI/CD
3. **NOT pytest full run**: Too slow for pre-commit
4. **NOT auto-fixing**: Let developers understand changes

## AI-Specific Considerations

### Common AI Errors This Prevents

1. **Test Level Mixing**: Custom validator ensures proper separation
2. **Mock Misuse**: Interface validation catches incorrect mocks
3. **Security Leaks**: Two-layer secret scanning
4. **Async Bugs**: Strict typing and flake8-async
5. **Dead Code**: AI often generates unused helpers

### Guidelines for AI Tools

When using Claude or other AI tools with this configuration:

1. **Mention the pre-commit setup** in your prompts
2. **Reference the test architecture** (logic/mock/integration)
3. **Specify async requirements** for HA code
4. **Ask for type hints** to pass mypy strict mode

## Metrics for Success

### Short Term (1 month)
- 0% security violations in commits
- <5% pre-commit rejections after initial cleanup
- 100% test discoverability
- <30 second average check time

### Long Term (3 months)
- 50% reduction in post-commit fixes
- 90% reduction in architecture violations
- Improved AI code generation quality
- Developer satisfaction >4/5

## Maintenance Notes

### Regular Updates Needed
1. **HA API changes**: Update ha-mock-validator when HA updates
2. **Python version**: Update pyupgrade when moving Python versions
3. **Security baselines**: Regenerate detect-secrets baseline monthly
4. **Tool versions**: Update pre-commit hooks quarterly

### Bypass Procedures
```bash
# Skip for WIP commits
git commit --no-verify -m "WIP: ..."

# Skip specific hooks
SKIP=mypy,pytest-collect git commit -m "..."

# Update baseline for secrets
detect-secrets scan --baseline .secrets.baseline
```

## Conclusion

This configuration balances comprehensive quality checks with developer productivity. The custom validators preserve this repository's innovative testing architecture while preventing common AI-generated code issues. The phased rollout ensures smooth adoption without disrupting ongoing work.