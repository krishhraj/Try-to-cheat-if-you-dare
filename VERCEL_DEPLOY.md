# 🚀 Vercel Deployment Guide

This guide will help you deploy your FastAPI application to Vercel.

## Prerequisites

1. A GitHub account with your repository pushed
2. A Vercel account (sign up at [vercel.com](https://vercel.com))
3. Vercel CLI (optional, for local testing)

## Deployment Steps

### Method 1: Deploy via Vercel Dashboard (Recommended)

1. **Sign in to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Sign in with your GitHub account

2. **Import Project**
   - Click "Add New..." → "Project"
   - Select your GitHub repository: `krishhraj/Try-to-cheat-if-you-dare`
   - Click "Import"

3. **Configure Project**
   - **Framework Preset**: Leave as "Other" or select "FastAPI" if available
   - **Root Directory**: Leave as `.` (root)
   - **Build Command**: Leave empty (no build needed for Python)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

4. **Environment Variables** (if needed)
   - Add any environment variables your app needs
   - For this project, none are required by default

5. **Deploy**
   - Click "Deploy"
   - Wait for the build to complete (~2-5 minutes)
   - Your API will be live at: `https://your-project.vercel.app`

### Method 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel
   ```
   - Follow the prompts
   - For production deployment: `vercel --prod`

## Project Structure for Vercel

```
.
├── api/
│   └── index.py          # Vercel serverless function entrypoint
├── backend/
│   ├── app/
│   │   └── main.py       # FastAPI application
│   └── models/
│       └── cheat_detector.py
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── runtime.txt          # Python version (optional)
```

## API Endpoints

After deployment, your API will be available at:
- **Root**: `https://your-project.vercel.app/`
- **Health Check**: `https://your-project.vercel.app/health`
- **API Docs**: `https://your-project.vercel.app/docs`
- **Detect Image**: `POST https://your-project.vercel.app/detect/image`
- **Detect Video**: `POST https://your-project.vercel.app/detect/video`
- **Stats**: `GET https://your-project.vercel.app/stats`

## Important Notes

### ⚠️ Limitations

1. **WebSocket Support**: 
   - WebSocket endpoints (`/ws/detect`) may not work on Vercel's serverless functions
   - Vercel has limited WebSocket support (requires Hobby plan or higher)
   - Consider using polling or separate WebSocket service for real-time features

2. **File Size Limits**:
   - Serverless functions have execution time limits (max 60 seconds for Pro)
   - Large video files may timeout
   - Consider using external storage (S3, Cloudinary) for large files

3. **Cold Starts**:
   - First request may be slower due to serverless cold starts
   - Subsequent requests are much faster

4. **OpenCV**:
   - Using `opencv-python-headless` is recommended for serverless
   - The current requirements.txt uses `opencv-python` which should work but is larger

### 🔧 Troubleshooting

**Build Fails:**
- Check that all dependencies in `requirements.txt` are compatible
- Ensure Python version in `runtime.txt` is supported (3.8, 3.9, 3.10, or 3.11)

**Import Errors:**
- Verify that `api/index.py` correctly imports the FastAPI app
- Check that all paths are correct relative to the project root

**Timeout Errors:**
- Large file processing may timeout
- Consider increasing timeout in `vercel.json` (requires Pro plan)
- Or optimize processing (e.g., resize images before processing)

**Module Not Found:**
- Ensure all dependencies are in `requirements.txt`
- Check that `.vercelignore` isn't excluding necessary files

## Testing Locally with Vercel CLI

```bash
# Install dependencies
pip install -r requirements.txt

# Test with Vercel dev server
vercel dev
```

This will start a local server that mimics Vercel's environment.

## Custom Domain

1. Go to your project settings in Vercel dashboard
2. Click "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions

## Environment Variables

To add environment variables:

1. Go to Project Settings → Environment Variables
2. Add variables for Production, Preview, and Development
3. Redeploy for changes to take effect

## Continuous Deployment

Vercel automatically deploys:
- **Production**: When you push to `main` branch
- **Preview**: For every pull request and branch push

## Monitoring

- View logs in Vercel dashboard → Project → Deployments → Function Logs
- Monitor function execution time and errors
- Check analytics for API usage

## Resources

- [Vercel Python Documentation](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [FastAPI on Vercel](https://vercel.com/guides/deploying-fastapi-with-vercel)
- [Vercel Serverless Function Limits](https://vercel.com/docs/concepts/functions/serverless-functions)

---

**Need Help?** Check the Vercel documentation or create an issue in the repository.

