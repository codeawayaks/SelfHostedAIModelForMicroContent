"""
Orchestration service for coordinating the generation pipeline
Sequences: Hook → Caption → CTA → Merge
"""
from typing import Optional
from backend.services.runpod_client import RunpodClient
from backend.services.cost_tracker import (
    HOOK_COST, CAPTION_COST, CTA_COST, MERGE_COST
)


class OrchestrationService:
    """Orchestrates the sequential generation of post components"""
    
    def __init__(self):
        self.runpod_client = RunpodClient()
    
    async def generate_post(
        self,
        input_type: str,
        input_content: str
    ) -> dict:
        """
        Generate a complete post by orchestrating all steps
        
        Args:
            input_type: "topic" or "prompt"
            input_content: The topic/keywords or full prompt
            
        Returns:
            Dictionary with hook, caption, cta, final_output, and cost breakdown
        """
        # Prepare context based on input type
        if input_type == "prompt":
            # If full prompt provided, extract topic and use prompt as context
            topic = input_content[:100]  # Use first 100 chars as topic identifier
            prompt_context = input_content
        else:
            # Topic/keywords mode
            topic = input_content
            prompt_context = None
        
        # Step 1: Generate Hook (Phi-2)
        hook = await self.runpod_client.generate_hook(topic, prompt_context)
        
        # Step 2: Generate Caption (Mistral 7B)
        caption = await self.runpod_client.generate_caption(topic, hook, prompt_context)
        
        # Step 3: Generate CTA (Phi-2)
        cta = await self.runpod_client.generate_cta(topic, hook, caption, prompt_context)
        
        # Step 4: Merge components into final output
        final_output = self._merge_components(hook, caption, cta)
        
        # Calculate costs
        total_cost = HOOK_COST + CAPTION_COST + CTA_COST + MERGE_COST
        
        return {
            "hook": hook,
            "caption": caption,
            "cta": cta,
            "final_output": final_output,
            "cost": total_cost,
            "hook_cost": HOOK_COST,
            "caption_cost": CAPTION_COST,
            "cta_cost": CTA_COST,
            "merge_cost": MERGE_COST
        }
    
    def _merge_components(self, hook: str, caption: str, cta: str) -> str:
        """
        Merge all components into a formatted final post
        
        Args:
            hook: Generated hook
            caption: Generated caption
            cta: Generated CTA
            
        Returns:
            Formatted post string ready for copy-paste
        """
        # Format the post with clear sections
        lines = []
        lines.append(hook)
        lines.append("")  # Empty line
        lines.append(caption)
        lines.append("")  # Empty line
        lines.append(cta)
        
        return "\n".join(lines)

