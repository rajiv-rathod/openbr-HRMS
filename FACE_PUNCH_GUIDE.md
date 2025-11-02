# 👤 Face Punch - Biometric Attendance on Your Laptop

## 🚀 Quick Start (5 Minutes)

### Step 1: Open Face Punch Interface
Open this link in your browser:
```
https://weary-crypt-5jrjxprjv5xhvxvq-5000.app.github.dev/login
```

### Step 2: Login
**Default Credentials:**
- Username: `admin`
- Password: `admin123`

Click **"Login & Go to Face Punch"**

### Step 3: Allow Camera Access
- Browser will ask for camera permission
- Click **"Allow"** to enable webcam

### Step 4: Start Camera
1. Click **"Start Camera"** button
2. You should see your face in the video feed
3. Green indicator shows: ✓ Face Detected

### Step 5: Enter Employee ID & Punch
1. Enter your Employee ID (e.g., `E001`)
2. Click either:
   - **🔓 IN** - Record arrival (morning punch)
   - **🔒 OUT** - Record departure (evening punch)

### Step 6: Success! 🎉
- Punch recorded successfully
- See confirmation message
- Stats update showing total punches today
- Employee ID field clears for next person

---

## 📋 Features

### ✅ What You Can Do
- **Real-time Face Detection**: See your face on screen with confidence score
- **Auto Face Recognition**: Detects your face automatically
- **IN/OUT Punch**: Quick buttons for arrival/departure
- **Employee ID**: Track by employee number
- **Confidence Score**: Shows face recognition accuracy (0-100%)
- **Daily Stats**: Track punches for today
- **Last Punch Time**: Shows when you last punched
- **API Response**: See detailed response from server

### 📸 Camera Requirements
- ✅ Laptop/Desktop webcam
- ✅ Good lighting (natural light is best)
- ✅ Face clearly visible in frame
- ✅ Face 12-24 inches from camera

---

## 🎯 How It Works

```
You                 Your Laptop
  │                     │
  │ Point at camera     │
  ├──────────────────→ 📷 Webcam
  │                     │
  │                  Face Detection
  │                  (ML model)
  │                     │
  │     Show confidence  │
  │ ←──────────────────  │
  │                      │
  │ Enter: E001 + IN    │
  │ Click: "IN" button  │
  ├──────────────────→ 📤 Send to OpenBR
  │                     │
  │                  /api/v1/attendance/punch
  │                     │
  │                  ✓ Recorded!
  │ ←──────────────────  │
  │                      │
  │ ✓ Success message    │
  │                      │
```

---

## 🔧 Settings & Customization

### Change Employee ID
Simply type a different Employee ID and press punch button

### Switch to Different Camera
Most systems default to built-in webcam. Some laptops allow selecting different cameras.

### Adjust Lighting
- Move to a well-lit area
- Avoid bright backlight
- Face should be evenly lit

### Confidence Threshold
Current setting: 95% confidence required
- Higher = More strict recognition
- Lower = Easier to pass (but less secure)

---

## ⚠️ Troubleshooting

### Problem: "Camera access denied"
**Solution:**
1. Check browser permissions settings
2. Go to: Settings → Privacy → Camera
3. Allow: `weary-crypt-5jrjxprjv5xhvxvq-5000.app.github.dev`
4. Reload page and try again

### Problem: "Face not detected"
**Solution:**
1. Check your laptop webcam works
2. Ensure good lighting
3. Position face 12-24 inches from camera
4. Face should be clearly visible (no glasses/masks)
5. Move directly in front of webcam

### Problem: "Low confidence score"
**Solution:**
1. Move closer to camera
2. Improve lighting
3. Remove sunglasses/dark glasses
4. Make sure face is fully visible
5. Look directly at camera

### Problem: "Punch not recording"
**Solution:**
1. Make sure you're logged in
2. Token might have expired (24 hours) - logout and login again
3. Check internet connection
4. Try refreshing the page

### Problem: "Camera video not showing"
**Solution:**
1. Refresh the page
2. Check if camera is in use by another app
3. Close other apps using camera
4. Restart browser
5. Try different browser (Chrome, Firefox, Safari)

---

## 🔐 Security Features

### Face Recognition
- Uses ML model (Face-API.js)
- Detects face features in real-time
- Confidence score (0-100%)
- No photos stored (unless punch is recorded)

### Authentication
- JWT token with 24-hour expiry
- Login required for face punch
- All punches logged with timestamp
- Employee ID tracked for audit

