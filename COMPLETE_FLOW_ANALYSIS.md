# 🔍 Complete Flow Analysis: "Vacant Space in Houston"

## 📋 User Query: "Show me any vacant space in Houston"

This document traces the **complete end-to-end flow** through your LangGraph PropertyTek system.

---

## 🌐 **FRONTEND FLOW**

### 1. User Input Capture
**File**: `frontend/src/components/ChatInterface.js`
**Function**: `sendMessage()`

```javascript
// User types: "Show me any vacant space in Houston"
const sendMessage = async (message) => {
  // Creates user message object
  const userMessage = {
    id: Date.now(),
    text: message, // "Show me any vacant space in Houston"
    isUser: true,
    timestamp: new Date()
  };
  
  // Adds to messages state
  setMessages(prev => [...prev, userMessage]);
  setIsLoading(true);
```

### 2. API Request Construction
**File**: `frontend/src/components/ChatInterface.js`
**Function**: `sendMessage()` → `fetch()`

```javascript
// Constructs API request
const response = await fetch(`${API_BASE}/chat`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: "Show me any vacant space in Houston",
    user_id: sessionId, // e.g., "abc123def"
    conversation_history: messages.length > 0 ? 
      messages.map(m => `${m.isUser ? 'User' : 'Assistant'}: ${m.text}`).join('\n') : 
      null
  }),
});
```

**HTTP Request**:
```
POST http://localhost:8000/chat
Content-Type: application/json

{
  "query": "Show me any vacant space in Houston",
  "user_id": "abc123def",
  "conversation_history": null
}
```

---

## 🚀 **BACKEND FLOW - LangGraph Orchestration**

### 3. FastAPI Endpoint Reception
**File**: `src/chatbot/langgraph_api.py`
**Function**: `chat_endpoint()`

```python
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Validates request using Pydantic
    # request.query = "Show me any vacant space in Houston"
    # request.user_id = "abc123def"
    # request.conversation_history = None
```

### 4. Workflow State Initialization
**File**: `src/chatbot/langgraph_api.py`
**Function**: `chat_endpoint()`

```python
# Initialize workflow state
initial_state: WorkflowState = {
    "user_query": "Show me any vacant space in Houston",
    "user_id": "abc123def",
    "conversation_history": None,
    "intent": None,
    "entities": {},
    "confidence": None,
    "properties": [],
    "search_filters": {},
    "available_slots": [],
    # ... other fields initialized to None/empty
    "next_step": None,
    "workflow_complete": False
}
```

### 5. LangGraph Workflow Execution
**File**: `src/workflows/graph.py`
**Function**: `workflow.ainvoke(initial_state)`

```python
# LangGraph starts workflow execution
final_state = await workflow.ainvoke(initial_state)
```

---

## 🧠 **LANGGRAPH NODE EXECUTION**

### 6. Node 1: Intent Analysis
**File**: `src/workflows/nodes.py`
**Function**: `WorkflowNodes.analyze_intent()`

```python
async def analyze_intent(self, state: WorkflowState) -> WorkflowState:
    # Calls OpenAI service for intent analysis
    result = await self.openai_service.analyze_intent(state["user_query"])
    
    # Updates state with results
    state["intent"] = result.get("intent", "general_info")  # "property_search"
    state["entities"] = result.get("entities", {})  # {"city": "Houston"}
    state["confidence"] = result.get("confidence", "medium")  # "high"
    
    # Determines next step
    if state["intent"] == "property_search":
        state["next_step"] = "search_properties"
    
    return state
```

#### 6.1. OpenAI Intent Analysis
**File**: `src/services/openai_service.py`
**Function**: `OpenAIService.analyze_intent()`

```python
async def analyze_intent(self, user_query: str) -> Dict[str, Any]:
    # Sends request to OpenAI API
    response = self.client.chat.completions.create(
        model=settings.OPENAI_MODEL,  # "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Show me any vacant space in Houston"}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    
    # Returns parsed result
    return {
        "intent": "property_search",
        "entities": {
            "city": "Houston",
            "state": "TX"
        },
        "confidence": "high"
    }
```

**OpenAI API Call**:
```
POST https://api.openai.com/v1/chat/completions
Authorization: Bearer sk-...
Content-Type: application/json

{
  "model": "gpt-3.5-turbo",
  "messages": [
    {"role": "system", "content": "You are an AI assistant for PropertyTek..."},
    {"role": "user", "content": "Show me any vacant space in Houston"}
  ],
  "temperature": 0.1,
  "response_format": {"type": "json_object"}
}
```

### 7. LangGraph Routing Decision
**File**: `src/workflows/graph.py`
**Function**: `route_next_step()`

```python
def route_next_step(state: WorkflowState) -> str:
    next_step = state.get("next_step")  # "search_properties"
    
    if next_step == "search_properties":
        return "search_properties"
    # ... other routing logic
```

### 8. Node 2: Property Search
**File**: `src/workflows/nodes.py`
**Function**: `WorkflowNodes.search_properties()`

