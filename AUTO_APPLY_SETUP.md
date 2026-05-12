# 🚀 Easy Apply Automation - Complete Setup Guide

## ⚠️ **IMPORTANT: Setup Required Before Auto-Apply**

The Auto-Apply feature uses intelligent AI to answer questions and fill forms automatically. You **MUST** configure your profile first!

---

## 📋 **Step-by-Step Setup**

### **Step 1: Configure User Profile** (Required)

The Easy Apply bot needs your personal information to answer job application questions. Configure this via the API:

#### **Option A: Using API Docs (Recommended)**

1. Open http://localhost:8000/docs
2. Find `POST /api/config/user`
3. Click "Try it out"
4. Use this template:

```json
{
  "section": "personal",
  "updates": {
    "first_name": "Your First Name",
    "last_name": "Your Last Name",
    "email": "your.email@example.com",
    "phone": "+1234567890",
    "location": "San Francisco, CA",
    "city": "San Francisco",
    "zip_code": "94102",
    "linkedin_url": "https://linkedin.com/in/yourprofile",
    "github_url": "https://github.com/yourusername",
    "portfolio_url": "https://yourwebsite.com"
  }
}
```

5. Click "Execute"

#### **Option B: Using curl**

```bash
curl -X POST http://localhost:8000/api/config/user \
  -H "Content-Type: application/json" \
  -d '{
    "section": "personal",
    "updates": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "location": "San Francisco, CA"
    }
  }'
```

---

### **Step 2: Configure Professional Information** (Required)

```json
{
  "section": "professional",
  "updates": {
    "current_company": "Tech Corp",
    "current_title": "Software Engineer",
    "years_of_experience": 5,
    "skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker"],
    "industry": "Technology"
  }
}
```

---

### **Step 3: Configure LinkedIn Credentials** (Required for Auto-Apply)

```json
{
  "section": "linkedin",
  "updates": {
    "email": "your-linkedin-email@example.com",
    "password": "your-linkedin-password"
  }
}
```

⚠️ **Security Note:** Credentials are stored locally in `backend/data/user_config.json`

---

### **Step 4: Set Resume Path** (Required)

```json
{
  "section": "application",
  "updates": {
    "resume_path": "C:/path/to/your/resume.pdf",
    "auto_follow_companies": false,
    "max_applications_per_day": 50
  }
}
```

---

### **Step 5: Configure Work Status** (Recommended)

```json
{
  "section": "work_status",
  "updates": {
    "work_authorization": "Yes",
    "requires_visa_sponsorship": "No",
    "currently_employed": "Yes",
    "notice_period": "2 weeks",
    "willing_to_relocate": "Yes"
  }
}
```

---

### **Step 6: Configure AI Provider** (Already set if you have OPENAI_API_KEY in .env)

```json
{
  "section": "ai",
  "updates": {
    "primary_provider": "openai",
    "openai_api_key": "sk-your-key-here",
    "openai_model": "gpt-3.5-turbo"
  }
}
```

---

## ✅ **Verify Configuration**

Check if your configuration is complete:

```bash
curl http://localhost:8000/api/config/validate
```

Expected response:
```json
{
  "success": true,
  "is_valid": true,
  "issues": {
    "missing": [],
    "invalid": []
  }
}
```

If `is_valid` is `false`, check the `issues` field and fix missing/invalid fields.

---

## 🎯 **Using Auto-Apply**

### **Method 1: Via Frontend UI** (Easiest)

1. Go to http://localhost:3000/jobs/search
2. Enter keywords (e.g., "Software Engineer")
3. Select location (e.g., "United States")
4. Set max jobs (e.g., 50)
5. **Select "Auto-Apply" mode** (important!)
6. Click "Searching LinkedIn..."
7. Wait for confirmation: "Auto-Apply Started!"
8. Applications run in background

### **Method 2: Via API**

```bash
curl -X POST http://localhost:8000/api/jobs/easy-apply/start \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "Software Engineer",
    "location": "United States",
    "max_applications": 10,
    "easy_apply_only": true,
    "use_advanced_bot": true
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Applying to 10 Easy Apply jobs in background...",
  "jobs_found": 25,
  "easy_apply_jobs": 10
}
```

---

## 📊 **Check Application Status**

### View Applications in Database

```bash
curl http://localhost:8000/api/jobs/applications
```

### Check Auto-Apply Statistics

```bash
curl http://localhost:8000/api/jobs/easy-apply/stats
```

Expected response:
```json
{
  "success": true,
  "stats": {
    "applications_attempted": 10,
    "applications_successful": 8,
    "applications_failed": 2,
    "questions_answered": 45,
    "resume_uploaded": 7
  }
}
```

---

## 🐛 **Troubleshooting**

