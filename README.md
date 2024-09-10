# Domika haomeassistant framework

Domika integration framework library.

## Development

### Create new database revision

```bash
cd src
DOMIKA_DB_URL="Put database url here" alembic -c domika_ha_framework/alembic.ini revision -m "Put revision message here"
```

### Upgrade head

```bash
cd src
DOMIKA_DB_URL="Put database url here" alembic -c domika_ha_framework/alembic.ini upgrade head
```