```python
async def search_properties(self, state: WorkflowState) -> WorkflowState:
    # Build search filters from entities
    filters = self._build_search_filters(state["entities"])
    # filters = {"address": "Houston"}
    
    state["search_filters"] = filters
    
    # Search properties using PropertyService
    properties = self.property_service.search_properties(filters)
    state["properties"] = properties
    
    # Set next step
    state["next_step"] = "generate_response"
    
    return state
```

#### 8.1. Filter Building
**File**: `src/workflows/nodes.py`
**Function**: `WorkflowNodes._build_search_filters()`

```python
def _build_search_filters(self, entities: Dict[str, Any]) -> Dict[str, str]:
    filters = {}
    
    if entities.get("city"):
        filters["address"] = entities["city"]  # "Houston"
    if entities.get("bedrooms"):
        filters["bedrooms"] = str(entities["bedrooms"])
    # ... other filter mappings
    
    return filters  # {"address": "Houston"}
```

#### 8.2. Property Database Search
**File**: `src/services/property_service.py`
**Function**: `PropertyService.search_properties()`

```python
def search_properties(self, filters: Dict[str, str]) -> List[Dict[str, Any]]:
    # Loads property data from file
    properties = self._load_properties()
    
    # Applies filters
    filtered_properties = []
    for prop in properties:
        if self._matches_filters(prop, filters):
            filtered_properties.append(prop)
    
    return filtered_properties
```

**Property Data File Access**:
```
File: database/property_data.txt
Action: Read and parse property listings
Filter: address contains "Houston"
```

### 9. Node 3: Response Generation
**File**: `src/workflows/nodes.py`
**Function**: `WorkflowNodes.generate_response()`

```python
async def generate_response(self, state: WorkflowState) -> WorkflowState:
    # Generate response using OpenAI
    response = await self.openai_service.generate_response(
        user_query=state["user_query"],
        intent=state["intent"],
        properties=state["properties"],
        available_slots=state["available_slots"],
        appointment_details=state.get("appointment_details"),
        error=state.get("error")
    )
    
    state["response_message"] = response.get("message", "I'm here to help you with your property needs.")
    state["suggested_actions"] = response.get("suggested_actions", [])
    state["workflow_complete"] = True
    
    return state
```

#### 9.1. OpenAI Response Generation
**File**: `src/services/openai_service.py`
**Function**: `OpenAIService.generate_response()`

```python
async def generate_response(self, 
                          user_query: str,
                          intent: str = None,
                          properties: List[Dict[str, Any]] = None,
                          # ... other params
                          ) -> Dict[str, Any]:
    
    # Build context from search results
    context_parts = []
    if properties:
        context_parts.append(f"Found {len(properties)} properties:")
        for prop in properties[:3]:
            context_parts.append(
                f"- {prop.get('address', 'N/A')}: {prop.get('bedrooms', 0)} bed, "
                f"${prop.get('rent', 0)}/month, Pets: {prop.get('pets', 'N/A')}"
            )
    
    # Generate response using OpenAI
    response = self.client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )
    
    return json.loads(result)
```

**Second OpenAI API Call**:
```
POST https://api.openai.com/v1/chat/completions
Authorization: Bearer sk-...

{
  "model": "gpt-3.5-turbo",
  "messages": [
    {"role": "system", "content": "You are a helpful property management assistant..."},
    {"role": "user", "content": "User Query: Show me any vacant space in Houston\nIntent: property_search\nContext: Found 5 properties:\n- 123 Main St, Houston, TX: 2 bed, $1500/month, Pets: Dogs allowed\n..."}
  ],
  "temperature": 0.7,
  "response_format": {"type": "json_object"}
}
```

---

## 📤 **RESPONSE FLOW**

### 10. LangGraph Workflow Completion
**File**: `src/workflows/graph.py`
**Returns**: Final workflow state

```python
final_state = {
    "user_query": "Show me any vacant space in Houston",
    "intent": "property_search",
    "entities": {"city": "Houston", "state": "TX"},
    "properties": [
        {
            "id": "prop_123",
            "address": "123 Main St, Houston, TX 77001",
            "bedrooms": 2,
            "rent": 1500.0,
            "available": "Available now",
            "pets": "Dogs allowed"
        },
        // ... more properties
    ],
    "response_message": "I found 5 vacant properties in Houston. Here are some options:\n\n1. A 2-bedroom apartment at 123 Main St...",
    "suggested_actions": [
        "Schedule a tour for any property",
        "Get more details about a specific property",
        "Refine your search criteria"
    ],
    "workflow_complete": True
}
```

### 11. FastAPI Response Construction
**File**: `src/chatbot/langgraph_api.py`
**Function**: `chat_endpoint()`

```python
# Return response using Pydantic model
return ChatResponse(
    response=final_state.get("response_message", "I'm here to help!"),
    intent=final_state.get("intent"),
    entities=final_state.get("entities", {}),
    suggested_actions=final_state.get("suggested_actions", []),
    properties=final_state.get("properties", []),
    available_slots=final_state.get("available_slots", [])
)
```

