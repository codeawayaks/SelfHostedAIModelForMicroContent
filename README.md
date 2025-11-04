# Runpod Text Models Integration

A full-stack web application for generating social media posts using Runpod.io's AI models. The system orchestrates multiple model calls to create complete posts with hooks, captions, and CTAs.

## Features

- **Multi-Model Orchestration**: Sequentially calls Phi-2 (Hook/CTA) and Mistral 7B (Caption) models
- **Cost Tracking**: Monitors and displays costs for each generation step (~$0.0005 per post)
- **Full Dashboard**: Modern React dashboard with input forms, output display, and history
- **History Management**: View, filter, and manage past generations
- **Flexible Input**: Support both topic/keywords and full prompt input modes
- **Formatted Output**: Ready-to-use post text with copy-to-clipboard functionality

## Architecture

### Backend (FastAPI)
- FastAPI REST API with async endpoints
- SQLite database for generation history
- Runpod.io API client with OpenAI-compatible endpoints
- Orchestration service for sequential model calls
- Cost tracking and monitoring

### Frontend (Next.js + React)
- Modern dashboard UI with TailwindCSS
- Input form with topic/prompt toggle
- Output display with component previews
- History view with pagination
- Real-time generation status

## Generation Flow

1. **Hook Generation** (Phi-2, ~2s, $0.00011): Creates engaging introduction
2. **Caption Generation** (Mistral 7B, ~5s, $0.00028): Generates main body text
3. **CTA Generation** (Phi-2, ~1s, $0.00006): Creates call-to-action
4. **Merge & Output** (~1s, $0.00005): Combines all components into final post

**Total Cost**: ~$0.0005 per post

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 18+
- Runpod.io account with deployed models

### Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   
   Create or edit your `.env` file and add your Runpod.io credentials:
   ```
   RUNPOD_API_KEY=your_runpod_api_key_here
   RUNPOD_PHI2_ENDPOINT_ID=your_phi2_endpoint_id_here
   RUNPOD_MISTRAL_ENDPOINT_ID=your_mistral_endpoint_id_here
   DATABASE_URL=sqlite:///./generations.db
   ```

3. **Run the backend server:**
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`
   API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure API URL (optional):**
   Create `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Run the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## Runpod.io Setup

See [RUNPOD_SETUP.md](./RUNPOD_SETUP.md) for detailed instructions on deploying models on Runpod.io.

## Usage

### Generate a Post

1. Open the dashboard in your browser
2. Choose input type: **Topic/Keywords** or **Full Prompt**
3. Enter your content
4. Click **Generate Post**
5. View the generated components and final output
6. Copy the formatted post to clipboard

### View History

1. Navigate to the **History** tab
2. Browse past generations
3. Click **View** to see full details
4. Click **Delete** to remove a generation

## API Endpoints

### Generate Post
```
POST /api/generate
Content-Type: application/json

{
  "input_type": "topic" | "prompt",
  "input_content": "your input here"
}
```

### Get History
```
GET /api/history?page=1&page_size=10
```

### Get Specific Generation
```
GET /api/history/{id}
```

### Delete Generation
```
DELETE /api/history/{id}
```

## Cost Breakdown

- Hook Generation: $0.00011
- Caption Generation: $0.00028
- CTA Generation: $0.00006
- Merge & Output: $0.00005
- **Total**: ~$0.0005 per post

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration management
│   ├── models/
│   │   ├── database.py      # Database models
│   │   └── schemas.py       # Pydantic schemas
│   ├── services/
│   │   ├── runpod_client.py # Runpod.io API client
│   │   ├── orchestration.py # Generation orchestration
│   │   └── cost_tracker.py  # Cost tracking
│   └── routers/
│       ├── generation.py    # Generation endpoints
│       └── history.py       # History endpoints
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js app directory
│   │   ├── components/      # React components
│   │   └── services/        # API client
│   └── package.json
├── requirements.txt
└── README.md
```

## Development

### Backend Development
```bash
# Run with auto-reload
uvicorn backend.main:app --reload

# Run with custom port
uvicorn backend.main:app --port 8001
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Database Migration
The database is automatically initialized on first run. To reset:
```bash
rm generations.db
# Restart the backend server
```

## Troubleshooting

### Backend Issues

1. **Database errors**: Ensure SQLite is available and the database file is writable
2. **Runpod API errors**: Verify your API key and endpoint IDs in `.env`
3. **Import errors**: Ensure you're running from the project root directory

### Frontend Issues

1. **API connection errors**: Check that the backend is running and `NEXT_PUBLIC_API_URL` is correct
2. **Build errors**: Run `npm install` again to ensure all dependencies are installed

### Runpod.io Issues

- Verify endpoint IDs are correct
- Check that endpoints are active and running
- Ensure API key has proper permissions
- Review Runpod.io logs for model-specific errors

## License

This project is open source and available under the MIT License.

