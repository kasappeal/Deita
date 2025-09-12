# PRD: Deita

## 1. Product overview

### 1.1 Document title and version

- PRD: Deita
- Version: 1.0.0

### 1.2 Product summary

Deita is a web-based platform designed to empower small business owners and students to extract, explore, and relate data from Excel and CSV files without requiring advanced spreadsheet or SQL skills. The platform enables users to upload files, explore and modify data, run SQL queries, and leverage AI to generate queries and receive suggestions for data relationships. Collaboration is supported via public workspace links, and the platform is accessible on desktop, tablet, and smartphone browsers.

Deita prioritizes ease of use, privacy, and accessibility, offering a seamless experience for both anonymous and registered users. The platform ensures GDPR compliance and provides robust data export options.

## 2. Goals

### 2.1 Business goals

- Lower the barrier for data analysis for non-technical users.
- Increase user engagement and retention through AI-powered features.
- Enable viral growth via public, shareable workspaces.
- Ensure compliance with GDPR and data privacy standards.

### 2.2 User goals

- Easily upload and explore data from Excel/CSV files.
- Relate and analyze data without technical expertise.
- Collaborate and share workspaces via public links.
- Export results for use in other tools.

### 2.3 Non-goals

- No support for file types other than Excel/CSV.
- No advanced user management or audit logs.
- No integrations with third-party storage providers at launch.

## 3. User personas

### 3.1 Key user types

- Small business owners
- Students
- Anonymous users
- Registered users

### 3.2 Basic persona details

- **Small business owner**: Needs to analyze sales, inventory, or customer data without technical skills.
- **Student**: Requires a simple tool for data exploration and assignments.
- **Anonymous user**: Wants to quickly try the platform without signing up.
- **Registered user**: Seeks persistent storage and workspace ownership.

### 3.3 Role-based access

- **Anonymous user**: Can create and use orphan workspaces, upload files, and share via public link.
- **Workspace owner (registered user)**: Can claim, manage, and delete owned workspaces, change visibility, and manage files/queries.

## 4. Functional requirements

- **File upload and management** (Priority: High)

  - Drag-and-drop upload for Excel/CSV files.
  - Support for files up to 50MB (orphan) and 200MB (owned).
  - Each Excel tab is treated as a separate table.
  - Rename and delete tables/files.

- **Data exploration** (Priority: High)

  - View and browse table data in a user-friendly interface.

- **SQL query execution** (Priority: High)

  - Run read-only SQL queries on uploaded tables.
  - Only SELECT queries allowed.

- **AI-powered assistance** (Priority: High)

  - Generate SQL from natural language questions.
  - Provide natural language explanations of results.
  - Suggest relationships and insights between tables.

- **Query management** (Priority: Medium)

  - Save, rename, and delete queries.

- **Workspace management** (Priority: High)

  - Create, claim, and delete workspaces.
  - Change workspace visibility (public/private for owned workspaces).
  - Automatic deletion of unused workspaces (30 days for orphan, 60 days for owned).

- **Collaboration** (Priority: Medium)

  - Share workspaces via public link.

- **Authentication** (Priority: High)

  - Magic link email authentication for sign-up and claiming workspaces.

- **Export** (Priority: Medium)
  - Export SQL query results to CSV/Excel.

## 5. User experience

### 5.1 Entry points & first-time user flow

- Direct access via browser (no login required).
- Drag-and-drop file upload on landing page.
- Option to sign up to claim workspace and enable advanced features.

### 5.2 Core experience

- **Upload and explore**: Users upload files and immediately see tables for exploration.
  - Ensures a fast, frictionless start.
- **Query and AI assistance**: Users can write SQL or ask questions in natural language.
  - AI provides both SQL and explanations, making data analysis accessible.
- **Save and share**: Users can save queries and share workspace links.
  - Promotes collaboration and repeat usage.

### 5.3 Advanced features & edge cases

- Multiple file uploads at once.
- Handling Excel files with multiple tabs.
- File size and storage limits enforced per workspace type.
- Automatic workspace deletion after inactivity.
- Workspace claiming and ownership transfer.

### 5.4 UI/UX highlights

- Responsive design for all devices.
- Intuitive drag-and-drop upload.
- Clear feedback for errors (e.g., file size/type limits).
- Simple, clean data table views.
- Prominent AI assistance and export options.

