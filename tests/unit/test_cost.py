"""Tests for cost tracking."""

from specinit.generator.cost import CostTracker


class TestCostTracker:
    """Tests for CostTracker."""

    def test_add_usage_calculates_cost(self):
        """Adding usage should calculate cost based on model pricing."""
        tracker = CostTracker()

        cost = tracker.add_usage(
            step_id="test_step",
            input_tokens=1000,
            output_tokens=500,
            model="claude-sonnet-4-5-20250929",
        )

        # Expected: (1000/1M * $3) + (500/1M * $15) = $0.003 + $0.0075 = $0.0105
        assert abs(cost - 0.0105) < 0.0001

    def test_get_step_cost(self):
        """get_step_cost should return cost for a specific step."""
        tracker = CostTracker()

        tracker.add_usage("step1", 1000, 500, "claude-sonnet-4-5-20250929")
        tracker.add_usage("step2", 2000, 1000, "claude-sonnet-4-5-20250929")

        step1_cost = tracker.get_step_cost("step1")
        step2_cost = tracker.get_step_cost("step2")

        assert step1_cost > 0
        assert step2_cost > step1_cost  # More tokens = higher cost

    def test_get_step_cost_nonexistent(self):
        """get_step_cost should return 0 for nonexistent step."""
        tracker = CostTracker()

        cost = tracker.get_step_cost("nonexistent")

        assert cost == 0.0

    def test_get_total_cost(self):
        """get_total_cost should sum all step costs."""
        tracker = CostTracker()

        tracker.add_usage("step1", 1000, 500, "claude-sonnet-4-5-20250929")
        tracker.add_usage("step2", 1000, 500, "claude-sonnet-4-5-20250929")

        total = tracker.get_total_cost()
        step1 = tracker.get_step_cost("step1")

        assert abs(total - (step1 * 2)) < 0.0001

    def test_get_total_tokens(self):
        """get_total_tokens should return total input and output tokens."""
        tracker = CostTracker()

        tracker.add_usage("step1", 1000, 500, "claude-sonnet-4-5-20250929")
        tracker.add_usage("step2", 2000, 1000, "claude-sonnet-4-5-20250929")

        input_tokens, output_tokens = tracker.get_total_tokens()

        assert input_tokens == 3000
        assert output_tokens == 1500

    def test_get_breakdown(self):
        """get_breakdown should return per-step usage details."""
        tracker = CostTracker()

        tracker.add_usage("step1", 1000, 500, "claude-sonnet-4-5-20250929")
        tracker.add_usage("step2", 2000, 1000, "claude-sonnet-4-5-20250929")

        breakdown = tracker.get_breakdown()

        assert "step1" in breakdown
        assert "step2" in breakdown
        assert breakdown["step1"]["input_tokens"] == 1000
        assert breakdown["step1"]["output_tokens"] == 500

    def test_accumulates_multiple_calls_same_step(self):
        """Multiple calls to same step should accumulate."""
        tracker = CostTracker()

        tracker.add_usage("step1", 1000, 500, "claude-sonnet-4-5-20250929")
        tracker.add_usage("step1", 1000, 500, "claude-sonnet-4-5-20250929")

        breakdown = tracker.get_breakdown()

        assert breakdown["step1"]["input_tokens"] == 2000
        assert breakdown["step1"]["output_tokens"] == 1000

    def test_estimate_cost(self):
        """estimate_cost should return reasonable range."""
        tracker = CostTracker()

        min_cost, max_cost = tracker.estimate_cost(
            estimated_input_tokens=10000,
            estimated_output_tokens=5000,
        )

        # Base: (10000/1M * $3) + (5000/1M * $15) = $0.03 + $0.075 = $0.105
        # Min: $0.105 * 0.7 = $0.0735
        # Max: $0.105 * 1.3 = $0.1365
        assert 0.07 <= min_cost <= 0.08
        assert 0.13 <= max_cost <= 0.14
        assert min_cost < max_cost

    def test_default_pricing_for_unknown_model(self):
        """Unknown models should use default pricing."""
        tracker = CostTracker()

        cost = tracker.add_usage(
            step_id="test",
            input_tokens=1000,
            output_tokens=500,
            model="unknown-model-123",
        )

        # Should use default pricing (same as sonnet)
        assert cost > 0

    def test_opus_pricing_higher_than_sonnet(self):
        """Opus model should have higher costs than Sonnet."""
        tracker1 = CostTracker()
        tracker2 = CostTracker()

        sonnet_cost = tracker1.add_usage("test", 1000, 500, "claude-sonnet-4-5-20250929")
        opus_cost = tracker2.add_usage("test", 1000, 500, "claude-opus-4-5-20251101")

        assert opus_cost > sonnet_cost