### Data Privacy
- Face photos only saved if punch is successful
- Photos stored in: `/tmp/biometric_uploads/`
- Can be deleted anytime
- No face data shared externally

---

## 📊 Understanding the Display

### Status Colors
- **Ready** (Green): System ready, camera off
- **Processing** (Yellow): Camera running, analyzing
- **Success** (Blue): Punch recorded successfully
- **Error** (Red): Something went wrong

### Confidence Bar
```
████████░░ 85% - Good face detection
███░░░░░░░ 35% - Too low, need better angle/lighting
██████████ 99% - Excellent face detection
```

### Stats Box
```
Total Punches Today: 5
Last Punch: 17:30:45
```

---

## 💡 Best Practices

### ✅ DO
- ✅ Ensure good lighting
- ✅ Face camera directly
- ✅ Keep face 12-24 inches away
- ✅ Use same position each time
- ✅ Check confidence score > 90%
- ✅ Verify punch was recorded

### ❌ DON'T
- ❌ Wear heavy makeup changes
- ❌ Use very dark sunglasses
- ❌ Tilt head too far
- ❌ Cover face with hand/phone
- ❌ Punch from very far away
- ❌ Change lighting drastically

---

## 🖥️ Browser Support

### ✅ Supported Browsers
- Chrome 90+ (Recommended)
- Firefox 88+
- Safari 14+
- Edge 90+

### ⚠️ Browser Requirements
- WebRTC support (for camera)
- JavaScript enabled
- TLS/HTTPS (secure connection)
- Local storage enabled (for token)

---

## 📱 Mobile/Tablet Use

Face punch **mostly works** on mobile but:
- ⚠️ Some devices have front camera limitations
- ⚠️ Browser might not support camera access
- ⚠️ Lighting more critical on phones
- ✅ Tablets work better than phones
- ✅ Landscape orientation recommended

---

## 🔗 Quick Links

| What | Link |
|------|------|
| **Login** | https://weary-crypt-5jrjxprjv5xhvxvq-5000.app.github.dev/login |
| **Face Punch** | https://weary-crypt-5jrjxprjv5xhvxvq-5000.app.github.dev/face-punch |
| **Server Health** | https://weary-crypt-5jrjxprjv5xhvxvq-5000.app.github.dev/api/v1/health |
| **API Docs** | https://weary-crypt-5jrjxprjv5xhvxvq-5000.app.github.dev/documentation |

---

## 📝 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Enter** | Submit form / Login |
| **Tab** | Move between fields |
| **Esc** | Close alerts |

---

## 🎓 How Face Recognition Works

1. **Camera Capture**: Your webcam records video
2. **Face Detection**: AI model detects face in frame
3. **Face Analysis**: Analyzes facial features
4. **Confidence Score**: Calculates match confidence
5. **Punch Recording**: If > 95% confidence, records punch
6. **Database Save**: Stores punch with timestamp & employee ID

---

## 📞 Need Help?

### Common Issues Checklist

Before contacting support, check:
- [ ] Camera is working (test in other app)
- [ ] You are logged in
- [ ] Browser has camera permission
- [ ] You have good lighting
- [ ] Face is clearly visible
- [ ] Internet connection is stable
- [ ] You're using supported browser

### Contact Support

If issues persist, check:
- Server logs: `tail -f /tmp/server.log`
- Browser console: Press F12 → Console tab
- Camera test: http://webcamtests.com/

---

## ✨ Tips & Tricks

### Tip 1: Best Lighting Setup
- Natural window light from front (best)
- Desk lamp on face level (good)
- Avoid backlit (light behind you)

### Tip 2: Consistent Position
- Sit at same distance from camera
- Face camera squarely
- Same lighting each time
- Improves recognition accuracy

### Tip 3: Multiple Employees
- Change Employee ID between punches
- Each person uses same interface
- System tracks all individually

### Tip 4: Speed Up Process
1. Pre-enter Employee ID
2. Position face in frame
3. Wait for ✓ Face Detected
4. Click punch button
5. ~2 seconds to record

---

## 🚀 Now You're Ready!

You can now:
- ✅ Use face recognition for attendance
- ✅ Punch IN/OUT from your laptop
- ✅ Track daily punch count
- ✅ See punch confirmations
- ✅ Review last punch time

**Let's get punching! Go to:**
```
https://weary-crypt-5jrjxprjv5xhvxvq-5000.app.github.dev/login
```

---

**Version**: 1.0  
**Last Updated**: November 1, 2025  
**Status**: ✅ Ready for Use
