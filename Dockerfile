FROM python:3.7
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
#### FROM HERE ####
#### TO HERE ####

WORKDIR /app

COPY . .




# Establece los permisos del archivo
RUN chmod +x /app/start_action_service.sh

USER 1001

ENV LOG_LEVEL=DEBUG
CMD ["./start_action_service.sh"]
