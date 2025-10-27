@echo off
cd ..
echo ==========================================
echo AWS LangChain Chatbot - Installation
echo ==========================================
echo.

REM Upgrade pip first
echo Step 1: Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo Step 2: Installing dependencies...
pip install -r requirements.txt
echo.

echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Create .env file with AWS credentials
echo 2. Enable Amazon Nova in AWS Console
echo 3. Setup DynamoDB: python setup_dynamodb.py
echo 4. Start API: python api.py
echo 5. Visit: http://localhost:8000/docs
echo.
echo Documentation:
echo - Main Guide: README.md
echo - API Examples: docs\API_EXAMPLES.md
echo - Model Config: docs\CHANGE_MODEL.md
echo.
pause

