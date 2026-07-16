@echo off
setlocal

set PROJECT_ID=kr-ai-hackathon26gmp-2216
set REGION=asia-northeast3

echo Configuring gcloud for project %PROJECT_ID%...
call gcloud config set project %PROJECT_ID%

echo Enabling required GCP APIs...
call gcloud services enable cloudfunctions.googleapis.com cloudscheduler.googleapis.com run.googleapis.com cloudbuild.googleapis.com

echo.
echo =======================================================
echo Deploying the Dashboard API to Cloud Run
echo This will serve the Dashboard UI and the API endpoints.
echo =======================================================
echo.

call gcloud run deploy sse-agent-dashboard ^
  --source . ^
  --region %REGION% ^
  --allow-unauthenticated ^
  --port 8000

echo.
echo Retrieving the Cloud Run URL...
for /f "tokens=*" %%i in ('gcloud run services describe sse-agent-dashboard --platform managed --region %REGION% --format="value(status.url)"') do set SERVICE_URL=%%i

echo Cloud Run Service URL: %SERVICE_URL%

echo.
echo Creating Cloud Scheduler Job to trigger Module A daily at 8 AM...
call gcloud scheduler jobs create http trigger-module-a-daily ^
  --schedule="0 8 * * *" ^
  --uri="%SERVICE_URL%/api/launch" ^
  --http-method=POST ^
  --time-zone="Asia/Seoul" ^
  --location=%REGION% ^
  --quiet

echo.
echo Deployment script finished!
endlocal
pause
