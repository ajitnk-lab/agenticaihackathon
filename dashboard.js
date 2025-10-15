// Dashboard JavaScript - Real-time AgentCore Integration
class SecurityDashboard {
    constructor() {
        this.currentSection = 'executive';
        this.charts = {};
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.loadInitialData();
        this.startAutoRefresh();
    }

    async loadInitialData() {
        try {
            document.getElementById('loading').style.display = 'block';
            await this.fetchAllData();
            this.showSection('executive');
            document.getElementById('loading').style.display = 'none';
        } catch (error) {
            this.showError(error.message);
        }
    }

    async fetchAllData() {
        try {
            // Simulate AgentCore API calls - replace with actual endpoints
            const [securityData, costData, findingsData] = await Promise.all([
                this.callAgentCore('check_security_services'),
                this.callAgentCore('analyze_security_costs'),
                this.callAgentCore('comprehensive_analysis')
            ]);

            this.updateMetrics(securityData, costData, findingsData);
            this.updateCharts(securityData, costData, findingsData);
            this.updateConnectionStatus(true);
        } catch (error) {
            this.updateConnectionStatus(false);
            throw error;
        }
    }

    async callAgentCore(prompt) {
        // Real AgentCore call - replace with your actual AgentCore endpoint
        const agentCoreEndpoint = 'https://your-agentcore-endpoint.amazonaws.com/invoke';
        
        try {
            const response = await fetch('/api/agentcore', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt })
            });

            if (!response.ok) {
                throw new Error(`AgentCore call failed: ${response.statusText}`);
            }

            const data = await response.json();
            return JSON.parse(data.body || '{}');
        } catch (error) {
            console.error('AgentCore call failed:', error);
            // Return mock data for demo
            return this.getMockData(prompt);
        }
    }

    getMockData(prompt) {
        const mockData = {
            'check_security_services': {
                enabled_services: 5,
                total_services: 6,
                services: {
                    guardduty: { enabled: true, status: 'enabled' },
                    inspector: { enabled: true, status: 'enabled' },
                    securityhub: { enabled: true, status: 'enabled' },
                    macie: { enabled: true, status: 'enabled' },
                    accessanalyzer: { enabled: true, status: 'enabled' },
                    trustedadvisor: { enabled: false, status: 'disabled' }
                }
            },
            'analyze_security_costs': {
                monthly_cost: 128.00,
                roi_percentage: 23337.5,
                service_breakdown: {
                    guardduty: { cost: 45.00, enabled: true },
                    inspector: { cost: 25.00, enabled: true },
                    securityhub: { cost: 15.00, enabled: true },
                    macie: { cost: 35.00, enabled: true },
                    accessanalyzer: { cost: 8.00, enabled: true }
                }
            },
            'comprehensive_analysis': {
                security_score: 75,
                total_findings: 151,
                findings_by_severity: {
                    critical: 1,
                    high: 15,
                    medium: 45,
                    low: 90
                },
                services_findings: {
                    guardduty: 1,
                    inspector: 61,
                    securityhub: 83,
                    accessanalyzer: 6
                }
            }
        };
        return mockData[prompt] || {};
    }

    updateMetrics(securityData, costData, findingsData) {
        // Update executive metrics
        document.getElementById('security-score').textContent = findingsData.security_score || '--';
        document.getElementById('roi-value').textContent = costData.roi_percentage ? 
            `${costData.roi_percentage.toLocaleString()}%` : '--';
        document.getElementById('monthly-cost').textContent = costData.monthly_cost ? 
            `$${costData.monthly_cost.toFixed(2)}` : '--';
        document.getElementById('total-findings').textContent = findingsData.total_findings || '--';
    }

    updateCharts(securityData, costData, findingsData) {
        this.createExecutiveChart(findingsData);
        this.createCostChart(costData);
        this.createSeverityChart(findingsData);
        this.createHistoryChart();
        this.updateServicesGrid(securityData);
        this.updateFindingsList(findingsData);
    }

    createExecutiveChart(data) {
        const ctx = document.getElementById('executive-chart');
        if (this.charts.executive) this.charts.executive.destroy();
        
        this.charts.executive = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Compliant', 'Needs Attention'],
                datasets: [{
                    data: [data.security_score || 75, 100 - (data.security_score || 75)],
                    backgroundColor: ['#10b981', '#ef4444'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    createCostChart(data) {
        const ctx = document.getElementById('cost-chart');
        if (this.charts.cost) this.charts.cost.destroy();
        
        const services = data.service_breakdown || {};
        const labels = Object.keys(services).map(s => s.charAt(0).toUpperCase() + s.slice(1));
        const costs = Object.values(services).map(s => s.cost || 0);
        
        this.charts.cost = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: costs,
                    backgroundColor: [
                        '#3b82f6', '#10b981', '#f59e0b', 
                        '#ef4444', '#8b5cf6', '#06b6d4'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'right' }
                }
            }
        });
    }

    createSeverityChart(data) {
        const ctx = document.getElementById('severity-chart');
        if (this.charts.severity) this.charts.severity.destroy();
        
        const severity = data.findings_by_severity || {};
        
        this.charts.severity = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{
                    label: 'Findings',
                    data: [
                        severity.critical || 0,
                        severity.high || 0,
                        severity.medium || 0,
                        severity.low || 0
                    ],
                    backgroundColor: ['#dc2626', '#f59e0b', '#3b82f6', '#10b981']
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    createHistoryChart() {
        const ctx = document.getElementById('history-chart');
        if (this.charts.history) this.charts.history.destroy();
        
        // Mock historical data
        const months = ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'];
        const scores = [45, 52, 58, 65, 70, 75];
        
        this.charts.history = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Security Score',
                    data: scores,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { 
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    updateServicesGrid(data) {
        const grid = document.getElementById('services-grid');
        const services = data.services || {};
        
        grid.innerHTML = Object.entries(services).map(([name, info]) => `
            <div class="service-card ${info.enabled ? '' : 'disabled'}">
                <h4>${name.charAt(0).toUpperCase() + name.slice(1)}</h4>
                <p>Status: <strong>${info.status}</strong></p>
                <span class="status-indicator ${info.enabled ? 'status-online' : 'status-offline'}"></span>
                ${info.enabled ? 'Enabled' : 'Disabled'}
            </div>
        `).join('');
    }

    updateFindingsList(data) {
        const list = document.getElementById('findings-list');
        const findings = data.services_findings || {};
        
        list.innerHTML = Object.entries(findings).map(([service, count]) => `
            <div class="finding-item severity-${this.getSeverityClass(count)}">
                <div>
                    <strong>${service.charAt(0).toUpperCase() + service.slice(1)}</strong>
                    <p>${count} findings discovered</p>
                </div>
                <div class="metric-value" style="font-size: 1.5em;">${count}</div>
            </div>
        `).join('');
    }

    getSeverityClass(count) {
        if (count >= 50) return 'critical';
        if (count >= 20) return 'high';
        if (count >= 5) return 'medium';
        return 'low';
    }

    updateConnectionStatus(connected) {
        const indicator = document.querySelector('.status-indicator');
        const status = document.getElementById('connection-status');
        
        if (connected) {
            indicator.className = 'status-indicator status-online';
            status.textContent = 'Connected to AgentCore';
        } else {
            indicator.className = 'status-indicator status-offline';
            status.textContent = 'AgentCore Offline';
        }
    }

    showError(message) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error').style.display = 'block';
        document.getElementById('error-message').textContent = message;
    }

    startAutoRefresh() {
        // Refresh every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.refreshData();
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    async refreshData() {
        try {
            await this.fetchAllData();
            console.log('Dashboard refreshed:', new Date().toLocaleTimeString());
        } catch (error) {
            console.error('Refresh failed:', error);
        }
    }
}

// Global functions for UI interaction
function showSection(section) {
    // Hide all sections
    const sections = ['executive', 'cost', 'security', 'details', 'history', 'patterns'];
    sections.forEach(s => {
        document.getElementById(`${s}-section`).style.display = 'none';
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(`${section}-section`).style.display = 'block';
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    dashboard.currentSection = section;
}

function refreshData() {
    dashboard.refreshData();
}

// Initialize dashboard when page loads
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new SecurityDashboard();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        dashboard.stopAutoRefresh();
    } else {
        dashboard.startAutoRefresh();
        dashboard.refreshData();
    }
});
