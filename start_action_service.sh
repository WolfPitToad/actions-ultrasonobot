#!/bin/bash
echo "Iniciando segundo servicio..."
cd /app
chmod +x /app/start_action_service.sh
#rasa rasa run actions -p $PORT --actions actions
rasa run actions -p $PORT 
#run rasa run actions -p $PORT