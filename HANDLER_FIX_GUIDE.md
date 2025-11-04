# Runpod Handler Code Fix Guide

## Problem
Your Runpod endpoint handler has a Pydantic validation error. The `ErrorResponse` model requires an `error` field, but the handler only provides `message` and `code`.

## Finding Your Handler Code

1. **If you deployed custom handler code:**
   - Check your local files where you prepared the handler
   - Or download from Runpod endpoint settings

2. **If using a Runpod template:**
   - The handler code is in the endpoint's container
   - You'll need to modify and redeploy

## Fix the ErrorResponse Model

### Option 1: Make 'error' field optional (Recommended)

In `/src/utils.py`, find the `ErrorResponse` class and update it:

```python
from pydantic import BaseModel
from typing import Optional

# BEFORE (broken):
class ErrorResponse(BaseModel):
    error: str  # Required field
    message: str
    code: int

# AFTER (fixed):
class ErrorResponse(BaseModel):
    error: Optional[str] = None  # Make it optional
    message: str
    code: int
```

### Option 2: Always provide 'error' field

In `/src/utils.py`, find the `create_error_response` function and update it:

```python
# BEFORE (broken):
def create_error_response(message: str, code: int = 400):
    return ErrorResponse(message=message, code=code)

# AFTER (fixed):
def create_error_response(message: str, code: int = 400):
    return ErrorResponse(
        error=message,      # Add this field
        message=message,
        code=code
    )
```

## Fix in engine.py

In `/src/engine.py` around line 107, you're calling `create_error_response`. Make sure it's using the fixed version:

```python
# In your generate function, when catching exceptions:
try:
    # ... your generation code ...
except Exception as e:
    yield {"error": create_error_response(str(e)).model_dump()}
```

## Complete Example Fix

Here's what your `/src/utils.py` should look like:

```python
from pydantic import BaseModel
from typing import Optional

class ErrorResponse(BaseModel):
    error: Optional[str] = None  # Optional field
    message: str
    code: int

def create_error_response(message: str, code: int = 400):
    """
    Create an error response that matches the ErrorResponse model.
    """
    return ErrorResponse(
        error=message,      # Provide error field
        message=message,    # Provide message field
        code=code          # Provide code field
    )
```

## Redeploying the Fix

1. **If using Runpod's web interface:**
   - Go to your endpoint settings
   - Update the handler code
   - Redeploy the endpoint

2. **If using Runpod SDK/CLI:**
   ```bash
   # Update your handler files locally
   # Then redeploy
   runpod deploy
   ```

3. **If using Docker/container:**
   - Update the handler code in your container
   - Rebuild and redeploy

## Testing the Fix

After redeploying, test with a simple request:
```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -d '{"input":{"prompt":"test"}}'
```

## Root Cause Investigation

After fixing the error handling, you should also investigate why the "EngineCore requestError" is occurring. This might be due to:
1. Invalid request format
2. Missing required parameters
3. Model not properly initialized
4. Resource constraints

Check your endpoint logs for more details about the original error.

## Alternative: Minimal Handler Template

If you want a clean handler template, here's a basic structure:

```python
# handler.py
import runpod
from typing import Dict, Any

def handler(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple handler that processes prompts.
    """
    try:
        input_data = job.get("input", {})
        prompt = input_data.get("prompt", "")
        
        if not prompt:
            return {
                "error": "Prompt is required",
                "message": "Prompt is required",
                "code": 400
            }
        
        # Your model inference here
        # result = your_model.generate(prompt)
        
        return {
            "output": "Generated text here"  # Replace with actual result
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "message": str(e),
            "code": 500
        }

runpod.serverless.start({"handler": handler})
```

This ensures all error responses include both `error` and `message` fields.

