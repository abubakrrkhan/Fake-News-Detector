import re
import time
import json
import requests
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse
from datetime import datetime
from loguru import logger
import tldextract
from bs4 import BeautifulSoup

class SourceCredibilityAnalyzer:
    """
    Analyzes the credibility of news sources
    """
    
    def __init__(self):
        """Initialize the source credibility analyzer"""
        logger.info("Initializing SourceCredibilityAnalyzer")
        
        # Load credibility database
        self.credibility_db = self._load_credibility_database()
        
        # Domain metadata cache
        self.domain_cache = {}
        
        # Request headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        
        # Rate limiting
        self.min_request_interval = 2  # seconds
        self.last_request_time = 0
        
        # Known fake news domains (simplified list for demo)
        self.fake_news_domains = [
            "fakenews", "fakemedia", "hoaxes", "conspiracy", 
            "fakenewsmedia.net", "fakereport", "notrealnews", 
            "fakesciencenews", "alternativefacts", "totallylegit"
        ]
        
        # Known credible news domains (simplified list for demo)
        self.credible_domains = [
            "reuters.com", "apnews.com", "npr.org", "bbc.com", 
            "nytimes.com", "washingtonpost.com", "wsj.com", 
            "theguardian.com", "economist.com", "bloomberg.com"
        ]
        
        # Initialize database of known credible and non-credible sources
        self.credible_sources = {
            "reuters.com": 0.95,
            "apnews.com": 0.95,
            "bbc.com": 0.9,
            "bbc.co.uk": 0.9,
            "nytimes.com": 0.85,
            "washingtonpost.com": 0.85,
            "theguardian.com": 0.85,
            "npr.org": 0.85,
            "bloomberg.com": 0.8,
            "economist.com": 0.85,
            "wsj.com": 0.8,
            "cnn.com": 0.75,
            "abcnews.go.com": 0.8,
            "nbcnews.com": 0.75,
            "thehill.com": 0.7,
            "politico.com": 0.75,
            "time.com": 0.8,
            "nature.com": 0.95,
            "science.org": 0.95,
            "sciencemag.org": 0.95,
            "newscientist.com": 0.85,
            "scientificamerican.com": 0.9,
            "smithsonianmag.com": 0.85,
            "nationalgeographic.com": 0.85,
            "popsci.com": 0.7,
            "snopes.com": 0.85,
            "factcheck.org": 0.85,
            "politifact.com": 0.85,
        }
        
        self.non_credible_sources = {
            "infowars.com": 0.1,
            "naturalnews.com": 0.15,
            "breitbart.com": 0.2,
            "dailycaller.com": 0.3,
            "zerohedge.com": 0.2,
            "sputniknews.com": 0.25,
            "rt.com": 0.3,
            "beforeitsnews.com": 0.1,
            "newsmax.com": 0.4,
            "americanthinker.com": 0.3,
            "thegatewaypundit.com": 0.2,
            "activistpost.com": 0.2,
            "worldtruth.tv": 0.1,
            "wnd.com": 0.3,
        }
        
        # Suspicious keywords in domain names
        self.suspicious_keywords = [
            'truth', 'real', 'exposed', 'uncensored', 'patriot', 'freedom', 
            'alternative', 'conspiracy', 'insider', 'breaking', 'viral', 
            'secret', 'shocking', 'illuminati', 'globalist', 'wake', 'awakening',
            'truther', 'planet', 'fake', 'hoax', 'lie', 'truenews', 'realnews'
        ]
        
        # Suspicious TLDs (Top Level Domains)
        self.suspicious_tlds = [
            '.info', '.xyz', '.top', '.biz', '.club', '.site',
            '.online', '.pro', '.network', '.ws', '.pw'
        ]
        
        # Patterns for detecting fake news sources
        self.fake_domain_patterns = [
            r'(\w+)truth\.(?:com|org|net|info)',          # Example: truthnews.com
            r'real(\w+)news\.(?:com|org|net|info)',       # Example: realalternativenews.com
            r'(\w+)exposed\.(?:com|org|net|info)',        # Example: governmentexposed.com
            r'(\w+)uncensored\.(?:com|org|net|info)',     # Example: newsuncensored.com
            r'(\w+)leaks\.(?:com|org|net|info)',          # Example: governmentleaks.com
            r'(\w+)conspiracy\.(?:com|org|net|info)',     # Example: worldconspiracy.com
            r'the(\w+)awakening\.(?:com|org|net|info)',   # Example: thegreatawakening.com
            r'(\w+)patriot(\w+)\.(?:com|org|net|info)',   # Example: truepatriotnews.com
            r'(\w+)freedom(\w+)\.(?:com|org|net|info)',   # Example: freedomfighterreport.com
            r'(\w+)truther(\w+)\.(?:com|org|net|info)',   # Example: truthernetwork.com
            r'fakenews(\w+)\.(?:com|org|net|info)',       # Example: fakenewsmedia.net
            r'(\w+)fakemedia\.(?:com|org|net|info)'       # Example: exposefakemedia.com
        ]
        
        # Create specific detection patterns for common hoaxes
        self.hoax_patterns = {
            "astronomical_disasters": [
                r'\b(planet[ary]?\s+alignment)\b.*\b(disaster|catastrophe|blackout)\b',
                r'\b(venus|mars|jupiter|saturn)\b.*\b(align\w*)\b.*\b(disaster|catastrophe|blackout)\b',
                r'\b(celestial\s+event)\b.*\b(power\s+outage|blackout)\b',
                r'\b(nasa|scientists)\b.*\b(covering\s+up|hiding|conceal)\b.*\b(planet|asteroid|meteor)\b'
            ],
            "health_conspiracies": [
                r'\b(vaccine|vaccination)\b.*\b(autism|mind\s+control|track|chip|5g)\b',
                r'\b(cure\s+for\s+cancer|cure\s+for\s+all\s+disease)\b.*\b(suppressed|hidden|secret)\b',
                r'\b(miracle\s+cure|miracle\s+mineral\s+solution|mms)\b'
            ],
            "political_conspiracies": [
                r'\b(deep\s+state|cabal|illuminati|new\s+world\s+order|nwo)\b',
                r'\b(government|cia|fbi)\b.*\b(controlling|control|manipulate)\b.*\b(weather|minds|population)\b',
                r'\b(microchip|rfid)\b.*\b(implant|track|control)\b.*\b(human|people|citizen)\b'
            ]
        }
        
        logger.info("SourceCredibilityAnalyzer initialized successfully")
    
    def _load_credibility_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Load the credibility database
        
        In a real implementation, this would load from a file or external API
        
        Returns:
            Dictionary with domain credibility information
        """
        # This is a simplified mock database for demonstration purposes
        # In a real system, this would be a comprehensive database of news sources
        
        db = {
            # Major reputable news sources
            "bbc.com": {"score": 0.95, "category": "RELIABLE", "bias": "SLIGHT_LEFT"},
            "reuters.com": {"score": 0.97, "category": "RELIABLE", "bias": "CENTER"},
            "apnews.com": {"score": 0.96, "category": "RELIABLE", "bias": "CENTER"},
            "npr.org": {"score": 0.92, "category": "RELIABLE", "bias": "SLIGHT_LEFT"},
            "economist.com": {"score": 0.93, "category": "RELIABLE", "bias": "CENTER"},
            "wsj.com": {"score": 0.92, "category": "RELIABLE", "bias": "SLIGHT_RIGHT"},
            "nytimes.com": {"score": 0.90, "category": "MOSTLY_RELIABLE", "bias": "LEFT"},
            "washingtonpost.com": {"score": 0.89, "category": "MOSTLY_RELIABLE", "bias": "LEFT"},
            "theguardian.com": {"score": 0.88, "category": "MOSTLY_RELIABLE", "bias": "LEFT"},
            "cnn.com": {"score": 0.80, "category": "MIXED", "bias": "LEFT"},
            "foxnews.com": {"score": 0.70, "category": "MIXED", "bias": "RIGHT"},
            
            # Known misinformation sources
            "infowars.com": {"score": 0.05, "category": "UNRELIABLE", "bias": "EXTREME_RIGHT"},
            "naturalnews.com": {"score": 0.10, "category": "UNRELIABLE", "bias": "EXTREME_RIGHT"},
            "breitbart.com": {"score": 0.40, "category": "QUESTIONABLE", "bias": "EXTREME_RIGHT"},
            
            # Fact-checking sites
            "snopes.com": {"score": 0.95, "category": "FACT_CHECKER", "bias": "SLIGHT_LEFT"},
            "factcheck.org": {"score": 0.95, "category": "FACT_CHECKER", "bias": "SLIGHT_LEFT"},
            "politifact.com": {"score": 0.93, "category": "FACT_CHECKER", "bias": "SLIGHT_LEFT"},
        }
        
        return db
    
    def analyze_source(self, url: str) -> Dict[str, Any]:
        """
        Analyze the credibility of a source based on its URL
        
        Args:
            url: URL of the source
            
        Returns:
            Dictionary with credibility information
        """
        try:
            logger.info(f"Analyzing source credibility: {url}")
            
            # Parse URL to get domain
            domain = self._extract_domain(url)
            if not domain:
                return self._create_unknown_result(url, "Invalid URL")
            
            # Check if domain is in known fake news list
            for fake_domain in self.fake_news_domains:
                if fake_domain in domain.lower():
                    logger.warning(f"Source domain {domain} matches known fake news pattern: {fake_domain}")
                    return self._create_unknown_result(url, "Matches known fake news pattern")
            
            # Check if domain is in known credible list
            for credible_domain in self.credible_domains:
                if credible_domain in domain.lower():
                    logger.info(f"Source domain {domain} matches known credible source: {credible_domain}")
                    return self._create_unknown_result(url, "Matches known credible source")
            
            # Check if domain is in our database
            base_domain = self._get_base_domain(domain)
            if base_domain in self.credibility_db:
                db_entry = self.credibility_db[base_domain].copy()
                
                result = {
                    "url": url,
                    "domain": domain,
                    "base_domain": base_domain,
                    "credibility_score": db_entry["score"],
                    "category": db_entry["category"],
                    "bias": db_entry.get("bias", "UNKNOWN"),
                    "source": "database",
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.info(f"Source found in database: {base_domain} - Score: {db_entry['score']}")
                return result
            
            # If not in database, check if it's in our cache
            if domain in self.domain_cache:
                logger.info(f"Source found in cache: {domain}")
                return self.domain_cache[domain]
            
            # Need to analyze the domain
            domain_info = self._analyze_domain(domain, url)
            
            # Store in cache
            self.domain_cache[domain] = domain_info
            
            return domain_info
            
        except Exception as e:
            logger.error(f"Error analyzing source {url}: {str(e)}")
            return self._create_unknown_result(url, str(e))
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            # Handle URLs without scheme
            if not url.startswith('http'):
                url = 'https://' + url
                
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Remove www. prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
                
            return domain
        except:
            return ""
    
    def _get_base_domain(self, domain: str) -> str:
        """Get base domain (e.g., nytimes.com from subdomain.nytimes.com)"""
        parts = domain.split('.')
        
        # Handle common domain patterns
        if len(parts) > 2:
            # Check for country-specific domains like co.uk
            if parts[-2] in ['co', 'com', 'org', 'net', 'gov', 'edu'] and parts[-1] in ['uk', 'au', 'nz', 'jp']:
                if len(parts) > 3:
                    return '.'.join(parts[-3:])
                return domain
            else:
                return '.'.join(parts[-2:])
        
        return domain
    
    def _create_unknown_result(self, url: str, reason: str = "") -> Dict[str, Any]:
        """Create result for unknown sources"""
        domain = self._extract_domain(url) or "unknown"
        
        result = {
            "url": url,
            "domain": domain,
            "base_domain": self._get_base_domain(domain),
            "credibility_score": 0.5,  # Neutral score for unknown sources
            "category": "UNKNOWN",
            "bias": "UNKNOWN",
            "source": "analysis",
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def _respect_rate_limit(self) -> None:
        """Respect rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
    
    def _analyze_domain(self, domain: str, url: str) -> Dict[str, Any]:
        """
        Analyze an unknown domain
        
        Args:
            domain: Domain to analyze
            url: Original URL
            
        Returns:
            Dictionary with credibility analysis
        """
        try:
            # Respect rate limiting
            self._respect_rate_limit()
            
            # In a real implementation, this would:
            # 1. Check domain age and registration info (WHOIS)
            # 2. Look for about page, contact info, transparency policy
            # 3. Check for HTTPS
            # 4. Look for privacy policy and terms of service
            # 5. Check if site has social media presence
            # 6. Look for author information on articles
            # 7. Check for citations and sources in content
            
            # For this demo, we'll do some basic checks
            
            # Check for HTTPS
            uses_https = url.startswith('https://')
            
            # Try to fetch and analyze homepage
            try:
                # Respect rate limiting
                self._respect_rate_limit()
                
                response = requests.get(f"https://{domain}", 
                                      headers=self.headers, 
                                      timeout=10, 
                                      allow_redirects=True)
                
                self.last_request_time = time.time()
                
                if response.status_code == 200:
                    # Check for contact info
                    has_contact_info = 'contact' in response.text.lower()
                    
                    # Check for about page
                    has_about_page = 'about' in response.text.lower()
                    
                    # Check for privacy policy
                    has_privacy_policy = 'privacy' in response.text.lower()
                    
                    # Update scores based on findings
                    base_score = 0.5  # Start with neutral score
                    
                    if uses_https:
                        base_score += 0.05
                    if has_contact_info:
                        base_score += 0.05
                    if has_about_page:
                        base_score += 0.05
                    if has_privacy_policy:
                        base_score += 0.05
                    
                    # In a real system, more sophisticated analysis would happen here
                    
                    # Determine category based on score
                    category = "UNKNOWN"
                    if base_score >= 0.8:
                        category = "LIKELY_RELIABLE"
                    elif base_score >= 0.6:
                        category = "MIXED"
                    elif base_score < 0.4:
                        category = "QUESTIONABLE"
                    
                    return {
                        "url": url,
                        "domain": domain,
                        "base_domain": self._get_base_domain(domain),
                        "credibility_score": base_score,
                        "category": category,
                        "bias": "UNKNOWN",  # Bias detection requires more analysis
                        "features": {
                            "https": uses_https,
                            "contact_info": has_contact_info,
                            "about_page": has_about_page,
                            "privacy_policy": has_privacy_policy
                        },
                        "source": "analysis",
                        "timestamp": datetime.now().isoformat()
                    }
                
            except requests.exceptions.RequestException:
                pass
            
            # If we couldn't analyze the site, provide a minimal result
            return {
                "url": url,
                "domain": domain,
                "base_domain": self._get_base_domain(domain),
                "credibility_score": 0.5,
                "category": "UNKNOWN",
                "bias": "UNKNOWN",
                "source": "limited_analysis",
                "features": {
                    "https": uses_https
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error during domain analysis: {str(e)}")
            return self._create_unknown_result(url, str(e))
    
    def get_credibility_score(self, url: str) -> Optional[float]:
        """
        Get a simple credibility score for a URL
        
        Args:
            url: The URL to analyze
            
        Returns:
            Credibility score between 0 (not credible) and 1 (highly credible),
            or None if the URL could not be analyzed
        """
        if not url:
            return None
            
        try:
            # Extract domain from URL
            extracted = tldextract.extract(url)
            domain = f"{extracted.domain}.{extracted.suffix}"
            
            # Log the domain being analyzed
            logger.debug(f"Analyzing source credibility for domain: {domain}")
            
            # If in known credible sources, return that score
            if domain in self.credible_sources:
                logger.debug(f"Domain {domain} found in credible sources database with score {self.credible_sources[domain]}")
                return self.credible_sources[domain]
            
            # If in known non-credible sources, return that score
            if domain in self.non_credible_sources:
                logger.debug(f"Domain {domain} found in non-credible sources database with score {self.non_credible_sources[domain]}")
                return self.non_credible_sources[domain]
            
            # If not in database, analyze the domain
            score = 0.5  # Start with neutral score
            
            # Check for suspicious keywords in domain
            for keyword in self.suspicious_keywords:
                if keyword.lower() in domain.lower():
                    score -= 0.1
                    logger.debug(f"Suspicious keyword found in domain: {keyword}")
                    break  # Only penalize once for keywords
            
            # Check for suspicious TLDs
            for tld in self.suspicious_tlds:
                if domain.lower().endswith(tld):
                    score -= 0.1
                    logger.debug(f"Suspicious TLD found: {tld}")
                    break  # Only penalize once for TLD
            
            # Check for patterns that indicate fake news domains
            for pattern in self.fake_domain_patterns:
                if re.search(pattern, domain.lower()):
                    score -= 0.2
                    logger.debug(f"Domain matches fake news pattern: {pattern}")
                    break  # Only penalize once for patterns
            
            # If subdomain contains suspicious words (like "truth.example.com")
            if extracted.subdomain:
                for keyword in self.suspicious_keywords:
                    if keyword.lower() in extracted.subdomain.lower():
                        score -= 0.05
                        logger.debug(f"Suspicious keyword found in subdomain: {keyword}")
                        break
            
            # Apply additional checks for obviously fake domains
            if "fake" in domain.lower() or "hoax" in domain.lower():
                score = 0.1  # Very low credibility
                logger.debug("Domain explicitly contains 'fake' or 'hoax'")
            
            # Check if the domain is brand new (may not be feasible in all environments)
            # This would require additional API calls to WHOIS services
            
            # Try to fetch site content for further analysis if score is ambiguous
            if 0.3 <= score <= 0.7:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    response = requests.get(url, headers=headers, timeout=5)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Check for "About Us" transparency
                        about_links = soup.find_all('a', text=re.compile(r'about', re.I))
                        if not about_links:
                            score -= 0.05
                            logger.debug("No 'About Us' link found")
                        
                        # Check for contact information
                        contact_links = soup.find_all('a', text=re.compile(r'contact', re.I))
                        if not contact_links:
                            score -= 0.05
                            logger.debug("No contact information found")
                        
                        # Check for excessive ads (simplified check)
                        iframes = soup.find_all('iframe')
                        ad_divs = soup.find_all('div', {'class': re.compile(r'ad|advertisement', re.I)})
                        if len(iframes) + len(ad_divs) > 10:
                            score -= 0.1
                            logger.debug("Excessive number of ads detected")
                        
                        # Check for sensational headlines
                        headlines = soup.find_all(['h1', 'h2', 'h3'])
                        sensational_count = 0
                        for headline in headlines:
                            text = headline.get_text().lower()
                            if any(phrase in text for phrase in ['shocking', 'you won\'t believe', 'incredible', 
                                                              'mind-blowing', 'secret', 'they don\'t want you to know']):
                                sensational_count += 1
                        
                        if sensational_count > 2:
                            score -= 0.15
                            logger.debug(f"Multiple sensational headlines detected: {sensational_count}")
                except Exception as e:
                    logger.warning(f"Error fetching website content for credibility analysis: {str(e)}")
                    # Slightly penalize for inaccessible content
                    score -= 0.05
            
            # Ensure score stays within bounds
            score = max(0.1, min(0.7, score))  # Unknown sources can't score higher than 0.7
            logger.info(f"Final credibility score for {domain}: {score}")
            return score
            
        except Exception as e:
            logger.error(f"Error in source credibility analysis: {str(e)}")
            return 0.5  # Return neutral score on error
    
    def check_for_hoax_patterns(self, text):
        """Check if the text contains common hoax patterns"""
        results = {}
        for category, patterns in self.hoax_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    if category not in results:
                        results[category] = []
                    results[category].append(pattern)
        
        if results:
            logger.warning(f"Found hoax patterns in text: {results}")
            return True, results
        return False, {}
            
    def get_domain_type(self, url):
        """Categorize the domain type based on TLD and other factors"""
        extracted = tldextract.extract(url)
        tld = f".{extracted.suffix}"
        
        if tld in ['.gov', '.edu', '.mil']:
            return "official", 0.9
        elif tld == '.org':
            # Check if it's a known fact-checking organization
            if extracted.domain in ['snopes', 'factcheck', 'politifact']:
                return "fact_checker", 0.9
            return "organization", 0.7
        elif tld in ['.com', '.net']:
            # Check if it's a major news organization
            if extracted.domain in ['cnn', 'bbc', 'nytimes', 'washingtonpost', 'reuters', 'ap']:
                return "mainstream_news", 0.85
            return "commercial", 0.5
        elif tld in self.suspicious_tlds:
            return "suspicious", 0.3
        else:
            return "other", 0.5 