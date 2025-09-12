# API Design

## Overview
The API for Deita is designed to be RESTful, secure, and easy to consume by the React frontend. It supports all core features: file upload, data exploration, SQL/AI queries, workspace management, authentication, and export.

## Main Endpoints

### Authentication

#### Get current user info

`GET /auth/me`

##### OpenAPI Specification

```yaml
get:
	summary: Get current authenticated user info
	tags:
		- Authentication
	security:
		- bearerAuth: []
	responses:
		'200':
			description: Current user info
			content:
				application/json:
					schema:
						type: object
						properties:
							id:
								type: string
								example: "user_123"
							email:
								type: string
								format: email
								example: "user@example.com"
							name:
								type: string
								example: "Jane Doe"
		'401':
			description: Unauthorized (missing or invalid token)
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
GET /auth/me

Authorization: Bearer <token>
```

##### Success Response Example

```http
200 OK

{
	"id": "user_123",
	"email": "user@example.com",
	"name": "Jane Doe"
}
```

##### Error Response Example

```http
401 Unauthorized

{
	"error": "Unauthorized."
}
```

#### Request magic link for email

`POST /auth/magic-link`

##### OpenAPI Specification

```yaml
post:
	summary: Request magic link for email authentication
	tags:
		- Authentication
	requestBody:
		required: true
		content:
			application/json:
				schema:
					type: object
					properties:
						email:
							type: string
							format: email
							example: user@example.com
					required:
						- email
	responses:
		'200':
			description: Magic link sent successfully
			content:
				application/json:
					schema:
						type: object
						properties:
							message:
								type: string
								example: Magic link sent to your email.
		'400':
			description: Invalid email or missing field
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Invalid email address.
		'429':
			description: Rate limit exceeded
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Too many requests. Please try again later.
```

##### Request Example

```http
POST /auth/magic-link

Content-Type: application/json

{
	"email": "user@example.com"
}
``` 

##### Success Response Example

```http
200 OK

{
	"message": "Magic link sent to your email."
}
``` 

##### Error Response Example

```http
400 Bad Request

{
	"error": "Invalid email address."
}
``` 

#### Verify magic link token

`POST /auth/verify`

##### OpenAPI Specification

```yaml
post:
	summary: Verify magic link token and issue JWT
	tags:
		- Authentication
	requestBody:
		required: true
		content:
			application/json:
				schema:
					type: object
					properties:
						token:
							type: string
							example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
					required:
						- token
	responses:
		'200':
			description: Token verified, JWT issued
			content:
				application/json:
					schema:
						type: object
						properties:
							jwt:
								type: string
								example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
							user:
								type: object
								properties:
									id:
										type: string
										example: "user_123"
									email:
										type: string
										format: email
										example: "user@example.com"
									name:
										type: string
										example: "Jane Doe"
		'400':
			description: Invalid or expired token
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Invalid or expired token.
		'429':
			description: Rate limit exceeded
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Too many requests. Please try again later.
							code:
								type: integer
								example: 429
```

##### Request Example

```http
POST /auth/verify

Content-Type: application/json

{
	"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

##### Success Response Example

```http
200 OK

{
	"jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
	"user": {
		"id": "user_123",
		"email": "user@example.com",
		"name": "Jane Doe"
	}
}
```

##### Error Response Example

```http
400 Bad Request

{
	"error": "Invalid or expired token."
}
```

### Workspace

#### Update workspace (visibility, claim, etc.)

`PATCH /workspaces/:workspace_id`

##### OpenAPI Specification

```yaml
patch:
	summary: Update workspace properties (visibility, claim, etc.)
	tags:
		- Workspace
	security:
		- bearerAuth: []
	parameters:
		- name: id
			in: path
			required: true
			schema:
				type: string
			example: 456
	requestBody:
		required: true
		content:
			application/json:
				schema:
					type: object
					properties:
						name:
							type: string
							example: "Sales Analysis"
						visibility:
							type: string
							enum: [public, private]
							example: "private"
						claim:
							type: boolean
							example: true
					# All fields optional for PATCH
	responses:
		'200':
			description: Workspace updated
			content:
				application/json:
					schema:
						type: object
						properties:
							id:
								type: string
								example: "456"
							name:
								type: string
								example: "Sales Analysis"
							visibility:
								type: string
								example: "private"
							owner:
								type: string
								example: "user_123"
		'400':
			description: Invalid input
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Invalid visibility value.
		'404':
			description: Workspace not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Workspace not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
PATCH /workspaces/456

Authorization: Bearer <token>
Content-Type: application/json

