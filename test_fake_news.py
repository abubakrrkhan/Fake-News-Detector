#!/usr/bin/env python
# coding: utf-8

"""
Test script for Fake News Detection System
This script tests various components of the fake news detection system
including astronomical hoaxes about blackouts.
"""

import sys
import os
import requests
import json
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logger.add("logs/tests.log", rotation="500 MB", level="INFO")

# Test if the API is running
def test_api_connection():
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            logger.info("API connection successful.")
            return True
        else:
            logger.error(f"API connection failed. Status code: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"API connection failed with error: {str(e)}")
        return False

# Test the fake news detection endpoint with different test cases
def test_fake_news_detection():
    endpoint = "http://localhost:8000/detect"
    
    # Test cases
    test_cases = [
        {
            "name": "Planetary Alignment Blackout Hoax",
            "request": {
                "text": "NASA confirms that a planetary alignment of Venus and Jupiter in November will cause a nationwide blackout. The rare alignment will cause a gravitational effect on the sun, resulting in solar flares that will disrupt electrical grids across the world. NASA scientists are warning people to prepare for up to 15 days without electricity.",
                "title": "NASA Warns of November Blackout Due to Planetary Alignment",
                "source_url": "fakenewsmedia.net/nasa-blackout-warning"
            },
            "expected_verdict": "FAKE"
        },
        {
            "name": "Factual Science News",
            "request": {
                "text": "A new study published in the journal Nature reveals that climate change is accelerating faster than previously thought. The research, conducted by scientists across 10 countries, compiled data from satellite observations and ground measurements over the past 50 years. The findings suggest that current models may have underestimated the rate of warming by approximately 0.1°C per decade.",
                "title": "New Research Shows Climate Change Accelerating Faster Than Expected",
                "source_url": "nature.com/articles/climate-research-2025"
            },
            "expected_verdict": "REAL"
        },
        {
            "name": "Health Conspiracy",
            "request": {
                "text": "BREAKING: Whistleblower from major pharmaceutical company reveals secret cure for all cancers has been suppressed for decades. The miracle cure, based on a natural compound found in a rare Amazonian plant, has been 100% effective in clinical trials but is being hidden from the public to protect billion-dollar cancer treatment industry profits.",
                "title": "EXPOSED: Secret Cancer Cure THEY Don't Want You to Know About",
                "source_url": "healthtruthrevealed.info/cancer-cure-conspiracy"
            },
            "expected_verdict": "FAKE"
        }
    ]
    
    results = []
    
    for test in test_cases:
        try:
            logger.info(f"Testing case: {test['name']}")
            
            # Send request to API
            response = requests.post(
                endpoint,
                json=test["request"],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                logger.error(f"Test failed with status code {response.status_code}")
                logger.error(f"Response: {response.text}")
                results.append({
                    "test": test["name"],
                    "status": "ERROR",
                    "error": f"API returned status code {response.status_code}"
                })
                continue
            
            # Parse response
            result = response.json()
            
            # Check if verdict matches expected
            actual_verdict = result["verdict"]
            expected_verdict = test["expected_verdict"]
            
            is_match = actual_verdict == expected_verdict or (
                expected_verdict == "FAKE" and "FAKE" in actual_verdict or
                expected_verdict == "REAL" and ("REAL" in actual_verdict or "TRUE" in actual_verdict)
            )
            
            if is_match:
                logger.info(f"Test passed: {test['name']} - Expected: {expected_verdict}, Got: {actual_verdict}")
                results.append({
                    "test": test["name"],
                    "status": "PASS",
                    "expected": expected_verdict,
                    "actual": actual_verdict,
                    "confidence": result["confidence"],
                    "explanation": result["explanation"]
                })
            else:
                logger.error(f"Test failed: {test['name']} - Expected: {expected_verdict}, Got: {actual_verdict}")
                results.append({
                    "test": test["name"],
                    "status": "FAIL",
                    "expected": expected_verdict,
                    "actual": actual_verdict,
                    "confidence": result["confidence"],
                    "explanation": result["explanation"]
                })
                
        except Exception as e:
            logger.error(f"Error testing {test['name']}: {str(e)}")
            results.append({
                "test": test["name"],
                "status": "ERROR",
                "error": str(e)
            })
    
    # Summarize results
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    
    logger.info(f"Test summary: {passed} passed, {failed} failed, {errors} errors")
    logger.info(f"Detailed results: {json.dumps(results, indent=2)}")
    
    return results

# Test the source credibility analyzer specifically
def test_source_credibility():
    try:
        from utils.source_credibility import SourceCredibilityAnalyzer
        
        analyzer = SourceCredibilityAnalyzer()
        
        test_urls = [
            {"url": "https://www.reuters.com/article/example", "expected_range": (0.8, 1.0)},
            {"url": "https://www.fakenewsmedia.net/article", "expected_range": (0.0, 0.3)},
            {"url": "https://www.planetalignment-truth.com/blackout", "expected_range": (0.0, 0.3)},
            {"url": "https://www.cnn.com/article", "expected_range": (0.7, 0.9)}
        ]
        
        results = []
        
        for test in test_urls:
            url = test["url"]
            expected_min, expected_max = test["expected_range"]
            
            score = analyzer.get_credibility_score(url)
            
            is_in_range = expected_min <= score <= expected_max
            
            if is_in_range:
                logger.info(f"Source credibility test passed for {url}: {score} (expected range: {expected_min}-{expected_max})")
                results.append({
                    "url": url,
                    "status": "PASS",
                    "score": score,
                    "expected_range": test["expected_range"]
                })
            else:
                logger.error(f"Source credibility test failed for {url}: {score} (expected range: {expected_min}-{expected_max})")
                results.append({
                    "url": url,
                    "status": "FAIL",
                    "score": score,
                    "expected_range": test["expected_range"]
                })
        
        logger.info(f"Source credibility test results: {json.dumps(results, indent=2)}")
        return results
        
    except Exception as e:
        logger.error(f"Error in source credibility test: {str(e)}")
        return None

# Test astronomical hoax patterns specifically
def test_astronomical_hoax_detection():
    try:
        from utils.source_credibility import SourceCredibilityAnalyzer
        
        analyzer = SourceCredibilityAnalyzer()
        
        test_texts = [
            {
                "text": "NASA confirms that Venus and Jupiter will align in November, causing massive power outages across the world. The gravitational pull will affect the sun and cause solar flares.",
                "expected": True
            },
            {
                "text": "Scientists are studying the upcoming conjunction of Venus and Jupiter, which will be visible in the night sky. This is a regular astronomical event with no effect on Earth's power grid.",
                "expected": False
            },
            {
                "text": "The planetary alignment next month will create a massive energy disruption leading to blackouts worldwide. Governments are hiding this information from the public.",
                "expected": True
            }
        ]
        
        results = []
        
        for test in test_texts:
            text = test["text"]
            expected = test["expected"]
            
            is_hoax, patterns = analyzer.check_for_hoax_patterns(text)
            
            if is_hoax == expected:
                logger.info(f"Astronomical hoax test passed: {is_hoax} (expected: {expected})")
                if is_hoax:
                    logger.info(f"Detected patterns: {patterns}")
                results.append({
                    "text": text[:50] + "...",
                    "status": "PASS",
                    "is_hoax": is_hoax,
                    "expected": expected,
                    "patterns": patterns if is_hoax else None
                })
            else:
                logger.error(f"Astronomical hoax test failed: {is_hoax} (expected: {expected})")
                results.append({
                    "text": text[:50] + "...",
                    "status": "FAIL",
                    "is_hoax": is_hoax,
                    "expected": expected,
                    "patterns": patterns if is_hoax else None
                })
        
        logger.info(f"Astronomical hoax detection test results: {json.dumps(results, indent=2)}")
        return results
        
    except Exception as e:
        logger.error(f"Error in astronomical hoax detection test: {str(e)}")
        return None

if __name__ == "__main__":
    print("Starting Fake News Detection System tests...")
    
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Run tests
    api_running = test_api_connection()
    
    if api_running:
        print("Testing fake news detection API...")
        fake_news_results = test_fake_news_detection()
        
        # Print summary of fake news detection results
        passes = sum(1 for r in fake_news_results if r["status"] == "PASS")
        total = len(fake_news_results)
        print(f"Fake news detection tests: {passes}/{total} passed")
    else:
        print("Skipping API tests as the API is not running.")
        print("Make sure to start the API with 'python run.py' before running the tests.")
    
    # Test components directly
    print("\nTesting source credibility analyzer...")
    credibility_results = test_source_credibility()
    if credibility_results:
        passes = sum(1 for r in credibility_results if r["status"] == "PASS")
        total = len(credibility_results)
        print(f"Source credibility tests: {passes}/{total} passed")
    
    print("\nTesting astronomical hoax detection...")
    hoax_results = test_astronomical_hoax_detection()
    if hoax_results:
        passes = sum(1 for r in hoax_results if r["status"] == "PASS")
        total = len(hoax_results)
        print(f"Astronomical hoax detection tests: {passes}/{total} passed")
    
    print("\nAll tests completed. See logs/tests.log for details.") 