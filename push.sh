#!/bin/bash
git init
git add .
git commit -m "Initial commit for video downloader API"
git branch -M main
git remote set-url origin https://github.com/afsana673/Sk_Habibulla_api.git 2>/dev/null || git remote add origin https://github.com/afsana673/Sk_Habibulla_api.git
git push -u origin main
