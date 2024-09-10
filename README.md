![GitHub License](https://img.shields.io/github/license/DevPocket/domika-ha-framework)
![PyPI - Version](https://img.shields.io/pypi/v/domika-ha-framework)

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
