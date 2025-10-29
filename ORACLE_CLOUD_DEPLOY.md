# Oracle Cloud Free Tier Deployment - Step by Step

**Oracle Cloud is FREE forever with no credit card required - perfect for 24/7 autonomous operation!**

## ✅ What You Get:
- Always Free VPS (2 OCPU, 12GB RAM)
- Runs 24/7 continuously
- No credit card required
- Perfect for our autonomous YouTube Shorts generator

---

## Step 1: Create Oracle Cloud Account

1. **Go to**: https://www.oracle.com/cloud/free/
2. **Click**: "Start for Free" (or "Try for Free")
3. **Fill in**:
   - Your email (`asaadbalum2@gmail.com`)
   - Password
   - Country
4. **Click**: "Create Account"
5. **Verify your email** - check inbox and click verification link

**No credit card needed!**

---

## Step 2: Create Compute Instance (VPS)

1. **Sign in** to Oracle Cloud Console: https://cloud.oracle.com/
2. **Click**: "Create a VM instance" (or go to Menu → Compute → Instances)
3. **Fill in**:
   - **Name**: `youtube-shorts-generator`
   - **Placement**: Use default (or closest to you)
   - **Image**: Click "Change image" → Select "Oracle Linux 8" or "Ubuntu 22.04"
   - **Shape**: Click "Change shape"
     - Select "VM.Standard.A1.Flex" (Always Free eligible)
     - OCPU: 2 (free tier max)
     - Memory: 12 GB
     - Click "Select Shape"
   - **Network**: Use default VCN
   - **SSH Keys**: Click "Generate SSH key pair" (or use your own)
   - Download the private key (save it safely!)

4. **Click**: "Create"
5. **Wait** 2-3 minutes for instance to be ready
6. **Copy the Public IP** address shown

---

## Step 3: Connect via SSH

### Windows:
1. **Install PuTTY** (or use Windows Terminal with SSH)
   - Download: https://www.putty.org/
   - OR use built-in SSH in PowerShell/Windows Terminal

2. **Connect**:
   ```powershell
   ssh -i path/to/your-private-key opc@YOUR_PUBLIC_IP
   ```
   Or with PuTTY:
   - Host: `opc@YOUR_PUBLIC_IP`
   - Auth → Private key: Select your `.key` file

### Linux/Mac:
```bash
chmod 400 your-private-key.key
ssh -i your-private-key.key opc@YOUR_PUBLIC_IP
```

**First time**: Type "yes" to accept fingerprint

---

## Step 4: Install Software on VPS

Once connected via SSH, run these commands:

### For Oracle Linux:
```bash
sudo yum update -y
sudo yum install python3 python3-pip git ffmpeg -y
```

### For Ubuntu:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip git ffmpeg -y
```

**Verify installation**:
```bash
python3 --version  # Should show Python 3.x
ffmpeg -version   # Should show FFmpeg info
```

---

## Step 5: Upload Your Code

### Option A: Git (Recommended)

1. **On your computer**, create a GitHub repository:
   - Go to github.com
   - Create new repository (private is fine)
   - Upload all your project files
   - Or use Git commands locally:
     ```bash
     git init
     git add .
     git commit -m "Initial commit"
     git remote add origin YOUR_GITHUB_URL
     git push -u origin main
     ```

2. **On the VPS** (via SSH):
   ```bash
   cd ~
   git clone YOUR_GITHUB_REPO_URL
   cd YShortsGen  # or whatever your repo is named
   ```

### Option B: Upload Files Manually

Use SCP or SFTP to upload files:
```bash
# On your computer (Windows PowerShell):
scp -i your-key -r * opc@YOUR_IP:~/YShortsGen/
```

---

## Step 6: Install Python Dependencies

**On the VPS**:
```bash
cd ~/YShortsGen
pip3 install -r requirements.txt
```

This may take 5-10 minutes.

---

## Step 7: Configure Environment Variables

**On the VPS**:
```bash
cd ~/YShortsGen
nano .env
```

**Copy everything from YOUR_KEYS.txt and paste into .env**, making sure format is:
```
GROQ_API_KEY=gsk_...
REDDIT_CLIENT_ID=...
# etc.
```

**Save**: Press `Ctrl+X`, then `Y`, then `Enter`

---

## Step 8: Test Run (Optional)

**On the VPS**:
```bash
cd ~/YShortsGen
python3 main.py single
```

This tests if everything works. Should create and upload one video.

---

## Step 9: Run as Background Service (24/7)

**On the VPS**, create systemd service:

```bash
sudo nano /etc/systemd/system/shorts-generator.service
```

**Paste this** (adjust paths if needed):
```ini
[Unit]
Description=YouTube Shorts Generator
After=network.target

[Service]
Type=simple
User=opc
WorkingDirectory=/home/opc/YShortsGen
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /home/opc/YShortsGen/main.py autonomous
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save and enable**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable shorts-generator
sudo systemctl start shorts-generator
```

**Check status**:
```bash
sudo systemctl status shorts-generator
```

**View logs**:
```bash
journalctl -u shorts-generator -f
```

---

## Step 10: Verify It's Running

1. **Check logs**:
   ```bash
   journalctl -u shorts-generator -n 50
   ```

2. **Check your YouTube channel** - videos should start appearing!

3. **Check database** (optional):
   ```bash
   sqlite3 ~/YShortsGen/shorts_db.sqlite "SELECT * FROM videos LIMIT 5;"
   ```

---

## Monitoring & Maintenance

### View Logs:
```bash
journalctl -u shorts-generator -f  # Live logs
tail -f ~/YShortsGen/shorts_generator.log  # App logs
```

### Restart Service:
```bash
sudo systemctl restart shorts-generator
```

### Stop Service:
```bash
sudo systemctl stop shorts-generator
```

### Check System Resources:
```bash
htop  # or 'top'
df -h  # Check disk space
free -h  # Check memory
```

---

## Troubleshooting

### "Service failed to start"
- Check logs: `journalctl -u shorts-generator -n 100`
- Verify .env file exists and has all keys
- Check Python path: `which python3`

### "FFmpeg not found"
- Install: `sudo yum install ffmpeg` (Oracle) or `sudo apt install ffmpeg` (Ubuntu)

### "Permission denied"
- Check file permissions: `chmod +x main.py`
- Check .env permissions: `chmod 600 .env`

### "YouTube upload fails"
- Check refresh token in .env
- View logs for specific error
- Verify YouTube API quotas (free tier: 10,000 units/day)

---

## Security Notes

1. **Keep your SSH key safe** - don't share it
2. **Don't commit .env to Git** - it's in .gitignore
3. **Firewall**: Oracle Cloud blocks most ports by default (good for security)
4. **Regular updates**: `sudo yum update` or `sudo apt update`

---

## That's It!

Your YouTube Shorts generator is now running 24/7 on Oracle Cloud, completely autonomous!

- ✅ Generates 3 videos daily (customizable)
- ✅ Uploads automatically to YouTube
- ✅ Runs forever (free tier)
- ✅ No credit card required
- ✅ Fully autonomous - zero human intervention needed

**Just monitor your YouTube channel and watch the videos appear!** 📹🚀