{
	"name": "Sales Analysis",
	"visibility": "private",
	"claim": true
}
```

##### Success Response Example

```http
200 OK

{
	"id": "456",
	"name": "Sales Analysis",
	"visibility": "private",
	"owner": "user_123"
}
```

##### Error Response Example

```http
400 Bad Request

{
	"error": "Invalid visibility value."
}
```
#### Delete workspace

`DELETE /workspaces/:workspace_id`

##### OpenAPI Specification

```yaml
delete:
	summary: Delete workspace by ID
	tags:
		- Workspace
	security:
		- bearerAuth: []
	parameters:
		- name: id
			in: path
			required: true
			schema:
				type: string
			example: 456
	responses:
		'204':
			description: Workspace deleted successfully (no content)
		'404':
			description: Workspace not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Workspace not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
DELETE /workspaces/456

Authorization: Bearer <token>
```

##### Success Response Example

```http
204 No Content
```

##### Error Response Example

```http
404 Not Found

{
	"error": "Workspace not found."
}
```
#### Get workspace details

`GET /workspaces/:workspace_id`

##### OpenAPI Specification

```yaml
get:
	summary: Get workspace details by ID
	tags:
		- Workspace
	security:
		- bearerAuth: []
	parameters:
		- name: id
			in: path
			required: true
			schema:
				type: string
			example: 456
	responses:
		'200':
			description: Workspace details
			content:
				application/json:
					schema:
						type: object
						properties:
							id:
								type: string
								example: "456"
							name:
								type: string
								example: "Sales Analysis"
							visibility:
								type: string
								example: "public"
							owner:
								type: string
								example: "user_123"
							created_at:
								type: string
								format: date-time
								example: "2025-08-30T12:34:56Z"
		'404':
			description: Workspace not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Workspace not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
GET /workspaces/456

Authorization: Bearer <token>
```

##### Success Response Example

```http
200 OK

{
	"id": "456",
	"name": "Sales Analysis",
	"visibility": "public",
	"owner": "user_123",
	"created_at": "2025-08-30T12:34:56Z"
}
```

##### Error Response Example

```http
404 Not Found

{
	"error": "Workspace not found."
}
```

#### Create workspace

`POST /workspaces`

##### OpenAPI Specification

```yaml
post:
	summary: Create a new workspace
	tags:
		- Workspace
	security:
		- bearerAuth: []
	requestBody:
		required: true
		content:
			application/json:
				schema:
					type: object
					properties:
						name:
							type: string
							example: "Sales Analysis"
						visibility:
							type: string
							enum: [public, private]
							example: "public"
					required:
						- name
	responses:
		'201':
			description: Workspace created
			content:
				application/json:
					schema:
						type: object
						properties:
							id:
								type: string
								example: "456"
							name:
								type: string
								example: "Sales Analysis"
							visibility:
								type: string
								example: "public"
							owner:
								type: string
								example: "user_123"
		'400':
			description: Invalid input
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Invalid workspace name.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
POST /workspaces

Authorization: Bearer <token>
Content-Type: application/json

{
	"name": "Sales Analysis",
	"visibility": "public"
}
```

##### Success Response Example

```http
201 Created

{
	"id": "456",
	"name": "Sales Analysis",
	"visibility": "public",
	"owner": "user_123"
}
```

##### Error Response Example

```http
400 Bad Request

{
	"error": "Invalid workspace name."
}
```

### File Management

#### List files in workspace

`GET /workspaces/:workspace_id/files`

##### OpenAPI Specification

```yaml
get:
	summary: List files in a workspace
	tags:
		- Workspace
	security:
		- bearerAuth: []
	parameters:
		- name: id
			in: path
			required: true
			schema:
				type: string
			example: 456
		- name: page
			in: query
			required: false
			schema:
				type: integer
			example: 1
		- name: size
			in: query
			required: false
			schema:
				type: integer
			example: 20
	responses:
		'200':
			description: List of files in workspace
			content:
				application/json:
					schema:
						type: object
						properties:
							files:
								type: array
								items:
									type: object
									properties:
										id:
											type: string
											example: "file_789"
										name:
											type: string
											example: "sales.csv"
										size:
											type: integer
											example: 102400
										uploaded_at:
											type: string
											format: date-time
											example: "2025-08-30T13:00:00Z"
							page:
								type: integer
								example: 1
							size:
								type: integer
								example: 20
							total:
								type: integer
								example: 2
		'404':
			description: Workspace not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Workspace not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
GET /workspaces/456/files?page=1&size=20

Authorization: Bearer <token>
```

##### Success Response Example

```http
200 OK

X-Page: 1
X-Size: 20
X-Total: 2

