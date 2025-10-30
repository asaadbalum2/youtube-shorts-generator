# Cloudflare Tunnel Setup (Free Stable URL)

## What is Cloudflare Tunnel?
- **Free**: No cost for basic usage
- **Stable URL**: Your app gets a permanent subdomain like `youtube-shorts-generator.yourname.trycloudflare.com`
- **Secure**: Encrypted connection
- **No port forwarding**: Works behind firewalls

## Setup Steps

### 1. Install Cloudflare Tunnel
```bash
# In Replit Shell
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb
```

### 2. Login to Cloudflare
```bash
cloudflared tunnel login
```
- This opens a browser window
- Login to your Cloudflare account (free)
- Authorize the tunnel

### 3. Create a Tunnel
```bash
cloudflared tunnel create youtube-shorts-generator
```
- This creates a tunnel and gives you a tunnel ID
- Save the tunnel ID (you'll need it)

### 4. Configure the Tunnel
Create a config file:
```bash
mkdir -p ~/.cloudflared
nano ~/.cloudflared/config.yml
```

Add this content (replace `YOUR_TUNNEL_ID` with actual ID):
```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /home/runner/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: youtube-shorts-generator.yourname.trycloudflare.com
    service: http://localhost:8080
  - service: http_status:404
```

### 5. Run the Tunnel
```bash
cloudflared tunnel run youtube-shorts-generator
```

### 6. Your Stable URL
Your app will be available at:
`https://youtube-shorts-generator.yourname.trycloudflare.com/dashboard`

## Auto-start with Replit
Add to your `main.py` to start tunnel automatically:
```python
import subprocess
import threading

def start_cloudflare_tunnel():
    subprocess.run(['cloudflared', 'tunnel', 'run', 'youtube-shorts-generator'])

# Start tunnel in background
tunnel_thread = threading.Thread(target=start_cloudflare_tunnel, daemon=True)
tunnel_thread.start()
```

## Benefits
- ✅ **Free forever**
- ✅ **Stable URL** (doesn't change)
- ✅ **HTTPS by default**
- ✅ **Works from anywhere**
- ✅ **No port forwarding needed**
