# Runpod.io Setup Guide

This guide will walk you through deploying Phi-2 and Mistral 7B models on Runpod.io and configuring them for use with this application.

## Prerequisites

- Runpod.io account ([sign up here](https://www.runpod.io/))
- API key from Runpod.io dashboard

## Step 1: Get Your API Key

1. Log in to your Runpod.io account
2. Navigate to **Settings** → **API Keys**
3. Generate a new API key or copy an existing one
4. Save this key for use in your `.env` file

## Step 2: Deploy Phi-2 Model

### Option A: Using Serverless Endpoints (Recommended)

1. Go to **Serverless** → **Endpoints** in the Runpod dashboard
2. Click **Create Endpoint**
3. Configure the endpoint:
   - **Template**: Select a vLLM template (e.g., "RunPod PyTorch")
   - **Model**: Enter `microsoft/Phi-2` or search for Phi-2
   - **Container Disk**: At least 20GB
   - **GPU Type**: Select based on your needs (e.g., RTX 4090, A100)
   - **Max Workers**: Set to 1-2 for cost efficiency
4. Click **Deploy**
5. Wait for deployment to complete (usually 5-10 minutes)
6. Copy the **Endpoint ID** (visible in the endpoint details)

### Option B: Using Existing Pod

1. Go to **Pods** → **Create Pod**
2. Select a GPU (e.g., RTX 4090)
3. Choose a template with PyTorch/vLLM
4. After the pod starts, deploy Phi-2 model manually
5. Note: This requires more setup but gives you more control

## Step 3: Deploy Mistral 7B Model

1. Follow the same steps as Phi-2 deployment
2. Use model identifier: `mistralai/Mistral-7B-Instruct-v0.1`
3. Ensure container disk is at least 30GB (Mistral 7B is larger)
4. Copy the **Endpoint ID** for Mistral

## Step 4: Verify Endpoint Configuration

### Check Endpoint Status

1. Go to **Serverless** → **Endpoints**
2. Verify both endpoints show **"Active"** status
3. Note the endpoint IDs

### Test Endpoint (Optional)

You can test the endpoints using the Runpod.io API or OpenAI-compatible client:

```bash
curl -X POST "https://api.runpod.ai/v2/{your_pod_endpoint_id_here}/openai/v1/chat/completions" \
  -H "Authorization: Bearer {api_key}
" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "microsoft/Phi-2",
    "messages": [{"role": "user", "content": "Hello, world!"}],
    "max_tokens": 100
  }'



## Step 5: Configure Application

1. Open your `.env` file
2. Add the configuration:

```env
RUNPOD_API_KEY=your_api_key_here
RUNPOD_PHI2_ENDPOINT_ID=your_phi2_endpoint_id_here
RUNPOD_MISTRAL_ENDPOINT_ID=your_mistral_endpoint_id_here
```

## Step 6: Model Configuration

### Phi-2 Endpoint

- **Model Name**: `microsoft/Phi-2` or `Phi-2`
- **Use Case**: Hook generation and CTA generation
- **Recommended Settings**:
  - Max tokens: 150-200 for hooks, 100 for CTAs
  - Temperature: 0.7-0.8

### Mistral 7B Endpoint

- **Model Name**: `mistralai/Mistral-7B-Instruct-v0.1` or `Mistral-7B-Instruct-v0.1`
- **Use Case**: Caption generation
- **Recommended Settings**:
  - Max tokens: 300-400
  - Temperature: 0.7

## API Endpoint Format

Runpod.io uses OpenAI-compatible API endpoints. The format is:

```
https://api.runpod.ai/v2/{ENDPOINT_ID}/openai/v1/chat/completions
```

The application automatically constructs these URLs using your endpoint IDs.

## Cost Considerations

### Serverless Endpoints

- **Idle Time**: No cost when not in use
- **Active Time**: Pay per second when processing requests
- **Cold Start**: First request may take longer (model loading)

### Estimated Costs

Based on the provided metrics:
- Hook Generation (Phi-2): ~2s, $0.00011
- Caption Generation (Mistral 7B): ~5s, $0.00028
- CTA Generation (Phi-2): ~1s, $0.00006
- Total: ~$0.0005 per post

**Note**: Actual costs may vary based on:
- GPU type selected
- Model loading times
- Request complexity
- Runpod.io pricing changes

## Troubleshooting

### Endpoint Not Responding

1. **Check Status**: Verify endpoint is "Active" in dashboard
2. **Check Logs**: Review endpoint logs for errors
3. **Test Directly**: Use curl or Postman to test the endpoint
4. **Verify API Key**: Ensure API key is correct and has permissions

### Model Not Found

1. **Verify Model Name**: Check the exact model identifier in Runpod
2. **Check Template**: Ensure the template supports the model
3. **Review Deployment**: Redeploy if model failed to load

### Cold Start Delays

- First request after idle period may take 30-60 seconds
- Subsequent requests are faster
- Consider keeping endpoints warm for production use

### Rate Limiting

- Runpod.io may have rate limits on free tier
- Upgrade plan if you hit limits
- Implement retry logic in the application

## Alternative: Using Custom Models

If you want to use different models or versions:

1. Deploy the model on Runpod.io
2. Note the model name/identifier
3. Update `backend/services/runpod_client.py`:
   - Change `model_name` in `generate_text()` method
   - Adjust prompt templates if needed

## Production Recommendations

1. **Monitor Costs**: Set up Runpod.io billing alerts
2. **Optimize Workers**: Adjust max workers based on traffic
3. **Error Handling**: Implement retry logic for transient failures
4. **Caching**: Consider caching similar requests to reduce costs
5. **Load Testing**: Test endpoints under expected load

## Additional Resources

- [Runpod.io Documentation](https://docs.runpod.io/)
- [Runpod Serverless Guide](https://docs.runpod.io/serverless)
- [OpenAI API Compatibility](https://docs.runpod.io/serverless/workers/vllm/openai-compatibility)
- [Runpod Community](https://discord.gg/runpod)

## Support

For Runpod.io specific issues:
- Check Runpod.io documentation
- Contact Runpod.io support
- Visit Runpod.io Discord community

For application issues, refer to the main [README.md](./README.md).

