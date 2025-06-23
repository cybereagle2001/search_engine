# 🌐 IMEDRA Browser

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Platform-Windows-brightgreen.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Platform-Linux-brightgreen.svg" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</div>

## 🚀 Overview

IMEDRA Browser is a specialized web browser designed for cybersecurity professionals. It combines the power of a modern web interface with intelligent domain scoring and security-focused features.

## ✨ Key Features

- **🔍 Intelligent Domain Scoring**: Built-in scoring system for cybersecurity domains
- **🎯 Security-First Design**: Focused on cybersecurity research and analysis
- **🖥️ Modern Interface**: Clean, intuitive UI built with Qt6
- **🔄 Real-time Updates**: Dynamic URL display and content rendering
- **📑 Tab Management**: Multi-tab support for efficient browsing

## 🎯 Domain Scoring System

The browser includes a sophisticated domain scoring system for cybersecurity websites:

| Domain | Trust Score |
|--------|-------------|
| portswigger.net | 1.7 |
| tenable.com | 1.6 |
| ceccouncil.org | 1.6 |
| proofpoint.com | 1.5 |
| okta.com | 1.5 |
| symantec.com | 1.5 |

## 🛠️ Technical Stack

- **Frontend**: PySide6 (Qt for Python)
- **Backend**: Flask
- **Web Engine**: QtWebEngine
- **Architecture**: Multi-threaded design with separate UI and server threads

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/IMEDRA_BROWSER.git
cd IMEDRA_BROWSER
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

## 🚀 Usage

Launch the browser:
```bash
python3 browser.py
```

### Navigation Features:
- `←` / `→`: Navigate back/forward
- `↻`: Reload page
- `⌂`: Return to home
- `Ctrl+T`: Open new tab

## 🔧 Development

The browser consists of two main components:
- `browser.py`: UI and browser functionality
- `app.py`: Flask backend server with domain scoring logic

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

## 🔒 Security

- All connections are monitored and scored based on domain trust
- Real-time security checks for visited domains
- Secure handling of browser sessions

---

<div align="center">
  <p>Made with ❤️ by IMEDRA Team</p>
  <p>© 2024 IMEDRA. All rights reserved.</p>
</div>