[
	{
		"id": "file_789",
		"name": "sales.csv",
		"size": 102400,
		"uploaded_at": "2025-08-30T13:00:00Z"
	},
	{
		"id": "file_790",
		"name": "inventory.xlsx",
		"size": 204800,
		"uploaded_at": "2025-08-30T13:05:00Z"
	}
]
```

##### Error Response Example

```http
404 Not Found

{
	"error": "Workspace not found."
}
```

#### List tables in file

`GET /workspaces/:workspace_id/files/:id/tables`

##### OpenAPI Specification

```yaml
get:
	summary: List tables in a file in workspace
	tags:
		- File Management
	security:
		- bearerAuth: []
	parameters:
		- name: wid
			in: path
			required: true
			schema:
				type: string
			example: 456
		- name: id
			in: path
			required: true
			schema:
				type: string
			example: file_789
		- name: page
			in: query
			required: false
			schema:
				type: integer
			example: 1
		- name: size
			in: query
			required: false
			schema:
				type: integer
			example: 20
	responses:
		'200':
			description: List of tables in file
			headers:
				X-Page:
					description: Current page number
					schema:
						type: integer
				X-Size:
					description: Page size
					schema:
						type: integer
				X-Total:
					description: Total number of tables
					schema:
						type: integer
			content:
				application/json:
					schema:
						type: array
						items:
							type: object
							properties:
								id:
									type: string
									example: "table_321"
								name:
									type: string
									example: "Sales"
								rows:
									type: integer
									example: 1000
								columns:
									type: integer
									example: 12
		'404':
			description: File not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: File not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
GET /workspaces/456/files/file_789/tables?page=1&size=20

Authorization: Bearer <token>
```

##### Success Response Example

```http
200 OK

X-Page: 1
X-Size: 20
X-Total: 2

[
	{
		"id": "table_321",
		"name": "Sales",
		"rows": 1000,
		"columns": 12
	},
	{
		"id": "table_322",
		"name": "Inventory",
		"rows": 500,
		"columns": 8
	}
]
```

##### Error Response Example

```http
404 Not Found

{
	"error": "File not found."
}
```
#### Rename file

`PATCH /workspaces/:workspace_id/files/:id`

##### OpenAPI Specification

```yaml
patch:
	summary: Rename file in workspace
	tags:
		- File Management
	security:
		- bearerAuth: []
	parameters:
		- name: wid
			in: path
			required: true
			schema:
				type: string
			example: 456
		- name: id
			in: path
			required: true
			schema:
				type: string
			example: file_789
	requestBody:
		required: true
		content:
			application/json:
				schema:
					type: object
					properties:
						name:
							type: string
							description: New file name
							example: "sales_2025.csv"
					required:
						- name
	responses:
		'200':
			description: File renamed successfully
			content:
				application/json:
					schema:
						type: object
						properties:
							id:
								type: string
								example: "file_789"
							name:
								type: string
								example: "sales_2025.csv"
							size:
								type: integer
								example: 102400
							uploaded_at:
								type: string
								format: date-time
								example: "2025-08-30T13:00:00Z"
							id:
								type: string
								example: "456"
		'400':
			description: Invalid file name
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Invalid file name.
		'404':
			description: File not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: File not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
PATCH /workspaces/456/files/file_789

Authorization: Bearer <token>
Content-Type: application/json

{
	"name": "sales_2025.csv"
}
```

##### Success Response Example

```http
200 OK

{
	"id": "file_789",
	"name": "sales_2025.csv",
	"size": 102400,
	"uploaded_at": "2025-08-30T13:00:00Z",
	"id": "456"
}
```

##### Error Response Example

```http
400 Bad Request

{
	"error": "Invalid file name."
}
```
#### Delete file

`DELETE /workspaces/:workspace_id/files/:id`

##### OpenAPI Specification

```yaml
delete:
	summary: Delete file by ID in workspace
	tags:
		- File Management
	security:
		- bearerAuth: []
	parameters:
		- name: wid
			in: path
			required: true
			schema:
				type: string
			example: 456
		- name: id
			in: path
			required: true
			schema:
				type: string
			example: file_789
	responses:
		'204':
			description: File deleted successfully (no content)
		'404':
			description: File not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: File not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
DELETE /workspaces/456/files/file_789

Authorization: Bearer <token>
```

##### Success Response Example

```http
204 No Content
```

##### Error Response Example

```http
404 Not Found

