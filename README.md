# Documentación para Levantar el Proyecto en GitHub Codespaces con Docker Compose

Este proyecto utiliza **Docker Compose** para gestionar múltiples servicios, incluyendo una aplicación **FastAPI**, una base de datos **PostgreSQL**, **pgAdmin**, **Prometheus**, y **Grafana**. A continuación, se detallan los pasos para levantar el proyecto en **GitHub Codespaces**.

---

## Estructura del Proyecto

El proyecto tiene la siguiente estructura de directorios:
red_social/
│
├── backend/
│ ├── app/
│ │ ├── init.py
│ │ ├── main.py
│ │ ├── models.py
│ │ ├── schemas.py
│ │ ├── crud.py
│ │ ├── database.py
│ │ └── templates/
│ │ └── index.html
│ ├── requirements.txt
│ └── Dockerfile
│
├── grafana/
│ └── provisioning/
│ ├── dashboards/
│ │ └── dashboard.yml
│ └── datasources/
│ └── datasource.yml
│
├── prometheus/
│ └── prometheus.yml
│
├── docker-compose.yml
└── README.md

Copy

---

## Servicios en Docker Compose

El archivo `docker-compose.yml` define los siguientes servicios:

1. **PostgreSQL**: Base de datos para la aplicación.
2. **FastAPI**: Backend de la aplicación.
3. **pgAdmin**: Interfaz gráfica para administrar PostgreSQL.
4. **Prometheus**: Sistema de monitoreo y alertas.
5. **Grafana**: Herramienta de visualización de métricas.

---

## Pasos para Levantar el Proyecto

### 1. Clonar el Repositorio
Clona el repositorio en tu entorno de **GitHub Codespaces**:

```bash
git clone <URL_DEL_REPOSITORIO>
cd red_social
2. Configurar Docker Compose
Asegúrate de que el archivo docker-compose.yml esté correctamente configurado. Aquí tienes un ejemplo:

yaml
Copy
version: '3.8'

services:
  db:
    image: postgres:latest
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: red_social
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - red_social_network

  backend:
    build: ./backend
    command: >
      sh -c "/app/wait-for-it.sh db:5432 --timeout=30 -- uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    networks:
      - red_social_network

  pgadmin:
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    depends_on:
      - db
    networks:
      - red_social_network

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    depends_on:
      - db
    networks:
      - red_social_network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    depends_on:
      - db
    networks:
      - red_social_network

volumes:
  postgres_data:
  grafana_data:

networks:
  red_social_network:
    driver: bridge
3. Levantar los Servicios
Ejecuta el siguiente comando para levantar todos los servicios:

bash
Copy
docker-compose up --build
Esto construirá las imágenes y levantará los contenedores.

4. Acceder a los Servicios
Una vez que los contenedores estén en ejecución, puedes acceder a los servicios desde tu navegador:

FastAPI: http://localhost:8000 (o la URL generada por Codespaces).

pgAdmin: http://localhost:5050 (o la URL generada por Codespaces).

Prometheus: http://localhost:9090 (o la URL generada por Codespaces).

Grafana: http://localhost:3000 (o la URL generada por Codespaces).

5. Configurar Grafana
Inicia sesión en Grafana con las credenciales predeterminadas:

Usuario: admin

Contraseña: admin

Configura el origen de datos de PostgreSQL en Grafana:

Ve a Configuration > Data Sources.

Selecciona PostgreSQL.

Configura la conexión con los siguientes detalles:

Host: db:5432

Database: red_social

User: user

Password: password

Importa un dashboard o crea uno nuevo para visualizar las métricas.

6. Detener los Servicios
Para detener los servicios, ejecuta:

bash
Copy
docker-compose down
Solución de Problemas Comunes
1. Error de conexión a PostgreSQL
Verifica que el servicio db esté en ejecución.

Asegúrate de que las credenciales (user, password, database) sean correctas.

2. Error en Prometheus
Revisa que el archivo prometheus.yml esté correctamente configurado.

Asegúrate de que el Postgres Exporter esté sirviendo métricas en http://postgres_exporter:9087/metrics.

3. Error en Grafana
Verifica que el origen de datos de PostgreSQL esté correctamente configurado.

Asegúrate de que Grafana tenga permisos para acceder a la base de datos.

