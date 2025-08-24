#!/bin/bash

# 🎛️ PANEL DE ADMINISTRACIÓN DOCKER - Dashboard de Gastos del Hogar
# Script súper fácil para administrar tu dashboard sin saber Docker

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() { echo -e "${CYAN}$1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️ $1${NC}"; }

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    print_error "Este script debe ejecutarse desde el directorio deployment/"
    exit 1
fi

# Función para mostrar estado
show_status() {
    print_header "📊 Estado de los servicios:"
    echo ""
    
    if docker-compose ps | grep -q "Up"; then
        print_success "Dashboard funcionando correctamente"
        
        # Mostrar información detallada
        echo ""
        print_info "Contenedores activos:"
        docker-compose ps
        
        # Verificar conectividad
        echo ""
        print_info "Verificando conectividad..."
        if curl -s -f http://localhost:8501/_stcore/health >/dev/null 2>&1; then
            print_success "Dashboard respondiendo correctamente"
        else
            print_warning "Dashboard podría estar iniciando..."
        fi
        
        # Mostrar uso de recursos
        echo ""
        print_info "Uso de recursos:"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
        
    else
        print_warning "Algunos servicios no están funcionando"
        docker-compose ps
    fi
}

# Función para ver logs
show_logs() {
    print_header "📝 Logs del dashboard:"
    echo ""
    print_info "Mostrando últimas 50 líneas... (Ctrl+C para salir)"
    echo ""
    docker-compose logs --tail=50 -f dashboard
}

# Función para reiniciar
restart_services() {
    print_header "🔄 Reiniciando servicios..."
    docker-compose restart
    print_success "Servicios reiniciados"
    sleep 5
    show_status
}

# Función para actualizar
update_app() {
    print_header "⬆️ Actualizando aplicación..."
    
    print_info "1. Haciendo backup de configuración..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    
    print_info "2. Descargando últimos cambios..."
    git pull
    
    print_info "3. Reconstruyendo imágenes..."
    docker-compose build --no-cache
    
    print_info "4. Reiniciando con nueva versión..."
    docker-compose up -d
    
    print_success "Aplicación actualizada"
    sleep 5
    show_status
}

# Función para detener todo
stop_all() {
    print_header "🛑 Deteniendo todos los servicios..."
    docker-compose down
    print_success "Todos los servicios detenidos"
}

# Función para iniciar todo
start_all() {
    print_header "🚀 Iniciando todos los servicios..."
    docker-compose up -d
    print_success "Servicios iniciados"
    sleep 5
    show_status
}

# Función para limpiar Docker
cleanup_docker() {
    print_header "🧹 Limpiando Docker (liberar espacio)..."
    
    print_warning "Esto eliminará imágenes, contenedores y volúmenes no utilizados"
    read -p "¿Continuar? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker system prune -a -f
        print_success "Limpieza completada"
        
        # Mostrar espacio liberado
        print_info "Espacio en disco:"
        df -h / | tail -1
    else
        print_info "Limpieza cancelada"
    fi
}

# Función para hacer backup
backup_config() {
    print_header "💾 Creando backup de configuración..."
    
    BACKUP_FILE="backup-dashboard-$(date +%Y%m%d_%H%M%S).tar.gz"
    
    tar -czf $BACKUP_FILE \
        .env \
        nginx/ssl/ \
        docker-compose.yml \
        nginx/nginx.conf
    
    print_success "Backup creado: $BACKUP_FILE"
    print_info "Guarda este archivo en un lugar seguro"
}

# Función para mostrar URLs importantes
show_urls() {
    print_header "🌐 URLs importantes:"
    echo ""
    
    # Obtener dominio del archivo de configuración
    DOMAIN=$(grep "server_name" nginx/nginx.conf | head -1 | awk '{print $2}' | sed 's/;//g')
    
    if [ "$DOMAIN" != "tu-dominio.com" ]; then
        print_info "📊 Dashboard: https://$DOMAIN"
        print_info "🔄 OAuth Callback: https://$DOMAIN/callback"
        print_info "🏥 Health Check: https://$DOMAIN/health"
    else
        print_warning "Dominio no configurado en nginx.conf"
    fi
    
    print_info "🏠 Local: http://localhost:8501"
    print_info "📋 Local Health: http://localhost:8501/_stcore/health"
}

# Función para mostrar ayuda
show_help() {
    print_header "📚 Ayuda - Comandos disponibles:"
    echo ""
    echo "  1) Estado - Ver estado de servicios"
    echo "  2) Logs - Ver logs en tiempo real"
    echo "  3) Reiniciar - Reiniciar todos los servicios"
    echo "  4) Actualizar - Actualizar aplicación desde Git"
    echo "  5) Parar - Detener todos los servicios"
    echo "  6) Iniciar - Iniciar todos los servicios"
    echo "  7) Limpiar - Limpiar Docker (liberar espacio)"
    echo "  8) Backup - Crear backup de configuración"
    echo "  9) URLs - Mostrar URLs importantes"
    echo "  0) Ayuda - Mostrar esta ayuda"
    echo "  q) Salir"
    echo ""
    print_info "📖 Documentación completa en README.md"
}

# Menú principal
main_menu() {
    while true; do
        clear
        print_header "🎛️ PANEL DE ADMINISTRACIÓN - Dashboard de Gastos del Hogar"
        print_info "Administra tu dashboard fácilmente sin conocer Docker"
        echo ""
        
        echo "1) 📊 Ver Estado"
        echo "2) 📝 Ver Logs"
        echo "3) 🔄 Reiniciar"
        echo "4) ⬆️ Actualizar"
        echo "5) 🛑 Parar Todo"
        echo "6) 🚀 Iniciar Todo"
        echo "7) 🧹 Limpiar Docker"
        echo "8) 💾 Hacer Backup"
        echo "9) 🌐 Ver URLs"
        echo "0) 📚 Ayuda"
        echo "q) 🚪 Salir"
        echo ""
        
        read -p "Selecciona una opción: " choice
        echo ""
        
        case $choice in
            1) show_status ;;
            2) show_logs ;;
            3) restart_services ;;
            4) update_app ;;
            5) stop_all ;;
            6) start_all ;;
            7) cleanup_docker ;;
            8) backup_config ;;
            9) show_urls ;;
            0) show_help ;;
            q|Q) print_success "¡Hasta luego!"; exit 0 ;;
            *) print_error "Opción inválida" ;;
        esac
        
        echo ""
        read -p "Presiona ENTER para continuar..."
    done
}

# Si se ejecuta con parámetro, ejecutar función directamente
if [ $# -eq 1 ]; then
    case $1 in
        status) show_status ;;
        logs) show_logs ;;
        restart) restart_services ;;
        update) update_app ;;
        stop) stop_all ;;
        start) start_all ;;
        cleanup) cleanup_docker ;;
        backup) backup_config ;;
        urls) show_urls ;;
        help) show_help ;;
        *) print_error "Comando desconocido: $1"; show_help ;;
    esac
else
    # Mostrar menú interactivo
    main_menu
fi