{
	"error": "File not found."
}
```
#### Upload file (Excel/CSV)

`POST /workspaces/:workspace_id/files`

##### OpenAPI Specification

```yaml
post:
	summary: Upload a file (Excel/CSV) to workspace
	tags:
		- File Management
	security:
		- bearerAuth: []
	parameters:
		- name: id
			in: path
			required: true
			schema:
				type: string
			example: 456
	requestBody:
		required: true
		content:
			multipart/form-data:
				schema:
					type: object
					properties:
						file:
							type: string
							format: binary
							description: File to upload (Excel/CSV)
					required:
						- file
	responses:
		'201':
			description: File uploaded successfully
			content:
				application/json:
					schema:
						type: object
						properties:
							id:
								type: string
								example: "file_789"
							name:
								type: string
								example: "sales.csv"
							size:
								type: integer
								example: 102400
							uploaded_at:
								type: string
								format: date-time
								example: "2025-08-30T13:00:00Z"
							id:
								type: string
								example: "456"
		'400':
			description: Invalid input or file type
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Invalid file type.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
		'404':
			description: Workspace not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Workspace not found.
```

##### Request Example

```http
POST /workspaces/456/files

Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@sales.csv
```

##### Success Response Example

```http
201 Created

{
	"id": "file_789",
	"name": "sales.csv",
	"size": 102400,
	"uploaded_at": "2025-08-30T13:00:00Z",
	"id": "456"
}
```

##### Error Response Example

```http
400 Bad Request

{
	"error": "Invalid file type."
}
```
- `POST /files` — Upload file (Excel/CSV)
- `DELETE /files/:id` — Delete file
- `PATCH /files/:id` — Rename file
- `GET /files/:id/tables` — List tables in file

### Table Data

#### List tables in workspace

`GET /workspaces/:workspace_id/tables`

##### OpenAPI Specification

```yaml
get:
	summary: List tables in a workspace
	tags:
		- Workspace
	security:
		- bearerAuth: []
	parameters:
		- name: id
			in: path
			required: true
			schema:
				type: string
			example: 456
		- name: page
			in: query
			required: false
			schema:
				type: integer
			example: 1
		- name: size
			in: query
			required: false
			schema:
				type: integer
			example: 20
	responses:
		'200':
			description: List of tables in workspace
			headers:
				X-Page:
					description: Current page number
					schema:
						type: integer
				X-Size:
					description: Page size
					schema:
						type: integer
				X-Total:
					description: Total number of tables
					schema:
						type: integer
			content:
				application/json:
					schema:
						type: array
						items:
							type: object
							properties:
								id:
									type: string
									example: "table_321"
								name:
									type: string
									example: "Sales"
								slug:
									type: string
									example: "sales"
								rows:
									type: integer
									example: 1000
								columns:
									type: integer
									example: 12
		'404':
			description: Workspace not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Workspace not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
GET /workspaces/456/tables?page=1&size=20

Authorization: Bearer <token>
```

##### Success Response Example

```http
200 OK

X-Page: 1
X-Size: 20
X-Total: 2

[
	{
		"id": "table_321",
		"name": "Sales",
		"slug": "sales",
		"rows": 1000,
		"columns": 12
	},
	{
		"id": "table_322",
		"name": "Inventory",
		"slug": "inventory",
		"rows": 500,
		"columns": 8
	}
]
```

##### Error Response Example

```http
404 Not Found

{
	"error" "Workspace not found"
}
```


#### Get table metadata

`GET /workspaces/:workspace_id/tables/:id`

##### OpenAPI Specification

```yaml
get:
	summary: Get table metadata in workspace
	tags:
		- Table Data
	security:
		- bearerAuth: []
	parameters:
		- name: wid
			in: path
			required: true
			schema:
				type: string
			example: 456
		- name: id
			in: path
			required: true
			schema:
				type: string
			example: table_321
	responses:
		'200':
			description: Table metadata
			content:
				application/json:
					schema:
						type: object
						properties:
							id:
								type: string
								example: "table_321"
							name:
								type: string
								example: "Sales"
							rows:
								type: integer
								example: 1000
							columns:
								type: integer
								example: 12
							schema:
								type: array
								items:
									type: object
									properties:
										name:
											type: string
											example: "customer_id"
										type:
											type: string
											example: "integer"
										nullable:
											type: boolean
											example: false
		'404':
			description: Table not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Table not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
GET /workspaces/456/tables/table_321

Authorization: Bearer <token>
```

##### Success Response Example

```http
200 OK

{
	"id": "table_321",
	"name": "Sales",
	"rows": 1000,
	"columns": 12,
	"schema": [
		{ "name": "customer_id", "type": "integer", "nullable": false },
		{ "name": "amount", "type": "float", "nullable": false },
		{ "name": "date", "type": "date", "nullable": true }
	]
}
```

##### Error Response Example

```http
404 Not Found

