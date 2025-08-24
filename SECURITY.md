# Política de Seguridad

## 🔐 Versiones Soportadas

Actualmente mantenemos soporte de seguridad para la siguiente versión:

| Versión | Soporte |
| ------- | ------ |
| 1.0.x   | ✅     |

## 🚨 Reportar una Vulnerabilidad

Si descubres una vulnerabilidad de seguridad, por favor sigue estos pasos:

1. **NO** crees un issue público
2. Envía un email a: [tu-email-de-seguridad@example.com]
3. Incluye una descripción detallada del problema
4. Proporciona pasos para reproducir la vulnerabilidad
5. Si es posible, incluye una solución sugerida

## 🛡️ Mejores Prácticas de Seguridad

### Variables de Entorno
- ✅ **NUNCA** commits archivos `.env` al repositorio
- ✅ Usa `.env.example` como plantilla
- ✅ Rota tus credenciales regularmente
- ✅ Usa credenciales diferentes para desarrollo y producción

### Credenciales de Azure
- ✅ Configura permisos mínimos necesarios
- ✅ Usa aplicaciones separadas para diferentes entornos
- ✅ Habilita logging y monitoreo de accesos
- ✅ Revisa los permisos de tu aplicación Azure regularmente

### API Keys de OpenAI
- ✅ Usa variables de entorno para almacenar keys
- ✅ Configura límites de uso apropiados
- ✅ Monitorea el uso de tu API key
- ✅ Rota las keys periódicamente

### Despliegue Seguro
- ✅ Usa HTTPS en producción
- ✅ Configura firewalls apropiados
- ✅ Mantén las dependencias actualizadas
- ✅ Habilita logging de seguridad

## 🔍 Auditorías de Dependencias

Ejecuta regularmente:

```bash
pip audit
```

Para verificar vulnerabilidades conocidas en las dependencias.

## 📞 Contacto

Para preguntas sobre seguridad, contacta:
- Email: [tu-email@example.com]
- Issues de seguridad: [Enlace a política de reporte]

## 🏆 Reconocimientos

Agradecemos a todos los investigadores de seguridad que reportan vulnerabilidades de manera responsable.
