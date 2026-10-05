#!/bin/bash

# গিট রিপোজিটরি শুরু না থাকলে করবে
git init

# সব পরিবর্তিত ফাইল যোগ করবে
git add .

# কোনো পরিবর্তন থাকলে ডায়নামিক মেসেজ (তারিখ-সময় সহ) দিয়ে কমিট করবে
if git diff-index --quiet HEAD --; then
    echo "No changes to commit."
else
    git commit -m "Update code: $(date '+%Y-%m-%d %H:%M:%S')"
fi

# মেইন ব্রাঞ্চ সেট করবে
git branch -M main

# রিমোট লিংক সেট বা যোগ করবে
git remote set-url origin https://github.com/afsana673/Sk_Habibulla_api.git 2>/dev/null || git remote add origin https://github.com/afsana673/Sk_Habibulla_api.git

# কোড পুশ করবে
git push -u origin main