{
	"error": "Table not found."
}
```

#### Get table data (paginated)

`GET /workspaces/:workspace_id/tables/:id/data`

##### OpenAPI Specification

```yaml
get:
	summary: Get paginated table data in workspace
	tags:
		- Table Data
	security:
		- bearerAuth: []
	parameters:
		- name: wid
			in: path
			required: true
			schema:
				type: string
			example: 456
		- name: id
			in: path
			required: true
			schema:
				type: string
			example: table_321
		- name: page
			in: query
			required: false
			schema:
				type: integer
			example: 1
		- name: size
			in: query
			required: false
			schema:
				type: integer
			example: 100
	responses:
		'200':
			description: Paginated table data
			headers:
				X-Page:
					description: Current page number
					schema:
						type: integer
				X-Size:
					description: Page size
					schema:
						type: integer
				X-Total:
					description: Total number of rows
					schema:
						type: integer
			content:
				application/json:
					schema:
						type: array
						items:
							type: object
							additionalProperties: true
		'404':
			description: Table not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Table not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
GET /workspaces/456/tables/table_321/data?page=1&size=100

Authorization: Bearer <token>
```

##### Success Response Example

```http
200 OK

X-Page: 1
X-Size: 100
X-Total: 1000

[
	{ "customer_id": 1, "amount": 100.5, "date": "2025-08-01" },
	{ "customer_id": 2, "amount": 200.0, "date": "2025-08-02" }
]
```

##### Error Response Example

```http
404 Not Found

{
	"error": "Table not found."
}
```

#### Rename table

`PATCH /workspaces/:workspace_id/tables/:id`

##### OpenAPI Specification

```yaml
patch:
	summary: Rename table in workspace
	tags:
		- Table Data
	security:
		- bearerAuth: []
	parameters:
		- name: wid
			in: path
			required: true
			schema:
				type: string
			example: 456
		- name: id
			in: path
			required: true
			schema:
				type: string
			example: table_321
	requestBody:
		required: true
		content:
			application/json:
				schema:
					type: object
					properties:
						name:
							type: string
							description: New table name
							example: "Customers"
					required:
						- name
	responses:
		'200':
			description: Table renamed successfully
			content:
				application/json:
					schema:
						type: object
						properties:
							id:
								type: string
								example: "table_321"
							name:
								type: string
								example: "Customers"
							rows:
								type: integer
								example: 1000
							columns:
								type: integer
								example: 12
							id:
								type: string
								example: "456"
		'400':
			description: Invalid table name
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Invalid table name.
		'404':
			description: Table not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Table not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
PATCH /workspaces/456/tables/table_321

Authorization: Bearer <token>
Content-Type: application/json

{
	"name": "Customers"
}
```

##### Success Response Example

```http
200 OK

{
	"id": "table_321",
	"name": "Customers",
	"rows": 1000,
	"columns": 12,
	"id": "456"
}
```

##### Error Response Example

```http
400 Bad Request

{
	"error": "Invalid table name."
}
```

```http
404 Not Found

{
	"error": "Table not found."
}
```

```http
401 Unauthorized

{
	"error": "Unauthorized."
}
```

#### Delete table

`DELETE /workspaces/:workspace_id/tables/:id`

##### OpenAPI Specification

```yaml
delete:
	summary: Delete table by ID in workspace
	tags:
		- Table Data
	security:
		- bearerAuth: []
	parameters:
		- name: wid
			in: path
			required: true
			schema:
				type: string
			example: 456
		- name: id
			in: path
			required: true
			schema:
				type: string
			example: table_321
	responses:
		'204':
			description: Table deleted successfully (no content)
		'404':
			description: Table not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Table not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
DELETE /workspaces/456/tables/table_321

Authorization: Bearer <token>
```

##### Success Response Example

```http
204 No Content
```

##### Error Response Example

```http
404 Not Found

{
	"error": "Table not found."
}
```

```http
401 Unauthorized

{
	"error": "Unauthorized."
}
```

### Query Management

#### List queries in workspace

`GET /workspaces/:workspace_id/queries`

##### OpenAPI Specification

```yaml
get:
	summary: List saved queries in a workspace
	tags:
		- Workspace
	security:
		- bearerAuth: []
	parameters:
		- name: id
			in: path
			required: true
			schema:
				type: string
			example: 456
		- name: page
			in: query
			required: false
			schema:
				type: integer
			example: 1
		- name: size
			in: query
			required: false
			schema:
				type: integer
			example: 20
	responses:
		'200':
			description: List of queries in workspace
			content:
				application/json:
					schema:
						type: object
						properties:
							queries:
								type: array
								items:
									type: object
									properties:
										id:
											type: string
											example: "query_101"
										name:
											type: string
											example: "Top Customers"
										created_at:
											type: string
											format: date-time
											example: "2025-08-30T14:00:00Z"
							page:
								type: integer
								example: 1
							size:
								type: integer
								example: 20
							total:
								type: integer
								example: 1
		'404':
			description: Workspace not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Workspace not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
