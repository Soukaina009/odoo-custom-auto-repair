FROM odoo:19.0

# Install Python dependencies for the chatbot module and blockchain
# Use /usr/bin/python3 -m pip for explicit path and break-system-packages
RUN /usr/bin/python3 -m pip install --upgrade --break-system-packages pip setuptools

# Install web3 and dependencies
RUN /usr/bin/python3 -m pip install --no-cache-dir --break-system-packages "web3>=6.0.0" requests packaging langchain openai faiss-cpu sentence-transformers python-dotenv

# Verify web3 is installed
RUN /usr/bin/python3 -c "import web3; print('web3 installed:', web3.__version__)"

