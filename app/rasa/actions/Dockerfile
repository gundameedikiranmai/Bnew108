FROM rasa/rasa:3.4.0

COPY . /app

WORKDIR /app
USER root
RUN pip install python-dotenv rasa-sdk requests

# Don't use root user to run code
USER 1001

EXPOSE 5055

ENV API_SERVER_URL="http://api:8888"

CMD ["run", "actions", "--debug"]