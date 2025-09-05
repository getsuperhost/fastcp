# Setting up Self-Hosted Runners for FastCP CI/CD

## Prerequisites
- Ubuntu 20.04+ server with sudo access
- GitHub repository access (admin/owner permissions)
- At least 2GB RAM, 2 CPU cores recommended

## Step 1: Download GitHub Actions Runner
```bash
# Create runner directory
mkdir -p ~/actions-runner && cd ~/actions-runner

# Download latest runner (check GitHub for latest version)
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz

# Extract
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz
```

## Step 2: Configure Runner
```bash
# Configure with repository details
./config.sh --url https://github.com/getsuperhost/fastcp --token YOUR_TOKEN_HERE

# Replace YOUR_TOKEN_HERE with token from:
# GitHub → Repository → Settings → Actions → Runners → Add runner → Copy token
```

## Step 3: Install Dependencies
```bash
# Install required packages for FastCP CI/CD
sudo apt update
sudo apt install -y curl wget gnupg2 software-properties-common

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Python 3.12
sudo apt install -y python3.12 python3.12-venv python3-pip

# Install MySQL client libraries
sudo apt install -y default-libmysqlclient-dev pkg-config
```

## Step 4: Start Runner Service
```bash
# Run as service (recommended for production)
sudo ./svc.sh install
sudo ./svc.sh start

# Or run interactively for testing
./run.sh
```

## Step 5: Verify Runner
- Go to GitHub → Repository → Settings → Actions → Runners
- Should see your runner listed as 'Online'
- Test with a push to trigger the workflow

## Troubleshooting
- Check runner logs: `./_diag/Worker_*.log`
- Ensure firewall allows outbound connections
- Verify GitHub token hasn't expired
- Check system resources (memory, disk space)

## Security Notes
- Runners have access to repository secrets
- Keep runner software updated
- Use dedicated user account for runner service
- Monitor runner usage and costs
