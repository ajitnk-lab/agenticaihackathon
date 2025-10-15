#!/usr/bin/env python3

# Add recommendations section to existing dashboard
recommendations_section = '''
        <!-- Recommendations Section -->
        <div id="recommendations" class="section hidden">
            <div class="drill-down">
                <h3>Security Recommendations & Action Items</h3>
                
                <div class="recommendation-card critical">
                    <div class="rec-header">
                        <span class="priority critical">CRITICAL</span>
                        <span class="service">Inspector</span>
                    </div>
                    <div class="rec-title">Patch 12 Critical CVE Vulnerabilities</div>
                    <div class="rec-desc">Critical security vulnerabilities detected in EC2 instances requiring immediate patching</div>
                    <div class="rec-actions">
                        <button class="action-btn primary" onclick="executeAction('patch-critical')">Auto-Patch Now</button>
                        <button class="action-btn secondary" onclick="showDetails('critical-cves')">View Details</button>
                    </div>
                    <div class="rec-impact">Impact: Prevents potential system compromise</div>
                </div>

                <div class="recommendation-card high">
                    <div class="rec-header">
                        <span class="priority high">HIGH</span>
                        <span class="service">GuardDuty</span>
                    </div>
                    <div class="rec-title">Block Malicious IP Communications</div>
                    <div class="rec-desc">Cryptocurrency mining activity detected from suspicious IP addresses</div>
                    <div class="rec-actions">
                        <button class="action-btn primary" onclick="executeAction('block-ips')">Block IPs</button>
                        <button class="action-btn secondary" onclick="showDetails('malicious-ips')">Investigate</button>
                    </div>
                    <div class="rec-impact">Impact: Stops ongoing threats and data exfiltration</div>
                </div>

                <div class="recommendation-card medium">
                    <div class="rec-header">
                        <span class="priority medium">MEDIUM</span>
                        <span class="service">Security Hub</span>
                    </div>
                    <div class="rec-title">Enable Automated Remediation</div>
                    <div class="rec-desc">83 findings could be automatically resolved with Security Hub automation</div>
                    <div class="rec-actions">
                        <button class="action-btn primary" onclick="executeAction('enable-automation')">Enable Auto-Fix</button>
                        <button class="action-btn secondary" onclick="showDetails('automation-rules')">Configure Rules</button>
                    </div>
                    <div class="rec-impact">Impact: Reduces manual effort by 70%</div>
                </div>

                <div class="recommendation-card low">
                    <div class="rec-header">
                        <span class="priority low">LOW</span>
                        <span class="service">Access Analyzer</span>
                    </div>
                    <div class="rec-title">Review Public S3 Bucket Access</div>
                    <div class="rec-desc">3 S3 buckets have public read access that may not be necessary</div>
                    <div class="rec-actions">
                        <button class="action-btn primary" onclick="executeAction('review-s3')">Review Access</button>
                        <button class="action-btn secondary" onclick="showDetails('public-buckets')">List Buckets</button>
                    </div>
                    <div class="rec-impact">Impact: Improves data security posture</div>
                </div>
            </div>

            <div class="drill-down">
                <h3>Cost Optimization Opportunities</h3>
                
                <div class="recommendation-card cost">
                    <div class="rec-header">
                        <span class="priority cost">COST SAVINGS</span>
                        <span class="service">Macie</span>
                    </div>
                    <div class="rec-title">Optimize Macie Scanning Schedule</div>
                    <div class="rec-desc">Reduce scanning frequency for low-risk buckets to save $15/month</div>
                    <div class="rec-actions">
                        <button class="action-btn primary" onclick="executeAction('optimize-macie')">Optimize Now</button>
                        <button class="action-btn secondary" onclick="showDetails('macie-schedule')">View Schedule</button>
                    </div>
                    <div class="rec-impact">Savings: $180/year with minimal risk increase</div>
                </div>

                <div class="recommendation-card cost">
                    <div class="rec-header">
                        <span class="priority cost">COST SAVINGS</span>
                        <span class="service">GuardDuty</span>
                    </div>
                    <div class="rec-title">Adjust VPC Flow Log Analysis</div>
                    <div class="rec-desc">Fine-tune VPC flow log monitoring to reduce unnecessary analysis</div>
                    <div class="rec-actions">
                        <button class="action-btn primary" onclick="executeAction('optimize-guardduty')">Adjust Settings</button>
                        <button class="action-btn secondary" onclick="showDetails('flow-logs')">Review Logs</button>
                    </div>
                    <div class="rec-impact">Savings: $60/year while maintaining security coverage</div>
                </div>
            </div>

            <div class="action-status hidden" id="action-status">
                <div class="status-content">
                    <div class="spinner"></div>
                    <span id="status-text">Executing action...</span>
                </div>
            </div>
        </div>'''

# CSS for recommendations
recommendations_css = '''
        .recommendation-card {
            background: white; padding: 1.5rem; margin: 1rem 0; 
            border-radius: 0.75rem; border-left: 6px solid #4f46e5;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1); transition: all 0.3s;
        }
        .recommendation-card:hover { transform: translateY(-2px); box-shadow: 0 8px 16px rgba(0,0,0,0.15); }
        
        .recommendation-card.critical { border-left-color: #dc2626; }
        .recommendation-card.high { border-left-color: #ea580c; }
        .recommendation-card.medium { border-left-color: #d97706; }
        .recommendation-card.low { border-left-color: #65a30d; }
        .recommendation-card.cost { border-left-color: #059669; }
        
        .rec-header { display: flex; justify-content: space-between; margin-bottom: 0.75rem; }
        .priority { 
            padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.75rem; 
            font-weight: bold; text-transform: uppercase;
        }
        .priority.critical { background: #fee2e2; color: #991b1b; }
        .priority.high { background: #fed7aa; color: #9a3412; }
        .priority.medium { background: #fef3c7; color: #92400e; }
        .priority.low { background: #dcfce7; color: #166534; }
        .priority.cost { background: #d1fae5; color: #065f46; }
        
        .service { 
            background: #f3f4f6; color: #374151; padding: 0.25rem 0.75rem; 
            border-radius: 1rem; font-size: 0.75rem; font-weight: bold;
        }
        
        .rec-title { font-size: 1.25rem; font-weight: bold; margin-bottom: 0.5rem; color: #1f2937; }
        .rec-desc { color: #6b7280; margin-bottom: 1rem; line-height: 1.5; }
        .rec-impact { color: #059669; font-weight: bold; font-size: 0.9rem; margin-top: 0.75rem; }
        
        .rec-actions { display: flex; gap: 0.75rem; margin: 1rem 0; }
        .action-btn {
            padding: 0.75rem 1.5rem; border: none; border-radius: 0.5rem;
            font-weight: bold; cursor: pointer; transition: all 0.3s;
        }
        .action-btn.primary { background: #4f46e5; color: white; }
        .action-btn.primary:hover { background: #3730a3; }
        .action-btn.secondary { background: #f3f4f6; color: #374151; }
        .action-btn.secondary:hover { background: #e5e7eb; }
        
        .action-status {
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: white; padding: 2rem; border-radius: 0.75rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3); z-index: 1000;
        }
        .status-content { display: flex; align-items: center; gap: 1rem; }'''

print("✅ Recommendations section created")
print("Add to navigation: <button class=\"nav-btn\" onclick=\"switchSection('recommendations')\">Recommendations</button>")
print("Add CSS to existing styles")
print("Add JavaScript functions for actions")
