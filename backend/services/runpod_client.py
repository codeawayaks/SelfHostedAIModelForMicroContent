"""
Runpod.io API client for Serverless API endpoints
Supports Phi-2 and Mistral 7B models
"""
import logging
import httpx
import asyncio
from typing import Optional
from backend.config import settings

logger = logging.getLogger(__name__)


class RunpodClient:
    """Client for interacting with Runpod.io Serverless API"""
    
    def __init__(self):
        # Validate settings when client is initialized
        from backend.config import get_settings
        validated_settings = get_settings()
        
        self.api_key = validated_settings.runpod_api_key
        self.phi2_endpoint_id = validated_settings.runpod_phi2_endpoint_id
        self.mistral_endpoint_id = validated_settings.runpod_mistral_endpoint_id
        # Use custom model names if provided, otherwise use defaults
        self.phi2_model_name = validated_settings.runpod_phi2_model_name or "microsoft/Phi-2"
        self.mistral_model_name = validated_settings.runpod_mistral_model_name or "mistralai/Mistral-7B-Instruct-v0.1"
        # Runpod Serverless API format
        self.base_url_template = "https://api.runpod.ai/v2/{endpoint_id}/run"
        self.timeout = 60.0  # Increased timeout for model loading
        
        # Different polling configurations for different models
        # Mistral is larger and typically slower, so we allow more time
        # With 5 second intervals: 360 attempts = 30 minutes, 1440 attempts = 2 hours
        self.phi2_max_poll_attempts = 360  # 30 minutes for Phi-2 (360 * 5s = 1800s = 30min)
        self.mistral_max_poll_attempts = 1440  # 120 minutes (2 hours) for Mistral (1440 * 5s = 7200s = 120min)
    
    def _get_endpoint_url(self, endpoint_id: str) -> str:
        """Get the full API endpoint URL"""
        return self.base_url_template.format(endpoint_id=endpoint_id)
    
    def _get_headers(self) -> dict:
        """Get request headers with API key"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    async def generate_text(
        self,
        prompt: str,
        model_type: str = "phi2",  # "phi2" or "mistral"
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        Generate text using Runpod.io model
        
        Args:
            prompt: The input prompt
            model_type: "phi2" or "mistral"
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text string
            
        Raises:
            Exception: If API call fails
        """
        # Select endpoint based on model type
        if model_type == "phi2":
            endpoint_id = self.phi2_endpoint_id
            model_name = self.phi2_model_name
        elif model_type == "mistral":
            endpoint_id = self.mistral_endpoint_id
            model_name = self.mistral_model_name
        else:
            raise ValueError(f"Unknown model_type: {model_type}")
        
        endpoint_url = self._get_endpoint_url(endpoint_id)
        
        # Prepare request payload for Runpod Serverless API
        # Format: {"input":{"prompt":"Your prompt"}}
        # Note: Some endpoints may expect different parameter names
        # We'll try with standard format first, but may need to adjust based on endpoint
        
        # Build payload with just prompt first (minimal required fields)
        payload = {
            "input": {
                "prompt": str(prompt)  # Ensure it's a string
            }
        }
        
        # Add optional parameters if the endpoint supports them
        # Some endpoints may not accept these in the input, so we try without first
        # If needed, these can be added back or moved to top level
        if max_tokens and max_tokens > 0:
            payload["input"]["max_tokens"] = int(max_tokens)
        if temperature is not None and 0 <= temperature <= 2:
            payload["input"]["temperature"] = float(temperature)
        
        logger.debug(f"Payload structure: {list(payload['input'].keys())}")
        
        # Make API request
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                logger.info(f"Calling Runpod endpoint: {endpoint_url}")
                logger.debug(f"Request payload: {payload}")
                
                response = await client.post(
                    endpoint_url,
                    headers=self._get_headers(),
                    json=payload
                )
                
                # Log response details for debugging
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")
                
                response.raise_for_status()
                
                result = response.json()
                logger.debug(f"Response result: {result}")
                
                # Runpod Serverless API response format
                # Check for async job status
                if "id" in result:
                    # This is an async job, we need to poll for results
                    job_id = result["id"]
                    # Use different max attempts based on model type
                    max_attempts = self.mistral_max_poll_attempts if model_type == "mistral" else self.phi2_max_poll_attempts
                    model_name_display = "Mistral" if model_type == "mistral" else "Phi-2"
                    logger.info(f"Received async job ID: {job_id} for {model_name_display}. Polling for results (max {max_attempts} minutes)...")
                    return await self._poll_job_status(endpoint_url, job_id, max_attempts, model_name_display)
                
                # Check for direct response (synchronous)
                if "output" in result:
                    output = result["output"]
                    extracted_text = self._extract_text_from_output(output)
                    if extracted_text:
                        return extracted_text
                
                # Fallback: try to extract text from any field
                if "text" in result:
                    return self._clean_text(str(result["text"]))
                elif "generated_text" in result:
                    return self._clean_text(str(result["generated_text"]))
                else:
                    raise Exception(f"Unexpected response format. Response: {result}")
                    
            except httpx.HTTPStatusError as e:
                error_detail = "Unknown error"
                error_response_full = None
                try:
                    error_response_full = e.response.json()
                    error_detail = error_response_full.get("error", error_response_full.get("message", str(error_response_full)))
                    logger.error(f"Full error response: {error_response_full}")
                except:
                    error_detail = e.response.text[:500]  # Limit error text length
                    logger.error(f"Error response text: {error_detail}")
                
                # Provide helpful troubleshooting info
                troubleshooting = (
                    f"\nTroubleshooting steps:\n"
                    f"1. Verify the endpoint ID '{endpoint_id}' is correct in your Runpod dashboard\n"
                    f"2. Check that the endpoint is active and the model is loaded\n"
                    f"3. Verify your API key has access to this endpoint\n"
                    f"4. Check Runpod endpoint logs for detailed error information\n"
                    f"5. Try testing the endpoint directly with curl or Postman"
                )
                
                raise Exception(f"Runpod API error ({e.response.status_code}): {error_detail}{troubleshooting}")
            except httpx.TimeoutException:
                raise Exception("Runpod API request timeout. The endpoint may be cold-starting or overloaded. Try again in a few moments.")
            except Exception as e:
                raise Exception(f"Error calling Runpod API: {str(e)}")
    
    async def _poll_job_status(self, endpoint_url: str, job_id: str, max_attempts: int = 60, model_name: str = "Model") -> str:
        """
        Poll for job status until completion
        
        Args:
            endpoint_url: The endpoint URL (without /status)
            job_id: The job ID to poll
            max_attempts: Maximum number of polling attempts (default 60 = 5 minutes with 5 second intervals)
            model_name: Name of the model for logging purposes
            
        Returns:
            Generated text string
        """
        status_url = endpoint_url.replace("/run", f"/status/{job_id}")
        
        last_status = None
        status_change_count = 0
        
        for attempt in range(max_attempts):
            # Wait 5 seconds between polls
            if attempt > 0:  # Don't wait before first attempt
                await asyncio.sleep(5)  # Wait 5 seconds between retries
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                try:
                    response = await client.get(
                        status_url,
                        headers=self._get_headers()
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    
                    # Check job status
                    status = result.get("status", "UNKNOWN")
                    queue_position = result.get("queue_position")
                    execution_time = result.get("execution_time")
                    
                    # Log status changes
                    if status != last_status:
                        status_change_count += 1
                        last_status = status
                        elapsed_seconds = attempt * 5  # 5 seconds per attempt
                        elapsed_minutes = elapsed_seconds // 60
                        elapsed_secs = elapsed_seconds % 60
                        logger.info(f"[{model_name}] Job {job_id} status: {status} (attempt {attempt + 1}, ~{elapsed_minutes}m {elapsed_secs}s elapsed)")
                        if queue_position:
                            logger.info(f"  Queue position: {queue_position}")
                        if execution_time:
                            logger.info(f"  Execution time: {execution_time}ms")
                    
                    # Log progress every 12 attempts (every minute)
                    if attempt > 0 and attempt % 12 == 0:  # Every 12 attempts = 60 seconds = 1 minute
                        elapsed_seconds = attempt * 5
                        elapsed_minutes = elapsed_seconds // 60
                        logger.info(f"[{model_name}] Job {job_id} still {status} after ~{elapsed_minutes} minutes...")
                    
                    if status == "COMPLETED":
                        output = result.get("output")
                        if output:
                            logger.info(f"Job {job_id} completed successfully")
                            extracted_text = self._extract_text_from_output(output)
                            if extracted_text:
                                return extracted_text
                            else:
                                raise Exception(f"Could not extract text from output: {output}")
                        else:
                            raise Exception("Job completed but no output found")
                    
                    elif status == "FAILED":
                        # Extract error information from various possible formats
                        error_info = result.get("error", {})
                        error_message = "Unknown error"
                        
                        if isinstance(error_info, dict):
                            # Try different possible error fields
                            error_message = (
                                error_info.get("message") or
                                error_info.get("error") or
                                error_info.get("detail") or
                                str(error_info)
                            )
                        elif isinstance(error_info, str):
                            error_message = error_info
                        else:
                            error_message = str(error_info)
                        
                        # Also check for error in output field
                        output = result.get("output")
                        if output and isinstance(output, dict):
                            output_error = output.get("error") or output.get("message")
                            if output_error:
                                error_message = output_error
                        
                        # Check for traceback or additional error details
                        traceback_info = result.get("traceback")
                        if traceback_info:
                            logger.error(f"Job {job_id} traceback: {traceback_info}")
                        
                        logger.error(f"Job {job_id} failed: {error_message}")
                        
                        # Provide more context about the failure
                        error_details = {
                            "job_id": job_id,
                            "error_message": error_message,
                            "execution_time_ms": result.get("executionTime"),
                            "delay_time_ms": result.get("delayTime"),
                            "worker_id": result.get("workerId")
                        }
                        logger.error(f"Job failure details: {error_details}")
                        
                        # Check for common error patterns and provide helpful suggestions
                        if "EngineCore" in error_message or "requestError" in error_message or "validation error" in error_message.lower():
                            # This is a known issue with some Runpod endpoint handlers
                            # The handler's ErrorResponse model requires an 'error' field but handler only provides 'message' and 'code'
                            raise Exception(
                                f"Endpoint Handler Bug Detected: {error_message}\n\n"
                                f"This is a bug in your Runpod endpoint handler code, not in the request format.\n"
                                f"The handler's ErrorResponse Pydantic model requires an 'error' field, but the handler\n"
                                f"is only providing 'message' and 'code' fields when creating error responses.\n\n"
                                f"To fix this in your Runpod endpoint handler:\n"
                                f"1. Check your handler code (likely in /src/utils.py in create_error_response function)\n"
                                f"2. Update the ErrorResponse model to make 'error' field optional, OR\n"
                                f"3. Include 'error' field when creating ErrorResponse: ErrorResponse(error=message, message=message, code=code)\n\n"
                                f"Alternatively, fix the underlying issue causing the 'EngineCore requestError'.\n"
                                f"The request format we're sending is correct: {{\"input\":{{\"prompt\":\"...\"}}}}"
                            )
                        
                        raise Exception(f"Job failed: {error_message}")
                    
                    # Status is IN_QUEUE or IN_PROGRESS, continue polling
                    if attempt == max_attempts - 1:
                        elapsed_seconds = max_attempts * 5
                        elapsed_minutes = elapsed_seconds // 60
                        raise Exception(
                            f"Job did not complete within ~{elapsed_minutes} minutes ({max_attempts * 5} seconds). "
                            f"Current status: {status}. "
                            f"You can check the job status manually at: {status_url}"
                        )
                        
                except httpx.HTTPStatusError as e:
                    if attempt == max_attempts - 1:
                        raise Exception(f"Error polling job status: {e.response.status_code} - {e.response.text}")
                    # Continue polling on HTTP errors (might be temporary)
                    logger.warning(f"Error polling job (attempt {attempt + 1}): {e.response.status_code}")
                    await asyncio.sleep(5)  # Wait 5 seconds before retry on error
                except Exception as e:
                    # Check if this is a job failure error (should not retry)
                    error_msg = str(e)
                    if "Job failed:" in error_msg:
                        # This is a job failure, don't retry, just raise
                        raise
                    
                    if attempt == max_attempts - 1:
                        raise
                    # Continue polling on other errors (network issues, etc.)
                    logger.warning(f"Error polling job (attempt {attempt + 1}): {str(e)}")
                    await asyncio.sleep(5)  # Wait 5 seconds before retry on error
        
        elapsed_seconds = max_attempts * 5
        elapsed_minutes = elapsed_seconds // 60
        raise Exception(f"Job did not complete within ~{elapsed_minutes} minutes ({max_attempts * 5} seconds)")
    
    def _extract_text_from_output(self, output) -> str:
        """
        Extract human-readable text from various output formats.
        Handles formats like:
        - String: direct text
        - Dict: {"text": "...", "generated_text": "...", etc.}
        - List with choices: [{"choices": [{"tokens": ["..."]}]}]
        - List with strings: ["text1", "text2"]
        """
        if isinstance(output, str):
            return self._clean_text(output)
        
        elif isinstance(output, dict):
            # Try common text fields
            for field in ["text", "generated_text", "output", "content", "message"]:
                if field in output:
                    return self._clean_text(str(output[field]))
            
            # Check if it's a choices format
            if "choices" in output:
                return self._extract_text_from_output(output["choices"])
            
            # Fallback: convert dict to string
            return self._clean_text(str(output))
        
        elif isinstance(output, list):
            if len(output) == 0:
                return ""
            
            # Handle list of dicts with choices/tokens
            for item in output:
                if isinstance(item, dict):
                    # Check for choices format: [{"choices": [{"tokens": ["..."]}]}]
                    if "choices" in item:
                        choices = item["choices"]
                        if isinstance(choices, list) and len(choices) > 0:
                            choice = choices[0]
                            if isinstance(choice, dict):
                                # Check for tokens array
                                if "tokens" in choice:
                                    tokens = choice["tokens"]
                                    if isinstance(tokens, list) and len(tokens) > 0:
                                        # Join tokens if they're strings
                                        text = " ".join(str(t) for t in tokens)
                                        return self._clean_text(text)
                                # Check for other text fields in choice
                                for field in ["text", "message", "content"]:
                                    if field in choice:
                                        return self._clean_text(str(choice[field]))
                    
                    # Check for direct text fields
                    for field in ["text", "generated_text", "output", "content"]:
                        if field in item:
                            return self._clean_text(str(item[field]))
            
            # Fallback: join list items
            text = " ".join(str(item) for item in output)
            return self._clean_text(text)
        
        else:
            return self._clean_text(str(output))
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and format text to be human-readable and ready to post.
        - Removes "OUTPUT:" prefix if present
        - Strips whitespace
        - Removes extra newlines
        - Cleans up formatting
        """
        if not text:
            return ""
        
        # Remove common prefixes
        text = text.strip()
        prefixes = ["OUTPUT:", "output:", "Response:", "response:"]
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        # Clean up whitespace
        # Replace multiple newlines with single newline
        import re
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Final trim
        return text.strip()
    
    async def generate_hook(self, topic: str, prompt_context: Optional[str] = None) -> str:
        """Generate hook using Phi-2 model"""
        if prompt_context:
            prompt = f"""Generate an engaging hook/introduction for a social media post about: {topic}

Context: {prompt_context}

Create a short, attention-grabbing hook (1-2 sentences) that will make people want to read more."""
        else:
            prompt = f"""Generate an engaging hook/introduction for a social media post about: {topic}

Create a short, attention-grabbing hook (1-2 sentences) that will make people want to read more."""
        
        return await self.generate_text(prompt, model_type="phi2", max_tokens=150, temperature=0.8)
    
    async def generate_caption(self, topic: str, hook: str, prompt_context: Optional[str] = None) -> str:
        """Generate caption using Mistral 7B model"""
        logger.info("Starting Mistral caption generation (this may take longer due to model size and queue times)...")
        if prompt_context:
            prompt = f"""Generate the main body/caption for a social media post.

Topic: {topic}
Hook: {hook}
Additional context: {prompt_context}

Create an engaging, informative caption (3-5 sentences) that expands on the hook and provides valuable information."""
        else:
            prompt = f"""Generate the main body/caption for a social media post.

Topic: {topic}
Hook: {hook}

Create an engaging, informative caption (3-5 sentences) that expands on the hook and provides valuable information."""
        
        return await self.generate_text(prompt, model_type="mistral", max_tokens=300, temperature=0.7)
    
    async def generate_cta(self, topic: str, hook: str, caption: str, prompt_context: Optional[str] = None) -> str:
        """Generate CTA using Phi-2 model"""
        if prompt_context:
            prompt = f"""Generate a compelling call-to-action (CTA) for a social media post.

Topic: {topic}
Hook: {hook}
Caption: {caption}
Additional context: {prompt_context}

Create a short, action-oriented CTA (1 sentence) that encourages engagement, such as asking a question, prompting a click, or inviting comments."""
        else:
            prompt = f"""Generate a compelling call-to-action (CTA) for a social media post.

Topic: {topic}
Hook: {hook}
Caption: {caption}

Create a short, action-oriented CTA (1 sentence) that encourages engagement, such as asking a question, prompting a click, or inviting comments."""
        
        return await self.generate_text(prompt, model_type="phi2", max_tokens=100, temperature=0.8)

