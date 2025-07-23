#!/bin/bash

# Script para construir las imágenes Docker de KegTracker Backend
# Versión Demo con datos pre-cargados vs Versión 0.1.0 limpia

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}KegTracker Backend - Build Script${NC}"
    echo ""
    echo "Uso: ./build-images.sh [COMANDO] [OPCIONES]"
    echo ""
    echo "Comandos:"
    echo "  demo     Construir y subir imagen demo multi-plataforma"
    echo "  release  Construir y subir imagen 0.1.0 multi-plataforma"
    echo "  both     Construir y subir ambas imágenes"
    echo "  help     Mostrar esta ayuda"
    echo ""
    echo "Opciones:"
    echo "  -t, --tag    Tag personalizado (default: 0.1.0)"
    echo "  -r, --repo   Repositorio (default: tinouy/kegtracker-backend)"
    echo ""
    echo "Ejemplos:"
    echo "  # Primero loguearse en Docker Hub"
    echo "  docker login"
    echo ""
    echo "  # Luego construir imágenes"
    echo "  ./build-images.sh demo"
    echo "  ./build-images.sh release -t 0.1.0"
    echo "  ./build-images.sh both"
}

# Variables por defecto
REPO="tinouy/kegtracker-backend"
TAG_DEMO="demo"
TAG_RELEASE="0.1.0"
COMMAND=""

# Procesar argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        demo|release|both|help)
            COMMAND="$1"
            shift
            ;;
        -t|--tag)
            TAG_RELEASE="$2"
            shift 2
            ;;
        -r|--repo)
            REPO="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Error: Argumento desconocido '$1'${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Verificar que se proporcionó un comando
if [[ -z "$COMMAND" ]]; then
    echo -e "${RED}Error: Debes especificar un comando${NC}"
    show_help
    exit 1
fi

# Función para construir imagen demo
build_demo() {
    echo -e "${BLUE}🚀 Construyendo imagen demo multi-plataforma...${NC}"
    echo -e "${YELLOW}   Imagen: ${REPO}:${TAG_DEMO}${NC}"
    echo -e "${YELLOW}   Plataformas: linux/amd64, linux/arm64${NC}"
    
    docker buildx build --platform linux/amd64,linux/arm64 -t "${REPO}:${TAG_DEMO}" -f Dockerfile.demo . --push --no-cache
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Imagen demo construida y subida exitosamente!${NC}"
        echo -e "${BLUE}   📦 Imagen: ${REPO}:${TAG_DEMO}${NC}"
        echo -e "${BLUE}   🗃️  Contiene base de datos demo pre-cargada${NC}"
        echo -e "${BLUE}   👥 Usuarios demo disponibles con contraseña: demo123${NC}"
        echo -e "${BLUE}   🌍 Disponible para: linux/amd64, linux/arm64${NC}"
    else
        echo -e "${RED}❌ Error construyendo imagen demo${NC}"
        exit 1
    fi
}

# Función para construir imagen de release
build_release() {
    echo -e "${BLUE}🚀 Construyendo imagen 0.1.0 (release) multi-plataforma...${NC}"
    echo -e "${YELLOW}   Imagen: ${REPO}:${TAG_RELEASE}${NC}"
    echo -e "${YELLOW}   Plataformas: linux/amd64, linux/arm64${NC}"
    
    docker buildx build --platform linux/amd64,linux/arm64 -t "${REPO}:${TAG_RELEASE}" -f Dockerfile . --push --no-cache
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Imagen 0.1.0 construida y subida exitosamente!${NC}"
        echo -e "${BLUE}   📦 Imagen: ${REPO}:${TAG_RELEASE}${NC}"
        echo -e "${BLUE}   🏭 Imagen limpia sin datos - requiere inicialización via /api/wizard/${NC}"
        echo -e "${BLUE}   🌍 Disponible para: linux/amd64, linux/arm64${NC}"
    else
        echo -e "${RED}❌ Error construyendo imagen 0.1.0${NC}"
        exit 1
    fi
}

# Función para verificar buildx y login
check_buildx() {
    echo -e "${BLUE}🔍 Verificando Docker Buildx y Docker Hub...${NC}"
    
    # Verificar Docker Buildx
    if ! docker buildx version &> /dev/null; then
        echo -e "${RED}❌ Docker Buildx no está disponible${NC}"
        echo -e "${YELLOW}   Instala Docker Desktop o habilita buildx${NC}"
        exit 1
    fi
    
    # Verificar login en Docker Hub usando ~/.docker/config.json
    DOCKER_CONFIG="$HOME/.docker/config.json"
    if [[ ! -f "$DOCKER_CONFIG" ]]; then
        echo -e "${RED}❌ No hay configuración de Docker encontrada${NC}"
        echo -e "${YELLOW}   Debes autenticarte primero:${NC}"
        echo -e "${BLUE}   docker login${NC}"
        exit 1
    fi
    
    # Verificar si hay credenciales para Docker Hub
    if ! grep -q "index.docker.io" "$DOCKER_CONFIG" 2>/dev/null; then
        echo -e "${RED}❌ No estás logueado en Docker Hub${NC}"
        echo -e "${YELLOW}   Debes autenticarte primero:${NC}"
        echo -e "${BLUE}   docker login${NC}"
        echo -e "${BLUE}   # Ingresa tu usuario y contraseña de Docker Hub${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker Buildx disponible${NC}"
    echo -e "${GREEN}✅ Configuración de Docker Hub encontrada en ~/.docker/config.json${NC}"
    echo -e "${GREEN}✅ Listo para construir y subir imágenes${NC}"
}

# Verificar buildx antes de cualquier operación (excepto help)
if [[ "$COMMAND" != "help" ]]; then
    check_buildx
fi

# Ejecutar comando
case $COMMAND in
    demo)
        build_demo
        ;;
    release)
        build_release
        ;;
    both)
        build_demo
        echo ""
        build_release
        ;;
    help)
        show_help
        ;;
esac

echo ""
echo -e "${GREEN}🎉 Proceso completado!${NC}"

# Mostrar imágenes disponibles
echo -e "${BLUE}📋 Imágenes Docker disponibles:${NC}"
docker images | grep kegtracker-backend | head -5