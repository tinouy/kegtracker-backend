# KegTracker Demo Data

Este directorio contiene los scripts y datos para crear la imagen demo de KegTracker.

## Estructura Demo

### 🏭 Cervecerías
- **Cervecería Norte**: Cervecería artesanal del norte
- **Cervecería Sur**: Cervecería artesanal del sur

### 👥 Usuarios Demo

Todos los usuarios tienen la contraseña: `demo123`

| Email | Rol | Cervecería | Descripción |
|-------|-----|------------|-------------|
| admin@demo.com | Global Admin | Norte | Administrador global del sistema |
| norte@demo.com | Admin | Norte | Administrador de Cervecería Norte |
| sur@demo.com | Admin | Sur | Administrador de Cervecería Sur |
| modnorte@demo.com | Moderator | Norte | Moderador de Cervecería Norte |
| modsur@demo.com | Moderator | Sur | Moderador de Cervecería Sur |
| usernorte@demo.com | User | Norte | Usuario regular de Cervecería Norte |
| usersur@demo.com | User | Sur | Usuario regular de Cervecería Sur |

### 🍺 Barriles Demo

#### Cervecería Norte
- **Keg IPA Norte 001**: 50L Keg con IPA Americana (35L, en uso)
- **Keg Lager Norte 002**: 30L Keg con Lager Premium (vacío)
- **Corni Stout Norte 003**: 19L Corni con Stout Imperial (lleno, listo)

#### Cervecería Sur
- **Keg Pilsner Sur 001**: 50L Keg con Pilsner Bohemia (42L, en uso)
- **Keg Wheat Sur 002**: 30L Keg con Wheat Beer (15L, en uso)
- **Corni Ale Sur 003**: 19L Corni con Pale Ale (vacío, sucio)

## Construcción de Imagen Demo

```bash
# Construir imagen demo
docker build -f Dockerfile.demo -t kegtracker-backend:demo .

# Construir imagen 0.1.0 (limpia)
docker build -f Dockerfile -t kegtracker-backend:0.1.0 .
```

## Acceso Demo

La demo estará disponible en: https://demo.kegtracker.beer

### Login URLs por Rol
- **Global Admin**: Acceso completo a todo el sistema
- **Admin**: Gestión completa de su cervecería
- **Moderator**: Gestión de usuarios y barriles de su cervecería
- **User**: Visualización y edición básica de barriles

## Archivos

- `README.md`: Esta documentación
- La base de datos demo se incluye directamente en la imagen Docker