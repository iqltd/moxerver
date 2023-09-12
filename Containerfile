# Set base image (host OS)
FROM python:3.11-slim-bookworm

ENV APP_HOME_DIR=/opt/moxerver


# By default, listen on port 5000
EXPOSE 5000/tcp

# Set the working directory in the container
WORKDIR $APP_HOME_DIR

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . $APP_HOME_DIR

# Setup db tables
CMD ["flask", "init_db"]

# Specify the command to run on container start
CMD [ "python", "./app.py" ]
