# Property-Based Tests

Property-based tests use [Hypothesis](https://hypothesis.readthedocs.io/) to generate random test data and verify that certain properties hold for all inputs.

## What are Property-Based Tests?

Instead of testing specific examples, property-based tests verify general properties:
- "Cost is always non-negative"
- "Sorting returns the same elements"
- "Encoding then decoding returns the original value"

## Running Property Tests

```bash
# Run all property tests
pytest tests/property/ -v

# Run with more examples (slower but more thorough)
HYPOTHESIS_PROFILE=ci pytest tests/property/

# Run in debug mode with maximum examples
HYPOTHESIS_PROFILE=debug pytest tests/property/
```

## Writing Property Tests

```python
from hypothesis import given
from hypothesis import strategies as st
import pytest

@pytest.mark.property
@given(
    x=st.integers(min_value=0, max_value=1000),
    y=st.integers(min_value=0, max_value=1000),
)
def test_addition_commutative(x: int, y: int) -> None:
    """Addition should be commutative."""
    assert x + y == y + x
```

## When to Use Property Tests

- Testing mathematical properties (commutative, associative, etc.)
- Validating parsing/serialization (round-trip property)
- Testing with many edge cases
- Verifying invariants hold for all inputs
