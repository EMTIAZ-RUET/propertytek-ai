# PropertyTek – Texas Rentals Assistant

PropertyTek is a conversational assistant focused on helping renters find properties across Texas. It handles incremental criteria (location, bedrooms, budget, pets) and guides users naturally through search, selection, and booking.

## Environment setup (conda)

Create and activate the `propertyTek` environment:

```bash
conda create -n propertyTek python=3.11 -y
conda activate propertyTek
pip install -r requirements.txt
```

Environment variables (set in shell or your preferred manager):

```bash
export OPENAI_API_KEY="your-key"
```

## Run the backend

```bash
python run_server.py
```

This starts the API with LangGraph workflow entry at `search_properties` to immediately extract search criteria and provide friendly fallbacks.

## Run the frontend

```bash
cd frontend
npm install --no-fund --no-audit
npm start -- --port 3000
```

Then open http://localhost:3000 in your browser.

## Key behavior

- Starts search even if only one field is provided; merges criteria across turns
- Redirects to Texas-only markets; prompts if city is outside Texas
- Guardrails for irrelevant topics; gentle redirection back to property search
- Hides available dates until a property is selected; prevents booking without selection

## Clean project layout

Top-level highlights only:

```
src/
  services/           # OpenAI, property data, sessions
  workflows/          # LangGraph graph + nodes (entry: search)
  main.py             # Backend entry (used by run_server)
frontend/             # React UI
data/properties.json  # Property dataset
config/settings.py    # Configuration (reads env)
```

## Notes

- Dataset is Texas-focused. If a user asks for a non-Texas city, the system offers Houston, Dallas, Austin, or San Antonio.
- Available dates are only shown after a property is selected.
- Booking requires selecting a single property.