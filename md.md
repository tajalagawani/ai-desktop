
  # SSH into VPS, pull changes, and build
  sshpass -p '@yJ5Yy#2tW9Le(x16v1U' ssh -o StrictHostKeyChecking=no root@92.112.181.127 'cd /var/www/ai-desktop && git pull && npm run build'

  # Restart PM2
  sshpass -p '@yJ5Yy#2tW9Le(x16v1U' ssh -o StrictHostKeyChecking=no root@92.112.181.127 'pm2 restart ai-desktop'

  Or as a single command:

  sshpass -p '@yJ5Yy#2tW9Le(x16v1U' ssh -o StrictHostKeyChecking=no root@92.112.181.127 'cd /var/www/ai-desktop && git pull && npm run build && pm2 restart ai-desktop'

> ok now try it 