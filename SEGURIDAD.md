# Recomendaciones de seguridad aplicadas

Este documento registra las recomendaciones solicitadas para la actividad y cómo se
aplicaron en el ecosistema de Mesa Financiera.

## Controles implementados

1. **Secretos fuera del código.** Las llaves se leen desde variables de entorno o
   GitHub Actions Secrets. El archivo `.env` está excluido del repositorio.
2. **Errores sin credenciales.** Los mensajes de error eliminan tokens y llaves antes
   de mostrarse en consola, para evitar filtraciones en los registros de Actions.
3. **Acceso cerrado por defecto.** Si no existe `TELEGRAM_CHAT_ID`, el bot no inicia
   la lectura de mensajes. Además, compara el chat recibido con el chat autorizado.
4. **Validación de entradas.** El ticker solo acepta de 1 a 12 caracteres seguros,
   debe incluir al menos una letra y rechaza comandos o símbolos inesperados.
5. **Defensa ante instrucciones maliciosas.** Los agentes tratan las respuestas de
   herramientas y los datos financieros como contenido no confiable; no obedecen
   instrucciones que aparezcan dentro de esos datos.
6. **Continuidad segura.** Si OpenAI no responde, Euler y Vera usan una salida
   determinista y conservan el aviso de que el contenido es educativo.
7. **Automatización acotada.** GitHub Actions tiene permisos de solo lectura,
   límite de tiempo, control de concurrencia, máximo de análisis por ejecución y
   retención limitada de artefactos.

## Verificación

Las pruebas automáticas comprueban la validación de tickers, el bloqueo cuando falta
el chat autorizado, la ocultación de secretos, el respaldo ante fallas de OpenAI, la
protección de los prompts y el cron de 15 minutos.

## Recomendaciones de operación

- Rotar inmediatamente cualquier llave que se publique o comparta por accidente.
- Mantener activada la autenticación de dos factores en GitHub y Telegram.
- Conceder a colaboradores únicamente el acceso necesario.
- Revisar periódicamente las ejecuciones y el consumo de las APIs.
- No publicar capturas que muestren el valor de un secreto; solo sus nombres.
