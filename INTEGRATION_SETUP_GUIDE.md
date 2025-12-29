# 🔗 Οδηγός Ενεργοποίησης Integrations

Αυτός ο οδηγός σε καθοδηγεί **βήμα-βήμα** για να ενεργοποιήσεις όλες τις integrations της πλατφόρμας.

---

## 📧 1. RESEND EMAIL SERVICE

### Τι είναι το Resend;
Υπηρεσία αποστολής emails με RESTful API (πιο σύγχρονη από SMTP).

### Βήματα:

#### 1.1. Δημιουργία Account
1. Πήγαινε στο: https://resend.com/signup
2. Κάνε εγγραφή με το email σου
3. Επιβεβαίωσε το email σου

#### 1.2. Παίρνεις το API Key
1. Μπες στο Dashboard: https://resend.com/api-keys
2. Πάτα **"Create API Key"**
3. Βάλε όνομα: "Research Platform"
4. Επίλεξε permissions: **"Sending access"**
5. Πάτα "Create"
6. **ΣΗΜΑΝΤΙΚΟ:** Αντίγραψε το API key ΤΩΡΑ (δεν θα το ξαναδείς!)

#### 1.3. Βάλε το στο .env
Άνοιξε το αρχείο `backend/.env` και βάλε:

```env
RESEND_API_KEY=re_your_actual_api_key_here
```

#### 1.4. Δοκιμή
Μπορείς να στείλεις test email από το Resend dashboard.

**Σημείωση:** Στο free tier:
- ✅ 100 emails/day
- ✅ 3,000 emails/month
- ⚠️ Μπορείς να στέλνεις μόνο από `onboarding@resend.dev` (ή να επαληθεύσεις το domain σου)

---

## ☁️ 2. GOOGLE DRIVE INTEGRATION

### Τι κάνει;
Επιτρέπει στους χρήστες να αποθηκεύουν/συγχρονίζουν papers στο Google Drive τους.

### Βήματα:

#### 2.1. Δημιουργία Google Cloud Project
1. Πήγαινε στο: https://console.cloud.google.com/
2. Πάτα **"Select a project"** → **"New Project"**
3. Βάλε όνομα: "Research Platform"
4. Πάτα **"Create"**

#### 2.2. Ενεργοποίηση Google Drive API
1. Στο menu, πάτα **"APIs & Services"** → **"Library"**
2. Ψάξε για: **"Google Drive API"**
3. Πάτα πάνω του και μετά **"Enable"**

#### 2.3. Δημιουργία OAuth Credentials
1. Πήγαινε στο **"APIs & Services"** → **"Credentials"**
2. Πάτα **"Create Credentials"** → **"OAuth client ID"**
3. Αν σου ζητήσει, πρώτα ρύθμισε το **OAuth consent screen**:
   - User Type: **External**
   - App name: "Research Platform"
   - User support email: Το email σου
   - Developer contact: Το email σου
   - Πάτα "Save and Continue"
   - Scopes: Άφησε τα default
   - Test users: Πρόσθεσε το email σου
   - Πάτα "Save and Continue"

4. Τώρα δημιούργησε το OAuth client:
   - Application type: **"Web application"**
   - Name: "Research Platform Web"
   - Authorized JavaScript origins:
     ```
     http://localhost:5173
     http://localhost:3000
     ```
   - Authorized redirect URIs:
     ```
     http://localhost:5173/settings/integrations/google-drive/callback
     http://localhost:3000/settings/integrations/google-drive/callback
     ```
   - Πάτα **"Create"**

#### 2.4. Αντιγραφή Credentials
Θα εμφανιστεί popup με:
- **Client ID**: Κάτι σαν `123456789-abcdef.apps.googleusercontent.com`
- **Client secret**: Κάτι σαν `GOCSPX-abc123`

Αντίγραψε και τα δύο!

#### 2.5. Βάλε τα στο .env
```env
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abc123def456ghi789
```

---

## 📦 3. DROPBOX INTEGRATION

### Τι κάνει;
Επιτρέπει backup/συγχρονισμό papers στο Dropbox.

### Βήματα:

#### 3.1. Δημιουργία Dropbox App
1. Πήγαινε στο: https://www.dropbox.com/developers/apps
2. Πάτα **"Create app"**
3. Επίλεξε:
   - API: **"Scoped access"**
   - Type of access: **"Full Dropbox"** (για πλήρη πρόσβαση)
   - Name: "Research Platform" (πρέπει να είναι unique)
4. Πάτα **"Create app"**

#### 3.2. Ρύθμιση App Settings
1. Στο **"Settings"** tab:
2. **Redirect URIs**: Πρόσθεσε:
   ```
   http://localhost:5173/settings/integrations/dropbox/callback
   http://localhost:3000/settings/integrations/dropbox/callback
   ```
3. Πάτα **"Add"**

#### 3.3. Ρύθμιση Permissions
1. Πήγαινε στο **"Permissions"** tab
2. Επίλεξε:
   - ✅ `files.metadata.write`
   - ✅ `files.content.write`
   - ✅ `files.content.read`
3. Πάτα **"Submit"**

#### 3.4. Παίρνεις τα Credentials
1. Πήγαινε πίσω στο **"Settings"** tab
2. Θα δεις:
   - **App key**: Αυτό είναι το `DROPBOX_APP_KEY`
   - **App secret**: Πάτα "Show" για να το δεις

#### 3.5. Βάλε τα στο .env
```env
DROPBOX_APP_KEY=abc123def456ghi789
DROPBOX_APP_SECRET=xyz987uvw654rst321
```

---

## 📚 4. MENDELEY INTEGRATION

### Τι κάνει;
Εισαγωγή βιβλιογραφικών αναφορών από Mendeley.

### Βήματα:

