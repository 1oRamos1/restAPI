#!/bin/bash
# הרץ אותו מתוך תיקיית mysite/frontend/src/
# bash update_frontend_urls.sh

set -e

echo "🔧 מעדכן URLs בפרונטאנד..."

# ==========================================
# 1. AuthContext.js
# ==========================================
sed -i '' "s|/dj-rest-auth/user/|/auth/user/|g" context/AuthContext.js
echo "✅ context/AuthContext.js"

# ==========================================
# 2. LoginModal.jsx
# ==========================================
sed -i '' "s|/dj-rest-auth/google/|/auth/google/|g" components/LoginModal.jsx
echo "✅ components/LoginModal.jsx"

# ==========================================
# 3. PasswordReset.jsx
# ==========================================
sed -i '' "s|/dj-rest-auth/password/reset/|/auth/password/reset/|g" pages/PasswordReset.jsx
echo "✅ pages/PasswordReset.jsx"

# ==========================================
# 4. PasswordResetConfirm.jsx
# ==========================================
sed -i '' "s|https://tracker-2528.onrender.com/dj-rest-auth/password/reset/confirm/|/auth/password/reset/confirm/|g" pages/PasswordResetConfirm.jsx
echo "✅ pages/PasswordResetConfirm.jsx"

# ==========================================
# 5. BuyProPage.jsx
# ==========================================
sed -i '' "s|'/upgrade-to-pro/'|'/user/upgrade-to-pro/'|g" pages/BuyProPage.jsx
echo "✅ pages/BuyProPage.jsx"

echo ""
echo "✅ הכל עודכן בהצלחה!"
echo ""
echo "שינויים שבוצעו:"
echo "  /dj-rest-auth/user/          → /auth/user/"
echo "  /dj-rest-auth/google/        → /auth/google/"
echo "  /dj-rest-auth/password/reset/ → /auth/password/reset/"
echo "  https://tracker-2528...confirm/ → /auth/password/reset/confirm/"
echo "  /upgrade-to-pro/             → /user/upgrade-to-pro/"
