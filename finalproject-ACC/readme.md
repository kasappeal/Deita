## Índice

0. [Ficha del proyecto](#0-ficha-del-proyecto)
1. [Descripción general del producto](#1-descripción-general-del-producto)
2. [Arquitectura del sistema](#2-arquitectura-del-sistema)
3. [Modelo de datos](#3-modelo-de-datos)
4. [Especificación de la API](#4-especificación-de-la-api)
5. [Historias de usuario](#5-historias-de-usuario)
6. [Tickets de trabajo](#6-tickets-de-trabajo)
7. [Pull requests](#7-pull-requests)

---

## 0. Ficha del proyecto

### **0.1. Tu nombre completo:**

Alberto Casero Campos

### **0.2. Nombre del proyecto:**

Deita

### **0.3. Descripción breve del proyecto:**

Deita es una plataforma cuyo objetivo principal es facilitar el análisis de información a partid de datos a personas no tećnicas. 

### **0.4. URL del proyecto:**

https://deita.casero.dev

### 0.5. URL o archivo comprimido del repositorio

https://github.com/kasappeal/Deita

---

## 1. Descripción general del producto

> Describe en detalle los siguientes aspectos del producto:

### **1.1. Objetivo:**

Deita is a web-based platform designed to empower small business owners and students to extract, explore, and relate data from Excel and CSV files without requiring advanced spreadsheet or SQL skills. The platform enables users to upload files, explore and modify data, run SQL queries, and leverage AI to generate queries and receive suggestions for data relationships. Collaboration is supported via public workspace links, and the platform is accessible on desktop, tablet, and smartphone browsers.

Deita prioritizes ease of use, privacy, and accessibility, offering a seamless experience for both anonymous and registered users. The platform ensures GDPR compliance and provides robust data export options.

### **1.2. Características y funcionalidades principales:**

* **File upload and management** (Priority: High)
  * Drag-and-drop upload for Excel/CSV files.
  * Support for files up to 50MB (orphan) and 200MB (owned).
  * Each Excel tab is treated as a separate table.
  * Rename and delete tables/files.

* **Data exploration** (Priority: High)
  * View and browse table data in a user-friendly interface.

* **SQL query execution** (Priority: High)
  * Run read-only SQL queries on uploaded tables.
  * Only SELECT queries allowed.

* **AI-powered assistance** (Priority: High)
  * Generate SQL from natural language questions.
  * Provide natural language explanations of results.
  * Suggest relationships and insights between tables.

* **Query management** (Priority: Medium)
  * Save, rename, and delete queries.

* **Workspace management** (Priority: High)
  * Create, claim, and delete workspaces.
  * Change workspace visibility (public/private for owned workspaces).
  * Automatic deletion of unused workspaces (30 days for orphan, 60 days for owned).

* **Collaboration** (Priority: Medium)
  * Share workspaces via public link.

* **Authentication** (Priority: High)
  * Magic link email authentication for sign-up and claiming workspaces.

* **Export** (Priority: Medium)
  * Export SQL query results to CSV/Excel.

### **1.3. Diseño y experiencia de usuario:**

> Proporciona imágenes y/o videotutorial mostrando la experiencia del usuario desde que aterriza en la aplicación, pasando por todas las funcionalidades principales.

https://www.loom.com/share/294a3c0b93564bf68929d26e677c2b93?sid=64e224c2-79c9-4021-bc31-10d890263b2c

### **1.4. Instrucciones de instalación:**
> Documenta de manera precisa las instrucciones para instalar y poner en marcha el proyecto en local (librerías, backend, frontend, servidor, base de datos, migraciones y semillas de datos, etc.)

https://github.com/kasappeal/Deita/blob/main/docs/11-dev-environment.md

---

## 2. Arquitectura del Sistema

### **2.1. Diagrama de arquitectura:**
> Usa el formato que consideres más adecuado para representar los componentes principales de la aplicación y las tecnologías utilizadas. Explica si sigue algún patrón predefinido, justifica por qué se ha elegido esta arquitectura, y destaca los beneficios principales que aportan al proyecto y justifican su uso, así como sacrificios o déficits que implica.

https://github.com/kasappeal/Deita/blob/main/docs/01-system-architecture.md

### **2.2. Descripción de componentes principales:**

> Describe los componentes más importantes, incluyendo la tecnología utilizada

https://github.com/kasappeal/Deita/blob/main/docs/01-system-architecture.md#key-components

### **2.3. Descripción de alto nivel del proyecto y estructura de ficheros**

> Representa la estructura del proyecto y explica brevemente el propósito de las carpetas principales, así como si obedece a algún patrón o arquitectura específica.

https://github.com/kasappeal/Deita/blob/main/docs/02-technology-stack.md
https://github.com/kasappeal/Deita/blob/main/docs/05-service-boundaries.md

### **2.4. Infraestructura y despliegue**

> Detalla la infraestructura del proyecto, incluyendo un diagrama en el formato que creas conveniente, y explica el proceso de despliegue que se sigue

https://github.com/kasappeal/Deita/blob/main/docs/01-system-architecture.md
https://github.com/kasappeal/Deita/blob/main/docs/09-deployment-best-practices.md


### **2.5. Seguridad**

> Enumera y describe las prácticas de seguridad principales que se han implementado en el proyecto, añadiendo ejemplos si procede

https://github.com/kasappeal/Deita/blob/main/docs/07-security.md

### **2.6. Tests**

> Describe brevemente algunos de los tests realizados

- Unit tests for [frontend](https://github.com/kasappeal/Deita/tree/main/frontend/src/__tests__)
- Unit and integration tests for [backend](https://github.com/kasappeal/Deita/tree/main/backend/app/tests) 

---

## 3. Modelo de Datos

### **3.1. Diagrama del modelo de datos:**

> Recomendamos usar mermaid para el modelo de datos, y utilizar todos los parámetros que permite la sintaxis para dar el máximo detalle, por ejemplo las claves primarias y foráneas.

https://github.com/kasappeal/Deita/blob/main/docs/03-data-model-design.md#entity-relationship-diagram-mermaidjs

### **3.2. Descripción de entidades principales:**

> Recuerda incluir el máximo detalle de cada entidad, como el nombre y tipo de cada atributo, descripción breve si procede, claves primarias y foráneas, relaciones y tipo de relación, restricciones (unique, not null…), etc.

https://github.com/kasappeal/Deita/blob/main/docs/03-data-model-design.md#key-entities

---

## 4. Especificación de la API

> Si tu backend se comunica a través de API, describe los endpoints principales (máximo 3) en formato OpenAPI. Opcionalmente puedes añadir un ejemplo de petición y de respuesta para mayor claridad

https://deitapi.casero.dev/docs
https://deitapi.casero.dev/v1/openapi.json

---

## 5. Historias de Usuario

> Documenta 3 de las historias de usuario principales utilizadas durante el desarrollo, teniendo en cuenta las buenas prácticas de producto al respecto.

https://github.com/kasappeal/Deita/issues/46

https://github.com/kasappeal/Deita/issues/2

https://github.com/kasappeal/Deita/issues/12

---

## 6. Tickets de Trabajo

> Documenta 3 de los tickets de trabajo principales del desarrollo, uno de backend, uno de frontend, y uno de bases de datos. Da todo el detalle requerido para desarrollar la tarea de inicio a fin teniendo en cuenta las buenas prácticas al respecto. 

https://github.com/kasappeal/Deita/issues/49

https://github.com/kasappeal/Deita/issues/34

https://github.com/kasappeal/Deita/issues/87

---

## 7. Pull Requests

> Documenta 3 de las Pull Requests realizadas durante la ejecución del proyecto

https://github.com/kasappeal/Deita/pull/122

https://github.com/kasappeal/Deita/pull/125

https://github.com/kasappeal/Deita/pull/137c