#### 4.1. Δημιουργία Mendeley Developer App
1. Πήγαινε στο: https://dev.mendeley.com/
2. Κάνε sign in με το Mendeley account σου (ή δημιούργησε ένα)
3. Πάτα **"My Apps"** → **"Create New App"**

#### 4.2. Συμπλήρωσε τα στοιχεία
- **Application name**: Research Platform
- **Description**: Research paper management platform
- **Redirect URL**:
  ```
  http://localhost:5173/settings/integrations/mendeley/callback
  ```

#### 4.3. Παίρνεις τα Credentials
Μετά τη δημιουργία, θα δεις:
- **Client ID**: Αριθμός (π.χ. `1234`)
- **Client Secret**: String (π.χ. `abcdef123456`)

#### 4.4. Βάλε τα στο .env
```env
MENDELEY_CLIENT_ID=1234
MENDELEY_CLIENT_SECRET=abcdef123456
```

---

## 📖 5. ZOTERO INTEGRATION

### Τι κάνει;
Εισαγωγή βιβλιογραφικών αναφορών από Zotero.

### Βήματα:

#### 5.1. Δημιουργία Zotero API Key
1. Πήγαινε στο: https://www.zotero.org/settings/keys
2. Κάνε login (ή δημιούργησε account)
3. Πάτα **"Create new private key"**

#### 5.2. Ρυθμίσεις
- **Key Description**: "Research Platform"
- **Personal Library**: Επίλεξε:
  - ✅ Allow library access
  - ✅ Allow notes access
  - ✅ Allow write access (αν θέλεις και export)

#### 5.3. Δημιουργία και Αντιγραφή
1. Πάτα **"Save Key"**
2. **ΣΗΜΑΝΤΙΚΟ**: Αντίγραψε το API key ΤΩΡΑ! (δεν θα το ξαναδείς)

**Σημείωση:** Το Zotero API key το βάζει ο κάθε χρήστης από το UI της πλατφόρμας (Settings → Integrations), όχι στο .env!

---

## ✅ ΤΕΛΙΚΟ .env FILE

Μετά από όλα τα παραπάνω, το `backend/.env` σου πρέπει να μοιάζει έτσι:

```env
# ==================== ΒΑΣΙΚΕΣ ΡΥΘΜΙΣΕΙΣ ====================
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/research_platform
REDIS_URL=redis://localhost:6379

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# ==================== AI SERVICES ====================
# Gemini (FREE) - https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_key

# Groq (FREE) - https://console.groq.com/keys
GROQ_API_KEY=your_groq_key

# OpenAI (Paid) - https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_key

# GPT-OSS Local
GPT_OSS_API_KEY=your_gpt_oss_key
GPT_OSS_BASE_URL=http://34.9.154.79:11481/api/chat/completions
GPT_OSS_MODEL=gpt-oss:120b

# ==================== EMAIL (RESEND) ====================
RESEND_API_KEY=re_your_resend_api_key_here
EMAIL_FROM=onboarding@resend.dev
EMAIL_FROM_NAME=Research Platform

# ==================== CLOUD STORAGE ====================
# Google Drive
GOOGLE_CLIENT_ID=123456789-abc.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abc123

# Dropbox
DROPBOX_APP_KEY=abc123def456
DROPBOX_APP_SECRET=xyz987uvw654

# ==================== REFERENCE MANAGERS ====================
# Mendeley
MENDELEY_CLIENT_ID=1234
MENDELEY_CLIENT_SECRET=abcdef123456

# ==================== FRONTEND ====================
FRONTEND_URL=http://localhost:5173
```

---

## 🧪 ΔΟΚΙΜΗ

Μετά από όλες τις ρυθμίσεις:

### 1. Restart Backend
```bash
cd backend
python -m uvicorn app.main:app --reload
```

Θα δεις στο console:
```
✅ CONFIGURATION LOADED
============================================================
📧 Resend Email: ✅ Configured
☁️  Google Drive: ✅ Configured
📦 Dropbox: ✅ Configured
📚 Mendeley: ✅ Configured
============================================================
```

### 2. Δοκίμασε Email
Από το frontend, δοκίμασε:
- Δημιουργία νέου account (πρέπει να στείλει welcome email)
- Πρόσκληση collaborator (πρέπει να στείλει invite email)

### 3. Δοκίμασε Integrations
Πήγαινε στο **Settings → Integrations** και δοκίμασε να συνδεθείς σε:
- Google Drive
- Dropbox
- Mendeley

---

## ⚠️ ΣΗΜΑΝΤΙΚΑ

1. **Μην βάλεις το .env file στο git!** (είναι ήδη στο `.gitignore`)
2. **Για production**: Άλλαξε τα redirect URIs με το production domain
3. **Security**: Μην μοιραστείς τα API keys με κανέναν
4. **Testing**: Χρησιμοποίησε test accounts για testing

---

## 🆘 ΠΡΟΒΛΗΜΑΤΑ;

### Email δεν στέλνεται
- Έλεγξε ότι το `RESEND_API_KEY` είναι σωστό
- Στο free tier, μπορείς να στέλνεις μόνο από `onboarding@resend.dev`
- Για custom domain, πρέπει να τον επαληθεύσεις στο Resend

### Google Drive δεν συνδέεται
- Έλεγξε ότι τα redirect URIs είναι ακριβώς τα ίδια
- Βεβαιώσου ότι το Google Drive API είναι enabled

### Dropbox error
- Έλεγξε τα permissions στο Permissions tab
- Κάνε Submit μετά από αλλαγές

### Mendeley δεν δουλεύει
- Τα Mendeley credentials είναι case-sensitive
- Βεβαιώσου ότι το redirect URI είναι σωστό

---

**Καλή επιτυχία! 🚀**
