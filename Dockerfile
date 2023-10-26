# Specify the parent image from which we build
FROM jasonchaffee/kali-linux

# Set the working directory
WORKDIR /server

# Copy files from your host to your current working directory
COPY . server

WORKDIR ./server

# Install python 3.11
RUN ./install_python_3_11.sh
RUN python3 --version
# Install requirements
RUN ./install-requirements.sh

WORKDIR ./scripts/install
# Install go, subfinder, and wordlists
RUN ./go.sh
RUN ./subfinder.sh
RUN ./wordlists.sh

# Go back to the root directory
WORKDIR /server/server
EXPOSE 8000
# Run the application
CMD ["/bin/bash", "-c", "./start-server.sh"]