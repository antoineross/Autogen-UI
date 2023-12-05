FROM python:3.11

# Create a non-root user
RUN useradd -m -u 1000 user

# Set user and environment variables
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory in the container
WORKDIR $HOME/app

# Copy the requirements.txt file to the container
COPY requirements.txt $HOME/app/

# Install Python dependencies from requirements.txt
RUN pip install -r $HOME/app/requirements.txt

# Copy the application files, including app.py
COPY . $HOME/app/

# Specify the command to run your application
CMD ["chainlit", "run", "app.py", "--port", "7860"]
