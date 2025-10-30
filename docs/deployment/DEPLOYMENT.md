# Deployment Guide

This guide covers deploying the YouTube Shorts Generator to free hosting platforms.

## Option 1: Railway (Recommended - Easiest)

Railway offers a free tier with $5/month credit, perfect for this project.

### Steps:

1. **Install Railway CLI**:
   ```bash
   npm i -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize Project**:
   ```bash
   railway init
   ```
   - Choose "Create new project"
   - Name it "youtube-shorts-generator"

4. **Configure Environment Variables**:
   ```bash
   railway variables
   ```
   Add all variables from your `.env` file (one by one, or use the web dashboard)

5. **Deploy**:
   ```bash
   railway up
   ```

6. **Monitor Logs**:
   ```bash
   railway logs
   ```

**Note**: Railway requires a credit card but won't charge for free tier usage. If you prefer completely free without card, use Option 3 or 4.

## Option 2: Render

Render has a free tier but note: it spins down after 15 minutes of inactivity. This may not work well for scheduled tasks.

### Steps:

1. Go to https://render.com/
2. Sign up with GitHub
3. Connect your repository
4. Create new "Web Service"
5. Configure:
   - **Name**: youtube-shorts-generator
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py autonomous`
   - **Plan**: Free

6. Add all environment variables in the "Environment" tab

7. Deploy

**Warning**: Free tier may not be ideal for scheduled tasks due to spin-down.

## Option 3: Replit (Free, No Card Required)

Replit offers free hosting with no credit card needed.

### Steps:

1. Go to https://replit.com/
2. Sign up (free)
3. Click "Create Repl"
4. Import from GitHub (connect your repo)
5. In the Secrets tab (🔒 icon), add all environment variables
6. Run `python main.py autonomous` in the shell

**Note**: Replit free tier may have resource limits, but works for this use case.

## Option 4: Oracle Cloud Free Tier (Best for 24/7)

Oracle offers a truly free VPS (Always Free tier) with no credit card required.

### Steps:

1. **Sign Up**:
   - Go to https://www.oracle.com/cloud/free/
   - Click "Start for Free"
   - Create account (no credit card needed)

2. **Create Compute Instance**:
   - Dashboard > "Create a VM instance"
   - Name: youtube-shorts-generator
   - Image: Oracle Linux or Ubuntu
   - Shape: VM.Standard.A1.Flex (Free tier)
   - Configure networking (use default VCN)
   - Add SSH keys (generate if needed)
   - Click "Create"

3. **SSH into Instance**:
   ```bash
   ssh opc@<your-instance-ip>
   ```

4. **Install Dependencies**:
   ```bash
   sudo yum update -y  # For Oracle Linux
   # OR
   sudo apt update && sudo apt upgrade -y  # For Ubuntu
   
   # Install Python
   sudo yum install python3 python3-pip git -y
   # OR
   sudo apt install python3 python3-pip git -y
   
   # Install FFmpeg
   sudo yum install ffmpeg -y
   # OR
   sudo apt install ffmpeg -y
   ```

5. **Clone Repository**:
   ```bash
   git clone <your-repo-url>
   cd YShortsGen
   ```

6. **Install Python Packages**:
   ```bash
   pip3 install -r requirements.txt
   ```

7. **Setup Environment**:
   ```bash
   cp .env.example .env
   nano .env  # Edit with your values
   ```

8. **Setup YouTube OAuth** (one-time):
   - Transfer `client_secrets.json` to server: `scp client_secrets.json opc@<ip>:~/YShortsGen/`
   - SSH and run: `python3 setup_youtube_oauth.py`
   - Transfer `token.pickle` back if needed

9. **Run in Background**:
   ```bash
   # Using screen (install if needed: sudo yum install screen)
   screen -S shorts-generator
   python3 main.py autonomous
   # Press Ctrl+A then D to detach
   
   # Or use nohup
   nohup python3 main.py autonomous > output.log 2>&1 &
   ```

10. **Keep Running** (optional - use systemd):
    Create `/etc/systemd/system/shorts-generator.service`:
    ```ini
    [Unit]
    Description=YouTube Shorts Generator
    After=network.target

    [Service]
    Type=simple
    User=opc
    WorkingDirectory=/home/opc/YShortsGen
    ExecStart=/usr/bin/python3 /home/opc/YShortsGen/main.py autonomous
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

    Enable and start:
    ```bash
    sudo systemctl enable shorts-generator
    sudo systemctl start shorts-generator
    sudo systemctl status shorts-generator
    ```

## Option 5: Docker (Any Platform)

If you have a VPS or can run Docker:

1. **Build Image**:
   ```bash
   docker build -t shorts-generator .
   ```

2. **Run Container**:
   ```bash
   docker-compose up -d
   ```

Or manually:
```bash
docker run -d \
  --name shorts-generator \
  --env-file .env \
  -v $(pwd)/temp:/app/temp \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/shorts_db.sqlite:/app/shorts_db.sqlite \
  shorts-generator
```

## Environment Variables on Hosting

When deploying, add these as environment variables:

- All variables from `.env`
- Ensure `token.pickle` is uploaded/accessible if using existing auth
- Or re-run OAuth setup after deployment

## Monitoring Your Deployment

1. **Check Logs**:
   - Railway: `railway logs`
   - Render: Dashboard > Logs
   - Replit: Shell output
   - Oracle VPS: `tail -f output.log` or `journalctl -u shorts-generator`

2. **Check Database**:
   - Download `shorts_db.sqlite` to inspect stats
   - View in SQLite browser

3. **Check Generated Videos**:
   - Check `output/` folder (if accessible)
   - Verify uploads on YouTube channel

## Scaling Considerations

- **Free tiers** are sufficient for 3-5 videos/day
- If you need more, consider upgrading hosting
- Monitor API quotas (YouTube has 10,000 units/day free)

## Troubleshooting Deployment

### "Module not found" errors:
- Ensure all dependencies in `requirements.txt` are installed
- Check Python version (3.8+)

### "FFmpeg not found":
- Ensure FFmpeg is installed on the system
- For Docker, it's included in the Dockerfile

### Environment variables not loading:
- Double-check variable names match exactly
- No quotes needed in hosting dashboards
- Restart service after adding variables

### Scheduled tasks not running:
- Check system timezone (should be correct)
- Verify cron/scheduler is working
- Check logs for errors

## Recommendations

- **Railway**: Best balance of ease and reliability
- **Oracle Cloud**: Best for true 24/7 free hosting
- **Replit**: Good for testing, may have limits
- **Self-hosted VPS**: Maximum control, needs maintenance

Choose based on your needs and technical comfort level!

