"""Cost tracking for Claude API usage."""

from dataclasses import dataclass, field

# Pricing per 1M tokens (as of late 2024)
MODEL_PRICING = {
    "claude-sonnet-4-5-20250929": {
        "input": 3.00,  # $3 per 1M input tokens
        "output": 15.00,  # $15 per 1M output tokens
    },
    "claude-opus-4-5-20251101": {
        "input": 15.00,  # $15 per 1M input tokens
        "output": 75.00,  # $75 per 1M output tokens
    },
    "claude-3-5-haiku-20241022": {
        "input": 0.80,  # $0.80 per 1M input tokens
        "output": 4.00,  # $4 per 1M output tokens
    },
    # Fallback for unknown models
    "default": {
        "input": 3.00,
        "output": 15.00,
    },
}


@dataclass
class StepUsage:
    """Token usage for a single step."""

    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0


@dataclass
class CostTracker:
    """Tracks API costs across generation steps."""

    steps: dict[str, StepUsage] = field(default_factory=dict)

    def add_usage(self, step_id: str, input_tokens: int, output_tokens: int, model: str) -> float:
        """Add token usage for a step and calculate cost."""
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])

        # Calculate cost
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        # Store or update step usage
        if step_id not in self.steps:
            self.steps[step_id] = StepUsage()

        self.steps[step_id].input_tokens += input_tokens
        self.steps[step_id].output_tokens += output_tokens
        self.steps[step_id].cost += total_cost

        return total_cost

    def get_step_cost(self, step_id: str) -> float:
        """Get the cost for a specific step."""
        if step_id in self.steps:
            return self.steps[step_id].cost
        return 0.0

    def get_total_cost(self) -> float:
        """Get total cost across all steps."""
        return sum(step.cost for step in self.steps.values())

    def get_total_tokens(self) -> tuple[int, int]:
        """Get total input and output tokens."""
        total_input = sum(step.input_tokens for step in self.steps.values())
        total_output = sum(step.output_tokens for step in self.steps.values())
        return total_input, total_output

    def get_breakdown(self) -> dict[str, dict[str, float]]:
        """Get cost breakdown by step."""
        return {
            step_id: {
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "cost": round(usage.cost, 4),
            }
            for step_id, usage in self.steps.items()
        }

    def estimate_cost(
        self,
        estimated_input_tokens: int,
        estimated_output_tokens: int,
        model: str = "claude-sonnet-4-5-20250929",
    ) -> tuple[float, float]:
        """Estimate cost range for a generation.

        Returns (min_cost, max_cost) based on typical variance.
        """
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])

        base_cost = (estimated_input_tokens / 1_000_000) * pricing["input"]
        base_cost += (estimated_output_tokens / 1_000_000) * pricing["output"]

        # Typical variance is +/- 30%
        min_cost = base_cost * 0.7
        max_cost = base_cost * 1.3

        return round(min_cost, 2), round(max_cost, 2)
