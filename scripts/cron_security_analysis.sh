#!/bin/bash
cd /persistent/home/ubuntu/workspace/agenticaihackathon
source scripts/memory_env.sh
python3 scripts/trigger_real_analysis.py >> logs/security_analysis.log 2>&1
echo "$(date): Security analysis completed" >> logs/security_analysis.log
