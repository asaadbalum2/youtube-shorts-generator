# Code Reorganization Plan

## Folder Structure:

```
YShortsGen/
├── core/                    # Core application logic
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── topic_discovery.py
│   ├── content_generator.py
│   ├── video_creator.py
│   ├── youtube_uploader.py
│   ├── scheduler.py
│   ├── email_reporter.py
│   └── error_recovery.py
│
├── web/                     # Web UI
│   ├── __init__.py
│   ├── web_ui.py
│   └── templates/
│       └── dashboard.html
│
├── scripts/                 # Utility scripts
│   ├── verify_secrets.py
│   ├── regenerate_youtube_token.py
│   ├── manual_auth.py
│   ├── setup_youtube_oauth.py
│   └── ... (all other scripts)
│
├── docs/                    # Documentation
│   └── (all .md files)
│
├── main.py                  # Main entry point (stays at root)
├── requirements.txt
├── Procfile
└── README.md                # Main readme stays at root
```

