# Обновление сервера 24XSTORE

После загрузки этих файлов в GitHub подключитесь к VPS и выполните:

```bash
cd /opt/ps-store-miniapp
git pull

# Создаём локальный секрет для ручной синхронизации каталога.
# .env уже исключён из Git и не попадёт в репозиторий.
if [ ! -f .env ]; then
  printf "ADMIN_SYNC_TOKEN=%s\nDEFAULT_TRY_RUB=2.28\nDEFAULT_MARKUP=0.10\n" "$(openssl rand -hex 24)" > .env
fi

docker rm -f ps-store-miniapp 2>/dev/null || true
docker build -t ps-store-miniapp .
docker run -d \
  --name ps-store-miniapp \
  --restart unless-stopped \
  --env-file .env \
  -p 80:10000 \
  ps-store-miniapp
```

Проверка:

```bash
curl http://127.0.0.1/api/health
```

Первая синхронизация каталога (4 страницы PS5 + 4 страницы PS4):

```bash
TOKEN=$(grep '^ADMIN_SYNC_TOKEN=' .env | cut -d= -f2-)
curl -X POST 'http://127.0.0.1/api/catalog-sync?max_pages=4' \
  -H "X-Admin-Token: $TOKEN"
```

После успешного ответа обновите страницу магазина. Для полного каталога можно позже увеличить `max_pages`, но лучше делать это постепенно, чтобы не создавать лишнюю нагрузку на PlayStation Store.