## 6. Narrative

A small business owner visits Deita, uploads sales and inventory files, and immediately explores the data. Unsure how to relate the tables, they ask the AI for help, which generates the necessary SQL and explains the results. The user saves useful queries, exports results to Excel, and shares the workspace link with a colleague. Later, they sign up to claim the workspace and keep their data persistent.

## 7. Success metrics

### 7.1 User-centric metrics

- Number of files uploaded per user.
- Frequency of AI-assisted queries.
- Number of workspaces created and shared.
- Export actions per user.

### 7.2 Business metrics

- User retention rate.
- Conversion rate from anonymous to registered users.
- Workspace sharing rate.

### 7.3 Technical metrics

- Average query execution time.
- File upload success rate.
- Workspace deletion compliance (timely removal).

## 8. Technical considerations

### 8.1 Integration points

- AI model for natural language to SQL and explanations.
- Email service for magic link authentication.
- File storage (local or cloud, e.g., Hertzner).

### 8.2 Data storage & privacy

- Encrypt data at rest and in transit.
- Store only Excel/CSV files and query metadata.
- GDPR-compliant data handling and user consent.
- Automatic deletion of unused data.

### 8.3 Scalability & performance

- Efficient handling of large files (up to 200MB).
- Scalable storage and compute for concurrent users.
- Responsive UI for large datasets.

### 8.4 Potential challenges

- Ensuring GDPR compliance across all features.
- Handling malformed or very large files.
- Preventing abuse of public workspaces.
- Managing AI accuracy and user expectations.

## 9. Milestones & sequencing

### 9.1 Project estimate

- Medium: 3-4 months

### 9.2 Team size & composition

- 4-6: Product manager, frontend developer, backend developer, AI/ML engineer, designer, QA

### 9.3 Suggested phases

- **Phase 1**: Core file upload, data exploration, and workspace management (1 month)
  - File upload, table view, workspace creation/deletion
- **Phase 2**: SQL query engine and AI assistance (1 month)
  - SQL execution, AI query generation, explanations
- **Phase 3**: Query management, export, and collaboration (1 month)
  - Save/rename/delete queries, export, public links
- **Phase 4**: Authentication, GDPR, and polish (1-2 months)
  - Magic link auth, compliance, UI/UX improvements

## 10. User stories

### 10.1. Create workspace

- **ID**: GH-000
- **Description**: As a user, I want a workspace to be automatically created when I first visit the platform so I can start working with data immediately, and I want to be able to create additional workspaces after signing up.
- **Acceptance criteria**:
  - An orphan workspace is automatically created when an anonymous user first visits the platform.
  - Anonymous users can only have one active orphan workspace at a time.
  - Registered users can create multiple owned workspaces.
  - Users must sign up to create additional workspaces beyond the initial orphan workspace.

### 10.2. Upload files to workspace

- **ID**: GH-001
- **Description**: As a user, I want to upload Excel or CSV files by drag-and-drop so I can analyze my data.
- **Acceptance criteria**:
  - User can upload files via drag-and-drop.
  - Only Excel/CSV files are accepted.
  - File size and workspace storage limits are enforced.

### 10.3. View list of tables in workspace

- **ID**: GH-002
- **Description**: As a user, I want to see a list of all tables/files in my workspace so I can select which one to explore.
- **Acceptance criteria**:
  - User can see a list of all tables/files in the workspace.

### 10.4. View data of a table in tabular format

- **ID**: GH-003
- **Description**: As a user, I want to view the data of a selected table in a tabular format so I can explore its contents.
- **Acceptance criteria**:
  - User can select a table/file from the list.
  - User can view the data in a tabular format.

### 10.5. Rename tables/files

- **ID**: GH-004
- **Description**: As a user, I want to rename tables or files in my workspace so I can organize my data.
- **Acceptance criteria**:
  - User can rename any table or file in the workspace.

### 10.6. Delete tables/files

- **ID**: GH-005
- **Description**: As a user, I want to delete tables or files from my workspace so I can remove unwanted data.
- **Acceptance criteria**:
  - User can delete any table or file in the workspace.

### 10.7. Run SQL queries

