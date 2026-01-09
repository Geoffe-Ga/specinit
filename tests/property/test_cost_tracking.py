"""Property-based tests for cost tracking functionality.

Tests cost calculation properties using Hypothesis for fuzz testing with
various input combinations.
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from specinit.generator.cost import CostTracker


@pytest.mark.property
class TestCostTrackerProperties:
    """Property-based tests for CostTracker."""

    @given(
        input_tokens=st.integers(min_value=0, max_value=1_000_000),
        output_tokens=st.integers(min_value=0, max_value=1_000_000),
    )
    def test_cost_is_non_negative(self, input_tokens: int, output_tokens: int) -> None:
        """Cost should always be non-negative for any token counts."""
        tracker = CostTracker()
        model = "claude-sonnet-4-5-20250929"

        tracker.add_usage(
            step_id="test_step",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
        )

        total_cost = tracker.get_total_cost()
        assert total_cost >= 0, "Cost should never be negative"

    @given(
        input_tokens=st.integers(min_value=1, max_value=10_000),
        output_tokens=st.integers(min_value=1, max_value=10_000),
    )
    def test_cost_increases_with_tokens(self, input_tokens: int, output_tokens: int) -> None:
        """Cost should increase as token count increases."""
        tracker1 = CostTracker()
        tracker2 = CostTracker()
        model = "claude-sonnet-4-5-20250929"

        # First tracker with base tokens
        tracker1.add_usage(
            step_id="test_step",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
        )

        # Second tracker with more tokens
        tracker2.add_usage(
            step_id="test_step",
            input_tokens=input_tokens * 2,
            output_tokens=output_tokens * 2,
            model=model,
        )

        assert tracker2.get_total_cost() > tracker1.get_total_cost(), (
            "Cost should increase with more tokens"
        )

    @given(
        steps=st.lists(
            st.tuples(
                st.text(min_size=1, max_size=20),  # step name
                st.integers(min_value=0, max_value=10_000),  # input tokens
                st.integers(min_value=0, max_value=10_000),  # output tokens
            ),
            min_size=1,
            max_size=10,
        )
    )
    def test_total_equals_sum_of_steps(self, steps: list[tuple[str, int, int]]) -> None:
        """Total cost should equal sum of individual step costs."""
        tracker = CostTracker()
        model = "claude-sonnet-4-5-20250929"

        # Add all usages
        for step_name, input_tokens, output_tokens in steps:
            tracker.add_usage(
                step_id=step_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=model,
            )

        # Calculate sum of individual step costs
        step_costs_sum = sum(tracker.get_step_cost(step_name) for step_name, _, _ in steps)

        total_cost = tracker.get_total_cost()

        # Allow small floating point error
        assert abs(total_cost - step_costs_sum) < 0.001, "Total cost should equal sum of step costs"

    @given(
        input_tokens=st.integers(min_value=0, max_value=100_000),
        output_tokens=st.integers(min_value=0, max_value=100_000),
        num_calls=st.integers(min_value=1, max_value=10),
    )
    def test_multiple_calls_same_step_accumulate(
        self, input_tokens: int, output_tokens: int, num_calls: int
    ) -> None:
        """Multiple calls to same step should accumulate correctly."""
        tracker = CostTracker()
        model = "claude-sonnet-4-5-20250929"

        # Add usage multiple times
        for _ in range(num_calls):
            tracker.add_usage(
                step_id="test_step",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=model,
            )

        # Get single call cost
        single_tracker = CostTracker()
        single_tracker.add_usage(
            step_id="test_step",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
        )
        single_cost = single_tracker.get_step_cost("test_step")

        # Multi-call cost should be num_calls * single_cost
        multi_cost = tracker.get_step_cost("test_step")

        # Allow small floating point error
        expected_cost = single_cost * num_calls
        assert abs(multi_cost - expected_cost) < 0.001, (
            f"Expected {expected_cost:.4f}, got {multi_cost:.4f}"
        )
