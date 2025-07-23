# KegTracker Backend

Backend API para el sistema de gestión de barriles KegTracker.

## 🚀 Versiones e Imágenes Docker

### 📦 Imágenes Disponibles

| Imagen | Tag | Descripción | Uso |
|--------|-----|-------------|-----|
| `tinouy/kegtracker-backend` | `demo` | **Demo con datos pre-cargados** | Para demos y pruebas |
| `tinouy/kegtracker-backend` | `0.1.0` | **Versión limpia de producción** | Para instalaciones nuevas |

### 🎯 Imagen Demo (`demo`)

**Contiene datos demo pre-inicializados:**

- ✅ Base de datos ya configurada
- ✅ 2 Cervecerías: "Cervecería Norte" y "Cervecería Sur"  
- ✅ 7 Usuarios demo con diferentes roles
- ✅ 6 Barriles de ejemplo con diferentes estados
- ✅ Listo para usar inmediatamente

**Usuarios Demo:**
```
Email: admin@demo.com     | Rol: Global Admin | Contraseña: demo123
Email: norte@demo.com     | Rol: Admin        | Contraseña: demo123
Email: sur@demo.com       | Rol: Admin        | Contraseña: demo123
Email: modnorte@demo.com  | Rol: Moderator    | Contraseña: demo123
Email: modsur@demo.com    | Rol: Moderator    | Contraseña: demo123
Email: usernorte@demo.com | Rol: User         | Contraseña: demo123
Email: usersur@demo.com   | Rol: User         | Contraseña: demo123
```

### 🏭 Imagen 0.1.0 (`0.1.0`)

**Imagen limpia para producción:**

- ✅ Sin datos pre-cargados
- ✅ Requiere inicialización via `/api/wizard/`
- ✅ Ideal para instalaciones nuevas
- ✅ Base de datos vacía

## 🛠️ Construcción de Imágenes

### Script Automatizado (Recomendado)

```bash
# Primero loguearse en Docker Hub
docker login

# Construir y subir imagen demo multi-plataforma
./build-images.sh demo

# Construir y subir imagen 0.1.0 multi-plataforma
./build-images.sh release

# Construir y subir ambas imágenes
./build-images.sh both
```

### Manual (Multi-plataforma)

```bash
# Primero loguearse en Docker Hub
docker login

# Imagen Demo (con base de datos pre-cargada)
docker buildx build --platform linux/amd64,linux/arm64 -t tinouy/kegtracker-backend:demo -f Dockerfile.demo . --push --no-cache

# Imagen 0.1.0 (limpia para producción)
docker buildx build --platform linux/amd64,linux/arm64 -t tinouy/kegtracker-backend:0.1.0 -f Dockerfile . --push --no-cache
```

## 🚀 Ejecución

### Con Docker Compose (Recomendado)

```bash
# Para demo
docker-compose up -d

# Para producción (editar docker-compose.yml primero)
# Cambiar: image: tinouy/kegtracker-backend:demo
# Por:     image: tinouy/kegtracker-backend:0.1.0
docker-compose up -d
```

### Directo con Docker

```bash
# Demo
docker run -p 8000:8000 tinouy/kegtracker-backend:demo

# Producción 0.1.0
docker run -p 8000:8000 tinouy/kegtracker-backend:0.1.0
```

## 🔧 Configuración

### Variables de Entorno

```bash
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_FQDN=https://your-domain.com
DB_ENGINE=sqlite
SECRET_KEY=your-secret-key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-password
SMTP_FROM=no-reply@your-domain.com
```

## 📡 API Endpoints

- **Documentación**: `http://localhost:8000/docs`
- **Health Check**: `GET /`
- **Autenticación**: `POST /api/auth/login`
- **Inicialización**: `POST /api/wizard/` (solo versión 0.1.0)

## 🗃️ Base de Datos

- **Desarrollo**: SQLite (`kegtracker.db`)
- **Producción**: SQLite o PostgreSQL (configurable)

### Migraciones

```bash
# Aplicar migraciones
alembic upgrade head

# Crear nueva migración
alembic revision --autogenerate -m "Description"
```

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con coverage
pytest --cov=app tests/
```

## 📝 Desarrollo

### Setup Local

```bash
# Clonar repositorio
git clone https://github.com/username/kegtracker-backend.git
cd kegtracker-backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor de desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Estructura del Proyecto

```
app/
├── api/          # Endpoints de la API
├── core/         # Configuración y autenticación
├── db/           # Modelos y base de datos
├── email/        # Templates de email
└── services/     # Servicios auxiliares

kegtracker.db     # Base de datos demo (solo para imagen demo)

Dockerfile        # Imagen 0.1.0 (limpia)
Dockerfile.demo   # Imagen demo (con datos)
build-images.sh   # Script de construcción
```

## 📄 Licencia

[MIT License](LICENSE) 