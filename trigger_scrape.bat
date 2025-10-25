@echo off
REM Trigger job scraping from Railway
REM Usage: trigger_scrape.bat

echo ============================================================
echo JOB AGGREGATION - RAILWAY SCRAPER
echo ============================================================
echo.

python trigger_scrape.py --url https://web-production-94ca.up.railway.app

echo.
echo ============================================================
echo Scraping complete!
echo ============================================================
pause
