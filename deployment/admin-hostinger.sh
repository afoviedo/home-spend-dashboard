#!/bin/bash

# 🎛️ PANEL DE ADMINISTRACIÓN HOSTINGER - Dashboard de Gastos del Hogar
# Optimizado para VPS Hostinger con N8N existente

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_header() { echo -e "${CYAN}$1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️ $1${NC}"; }

# Verificar ubicación
if [ ! -f "docker-compose-hostinger.yml" ]; then
    print_error "Este script debe ejecutarse desde el directorio deployment/"
    exit 1
fi

COMPOSE_FILE="docker-compose-hostinger.yml"

# ================================
# FUNCIONES ESPECÍFICAS HOSTINGER
# ================================

show_hostinger_status() {
    print_header "📊 Estado en Hostinger VPS:"
    echo ""
    
    # Mostrar todos los contenedores Docker (incluyendo N8N)
    print_info "Todos los contenedores Docker en el VPS:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    
    # Estado específico del dashboard
    if docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
        print_success "Dashboard funcionando correctamente"
        
        echo ""
        print_info "Dashboard - Información detallada:"
        docker-compose -f $COMPOSE_FILE ps
        
        # Verificar conectividad del dashboard
        echo ""
        print_info "Verificando conectividad..."
        if curl -s -f http://localhost:8502/_stcore/health >/dev/null 2>&1; then
            print_success "Dashboard respondiendo en puerto 8502"
        else
            print_warning "Dashboard podría estar iniciando en puerto 8502..."
        fi
        
        # Mostrar uso de recursos
        echo ""
        print_info "Uso de recursos (Dashboard + N8N + otros):"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
        
        # Información de red
        echo ""
        print_info "Redes Docker:"
        docker network ls | grep -E "(dashboard|n8n|hostinger)"
        
    else
        print_warning "Dashboard no está funcionando correctamente"
        docker-compose -f $COMPOSE_FILE ps
    fi
    
    # Información del servidor Hostinger
    echo ""
    print_info "Información del VPS Hostinger:"
    echo "  💾 Espacio en disco:"
    df -h / | tail -1
    echo "  🧠 Memoria:"
    free -h | grep Mem
    echo "  ⚡ Carga del sistema:"
    uptime
}

show_combined_logs() {
    print_header "📝 Logs del Dashboard:"
    echo ""
    print_info "Logs del dashboard (últimas 50 líneas)..."
    echo ""
    docker-compose -f $COMPOSE_FILE logs --tail=50 -f dashboard
}

show_all_services_status() {
    print_header "🌐 Estado de todos los servicios en Hostinger:"
    echo ""
    
    print_info "Contenedores Docker activos:"
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    
    print_info "Puertos en uso:"
    sudo netstat -tlnp | grep LISTEN | grep -E "(80|443|5678|8080|8443|8502)" | head -10
    echo ""
    
    print_info "Servicios systemd principales:"
    sudo systemctl status docker --no-pager -l | head -3
}

restart_dashboard() {
    print_header "🔄 Reiniciando Dashboard (manteniendo N8N)...")
    docker-compose -f $COMPOSE_FILE restart
    print_success "Dashboard reiniciado"
    sleep 5
    show_hostinger_status
}

update_dashboard() {
    print_header "⬆️ Actualizando Dashboard en Hostinger..."
    
    print_info "1. Backup de configuración..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    
    print_info "2. Descargando cambios..."
    git pull
    
    print_info "3. Reconstruyendo dashboard (N8N no se ve afectado)..."
    docker-compose -f $COMPOSE_FILE build --no-cache dashboard
    
    print_info "4. Reiniciando solo el dashboard..."
    docker-compose -f $COMPOSE_FILE up -d
    
    print_success "Dashboard actualizado"
    sleep 5
    show_hostinger_status
}

stop_dashboard() {
    print_header "🛑 Deteniendo Dashboard (N8N permanece activo)...")
    docker-compose -f $COMPOSE_FILE down
    print_success "Dashboard detenido - N8N y otros servicios siguen funcionando"
    
    echo ""
    print_info "Servicios que siguen activos:"
    docker ps --format "table {{.Names}}\t{{.Status}}"
}

start_dashboard() {
    print_header "🚀 Iniciando Dashboard en Hostinger...")
    docker-compose -f $COMPOSE_FILE up -d
    print_success "Dashboard iniciado"
    sleep 5
    show_hostinger_status
}

cleanup_dashboard() {
    print_header "🧹 Limpieza del Dashboard (preservando N8N)..."
    
    print_warning "Esto eliminará imágenes y volúmenes no utilizados del dashboard"
    read -p "¿Continuar? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Limpiar solo imágenes relacionadas con el dashboard
        docker image prune -f
        print_success "Limpieza completada"
        
        print_info "Espacio liberado:"
        df -h / | tail -1
    else
        print_info "Limpieza cancelada"
    fi
}

backup_dashboard() {
    print_header "💾 Backup del Dashboard..."
    
    BACKUP_FILE="backup-dashboard-hostinger-$(date +%Y%m%d_%H%M%S).tar.gz"
    
    tar -czf $BACKUP_FILE \
        .env \
        nginx/ssl/ \
        docker-compose-hostinger.yml \
        nginx/nginx-hostinger.conf
    
    print_success "Backup creado: $BACKUP_FILE"
    print_info "Backup incluye solo configuración del dashboard, no afecta N8N"
}