GET /workspaces/456/queries?page=1&size=20

Authorization: Bearer <token>
```

##### Success Response Example

```http
200 OK

X-Page: 1
X-Size: 20
X-Total: 1

[
	{
		"id": "query_101",
		"name": "Top Customers",
		"created_at": "2025-08-30T14:00:00Z"
	}
]
```

##### Error Response Example

```http
404 Not Found

{
	"error": "Workspace not found."
}
```


#### Save query

`POST /workspaces/:workspace_id/queries`

##### OpenAPI Specification

```yaml
post:
	summary: Save a new query in workspace
	tags:
		- Query Management
	security:
		- bearerAuth: []
	parameters:
		- name: wid
			in: path
			required: true
			schema:
				type: string
			example: 456
	requestBody:
		required: true
		content:
			application/json:
				schema:
					type: object
					properties:
						name:
							type: string
							example: "Top Customers"
						query:
							type: string
							example: "SELECT * FROM customers ORDER BY total DESC LIMIT 10"
					required:
						- name
						- query
	responses:
		'201':
			description: Query saved
			content:
				application/json:
					schema:
						type: object
						properties:
							id:
								type: string
								example: "query_101"
							name:
								type: string
								example: "Top Customers"
							query:
								type: string
								example: "SELECT * FROM customers ORDER BY total DESC LIMIT 10"
							created_at:
								type: string
								format: date-time
								example: "2025-08-30T14:00:00Z"
							id:
								type: string
								example: "456"
		'400':
			description: Invalid input
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Invalid query.
		'404':
			description: Workspace not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Workspace not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
POST /workspaces/456/queries

Authorization: Bearer <token>
Content-Type: application/json

{
	"name": "Top Customers",
	"query": "SELECT * FROM customers ORDER BY total DESC LIMIT 10"
}
```

##### Success Response Example

```http
201 Created

{
	"id": "query_101",
	"name": "Top Customers",
	"query": "SELECT * FROM customers ORDER BY total DESC LIMIT 10",
	"created_at": "2025-08-30T14:00:00Z",
	"id": "456"
}
```

##### Error Response Example

```http
400 Bad Request

{
	"error": "Invalid query."
}
```

```http
404 Not Found

{
	"error": "Workspace not found."
}
```

```http
401 Unauthorized

{
	"error": "Unauthorized."
}
```

### Query Execution

#### Execute query (SELECT only)

`POST /workspaces/:workspace_id/query`

##### OpenAPI Specification

```yaml
post:
	summary: Execute a SQL query (SELECT only) in workspace
	tags:
		- Query Execution
	security:
		- bearerAuth: []
	parameters:
		- name: wid
			in: path
			required: true
			schema:
				type: string
			example: 456
	requestBody:
		required: true
		content:
			application/json:
				schema:
					type: object
					properties:
						query:
							type: string
							example: "SELECT * FROM customers WHERE country = 'US' LIMIT 10"
					required:
						- query
	responses:
		'200':
			description: Query executed successfully
			headers:
				X-Page:
					description: Current page number
					schema:
						type: integer
				X-Size:
					description: Page size
					schema:
						type: integer
				X-Total:
					description: Total number of rows
					schema:
						type: integer
			content:
				application/json:
					schema:
						type: array
						items:
							type: object
							additionalProperties: true
		'400':
			description: Invalid query or not a SELECT statement
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Only SELECT queries are allowed.
		'404':
			description: Workspace not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Workspace not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
POST /workspaces/456/query

Authorization: Bearer <token>
Content-Type: application/json

{
	"query": "SELECT * FROM customers WHERE country = 'US' LIMIT 10"
}
```

##### Success Response Example

```http
200 OK

X-Page: 1
X-Size: 10
X-Total: 100

[
	{ "customer_id": 1, "name": "Alice", "country": "US" },
	{ "customer_id": 2, "name": "Bob", "country": "US" }
]
```

##### Error Response Example

```http
400 Bad Request

{
	"error": "Only SELECT queries are allowed."
}
```

```http
404 Not Found

{
	"error": "Workspace not found."
}
```

```http
401 Unauthorized