- **ID**: GH-006
- **Description**: As a user, I want to run read-only SQL queries on my data tables so I can analyze my data.
- **Acceptance criteria**:
  - User can enter and execute SELECT queries.
  - Only read-type queries are allowed.

### 10.8. Generate SQL from natural language

- **ID**: GH-007
- **Description**: As a user, I want to ask questions in natural language and have the AI generate the corresponding SQL query.
- **Acceptance criteria**:
  - User can enter a question in natural language.
  - AI generates a valid SQL query based on the question.

### 10.9. Receive natural language explanation of results

- **ID**: GH-008
- **Description**: As a user, I want the AI to provide a natural language explanation of my SQL query results so I can better understand the data.
- **Acceptance criteria**:
  - After running a query, the AI provides a clear explanation of the results in natural language.

### 10.10. Receive AI suggestions for data relationships

- **ID**: GH-009
- **Description**: As a user, I want the AI to suggest relationships or insights between tables so I can discover useful connections in my data.
- **Acceptance criteria**:
  - AI suggests possible relationships or insights between tables after file upload or on request.

### 10.11. Save queries

- **ID**: GH-010
- **Description**: As a user, I want to save my SQL queries with a custom name so I can reuse them later.
- **Acceptance criteria**:
  - User can save any executed query with a custom name.

### 10.12. Rename saved queries

- **ID**: GH-011
- **Description**: As a user, I want to rename my saved queries so I can keep them organized.
- **Acceptance criteria**:
  - User can rename any saved query.

### 10.13. Delete saved queries

- **ID**: GH-012
- **Description**: As a user, I want to delete saved queries so I can remove those I no longer need.
- **Acceptance criteria**:
  - User can delete any saved query.

### 10.14. Delete workspace

- **ID**: GH-013
- **Description**: As a user, I want to delete a workspace and all its data if I am the owner, or if it is unclaimed.
- **Acceptance criteria**:
  - Only owners can delete owned workspaces.
  - Orphan workspaces can be deleted by any user.
  - All data is removed upon deletion.

### 10.15. Signup with magic link

- **ID**: GH-014
- **Description**: As a user, I want to sign up using a magic link sent to my email so I can claim and own workspaces.
- **Acceptance criteria**:
  - User can sign up with email and receive a magic link.

### 10.16. Claim orphan workspace

- **ID**: GH-015
- **Description**: As a user, I want to claim an orphan workspace after signing up so I can become its owner.
- **Acceptance criteria**:
  - User can claim an orphan workspace and become its owner.

### 10.17. Automatic workspace deletion

- **ID**: GH-016
- **Description**: As a user, I want unused workspaces to be deleted automatically after a set period so that old data is not retained indefinitely.
- **Acceptance criteria**:
  - Orphan workspaces deleted after 30 days of inactivity.
  - Owned workspaces deleted after 60 days of inactivity.

### 10.18. Change workspace visibility

- **ID**: GH-017
- **Description**: As a workspace owner, I want to change the visibility of my workspace between public and private so I can control access.
- **Acceptance criteria**:
  - Owner can toggle visibility.
  - Orphan workspaces are always public.

### 10.19. Share workspace via public link

- **ID**: GH-018
- **Description**: As a user, I want to share my workspace with others using a public link so they can view or collaborate.
- **Acceptance criteria**:
  - Each workspace has a unique URL.
  - Anyone with the link can access the workspace (subject to visibility settings).

### 10.20. Export query results

- **ID**: GH-019
- **Description**: As a user, I want to export the results of my SQL queries to CSV or Excel files so I can use the data elsewhere.
- **Acceptance criteria**:
  - User can export query results in CSV or Excel format.

### 10.21. Authentication and security

- **ID**: GH-020
- **Description**: As a user, I want my data to be secure and my privacy protected in compliance with GDPR.
- **Acceptance criteria**:
  - Data is encrypted at rest and in transit.
  - User consent is obtained for data storage.
  - Users can request deletion of their data.

### 10.22. Delete expired export links and files

- **ID**: GH-021
- **Description**: As a user, I want expired export links and their files to be deleted automatically so that old exported data is not retained.
- **Acceptance criteria**:
  - Export links expire after a set period (e.g., 1 hour).
  - Expired export files are deleted from storage and removed from the workspace.
  - User receives an error if trying to access an expired export link.
