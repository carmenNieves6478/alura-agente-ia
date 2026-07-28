# Base de Conocimiento del Producto - NexusSaaS

## 1. Visión General de la Plataforma
NexusSaaS es una plataforma digital basada en la nube diseñada para la automatización de flujos de trabajo empresariales y análisis predictivo mediante inteligencia artificial.

## 2. Arquitectura Tecnológica y Stack
- **Frontend**: React 18, TypeScript, TailwindCSS.
- **Backend**: Python (FastAPI) para servicios de IA y procesamiento asíncrono; Node.js (NestJS) para la API principal de microservicios.
- **Bases de Datos**: PostgreSQL para datos relacionales estructurados, Redis para almacenamiento en caché y gestión de sesiones, y Qdrant como base de datos vectorial para embeddings.
- **Infraestructura Cloud**: Desplegado en Oracle Cloud Infrastructure (OCI) Compute Instances con Kubernetes (OKE).
- **Seguridad**: Autenticación OAuth 2.0 / JWT con MFA obligatorio para cuentas de administradores.

## 3. Características Principales
- **Agentes Autónomos**: Creación de bots de atención y automatización sin código (No-Code workflow builder).
- **Integraciones**: Conectores nativos con Slack, Microsoft Teams, Salesforce, HubSpot y webhooks personalizados.
- **Motor de Analítica**: Tableros en tiempo real con métricas de rendimiento y predicción de demanda.

## 4. Requisitos del Sistema para Clientes
- Navegadores soportados: Google Chrome (v100+), Mozilla Firefox (v95+), Safari (v15+), Microsoft Edge.
- Conexión a internet mínima de 5 Mbps.