show_hostinger_urls() {
    print_header "🌐 URLs en Hostinger VPS:"
    echo ""
    
    # Obtener dominio e IP del servidor
    DOMAIN=$(grep "server_name" nginx/nginx-hostinger.conf | head -1 | awk '{print $2}' | sed 's/;//g')
    SERVER_IP=$(curl -s https://ipinfo.io/ip)
    
    if [ "$DOMAIN" != "tu-dominio.com" ]; then
        print_info "📊 Dashboard: https://$DOMAIN"
        print_info "🔄 OAuth Callback: https://$DOMAIN/callback"
        print_info "🏥 Health Check: https://$DOMAIN/app-health"
    else
        print_warning "Dominio no configurado en nginx-hostinger.conf"
    fi
    
    print_info "🏠 Acceso directo: http://$SERVER_IP:8502"
    print_info "📋 Health local: http://localhost:8502/_stcore/health"
    print_info "🔧 Debug local: http://localhost:8080"
    echo ""
    print_info "N8N (si está configurado):"
    print_info "🤖 N8N Dashboard: http://$SERVER_IP:5678"
}

check_conflicts() {
    print_header "🔍 Verificando conflictos con N8N y otros servicios:"
    echo ""
    
    print_info "Puertos utilizados:"
    sudo netstat -tlnp | grep LISTEN | grep -E "(80|443|5678|8080|8443|8502)" 
    echo ""
    
    print_info "Redes Docker:"
    docker network ls
    echo ""
    
    print_info "Volúmenes Docker:"
    docker volume ls | grep -E "(dashboard|n8n)"
    echo ""
    
    # Verificar conflictos específicos
    if sudo netstat -tlnp | grep -q ":8502 "; then
        print_warning "Puerto 8502 ocupado por otro servicio"
    else
        print_success "Puerto 8502 disponible para el dashboard"
    fi
    
    if docker ps | grep -q "n8n"; then
        print_success "N8N detectado y funcionando correctamente"
    else
        print_info "N8N no detectado en este VPS"
    fi
}

show_hostinger_help() {
    print_header "📚 Ayuda - Dashboard en Hostinger VPS:"
    echo ""
    echo "  1) Estado - Estado del dashboard y todos los servicios"
    echo "  2) Logs - Ver logs del dashboard en tiempo real"
    echo "  3) Reiniciar - Reiniciar solo el dashboard"
    echo "  4) Actualizar - Actualizar dashboard desde Git"
    echo "  5) Parar - Detener solo el dashboard"
    echo "  6) Iniciar - Iniciar dashboard"
    echo "  7) Limpiar - Limpiar Docker del dashboard"
    echo "  8) Backup - Backup de configuración"
    echo "  9) URLs - Mostrar todas las URLs"
    echo "  10) Conflictos - Verificar conflictos con N8N"
    echo "  11) Servicios - Estado de todos los servicios"
    echo "  0) Ayuda - Mostrar esta ayuda"
    echo "  q) Salir"
    echo ""
    print_info "📖 Configuración específica para Hostinger VPS"
    print_info "🤖 Compatible con N8N y otros servicios Docker"
}

# ================================
# MENÚ PRINCIPAL HOSTINGER
# ================================

main_menu() {
    while true; do
        clear
        print_header "🎛️ PANEL HOSTINGER VPS - Dashboard de Gastos del Hogar"
        print_info "Administración compatible con N8N y otros servicios Docker"
        echo ""
        
        echo "1)  📊 Estado Dashboard"
        echo "2)  📝 Ver Logs"
        echo "3)  🔄 Reiniciar Dashboard"
        echo "4)  ⬆️ Actualizar Dashboard"
        echo "5)  🛑 Parar Dashboard"
        echo "6)  🚀 Iniciar Dashboard"
        echo "7)  🧹 Limpiar Dashboard"
        echo "8)  💾 Backup"
        echo "9)  🌐 Ver URLs"
        echo "10) 🔍 Verificar Conflictos"
        echo "11) 🌐 Todos los Servicios"
        echo "0)  📚 Ayuda"
        echo "q)  🚪 Salir"
        echo ""
        
        read -p "Selecciona una opción: " choice
        echo ""
        
        case $choice in
            1) show_hostinger_status ;;
            2) show_combined_logs ;;
            3) restart_dashboard ;;
            4) update_dashboard ;;
            5) stop_dashboard ;;
            6) start_dashboard ;;
            7) cleanup_dashboard ;;
            8) backup_dashboard ;;
            9) show_hostinger_urls ;;
            10) check_conflicts ;;
            11) show_all_services_status ;;
            0) show_hostinger_help ;;
            q|Q) print_success "¡Hasta luego!"; exit 0 ;;
            *) print_error "Opción inválida" ;;
        esac
        
        echo ""
        read -p "Presiona ENTER para continuar..."
    done
}

# Ejecutar función directa si se pasa parámetro
if [ $# -eq 1 ]; then
    case $1 in
        status) show_hostinger_status ;;
        logs) show_combined_logs ;;
        restart) restart_dashboard ;;
        update) update_dashboard ;;
        stop) stop_dashboard ;;
        start) start_dashboard ;;
        cleanup) cleanup_dashboard ;;
        backup) backup_dashboard ;;
        urls) show_hostinger_urls ;;
        conflicts) check_conflicts ;;
        services) show_all_services_status ;;
        help) show_hostinger_help ;;
        *) print_error "Comando desconocido: $1"; show_hostinger_help ;;
    esac
else
    main_menu
fi
