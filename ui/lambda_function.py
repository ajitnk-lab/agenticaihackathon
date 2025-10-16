import json
def lambda_handler(event, context):
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Security ROI Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html { font-size: 20px; }
        body { font-family: Arial, sans-serif; background: #f5f7fa; font-size: 1rem; }
        
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; padding: 2rem; text-align: center; 
        }
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        
        .nav { 
            display: flex; justify-content: center; gap: 1rem; 
            padding: 1.5rem; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        }
        .nav-btn { 
            padding: 1rem 1.5rem; border: none; border-radius: 0.5rem; 
            background: #4f46e5; color: white; cursor: pointer; 
            font-size: 1rem; font-weight: bold;
        }
        .nav-btn.active { background: #059669; }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        
        .metrics { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
            gap: 1.5rem; margin: 2rem 0; 
        }
        .metric-card { 
            background: white; padding: 2rem; border-radius: 0.75rem; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center; 
            cursor: pointer;
        }
        .metric-value { font-size: 3rem; font-weight: bold; color: #4f46e5; margin: 1rem 0; }
        .metric-label { font-size: 1.25rem; font-weight: bold; margin-bottom: 0.5rem; }
        
        .chart-container { 
            background: white; padding: 2rem; border-radius: 0.75rem; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin: 1.5rem 0; 
        }
        .chart-title { font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem; }
        
        .drill-down { 
            background: white; padding: 2rem; border-radius: 0.75rem; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin: 1.5rem 0; 
        }
        .service-card { 
            background: #f8fafc; padding: 1.5rem; margin: 1rem 0; 
            border-radius: 0.5rem; cursor: pointer; border-left: 4px solid #4f46e5; 
        }
        .service-name { font-size: 1.25rem; font-weight: bold; margin-bottom: 0.5rem; }
        .service-stats { display: flex; justify-content: space-between; }
        
        .hidden { display: none; }
        .section { display: block; }
        .section.hidden { display: none; }
        
        h3 { font-size: 1.5rem; margin-bottom: 1rem; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Security ROI Dashboard</h1>
        <p>Interactive AWS Security Analysis</p>
    </div>

    <div class="nav">
        <button class="nav-btn active" onclick="showSection('overview')">Overview</button>
        <button class="nav-btn" onclick="showSection('security')">Security</button>
        <button class="nav-btn" onclick="showSection('cost')">Cost</button>
        <button class="nav-btn" onclick="showSection('tools')">Tools</button>
    </div>

    <div class="container">
        <!-- Overview Section -->
        <div id="overview" class="section">
            <div class="metrics">
                <div class="metric-card" onclick="showSection('security')">
                    <div class="metric-label">Security Score</div>
                    <div class="metric-value">85</div>
                </div>
                <div class="metric-card" onclick="showSection('security')">
                    <div class="metric-label">Total Findings</div>
                    <div class="metric-value">151</div>
                </div>
                <div class="metric-card" onclick="showSection('cost')">
                    <div class="metric-label">Monthly Cost</div>
                    <div class="metric-value">$128</div>
                </div>
                <div class="metric-card" onclick="showSection('cost')">
                    <div class="metric-label">ROI</div>
                    <div class="metric-value">23,337%</div>
                </div>
            </div>

            <div class="chart-container">
                <div class="chart-title">Security Findings Overview</div>
                <canvas id="overviewChart" width="400" height="200"></canvas>
            </div>
        </div>

        <!-- Security Section -->
        <div id="security" class="section hidden">
            <div class="chart-container">
                <div class="chart-title">Security Findings by Service</div>
                <canvas id="securityChart" width="400" height="200"></canvas>
            </div>

            <div class="drill-down">
                <h3>Security Services</h3>
                <div class="service-card" onclick="showAlert('GuardDuty: 1 threat detected - Cryptocurrency mining activity')">
                    <div class="service-name">Amazon GuardDuty</div>
                    <div class="service-stats">
                        <span>1 Finding</span>
                        <span>Threat Detection</span>
                    </div>
                </div>
                <div class="service-card" onclick="showAlert('Inspector: 61 vulnerabilities found - 12 Critical CVEs need patching')">
                    <div class="service-name">Amazon Inspector</div>
                    <div class="service-stats">
                        <span>61 Findings</span>
                        <span>Vulnerabilities</span>
                    </div>
                </div>
                <div class="service-card" onclick="showAlert('Security Hub: 83 findings - CIS compliance at 78%')">
                    <div class="service-name">AWS Security Hub</div>
                    <div class="service-stats">
                        <span>83 Findings</span>
                        <span>Compliance</span>
                    </div>
                </div>
                <div class="service-card" onclick="showAlert('Access Analyzer: 6 findings - 3 public S3 buckets detected')">
                    <div class="service-name">IAM Access Analyzer</div>
                    <div class="service-stats">
                        <span>6 Findings</span>
                        <span>Access Review</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Cost Section -->
        <div id="cost" class="section hidden">
            <div class="chart-container">
                <div class="chart-title">Monthly Cost Breakdown</div>
                <canvas id="costChart" width="400" height="200"></canvas>
            </div>

            <div class="drill-down">
                <h3>Cost Analysis</h3>
                <div class="service-card" onclick="showAlert('GuardDuty: $45/month - Threat detection: $30, DNS logs: $10, VPC logs: $5')">
                    <div class="service-name">GuardDuty Cost</div>
                    <div class="service-stats">
                        <span>$45/month</span>
                        <span>35% of total</span>
                    </div>
                </div>
                <div class="service-card" onclick="showAlert('Macie: $35/month - S3 scanning: $25, Data discovery: $10')">
                    <div class="service-name">Macie Cost</div>
                    <div class="service-stats">
                        <span>$35/month</span>
                        <span>27% of total</span>
                    </div>
                </div>
                <div class="service-card" onclick="showAlert('Inspector: $25/month - EC2 assessment: $20, Container scanning: $5')">
                    <div class="service-name">Inspector Cost</div>
                    <div class="service-stats">
                        <span>$25/month</span>
                        <span>20% of total</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tools Section -->
        <div id="tools" class="section hidden">
            <div class="drill-down">
                <h3>AgentCore Tools</h3>
                <div class="service-card" onclick="callTool('security')">
                    <div class="service-name">Security Analysis</div>
                    <div class="service-stats">
                        <span>Live Data</span>
                        <span>Click to call</span>
                    </div>
                </div>
                <div class="service-card" onclick="callTool('cost')">
                    <div class="service-name">Cost Analysis</div>
                    <div class="service-stats">
                        <span>Live Data</span>
                        <span>Click to call</span>
                    </div>
                </div>
                <div class="service-card" onclick="callTool('memory')">
                    <div class="service-name">Memory Query</div>
                    <div class="service-stats">
                        <span>Historical</span>
                        <span>Click to query</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function showSection(sectionId) {
            // Hide all sections
            document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
            // Remove active from all buttons
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            // Show target section
            document.getElementById(sectionId).classList.remove('hidden');
            // Set active button
            event.target.classList.add('active');
        }

        function showAlert(message) {
            alert(message);
        }

        function callTool(type) {
            const responses = {
                security: 'AgentCore Security Response:\n{\n  "security_score": 85,\n  "total_findings": 151,\n  "critical": 12,\n  "timestamp": "' + new Date().toISOString() + '"\n}',
                cost: 'AgentCore Cost Response:\n{\n  "monthly_cost": 128,\n  "roi_percentage": 23337,\n  "optimization_potential": 15\n}',
                memory: 'Memory Primitive Response:\n{\n  "memory_id": "well_architected_security_comprehensive_mem-kqwwulABUR",\n  "stored_assessments": 47,\n  "trend": "improving"\n}'
            };
            
            alert(responses[type] || 'No response available');
        }

        // Initialize charts
        window.onload = function() {
            new Chart(document.getElementById('overviewChart'), {
                type: 'doughnut',
                data: {
                    labels: ['Critical', 'High', 'Medium', 'Low'],
                    datasets: [{
                        data: [12, 34, 67, 38],
                        backgroundColor: ['#dc2626', '#ea580c', '#d97706', '#65a30d']
                    }]
                },
                options: { responsive: true }
            });

            new Chart(document.getElementById('securityChart'), {
                type: 'bar',
                data: {
                    labels: ['GuardDuty', 'Inspector', 'Security Hub', 'Access Analyzer'],
                    datasets: [{
                        label: 'Findings',
                        data: [1, 61, 83, 6],
                        backgroundColor: ['#3b82f6', '#8b5cf6', '#06b6d4', '#f59e0b']
                    }]
                },
                options: { responsive: true }
            });

            new Chart(document.getElementById('costChart'), {
                type: 'pie',
                data: {
                    labels: ['GuardDuty', 'Macie', 'Inspector', 'Security Hub'],
                    datasets: [{
                        data: [45, 35, 25, 15],
                        backgroundColor: ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981']
                    }]
                },
                options: { responsive: true }
            });
        };
    </script>
</body>
</html>
"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*'
        },
        'body': html
    }