{
	"error": "Unauthorized."
}
```

### AI Assistance


#### Query data from natural language prompt

`POST /workspaces/:workspace_id/ai/query`

##### OpenAPI Specification

```yaml
post:
	summary: Query data using a natural language prompt (AI-powered)
	tags:
		- AI Assistance
	security:
		- bearerAuth: []
	parameters:
		- name: wid
			in: path
			required: true
			schema:
				type: string
			example: 456
	requestBody:
		required: true
		content:
			application/json:
				schema:
					type: object
					properties:
						prompt:
							type: string
							example: "Show me the top 10 customers by total sales."
					required:
						- prompt
	responses:
		'200':
			description: Retrieved data for prompt
			headers:
				X-Page:
					description: Current page number
					schema:
						type: integer
				X-Size:
					description: Page size
					schema:
						type: integer
				X-Total:
					description: Total number of rows
					schema:
						type: integer
			content:
				application/json:
					schema:
						type: array
						items:
							type: object
							additionalProperties: true
		'400':
			description: Invalid prompt or unable to retrieve data
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unable to retrieve data from prompt.
		'404':
			description: Workspace not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Workspace not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
POST /workspaces/456/ai/query

Authorization: Bearer <token>
Content-Type: application/json

{
	"prompt": "Show me the top 10 customers by total sales."
}
```

##### Success Response Example

```http
200 OK

X-Page: 1
X-Size: 10
X-Total: 100

[
	{ "customer_id": 1, "name": "Alice", "total_sales": 1000.0 },
	{ "customer_id": 2, "name": "Bob", "total_sales": 950.0 }
]
```

##### Error Response Example

```http
400 Bad Request

{
	"error": "Unable to retrieve data from prompt."
}
```

```http
404 Not Found

{
	"error": "Workspace not found."
}
```


#### Suggest relationships/insights between tables

`POST /workspaces/:workspace_id/ai/suggest-relationships`


##### OpenAPI Specification

```yaml
post:
	summary: Suggest relationships or insights between tables (AI-powered)
	tags:
		- AI Assistance
	security:
		- bearerAuth: []
	parameters:
		- name: wid
			in: path
			required: true
			schema:
				type: string
			example: 456
	requestBody:
		required: true
		content:
			application/json:
				schema:
					type: object
					properties:
						tables:
							type: array
							items:
								type: string
							example: ["table_321", "table_322"]
					required:
						- tables
	responses:
		'200':
			description: Suggested relationships or insights
			content:
				application/json:
					schema:
						type: object
						properties:
							relationships:
								type: array
								items:
									type: object
									properties:
										table1_id:
											type: string
											example: "table_321"
										table2_id:
											type: string
											example: "table_322"
										fields_to_join:
											type: array
											items:
												type: object
												properties:
													table1_field:
														type: string
														example: "customer_id"
													table2_field:
														type: string
														example: "id"
										description:
											type: string
											example: "Sales table can be joined with Customers on customer_id = id."
										confidence:
											type: number
											format: float
											example: 0.95
		'400':
			description: Invalid input or unable to suggest relationships
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unable to suggest relationships.
		'404':
			description: Workspace not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Workspace not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
POST /workspaces/456/ai/suggest-relationships

Authorization: Bearer <token>
Content-Type: application/json

{
	"tables": ["table_321", "table_322"]
}
```

##### Success Response Example

```http
200 OK

{
	"relationships": [
		{
			"tables_to_join": ["table_321", "table_322"],
			"fields_to_join": [
				{
					"table1_field": "customer_id",
					"table2_field": "id"
				}
			],
			"description": "Sales table can be joined with Customers on customer_id = id.",
			"confidence": 0.95
		}
	]
}
```

##### Error Response Example

```http
400 Bad Request

{
	"error": "Unable to suggest relationships."
}
```

```http
404 Not Found

{
	"error": "Workspace not found."
}
```

```http
401 Unauthorized

{
	"error": "Unauthorized."
}
```
```http
401 Unauthorized

{
	"error": "Unauthorized."
}
```

#### Explain query results in natural language

`POST /workspaces/:workspace_id/ai/explain-results`

##### OpenAPI Specification

```yaml
post:
	summary: Explain query results in natural language (AI-powered)
	tags:
		- AI Assistance
	security:
		- bearerAuth: []
	parameters:
		- name: wid
			in: path
			required: true
			schema:
				type: string
			example: 456
	requestBody:
		required: true
		content:
			application/json:
				schema:
					type: object
					properties:
						query:
							type: string
							example: "SELECT country, COUNT(*) FROM customers GROUP BY country"
						results:
							type: array
							items:
								type: object
								additionalProperties: true
					required:
						- query
						- results
	responses:
		'200':
			description: Natural language explanation of query results
			content:
				application/json:
					schema:
						type: object
						properties:
							explanation:
								type: string
								example: "The query shows the number of customers in each country. The United States has the highest count."
		'400':
			description: Invalid input or unable to explain results
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unable to explain results.
		'404':
			description: Workspace not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Workspace not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
