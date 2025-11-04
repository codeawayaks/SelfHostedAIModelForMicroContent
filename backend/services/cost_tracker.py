"""
Cost tracking service for Runpod API calls
Based on provided metrics:
- Hook Generation (Phi-2): ~2s, $0.00011
- Caption Generation (Mistral 7B): ~5s, $0.00028
- CTA Generation (Phi-2): ~1s, $0.00006
- Merge & Output: ~1s, $0.00005
Total: ~$0.0005 per post
"""

# Fixed costs per generation step
HOOK_COST = 0.00011
CAPTION_COST = 0.00028
CTA_COST = 0.00006
MERGE_COST = 0.00005


def calculate_total_cost() -> float:
    """Calculate total cost for a complete post generation"""
    return HOOK_COST + CAPTION_COST + CTA_COST + MERGE_COST


def get_step_costs() -> dict:
    """Get cost breakdown for each step"""
    return {
        "hook": HOOK_COST,
        "caption": CAPTION_COST,
        "cta": CTA_COST,
        "merge": MERGE_COST,
        "total": calculate_total_cost()
    }

