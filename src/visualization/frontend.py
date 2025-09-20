"""
Enhanced LangGraph Workflow Visualization Frontend
Shows live data flow animations between nodes in real-time
"""

# Enhanced HTML template with live data flow animations
VISUALIZATION_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LangGraph Workflow Visualization - Live Data Flow</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
            color: #e0e6ed;
            min-height: 100vh;
            overflow: hidden;
        }
        
        .container {
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            padding: 20px;
            text-align: center;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .header h1 {
            margin: 0;
            color: #64b5f6;
            font-weight: 300;
            font-size: 24px;
        }
        
        .header .subtitle {
            color: #81c784;
            font-size: 14px;
            margin-top: 8px;
            opacity: 0.8;
        }
        
        .controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            background: rgba(255, 255, 255, 0.03);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .visualization-area {
            display: flex;
            flex: 1;
            overflow: hidden;
        }
        
        .graph-container {
            flex: 2;
            position: relative;
            background: radial-gradient(circle at 50% 50%, rgba(100, 181, 246, 0.05) 0%, transparent 50%);
            overflow: hidden;
        }
        
        .info-panel {
            flex: 1;
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            border-left: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            overflow-y: auto;
        }
        
        /* Node Styles with Enhanced Animations */
        .node {
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
        }
        
        .node:hover {
            filter: drop-shadow(0 8px 16px rgba(100, 181, 246, 0.4)) brightness(1.1);
        }
        
        .node rect {
            fill: rgba(255, 255, 255, 0.08);
            stroke: #64b5f6;
            stroke-width: 2;
            rx: 12;
            ry: 12;
            transition: all 0.4s ease;
        }
        
        .node.pending rect { 
            fill: rgba(255, 152, 0, 0.1); 
            stroke: #ff9800;
            box-shadow: 0 0 20px rgba(255, 152, 0, 0.3);
        }
        
        .node.running rect { 
            fill: rgba(33, 150, 243, 0.15); 
            stroke: #2196F3;
            animation: nodeGlow 2s ease-in-out infinite alternate;
            filter: drop-shadow(0 0 20px rgba(33, 150, 243, 0.6));
        }
        
        .node.completed rect { 
            fill: rgba(76, 175, 80, 0.1); 
            stroke: #4caf50;
            box-shadow: 0 0 15px rgba(76, 175, 80, 0.2);
            animation: nodeCompleted 0.5s ease-out;
        }
        
        .node.error rect { 
            fill: rgba(244, 67, 54, 0.1); 
            stroke: #f44336;
            animation: errorPulse 1s ease-in-out infinite;
        }
        
        .node.skipped rect { 
            fill: rgba(158, 158, 158, 0.05); 
            stroke: #616161;
            stroke-dasharray: 5,5;
        }
        
        .node text {
            font-size: 11px;
            text-anchor: middle;
            dominant-baseline: central;
            fill: #e0e6ed;
            pointer-events: none;
            font-weight: 500;
        }
        
        .node .node-status {
            font-size: 9px;
            fill: #b0bec5;
        }
        
        /* Enhanced Edge Styles with Live Data Flow */
        .link {
            fill: none;
            stroke: rgba(255, 255, 255, 0.2);
            stroke-width: 2;
            marker-end: url(#arrowhead);
            transition: all 0.4s ease;
        }
        
        .link.active {
            stroke: #64b5f6;
            stroke-width: 4;
            animation: dataFlow 1.5s linear infinite;
            filter: drop-shadow(0 0 8px #64b5f6);
        }
        
        .link.highlighted {
            stroke: #81c784;
            stroke-width: 3;
            filter: drop-shadow(0 0 6px #81c784);
        }
        
        /* Enhanced Particle Animation for Data Flow */
        .flow-particle {
            fill: #64b5f6;
            r: 4;
            animation: particleFlow 2s linear infinite;
            pointer-events: none;
        }
        
        .flow-particle.incoming {
            fill: #64b5f6;
            filter: drop-shadow(0 0 8px #64b5f6);
        }
        
        .flow-particle.outgoing {
            fill: #81c784;
            filter: drop-shadow(0 0 8px #81c784);
        }
        
        .flow-particle.data {
            fill: #f093fb;
            filter: drop-shadow(0 0 8px #f093fb);
        }
        
        /* Enhanced Data Flow Animations */
        @keyframes dataFlow {
            0% { 
                stroke-dasharray: 8,8; 
                stroke-dashoffset: 0;
                stroke-width: 4;
            }
            50% {
                stroke-width: 6;
                filter: drop-shadow(0 0 12px currentColor);
            }
            100% { 
                stroke-dasharray: 8,8; 
                stroke-dashoffset: 16;
                stroke-width: 4;
            }
        }
        
        @keyframes particleFlow {
            0% { 
                opacity: 0;
                transform: scale(0.5);
            }
            10% { 
                opacity: 1;
                transform: scale(1);
            }
            90% { 
                opacity: 1;
                transform: scale(1);
            }
            100% { 
                opacity: 0;
                transform: scale(0.8);
            }
        }
        
        @keyframes nodeGlow {
            0% { 
                stroke: #2196F3;
                filter: drop-shadow(0 0 10px rgba(33, 150, 243, 0.5));
            }
            100% { 
                stroke: #42a5f5;
                filter: drop-shadow(0 0 20px rgba(33, 150, 243, 0.8));
            }
        }
        
        @keyframes errorPulse {
            0%, 100% { stroke: #f44336; }
            50% { stroke: #ff5722; }
        }
        
        @keyframes nodeCompleted {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        /* Live Execution Indicator */
        .live-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #81c784;
            border-radius: 50%;
            margin-right: 8px;
            animation: liveDot 1.5s ease-in-out infinite;
        }
        
        @keyframes liveDot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
        }
        
        /* Controls and Buttons */
        button {
            padding: 10px 18px;
            border: none;
            border-radius: 6px;
            background: linear-gradient(135deg, #64b5f6 0%, #42a5f5 100%);
            color: white;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(100, 181, 246, 0.3);
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(100, 181, 246, 0.4);
        }
        
        .execution-item {
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-left: 4px solid #64b5f6;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .execution-item:hover {
            background: rgba(255, 255, 255, 0.08);
            transform: translateX(4px);
        }
        
        .execution-item.active {
            background: rgba(100, 181, 246, 0.15);
            border-left-color: #42a5f5;
        }
        
        .execution-item.live {
            border-left-color: #81c784;
            background: rgba(129, 199, 132, 0.1);
            animation: livePulse 2s ease-in-out infinite;
        }
        
        @keyframes livePulse {
            0%, 100% { border-left-color: #81c784; }
            50% { border-left-color: #4caf50; }
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 16px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-pending { background: rgba(255, 152, 0, 0.2); color: #ffb74d; border: 1px solid #ff9800; }
        .status-running { background: rgba(33, 150, 243, 0.2); color: #64b5f6; border: 1px solid #2196F3; }
        .status-completed { background: rgba(76, 175, 80, 0.2); color: #81c784; border: 1px solid #4caf50; }
        .status-error { background: rgba(244, 67, 54, 0.2); color: #e57373; border: 1px solid #f44336; }
        .status-skipped { background: rgba(158, 158, 158, 0.1); color: #9e9e9e; border: 1px solid #616161; }
        
        .zoom-controls {
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .zoom-btn {
            width: 40px;
            height: 40px;
            border: none;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            color: #e0e6ed;
            cursor: pointer;
            font-size: 18px;
            transition: all 0.3s ease;
        }
        
        .zoom-btn:hover {
            background: rgba(100, 181, 246, 0.2);
            transform: scale(1.1);
        }
        
        .node-details {
            margin-top: 20px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .data-section {
            margin: 15px 0;
            padding: 12px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 6px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        .data-section h4 {
            margin: 0 0 8px 0;
            color: #81c784;
            font-size: 12px;
            font-weight: 500;
        }
        
        pre {
            background: rgba(0, 0, 0, 0.3);
            padding: 10px;
            border-radius: 4px;
            font-size: 11px;
            color: #b0bec5;
            overflow-x: auto;
            margin: 5px 0;
        }
        
        .info-panel h3 {
            color: #64b5f6;
            margin-top: 0;
            font-weight: 400;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>LangGraph Workflow Visualization</h1>
            <div class="subtitle">Live Data Flow Animation - Real-time Execution</div>
        </div>
        
        <div class="controls">
            <div>
                <button onclick="refreshData()">🔄 Refresh</button>
                <button onclick="clearExecutions()">🗑️ Clear All</button>
                <button onclick="resetZoom()">🎯 Reset View</button>
                <button onclick="toggleLiveMode()" id="live-mode-btn">⏸️ Pause Live</button>
            </div>
            <div>
                <label>Auto-refresh: <input type="checkbox" id="auto-refresh" checked></label>
                <span style="margin-left: 15px;">
                    <span class="live-indicator"></span>
                    <span id="live-status">Live Mode Active</span>
                </span>
            </div>
        </div>
        
        <div class="visualization-area">
            <div class="graph-container">
                <svg id="workflow-graph"></svg>
                <div class="zoom-controls">
                    <button class="zoom-btn" onclick="zoomIn()">+</button>
                    <button class="zoom-btn" onclick="zoomOut()">−</button>
                    <button class="zoom-btn" onclick="resetZoom()">⌂</button>
                </div>
            </div>
            
            <div class="info-panel">
                <h3>Execution History</h3>
                <div id="executions-list"></div>
                
                <div class="node-details" id="node-details">
                    <h3 id="node-title">Node Details</h3>
                    <div id="node-content">Click on a node to view details</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        class WorkflowVisualizer {
            constructor() {
                this.executions = new Map();
                this.currentExecution = null;
                this.refreshInterval = null;
                this.zoom = null;
                this.liveMode = true;
                this.lastExecutionId = null;
                
                this.initializeVisualization();
                this.startAutoRefresh();
            }

            async startAutoRefresh() {
                await this.refreshData();
                const autoRefreshCheckbox = document.getElementById('auto-refresh');
                
                const refreshLoop = () => {
                    if (autoRefreshCheckbox.checked && this.liveMode) {
                        this.refreshLiveData();
                    }
                    setTimeout(refreshLoop, 500); // Faster refresh for live updates
                };
                
                setTimeout(refreshLoop, 500);
            }

            async refreshLiveData() {
                try {
                    const response = await fetch('/visualization/live');
                    const liveData = await response.json();
                    
                    if (liveData.execution) {
                        const executionId = liveData.execution.id;
                        
                        // Check if this is a new execution
                        if (executionId !== this.lastExecutionId) {
                            this.lastExecutionId = executionId;
                            this.executions.set(executionId, liveData.execution);
                            this.updateExecutionsList();
                        }
                        
                        // Update current execution with live data
                        if (this.currentExecution === executionId) {
                            const previousExecution = this.executions.get(this.currentExecution);
                            this.executions.set(this.currentExecution, liveData.execution);
                            
                            // Animate changes in real-time with data flow
                            if (previousExecution) {
                                this.animateLiveDataFlow(previousExecution, liveData.execution);
                            }
                            
                            this.updateVisualization();
                        }
                        
                        // Auto-select latest execution if none selected
                        if (!this.currentExecution) {
                            this.selectExecution(executionId);
                        }
                        
                        // Update live status
                        this.updateLiveStatus(true);
                    } else {
                        this.updateLiveStatus(false);
                    }
                } catch (error) {
                    console.error('Failed to refresh live data:', error);
                    this.updateLiveStatus(false);
                }
            }

            updateLiveStatus(isActive) {
                const statusElement = document.getElementById('live-status');
                const liveBtn = document.getElementById('live-mode-btn');
                
                if (isActive) {
                    statusElement.textContent = 'Live Mode Active';
                    statusElement.style.color = '#81c784';
                    liveBtn.textContent = '⏸️ Pause Live';
                } else {
                    statusElement.textContent = 'No Active Execution';
                    statusElement.style.color = '#9e9e9e';
                    liveBtn.textContent = '▶️ Resume Live';
                }
            }

            toggleLiveMode() {
                this.liveMode = !this.liveMode;
                const liveBtn = document.getElementById('live-mode-btn');
                
                if (this.liveMode) {
                    liveBtn.textContent = '⏸️ Pause Live';
                    this.updateLiveStatus(true);
                } else {
                    liveBtn.textContent = '▶️ Resume Live';
                    this.updateLiveStatus(false);
                }
            }

            async refreshData() {
                try {
                    const response = await fetch('/visualization/workflow');
                    const data = await response.json();
                    
                    // Update executions and track changes for live animation
                    const previousExecutions = new Map(this.executions);
                    Object.entries(data.executions).forEach(([id, execution]) => {
                        const previousExecution = previousExecutions.get(id);
                        this.executions.set(id, execution);
                        
                        // Trigger live animations for node status changes
                        if (previousExecution) {
                            this.animateLiveDataFlow(previousExecution, execution);
                        }
                    });
                    
                    this.updateExecutionsList();
                    
                    // Auto-select latest execution
                    if (this.executions.size > 0) {
                        const latest = Array.from(this.executions.values())
                            .sort((a, b) => new Date(b.start_time) - new Date(a.start_time))[0];
                        if (!this.currentExecution || this.currentExecution !== latest.id) {
                            this.selectExecution(latest.id);
                        }
                    }
                } catch (error) {
                    console.error('Failed to refresh data:', error);
                }
            }

            initializeVisualization() {
                const container = document.querySelector('.graph-container');
                const width = container.clientWidth;
                const height = container.clientHeight;

                const svg = d3.select('#workflow-graph')
                    .attr('width', width)
                    .attr('height', height);

                // Create zoom behavior
                this.zoom = d3.zoom()
                    .scaleExtent([0.3, 3])
                    .on('zoom', (event) => {
                        svg.select('.zoom-group').attr('transform', event.transform);
                    });

                svg.call(this.zoom);

                // Create main group for zoom/pan
                const g = svg.append('g').attr('class', 'zoom-group');

                // Add arrow marker definitions
                svg.append('defs').append('marker')
                    .attr('id', 'arrowhead')
                    .attr('viewBox', '0 -5 10 10')
                    .attr('refX', 8)
                    .attr('refY', 0)
                    .attr('markerWidth', 6)
                    .attr('markerHeight', 6)
                    .attr('orient', 'auto')
                    .append('path')
                    .attr('d', 'M0,-5L10,0L0,5')
                    .attr('fill', 'rgba(255, 255, 255, 0.6)');

                // Complete workflow structure with all possible paths
                this.workflowStructure = {
                    nodes: [
                        { id: 'analyze_intent', label: 'Intent\\nAnalyzer', x: 150, y: 300, type: 'processor' },
                        { id: 'search_properties', label: 'Property\\nSearch', x: 350, y: 200, type: 'processor' },
                        { id: 'reflect', label: 'Reflection\\nEngine', x: 550, y: 200, type: 'decision' },
                        { id: 'get_available_slots', label: 'Available\\nSlots', x: 350, y: 400, type: 'processor' },
                        { id: 'collect_user_info', label: 'User Info\\nCollection', x: 550, y: 400, type: 'processor' },
                        { id: 'create_calendar_event', label: 'Calendar\\nManager', x: 750, y: 350, type: 'processor' },
                        { id: 'send_sms_confirmation', label: 'SMS\\nSender', x: 750, y: 450, type: 'processor' },
                        { id: 'generate_response', label: 'Response\\nGenerator', x: 950, y: 300, type: 'processor' }
                    ],
                    links: [
                        // From analyze_intent - conditional routing
                        { source: 'analyze_intent', target: 'search_properties', id: 'link1', type: 'conditional' },
                        { source: 'analyze_intent', target: 'get_available_slots', id: 'link2', type: 'conditional' },
                        { source: 'analyze_intent', target: 'generate_response', id: 'link3', type: 'conditional' },
                        
                        // Property search flow
                        { source: 'search_properties', target: 'reflect', id: 'link4', type: 'sequential' },
                        { source: 'reflect', target: 'generate_response', id: 'link5', type: 'conditional' },
                        { source: 'reflect', target: 'search_properties', id: 'link6', type: 'loop' },
                        
                        // Booking flow
                        { source: 'get_available_slots', target: 'collect_user_info', id: 'link7', type: 'sequential' },
                        { source: 'collect_user_info', target: 'create_calendar_event', id: 'link8', type: 'conditional' },
                        { source: 'collect_user_info', target: 'generate_response', id: 'link9', type: 'conditional' },
                        { source: 'create_calendar_event', target: 'send_sms_confirmation', id: 'link10', type: 'conditional' },
                        { source: 'create_calendar_event', target: 'generate_response', id: 'link11', type: 'conditional' },
                        { source: 'send_sms_confirmation', target: 'generate_response', id: 'link12', type: 'sequential' }
                    ]
                };

                this.renderWorkflow();
            }

            renderWorkflow() {
                const svg = d3.select('#workflow-graph .zoom-group');
                
                // Clear existing content
                svg.selectAll('*').remove();
                
                // Render links with enhanced styling
                const linkGroup = svg.append('g').attr('class', 'links');
                
                const links = linkGroup.selectAll('.link')
                    .data(this.workflowStructure.links)
                    .enter()
                    .append('path')
                    .attr('class', 'link')
                    .attr('id', d => d.id)
                    .attr('d', d => {
                        const source = this.workflowStructure.nodes.find(n => n.id === d.source);
                        const target = this.workflowStructure.nodes.find(n => n.id === d.target);
                        if (!source || !target) return '';
                        
                        // Create curved path
                        const dx = target.x - source.x;
                        const dy = target.y - source.y;
                        const dr = Math.sqrt(dx * dx + dy * dy) * 0.3;
                        
                        return `M${source.x},${source.y}A${dr},${dr} 0 0,1 ${target.x},${target.y}`;
                    })
                    .attr('marker-end', 'url(#arrowhead)');

                // Render nodes with enhanced interactivity
                const nodeGroup = svg.append('g').attr('class', 'nodes');
                
                const nodes = nodeGroup.selectAll('.node')
                    .data(this.workflowStructure.nodes)
                    .enter()
                    .append('g')
                    .attr('class', 'node')
                    .attr('transform', d => `translate(${d.x},${d.y})`)
                    .on('click', (event, d) => this.showNodeDetails(d));

                // Add node rectangles
                nodes.append('rect')
                    .attr('width', 120)
                    .attr('height', 60)
                    .attr('x', -60)
                    .attr('y', -30);

                // Add node labels
                nodes.append('text')
                    .attr('class', 'node-label')
                    .attr('dy', '-5')
                    .text(d => d.label.replace('\\n', ' '));

                // Add status indicators
                nodes.append('text')
                    .attr('class', 'node-status')
                    .attr('dy', '15')
                    .text('pending');

                this.updateVisualization();
            }

            animateLiveDataFlow(previousExecution, currentExecution) {
                if (!previousExecution.nodes || !currentExecution.nodes) return;
                
                // Track node status changes and animate data flow
                currentExecution.nodes.forEach(currentNode => {
                    const previousNode = previousExecution.nodes.find(n => n.node_id === currentNode.node_id);
                    
                    // If node status changed, trigger animations
                    if (!previousNode || previousNode.status !== currentNode.status) {
                        this.animateNodeStatusChange(currentNode);
                        
                        // If node just started running, animate data flow from dependencies
                        if (currentNode.status === 'running') {
                            this.animateIncomingDataFlow(currentNode.node_id);
                        }
                        
                        // If node completed, animate data flow to next nodes
                        if (currentNode.status === 'completed') {
                            this.animateOutgoingDataFlow(currentNode.node_id);
                        }
                    }
                });
                
                // Check for new nodes that started running
                currentExecution.nodes.forEach(currentNode => {
                    if (currentNode.status === 'running') {
                        const wasRunning = previousExecution.nodes.find(n => 
                            n.node_id === currentNode.node_id && n.status === 'running'
                        );
                        
                        if (!wasRunning) {
                            // New node started running, animate data flow
                            this.animateIncomingDataFlow(currentNode.node_id);
                        }
                    }
                });
            }

            animateIncomingDataFlow(nodeId) {
                // Find all connections leading to this node
                this.workflowStructure.links.forEach(link => {
                    if (link.target === nodeId) {
                        // Animate data flowing from source to target
                        this.animateDataFlow(link.source, link.target, 'incoming');
                        
                        // Activate the connection with glowing effect
                        const linkElement = d3.select(`#${link.id}`);
                        linkElement
                            .classed('active', true)
                            .style('stroke', '#64b5f6')
                            .style('stroke-width', '4px')
                            .style('filter', 'drop-shadow(0 0 8px #64b5f6)');
                        
                        // Deactivate after animation
                        setTimeout(() => {
                            linkElement
                                .classed('active', false)
                                .style('stroke', 'rgba(255, 255, 255, 0.2)')
                                .style('stroke-width', '2px')
                                .style('filter', 'none');
                        }, 2000);
                    }
                });
            }

            animateOutgoingDataFlow(nodeId) {
                // Find all connections from this node
                this.workflowStructure.links.forEach(link => {
                    if (link.source === nodeId) {
                        // Delay outgoing animation slightly for better visual flow
                        setTimeout(() => {
                            this.animateDataFlow(link.source, link.target, 'outgoing');
                            
                            // Activate the connection
                            const linkElement = d3.select(`#${link.id}`);
                            linkElement
                                .classed('active', true)
                                .style('stroke', '#81c784')
                                .style('stroke-width', '4px')
                                .style('filter', 'drop-shadow(0 0 8px #81c784)');
                            
                            // Deactivate after animation
                            setTimeout(() => {
                                linkElement
                                    .classed('active', false)
                                    .style('stroke', 'rgba(255, 255, 255, 0.2)')
                                    .style('stroke-width', '2px')
                                    .style('filter', 'none');
                            }, 2000);
                        }, 500);
                    }
                });
            }

            animateDataFlow(sourceId, targetId, flowType = 'data') {
                const source = this.workflowStructure.nodes.find(n => n.id === sourceId);
                const target = this.workflowStructure.nodes.find(n => n.id === targetId);
                
                if (!source || !target) return;

                // Create multiple animated particles for better visual effect
                const particleCount = flowType === 'incoming' ? 3 : 2;
                
                for (let i = 0; i < particleCount; i++) {
                    setTimeout(() => {
                        this.createFlowParticle(source, target, flowType, i);
                    }, i * 200); // Stagger particles
                }
            }

            createFlowParticle(source, target, flowType, index) {
                const svg = d3.select('#workflow-graph .zoom-group');
                
                // Create particle with different styles based on flow type
                const particle = svg.append('circle')
                    .attr('class', `flow-particle ${flowType}`)
                    .attr('r', flowType === 'incoming' ? 5 : 4)
                    .attr('cx', source.x)
                    .attr('cy', source.y);

                // Add glow effect
                particle.style('filter', 'drop-shadow(0 0 6px currentColor)');

                // Animate particle along path with easing
                particle.transition()
                    .duration(1500 + (index * 100))
                    .ease(d3.easeCubicInOut)
                    .attr('cx', target.x)
                    .attr('cy', target.y)
                    .style('opacity', 0.8)
                    .on('end', () => {
                        // Create ripple effect at target
                        this.createRippleEffect(target.x, target.y, flowType);
                        particle.remove();
                    });
            }

            createRippleEffect(x, y, flowType) {
                const svg = d3.select('#workflow-graph .zoom-group');
                
                // Create expanding circle ripple
                const ripple = svg.append('circle')
                    .attr('cx', x)
                    .attr('cy', y)
                    .attr('r', 0)
                    .style('fill', 'none')
                    .style('stroke', flowType === 'incoming' ? '#64b5f6' : '#81c784')
                    .style('stroke-width', '2px')
                    .style('opacity', '0.8');

                // Animate ripple expansion
                ripple.transition()
                    .duration(800)
                    .ease(d3.easeOutQuad)
                    .attr('r', 30)
                    .style('opacity', 0)
                    .on('end', () => ripple.remove());
            }

            animateNodeStatusChange(node) {
                const nodeElement = d3.select(`.node`).filter(d => d.id === node.node_id);
                
                // Add pulsing effect for running nodes
                if (node.status === 'running') {
                    nodeElement.select('rect')
                        .transition()
                        .duration(500)
                        .style('stroke-width', '4px')
                        .transition()
                        .duration(500)
                        .style('stroke-width', '2px');
                }
                
                // Flash effect for completed nodes
                if (node.status === 'completed') {
                    nodeElement.select('rect')
                        .transition()
                        .duration(300)
                        .style('fill-opacity', 0.8)
                        .transition()
                        .duration(300)
                        .style('fill-opacity', 0.3);
                }
            }

            updateVisualization() {
                if (!this.currentExecution) return;

                const execution = this.executions.get(this.currentExecution);
                if (!execution) return;

                // Update node statuses with enhanced animations
                execution.nodes.forEach(nodeExec => {
                    const nodeElement = d3.select(`.node`).filter(d => d.id === nodeExec.node_id);
                    
                    // Update node class and status text
                    nodeElement
                        .attr('class', `node ${nodeExec.status}`)
                        .select('.node-status')
                        .text(nodeExec.status);

                    // Enhanced animations for different statuses
                    if (nodeExec.status === 'running') {
                        // Animate data flow for running nodes
                        this.workflowStructure.links.forEach(link => {
                            if (link.target === nodeExec.node_id) {
                                this.animateDataFlow(link.source, link.target, 'incoming');
                            }
                        });
                        
                        // Add pulsing effect to running node
                        nodeElement.select('rect')
                            .transition()
                            .duration(1000)
                            .style('stroke-width', '4px')
                            .style('filter', 'drop-shadow(0 0 15px rgba(33, 150, 243, 0.5))')
                            .transition()
                            .duration(1000)
                            .style('stroke-width', '2px')
                            .style('filter', 'drop-shadow(0 0 8px rgba(33, 150, 243, 0.3))');
                    }
                    
                    if (nodeExec.status === 'completed') {
                        // Flash effect for completed nodes
                        nodeElement.select('rect')
                            .transition()
                            .duration(300)
                            .style('fill-opacity', 0.8)
                            .transition()
                            .duration(300)
                            .style('fill-opacity', 0.3);
                    }
                });

                // Animate connections based on execution flow
                this.animateExecutionConnections(execution);
            }

            animateExecutionConnections(execution) {
                // Find the execution path based on completed nodes
                const completedNodes = execution.nodes.filter(n => n.status === 'completed');
                const runningNodes = execution.nodes.filter(n => n.status === 'running');
                
                // Animate connections between completed nodes
                completedNodes.forEach((node, index) => {
                    if (index > 0) {
                        const prevNode = completedNodes[index - 1];
                        const link = this.workflowStructure.links.find(l => 
                            l.source === prevNode.node_id && l.target === node.node_id
                        );
                        
                        if (link) {
                            // Animate data flow between completed nodes
                            setTimeout(() => {
                                this.animateDataFlow(prevNode.node_id, node.node_id, 'completed');
                            }, index * 300);
                        }
                    }
                });
                
                // Animate connections to running nodes
                runningNodes.forEach(node => {
                    const incomingLinks = this.workflowStructure.links.filter(l => l.target === node.node_id);
                    incomingLinks.forEach(link => {
                        const sourceNode = execution.nodes.find(n => n.node_id === link.source);
                        if (sourceNode && sourceNode.status === 'completed') {
                            // Animate data flow from completed source to running target
                            this.animateDataFlow(link.source, link.target, 'incoming');
                        }
                    });
                });
            }

            showNodeDetails(node) {
                if (!this.currentExecution) return;

                const execution = this.executions.get(this.currentExecution);
                const nodeExec = execution?.nodes.find(n => n.node_id === node.id);

                document.getElementById('node-title').textContent = node.label.replace('\\n', ' ');
                
                let content = `
                    <div class="data-section">
                        <h4>Node Information</h4>
                        <p><strong>ID:</strong> ${node.id}</p>
                        <p><strong>Type:</strong> ${node.type}</p>
                        <p><strong>Status:</strong> <span class="status-badge status-${nodeExec?.status || 'pending'}">${nodeExec?.status || 'pending'}</span></p>
                    </div>
                `;

                if (nodeExec) {
                    content += `
                        <div class="data-section">
                            <h4>Input Data</h4>
                            <pre>${JSON.stringify(nodeExec.input_data || {}, null, 2)}</pre>
                        </div>
                        <div class="data-section">
                            <h4>Output Data</h4>
                            <pre>${JSON.stringify(nodeExec.output_data || {}, null, 2)}</pre>
                        </div>
                    `;

                    if (nodeExec.error_message) {
                        content += `
                            <div class="data-section">
                                <h4>Error</h4>
                                <pre style="color: #e57373;">${nodeExec.error_message}</pre>
                            </div>
                        `;
                    }

                    if (nodeExec.duration_ms) {
                        content += `
                            <div class="data-section">
                                <h4>Execution Time</h4>
                                <p>${nodeExec.duration_ms}ms</p>
                            </div>
                        `;
                    }
                }

                document.getElementById('node-content').innerHTML = content;
            }

            selectExecution(executionId) {
                this.currentExecution = executionId;
                
                // Update UI
                document.querySelectorAll('.execution-item').forEach(item => {
                    item.classList.remove('active');
                });
                
                const selectedItem = document.querySelector(`[data-execution-id="${executionId}"]`);
                if (selectedItem) {
                    selectedItem.classList.add('active');
                }

                this.updateVisualization();
            }

            updateExecutionsList() {
                const container = document.getElementById('executions-list');
                const executions = Array.from(this.executions.values())
                    .sort((a, b) => new Date(b.start_time) - new Date(a.start_time));

                container.innerHTML = executions.map(exec => {
                    const isLive = exec.status === 'running';
                    const isActive = exec.id === this.currentExecution;
                    const classes = ['execution-item'];
                    if (isActive) classes.push('active');
                    if (isLive) classes.push('live');
                    
                    return `
                        <div class="${classes.join(' ')}" 
                             data-execution-id="${exec.id}" 
                             onclick="visualizer.selectExecution('${exec.id}')">
                            <div><strong>Query:</strong> ${exec.user_query}</div>
                            <div><small>${new Date(exec.start_time).toLocaleTimeString()}</small></div>
                            <div><span class="status-badge status-${exec.status}">${exec.status}</span></div>
                            ${isLive ? '<div><small style="color: #81c784;">🔄 Live Execution</small></div>' : ''}
                        </div>
                    `;
                }).join('');
            }
        }

        // Global functions for controls
        function refreshData() {
            visualizer.refreshData();
        }

        function clearExecutions() {
            fetch('/visualization/clear', { method: 'POST' })
                .then(() => {
                    visualizer.executions.clear();
                    visualizer.currentExecution = null;
                    visualizer.updateExecutionsList();
                    document.getElementById('node-content').innerHTML = 'Click on a node to view details';
                });
        }

        function toggleLiveMode() {
            visualizer.toggleLiveMode();
        }

        function zoomIn() {
            const svg = d3.select('#workflow-graph');
            svg.transition().call(visualizer.zoom.scaleBy, 1.5);
        }

        function zoomOut() {
            const svg = d3.select('#workflow-graph');
            svg.transition().call(visualizer.zoom.scaleBy, 1 / 1.5);
        }

        function resetZoom() {
            const svg = d3.select('#workflow-graph');
            svg.transition().call(visualizer.zoom.transform, d3.zoomIdentity);
        }

        // Initialize visualizer when page loads
        let visualizer;
        document.addEventListener('DOMContentLoaded', () => {
            visualizer = new WorkflowVisualizer();
        });
    </script>
</body>
</html>
"""
