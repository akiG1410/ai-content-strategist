# 🎯 AI Content Marketing Strategist

> **Generate professional content marketing strategies and 30-day calendars powered by AI**

An intelligent content strategy generator that uses CrewAI and Claude Sonnet to analyze your brand and create comprehensive marketing strategies with actionable content calendars.

[![Built with CrewAI](https://img.shields.io/badge/Built%20with-CrewAI-blue)](https://www.crewai.com/)
[![Powered by Claude](https://img.shields.io/badge/Powered%20by-Claude-orange)](https://www.anthropic.com/)
[![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red)](https://streamlit.io/)

## ✨ Features

### 🤖 **AI-Powered Strategy Generation**
- **5 Distinct Strategies**: Get multiple strategic approaches tailored to your brand
- **Smart Analysis**: AI analyzes your industry, audience, and resources
- **Channel Distribution**: Intelligent content distribution across your selected platforms
- **30-Day Calendar**: Complete content calendar with 20-25 actionable pieces

### 📊 **Professional Outputs**
- **Strategy Document (DOCX)**: Comprehensive Word document with all 5 strategies
- **Calendar Document (DOCX)**: Detailed content calendar with execution notes
- **Excel Workbook (XLSX)**: Interactive spreadsheet with 4 tabs:
  - Monthly Calendar View
  - Content Details
  - Weekly Checklist
  - Metrics Tracker

### 🔒 **Enterprise-Grade Security**
- **Input Validation**: XSS protection with 20+ injection pattern detection
- **Rate Limiting**: Session-based limiting (5 generations/hour)
- **Authentication**: Optional beta password protection
- **PII-Safe Logging**: Automatic redaction of sensitive data
- **Secure API Client**: Retry logic and error handling

### 🎨 **User-Friendly Interface**
- **8-Step Wizard**: Guided workflow for easy strategy creation
- **Progress Tracking**: Visual progress indicators
- **Instant Preview**: Review all inputs before generation
- **Multi-Channel Support**: Select 1-3 primary channels from 11 options

## 🚀 Live Demo

**Coming Soon!** This app will be deployed to Streamlit Cloud.

## 📋 Prerequisites

- Python 3.11+
- OpenRouter API key (for Claude Sonnet 4.5 access)
- Git

## 💻 Local Installation

### 1. Clone the Repository

```bash
git clone https://github.com/akig1410/ai-content-strategist.git
cd ai-content-strategist
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Secrets

Create `.streamlit/secrets.toml`:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` and add your API key:

```toml
OPENROUTER_API_KEY = "sk-or-v1-YOUR_ACTUAL_KEY_HERE"

# Optional: Enable password protection
# BETA_PASSWORD = "your-secure-password"
```

**Get your API key:** [OpenRouter Keys](https://openrouter.ai/keys)

### 5. Run the Application

```bash
streamlit run src/streamlit_app.py
```

The app will open at `http://localhost:8501`

## 🌐 Deployment to Streamlit Cloud

### 1. Fork or Push to GitHub

```bash
# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - AI Content Marketing Strategist"

# Add remote (replace with your repo)
git remote add origin https://github.com/akig1410/ai-content-strategist.git

# Push
git push -u origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository: `akig1410/ai-content-strategist`
4. Set main file path: `src/streamlit_app.py`
5. Set Python version: `3.11`
6. Click "Deploy"

### 3. Configure Secrets

In your app settings on Streamlit Cloud:

1. Go to **Settings** → **Secrets**
2. Add your secrets:

```toml
OPENROUTER_API_KEY = "sk-or-v1-YOUR_KEY_HERE"

# Optional: Enable password protection for beta access
BETA_PASSWORD = "your-secure-password"

# Optional: Force production mode
ENVIRONMENT = "production"
```

3. Click "Save"

### 4. Test Your Deployment

- Wait for the build to complete (2-3 minutes)
- Visit your app URL
- Test the full workflow with a sample brand

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 📖 Usage Guide

### Step-by-Step Workflow

1. **Brand Basics**: Enter brand name, industry, and website
2. **Target Audience**: Describe your ideal customers (50+ characters)
3. **Business Goals**: Select 1-4 primary objectives
4. **Content Channels**: Choose active channels and select 1-3 primary ones
5. **Resources**: Set budget, time commitment, and available resources
6. **Brand Details**: Add value proposition and products/services
7. **Additional Info**: Optional competitor and success information
8. **Review & Generate**: Confirm inputs and generate strategies

### What You'll Get

**Phase 1: Strategy Generation** (~2-3 minutes)
- Comprehensive brand analysis
- 5 distinct content strategies
- Each with pros, cons, and content ideas

**Phase 2: Calendar Creation** (~3-4 minutes)
- 20-25 content pieces for the selected strategy
- Week-by-week breakdown
- Execution notes and CTAs
- Effort levels and engagement predictions

### Example Output

For a B2B SaaS company targeting enterprise clients:

```
Strategy 1: Thought Leadership Powerhouse
- Focus: Industry insights and expert positioning
- Channels: LinkedIn (60%), Blog (25%), Email (15%)
- Content Mix: 40% Educational, 35% Thought Leadership, 25% Promotional
- Posting: 4-5x per week
```

## 🏗️ Architecture

```
ai-content-strategist/
├── src/
│   ├── streamlit_app.py       # Main Streamlit application
│   ├── main.py                 # CrewAI agents definition
│   ├── content_parser.py       # AI output parsing
│   ├── document_generator.py   # DOCX generation
│   ├── excel_generator.py      # XLSX generation
│   ├── security/               # Security modules
│   │   ├── input_validator.py  # Input validation & XSS protection
│   │   ├── rate_limiter.py     # Rate limiting
│   │   └── auth.py             # Authentication
│   ├── config/                 # Configuration
│   │   └── secure_config.py    # Environment & secrets management
│   ├── api/                    # API clients
│   │   └── secure_client.py    # Secure OpenRouter client
│   └── utils/                  # Utilities
│       ├── file_handler.py     # File operations
│       └── secure_logger.py    # PII-safe logging
├── .streamlit/
│   ├── config.toml             # Streamlit configuration
│   └── secrets.toml.example    # Secrets template
├── scripts/
│   ├── check_secrets.sh        # Security verification
│   └── test_security.py        # Security tests
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables

Set in `.streamlit/secrets.toml`:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | ✅ Yes | Your OpenRouter API key |
| `BETA_PASSWORD` | ❌ No | Enable password protection |
| `ENVIRONMENT` | ❌ No | `production` or `development` |
| `MAX_REQUESTS` | ❌ No | Override rate limit (default: 5) |
| `WINDOW_SECONDS` | ❌ No | Rate limit window (default: 3600) |

### Rate Limiting

**Production Mode** (default):
- 5 strategy generations per hour per session
- Prevents abuse and manages API costs

**Development Mode**:
- Unlimited generations
- Enabled automatically when running locally

### Authentication

**Disable** (default):
- No password required
- Public access

**Enable**:
```toml
BETA_PASSWORD = "your-password-here"
```
- Users must enter password
- SHA256 hashing
- Session-based authentication

## 🛡️ Security Features

✅ **Input Validation**: All user inputs validated with whitelist checking
✅ **XSS Protection**: HTML escaping and injection pattern detection
✅ **Rate Limiting**: Prevents abuse with session-based tracking
✅ **Secure Logging**: PII automatically redacted from logs
✅ **API Security**: Exponential backoff and retry logic
✅ **No File Writes**: Uses Streamlit download buttons (Cloud-safe)

## 🧪 Testing

### Run Security Tests

```bash
# Test all security modules
./venv/bin/python scripts/test_security.py

# Check for secrets in repository
./scripts/check_secrets.sh
```

### Expected Results

```
✅ Input Validator: All tests passed
✅ Rate Limiter: All tests passed
✅ Secure Config: All tests passed
✅ Authenticator: All tests passed
```

## 📊 Technology Stack

| Component | Technology |
|-----------|-----------|
| **AI Framework** | CrewAI 1.6.1 |
| **LLM** | Claude Sonnet 4.5 (via OpenRouter) |
| **UI Framework** | Streamlit 1.52.0 |
| **Document Generation** | python-docx, openpyxl |
| **API Client** | OpenAI SDK (OpenRouter compatible) |
| **Security** | Custom security modules |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CrewAI** - For the amazing multi-agent framework
- **Anthropic** - For Claude Sonnet 4.5
- **Streamlit** - For the intuitive web framework
- **OpenRouter** - For unified LLM API access

## 📧 Contact

**Author**: Akash Gupta
**GitHub**: [@akig1410](https://github.com/akig1410)

## 🐛 Issues & Support

Found a bug? Have a feature request?

- 🐛 [Report an Issue](https://github.com/akig1410/ai-content-strategist/issues)
- 💬 [Discussions](https://github.com/akig1410/ai-content-strategist/discussions)

## 🗺️ Roadmap

- [ ] User accounts and saved strategies
- [ ] Export to additional formats (PDF, PPT)
- [ ] Multi-language support
- [ ] API endpoint for integrations
- [ ] Analytics dashboard
- [ ] Team collaboration features

---

**Made with ❤️ using CrewAI and Claude**
