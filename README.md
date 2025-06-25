# Fake-News-Detector

A sophisticated AI-powered system designed to detect and analyze fake news across multiple languages. This system leverages various machine learning techniques including fact checking, source credibility analysis, sentiment analysis, and image verification to provide accurate fake news detection.

## Key Features

- **Multi-language Support**: Detects fake news in various languages
- **AI-Powered Analysis**: Uses advanced machine learning models for content verification
- **Source Credibility Check**: Evaluates the reliability of news sources
- **Fact Verification**: Cross-checks claims with trusted sources
- **Sentiment Analysis**: Identifies emotional manipulation in news
- **Image Analysis**: Detects manipulated or misleading images
- **Web Interface**: User-friendly interface for easy news verification

## Project Structure
fake-news-detector/
├── app/ # Main application directory
│ ├── main.py # FastAPI application
│ └── static/ # Static files (HTML, CSS, JS)
├── services/ # Core services
│ ├── fact_checking.py # Fact verification service
│ ├── image_verification.py # Image analysis
│ ├── news_verification.py # News content verification
│ ├── translation.py # Language translation service
│ └── web_scraper.py # Web content scraping
├── models/ # ML model management
├── utils/ # Utility functions
└── logs/ # Application logs


## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fake-news-detector.git
cd fake-news-detector
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the setup script:
```bash
# For Windows
setup.bat

# For Linux/Mac
./setup.sh
```

4. Start the server:
```bash
# For Windows
start_server.bat

# For Linux/Mac
python run.py
```

## Usage

1. Access the web interface at: `http://localhost:8000`
2. Enter the news article URL or text
3. Click "Analyze" to get detailed verification results
4. View the analysis including:
   - Fake news probability
   - Source credibility score
   - Sentiment analysis
   - Fact-checking results
   - Image verification (if applicable)

## Testing

Run the test suite:
```bash
python test_fake_news.py
python test_setup.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