### Issue 1: "User configuration is incomplete"

**Problem:** Missing required fields

**Solution:**
1. Run `/api/config/validate` to see what's missing
2. Configure missing fields using `/api/config/user`
3. Required fields: `first_name`, `last_name`, `email`, `phone`, `location`, `openai_api_key`

### Issue 2: "No Easy Apply jobs found"

**Problem:** All jobs in search results require external applications

**Solution:**
- Try different keywords
- Try different locations
- LinkedIn might not have many Easy Apply jobs for your search

### Issue 3: "Failed to login to LinkedIn"

**Problem:** Invalid LinkedIn credentials or verification required

**Solution:**
1. Check your LinkedIn email/password in config
2. LinkedIn might require manual verification (CAPTCHA, 2FA)
3. Try logging in manually first at https://linkedin.com

### Issue 4: Only found 25 jobs instead of 50

**Problem:** LinkedIn limitation for specific search

**Solution:**
- This is normal - LinkedIn only shows jobs matching your filters
- Try broader keywords or different locations
- The scraper will get all available jobs (could be less than requested)

### Issue 5: "Resume not found"

**Problem:** Resume path is invalid

**Solution:**
1. Use absolute path: `C:/Users/YourName/Desktop/resume.pdf`
2. Make sure file exists and is PDF format
3. Update resume_path in config

---

## 📝 **What the Bot Does**

When you click "Auto-Apply", here's what happens:

1. **Searches LinkedIn** for jobs matching your criteria
2. **Filters Easy Apply jobs** only (skips external applications)
3. **Logs into LinkedIn** using your credentials
4. **For each job:**
   - Clicks "Easy Apply" button
   - Answers ALL questions intelligently:
     - Personal info (name, email, phone)
     - Work experience (years, current company)
     - Work authorization
     - Salary expectations
     - Why this company/role
   - Uploads your resume if prompted
   - Follows company if configured
   - Navigates through multi-step forms (Next → Review → Submit)
   - Takes screenshot if application fails
   - Saves all data to database
5. **Returns summary** of applications

---

## 🎓 **Question Answering Examples**

The bot can answer 30+ types of questions:

| Question Type | Example | Bot Answer (from your config) |
|--------------|---------|-------------------------------|
| Name | "What's your name?" | "John Doe" |
| Email | "Email address" | "john@example.com" |
| Phone | "Phone number" | "+1234567890" |
| Experience | "Years of experience?" | "5" |
| Current Company | "Current employer?" | "Tech Corp" |
| Work Authorization | "Authorized to work in US?" | "Yes" |
| Visa Sponsorship | "Require visa sponsorship?" | "No" |
| Salary | "Expected salary?" | From your config |
| Why this company? | "Why do you want to work here?" | AI-generated based on job |

**Unknown questions** are answered by AI (OpenAI/DeepSeek/Gemini)

---

## 🔒 **Security Notes**

- Credentials are stored in `backend/data/user_config.json`
- File is NOT encrypted (consider using environment variables for production)
- Screenshots saved in `backend/screenshots/` (may contain sensitive data)
- Database tracks all applications in `data/linkedin_automation.db`

---

## 📈 **Best Practices**

1. **Start small:** Test with 5-10 jobs first
2. **Verify config:** Always run `/api/config/validate` before bulk applying
3. **Monitor applications:** Check database or API for results
4. **Review screenshots:** Failed applications have screenshots for debugging
5. **Update resume:** Keep resume path current
6. **Use delays:** System waits 5 seconds between applications (configurable)
7. **Check daily limits:** LinkedIn may limit applications per day

---

## 🎉 **Success Indicators**

You know it's working when you see:

✅ "Auto-Apply Started!" alert
✅ Background process starts applying
✅ Applications appear in database (`/api/jobs/applications`)
✅ Stats show successful applications (`/api/jobs/easy-apply/stats`)
✅ No error screenshots in `backend/screenshots/`

---

## 📞 **Need Help?**

1. Check `/api/config/validate` for configuration issues
2. Check `/api/jobs/easy-apply/stats` for bot status
3. Check `backend/screenshots/` for error screenshots
4. Check browser console (F12) for frontend errors
5. Check backend logs for detailed error messages

---

## 🚀 **Quick Start Checklist**

- [ ] Configure personal info (`/api/config/user` with `section: "personal"`)
- [ ] Configure professional info (`section: "professional"`)
- [ ] Set LinkedIn credentials (`section: "linkedin"`)
- [ ] Set resume path (`section: "application"`)
- [ ] Verify configuration (`/api/config/validate`)
- [ ] Test with 5 jobs first
- [ ] Check results in database
- [ ] Scale up to more jobs

**You're ready to auto-apply! 🎊**
