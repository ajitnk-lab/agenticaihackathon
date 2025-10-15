#!/bin/bash
# Setup cron job to run security analysis every 2 hours

PROJECT_DIR="/persistent/home/ubuntu/workspace/agenticaihackathon"

# Create cron job script
cat > "$PROJECT_DIR/scripts/cron_security_analysis.sh" << 'EOF'
#!/bin/bash
cd /persistent/home/ubuntu/workspace/agenticaihackathon
source scripts/memory_env.sh
python3 scripts/trigger_real_analysis.py >> logs/security_analysis.log 2>&1
echo "$(date): Security analysis completed" >> logs/security_analysis.log
EOF

# Make it executable
chmod +x "$PROJECT_DIR/scripts/cron_security_analysis.sh"

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

# Add cron job (every 2 hours)
(crontab -l 2>/dev/null; echo "0 */2 * * * $PROJECT_DIR/scripts/cron_security_analysis.sh") | crontab -

echo "✅ Cron job created!"
echo "   Runs every 2 hours: $PROJECT_DIR/scripts/cron_security_analysis.sh"
echo "   Logs: $PROJECT_DIR/logs/security_analysis.log"
echo ""
echo "📋 Cron schedule:"
crontab -l | grep security_analysis
echo ""
echo "🔍 To check logs:"
echo "   tail -f $PROJECT_DIR/logs/security_analysis.log"
echo ""
echo "❌ To remove cron job:"
echo "   crontab -l | grep -v security_analysis | crontab -"
