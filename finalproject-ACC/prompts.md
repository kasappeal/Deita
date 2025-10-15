> Detalla en esta sección los prompts principales utilizados durante la creación del proyecto, que justifiquen el uso de asistentes de código en todas las fases del ciclo de vida del desarrollo. Esperamos un máximo de 3 por sección, principalmente los de creación inicial o  los de corrección o adición de funcionalidades que consideres más relevantes.
Puedes añadir adicionalmente la conversación completa como link o archivo adjunto si así lo consideras


## Índice

1. [Descripción general del producto](#1-descripción-general-del-producto)
2. [Arquitectura del sistema](#2-arquitectura-del-sistema)
3. [Modelo de datos](#3-modelo-de-datos)
4. [Especificación de la API](#4-especificación-de-la-api)
5. [Historias de usuario](#5-historias-de-usuario)
6. [Tickets de trabajo](#6-tickets-de-trabajo)
7. [Pull requests](#7-pull-requests)

---

## 1. Descripción general del producto

**Prompt 1:**

Using Github Copilot and [PRD chat mode](https://github.com/github/awesome-copilot/blob/main/chatmodes/prd.chatmode.md) + Github, Sequential Thinking and Memory MCPs

```markdown
I want to build a platform called "Deita". 

Its main goal is to be the tool to be used to extract the information needed for people that works with data in file formats like Excel or CSV but don't have deep knoledge about how to use Excel to, for example, make a vlookup to cross information between two tabs or two files.

## Features

* Upload files to workspace: users must can upload CSV or Excel files by drag and drop files into the web site
* Explore data: user must be able to expore tables data
* Modify data: users must be able to delete tables (files) or modify its names.
* Run SQL queries against data: users must be able to run SQL queries over the tables created by uploading files
* Ask AI for information: if user doens't know how to write SQL, must be able to ask AI to retrieve the data they want. AI must generate the SQL, run it and return the information.
* Receive AI suggestions: user should be able to receive AI suggestions about the data they upload. Suggestions can be how to relate different tables of insights about data uploaded.
* Save queries: users must be able to save queries with a name to be reused in the future.
* Rename/delete queries: users must be able to rename/delete queries.
* Delete workspace: users should be able to delete a workspace, if workspace is not owned by any user. If a workspace is owned, only the owner can delete the workspace. When a workspace is deleted, all files and data generated must be deleted from the server.
* Signup: users must be able to signup. 
* Claim for a workspace: when a workspace is created for an anonymous user, has no owner and it can be claimed for a signed up user. When a workspace is claimed for a signed up user, the user becames the workspace owner.
* Automatic workspace deletion: when a workspaces has been unused for 30 days and has no owner, must be deleted. If the workspace has owner, it must be deleted after 60 days of unuse.
* Change workspace visibility: every orphan workspace has public visibility. Owned workspaces can have public or private visibility and it can be changed by the workspace owner.
* Export data: data results must be exported in CSV/Excel

## Requirements

* Be a web app that anyone can use just by using a browser in its desktop/tablet/smartphone
* No login required: just enter and start using the tool
* Despite no login required, if user comes back to the web using the same browser, data must be kept
* Workspaces must be shareable publicly
* Excel and CSV formats must be supported
* Only Excel and CSV files must be uploaded to the platform
* Orphan workspaces must be deleted after 30 days of unuse
* Files can't have more than 50MB of size in orphan repositores and 200MB on owned workspaces
* Orphan workspaces can't have more than 50MB of stored files and owned workspaces can have up to 200MB
* A signed up user can't have more than 200MB stored in all workspaces
* Each file must be treated as a table in a database. In the case of Excel files with multiple tabs, each tab must be considered as a database table.
* Only read-type SQL queries must be allowed. No inserts, updates, deletes, ddl or any other SQL operation must be allowed.
* Every workspace must have its own URL

## Expected output

Generate a PRD document in markdown format and a list of 

```

**Prompt 2:**

Using Github Copilot and [PRD chat mode](https://github.com/github/awesome-copilot/blob/main/chatmodes/prd.chatmode.md) + Github, Sequential Thinking and Memory MCPs

```markdown
could you breakdown more the tasks in smaller ones?

For example:

In GH-002 the acceptance criteria is:

User can see a list of tables/files.
User can view data in a tabular format.
I would break down this into two user stories:

View a list of tables in workspace
View data of one table in tabular format
Another example: in GH-003 "Modify tables/files" acceptance criteria items are:

User can rename tables/files.
User can delete tables/files.
I would prefer to have two user stories:

Rename tables/files
Delete tables/files
My point of view about user story is that a user story has to be a single simple action the user can make or receive from the system.

By having smaller user stories, we can focus more on how each user story must work and we can split the work to be accomplished in paralell.

What do you whink?
``` 

**Prompt 3:**

Using Github Copilot and [Principal Software Engineer chat mode](https://github.com/github/awesome-copilot/blob/main/chatmodes/principal-software-engineer.chatmode.md) + Github, Sequential Thinking and Memory MCPs

```markdown
We have to design the whole system architecture and document it.

## Instructions

Follow strictly this steps. Do not start go to a next step without ask the user if you can.

1. Analyze deeply #file:prd.md (take your time, hours if needed)
2. Make any question you have using a numbered list, one question per line
3. Suggest me the best architecture and good practices to use including: 
    - Comprehensive architectural analysis and recommendations
    - Overall System Architecture
    - Technology Stack Recommendations
    - Data Model Design
    - API Design & Service Boundaries
    - Performance & Scalability Considerations
    - Security Considerations
    - Development Best Practices
    - Deployment Best Practices
    - Risk Assessment & Technical Debt Considerations
4. Generate all the documentation using markdown in a `docs` folder. Use plantuml for C4 diagrams and mermaidjs for any other diagram you need to design. The purpose of this documents will be documentation to be used for humans and LLMs to create code based on that rules.
``` 

---

## 2. Arquitectura del Sistema

### **2.1. Diagrama de arquitectura:**

**Prompt 1:**

Using Github Copilot and [PRD chat mode](https://github.com/github/awesome-copilot/blob/main/chatmodes/prd.chatmode.md) + Github, Sequential Thinking and Memory MCPs

```markdown
We have to design the whole system architecture.

Instructions
1. Analyze deeply #file:prd.md (take your time, hours if needed)
Make any question you have using a numbered list, one question per line
Suggest me the best architecture and good practices to use including:
Comprehensive architectural analysis and recommendations
Overall System Architecture
Technology Stack Recommendations
Data Model Design
API Design & Service Boundaries
Performance & Scalability Considerations
Security Considerations
Development Best Practices
Deployment Best Practices
Risk Assessment & Technical Debt Considerations
Generate all the documentation using markdown in a docs folder. Use plantuml for C4 diagrams and mermaidjs for any other diagram you need to design. The purpose of this documents will be documentation to be used for humans and LLMs to create code based on that rules.
Ask for confirmation before go for the next step.
```

### **2.2. Descripción de componentes principales:**

Prompt de 2.1

### **2.3. Descripción de alto nivel del proyecto y estructura de ficheros**

Prompt de 2.1

### **2.4. Infraestructura y despliegue**

Prompt de 2.1

### **2.5. Seguridad**

Prompt de 2.1

### **2.6. Tests**

Prompt de 2.1

---

### 3. Modelo de Datos

Prompt de 2.1

---

### 4. Especificación de la API

There's no one prompt. It  has been iterative while developing.

---

### 5. Historias de Usuario

I just forgot to save the prompt, but basically I asked to use GitHub MCP to create issues with User Stories and for each User Story, create three type of subtask: UX/UI design, frontend development and backend development.

For each type of subtask I provided an example template for each type of task.

---

### 6. Tickets de Trabajo

Prompt used in previous section created all job tickets.

---

### 7. Pull Requests

By asigning GitHub Issues to Copilot, it came came back with the PR.
