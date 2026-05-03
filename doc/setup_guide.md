# Detailed Setup Guide

## Getting IBM Watson API Credentials

### Step 1: Create IBM Cloud Account
1. Go to [IBM Cloud](https://cloud.ibm.com)
2. Click "Create an IBM Cloud account"
3. Fill in your details (free tier available)

### Step 2: Create Natural Language Understanding Service
1. Log into IBM Cloud
2. Click "Create resource"
3. Search for "Natural Language Understanding"
4. Select the service
5. Choose the "Lite" plan (free)
6. Click "Create"

### Step 3: Get API Credentials
1. Go to your Resource List
2. Click on your Natural Language Understanding service
3. Click "Service credentials"
4. Click "New credential"
5. Click "Add"
6. Click "View credentials"
7. Copy the `apikey` and `url` values

### Step 4: Configure the Application

**Option A: Using config.py file**
```python
API_KEY = "your-copied-apikey"
SERVICE_URL = "your-copied-url"