POST /workspaces/456/ai/explain-results

Authorization: Bearer <token>
Content-Type: application/json

{
	"query": "SELECT country, COUNT(*) FROM customers GROUP BY country",
	"results": [
		{ "country": "US", "count": 50 },
		{ "country": "CA", "count": 20 }
	]
}
```

##### Success Response Example

```http
200 OK

{
	"explanation": "The query shows the number of customers in each country. The United States has the highest count."
}
```

##### Error Response Example

```http
400 Bad Request

{
	"error": "Unable to explain results."
}
```

```http
404 Not Found

{
	"error": "Workspace not found."
}
```

```http
401 Unauthorized

{
	"error": "Unauthorized."
}
```

- `POST /workspaces/:workspace_id/ai/explain-results` — Explain query results in natural language
- `POST /workspaces/:workspace_id/ai/suggest-relationships` — Suggest relationships/insights between tables

### Export

#### Export query results (CSV/Excel)

`POST /workspaces/:workspace_id/export`

##### OpenAPI Specification

```yaml
post:
	summary: Export query results to CSV or Excel
	tags:
		- Export
	security:
		- bearerAuth: []
	parameters:
		- name: wid
			in: path
			required: true
			schema:
				type: string
			example: 456
	requestBody:
		required: true
		content:
			application/json:
				schema:
					type: object
					properties:
						query:
							type: string
							example: "SELECT * FROM customers WHERE country = 'US'"
						format:
							type: string
							enum: [csv, excel]
							example: "csv"
					required:
						- query
						- format
	responses:
		'201':
			description: Export link created
			content:
				application/json:
					schema:
						type: object
						properties:
							link:
								type: string
								example: "https://deita.app/exports/exp_12345.csv?expires=2025-08-30T15:00:00Z"
							expires_at:
								type: string
								format: date-time
								example: "2025-08-30T15:00:00Z"
		'400':
			description: Invalid query or format
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Invalid query or format.
		'404':
			description: Workspace not found
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Workspace not found.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
POST /workspaces/456/export

Authorization: Bearer <token>
Content-Type: application/json

{
	"query": "SELECT * FROM customers WHERE country = 'US'",
	"format": "csv"
}
```

##### Success Response Example

```http
201 Created

{
	"link": "https://deita.app/workspaces/123/exports/abc123-auiasdas-122i3-444",
	"expires_at": "2025-08-30T15:00:00Z"
}
```

##### Error Response Example

```http
400 Bad Request

{
	"error": "Invalid query or format."
}
```

```http
404 Not Found

{
	"error": "Workspace not found."
}
```

```http
401 Unauthorized

{
	"error": "Unauthorized."
}
```


#### Download exported file

`GET /workspaces/:workspace_id/exports/:export_id`

##### OpenAPI Specification

```yaml
get:
	summary: Download exported file from workspace
	tags:
		- Export
	security:
		- bearerAuth: []
	parameters:
		- name: wid
			in: path
			required: true
			schema:
				type: string
			example: 123
		- name: export_id
			in: path
			required: true
			schema:
				type: string
			example: abc123-auiasdas-122i3-444
	responses:
		'200':
			description: Exported file download
			content:
				application/octet-stream:
					schema:
						type: string
						format: binary
		'404':
			description: Exported file not found or expired
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Exported file not found or expired.
		'401':
			description: Unauthorized
			content:
				application/json:
					schema:
						type: object
						properties:
							error:
								type: string
								example: Unauthorized.
```

##### Request Example

```http
GET /workspaces/123/exports/abc123-auiasdas-122i3-444

Authorization: Bearer <token>
```

##### Success Response Example

```http
200 OK

Content-Type: application/octet-stream

[binary file content]
```

##### Error Response Example

```http
404 Not Found

{
	"error": "Exported file not found or expired."
}
```

```http
401 Unauthorized

{
	"error": "Unauthorized."
}
```

## API Design Principles
- **RESTful, resource-oriented URLs**
- **JWT-based authentication** (magic link)
- **Input validation and error handling**
- **Pagination for large datasets**
- **Rate limiting and abuse prevention**
- **OpenAPI/Swagger documentation**

## Extensibility
- API supports future features: query sharing, export history, advanced AI endpoints.