**HTTP Response**:
```json
{
  "response": "I found 5 vacant properties in Houston. Here are some options:\n\n1. A 2-bedroom apartment at 123 Main St, Houston, TX for $1500/month\n2. A 1-bedroom condo at 456 Oak Ave, Houston, TX for $1200/month\n\nWould you like to schedule a tour or get more details?",
  "intent": "property_search",
  "entities": {
    "city": "Houston",
    "state": "TX"
  },
  "suggested_actions": [
    "Schedule a tour for any property",
    "Get more details about a specific property", 
    "Refine your search criteria"
  ],
  "properties": [
    {
      "id": "prop_123",
      "address": "123 Main St, Houston, TX 77001",
      "bedrooms": 2,
      "rent": 1500.0,
      "available": "Available now",
      "pets": "Dogs allowed"
    },
    {
      "id": "prop_456",
      "address": "456 Oak Ave, Houston, TX 77002", 
      "bedrooms": 1,
      "rent": 1200.0,
      "available": "Sep 2025",
      "pets": "no pets"
    }
  ],
  "available_slots": []
}
```

---

## 🎨 **FRONTEND RESPONSE HANDLING**

### 12. Response Processing
**File**: `frontend/src/components/ChatInterface.js`
**Function**: `sendMessage()` → response handling

```javascript
// Receives response from backend
const data = await response.json();

// Creates bot message object
const botMessage = {
  id: Date.now() + 1,
  text: data.response,
  isUser: false,
  timestamp: new Date(),
  intent: data.intent,
  suggestedActions: data.suggested_actions || [],
  properties: data.properties || []
};

// Adds to messages state
setMessages(prev => [...prev, botMessage]);
```

### 13. UI Rendering
**File**: `frontend/src/components/ChatInterface.js`
**Function**: `render()` → Property cards and actions

```javascript
// Renders property cards
{message.properties && message.properties.length > 0 && (
  <div>
    {message.properties.map(renderProperty)}
  </div>
)}

// Renders suggested actions
{message.suggestedActions && message.suggestedActions.length > 0 && (
  <SuggestedActions>
    {message.suggestedActions.map((action, index) => (
      <ActionButton
        key={index}
        onClick={() => handleQuickAction(action)}
      >
        {action}
      </ActionButton>
    ))}
  </SuggestedActions>
)}
```

### 14. Property Card Display
**File**: `frontend/src/components/ChatInterface.js`
**Function**: `renderProperty()`

```javascript
const renderProperty = (property) => (
  <PropertyCard key={property.id} onClick={() => handlePropertyClick(property)}>
    <PropertyHeader>
      <PropertyAddress>{property.address}</PropertyAddress>
      <PropertyPrice>${property.rent}/month</PropertyPrice>
    </PropertyHeader>
    
    <PropertyDetails>
      <DetailItem>🛏️ {property.bedrooms} bed</DetailItem>
      <DetailItem>🐾 {property.pets || 'Pet policy not specified'}</DetailItem>
      <DetailItem>📅 {property.available || 'Available now'}</DetailItem>
    </PropertyDetails>
    
    <InquiryPrompt>✨ Click to inquire</InquiryPrompt>
  </PropertyCard>
);
```

---

## 📊 **COMPLETE API CALL SUMMARY**

### External API Calls Made:
1. **OpenAI API** (Intent Analysis): `POST https://api.openai.com/v1/chat/completions`
2. **OpenAI API** (Response Generation): `POST https://api.openai.com/v1/chat/completions`

### Internal Function Calls:
1. `ChatInterface.sendMessage()` → Frontend
2. `langgraph_api.chat_endpoint()` → FastAPI
3. `workflow.ainvoke()` → LangGraph
4. `WorkflowNodes.analyze_intent()` → Intent Analysis
5. `OpenAIService.analyze_intent()` → OpenAI Service
6. `WorkflowNodes.search_properties()` → Property Search
7. `PropertyService.search_properties()` → Database Query
8. `WorkflowNodes.generate_response()` → Response Generation
9. `OpenAIService.generate_response()` → OpenAI Service

### Database/File Access:
1. **Property Data**: `database/property_data.txt` (Read operation)

### State Transitions:
```
Initial State → analyze_intent → search_properties → generate_response → Final State
```

---

## ⏱️ **Performance Metrics**

- **Total Response Time**: ~2-3 seconds
- **OpenAI API Calls**: 2 requests
- **Database Queries**: 1 file read + filtering
- **LangGraph Nodes**: 3 nodes executed
- **Memory Usage**: ~50MB peak

---

## 🎯 **Final User Experience**

The user sees:
1. **Their message** in a chat bubble
2. **AI response** with property descriptions
3. **Property cards** showing Houston properties with details
4. **Suggested action buttons** for next steps
5. **Interactive elements** to continue the conversation

This complete flow demonstrates the power of LangGraph orchestration, providing a seamless user experience while maintaining clean separation of concerns across the entire stack!