# REST API Guide

## Overview

This Django application provides a simple REST API built with Django REST Framework. The API follows RESTful conventions and includes authentication, pagination, and browsable API interface.

## Base URL

- **Development**: `http://localhost:8000/api/`
- **Production**: `https://your-domain.com/api/`

## Authentication

The API uses session-based authentication by default. You can authenticate via:

1. **Browsable API**: Visit `/api/auth/login/` to log in through the web interface
2. **Session Authentication**: Use Django's session authentication
3. **Basic Authentication**: Send username/password in Authorization header

## API Endpoints

### API Root
- **GET** `/api/` - API information and available endpoints

### Posts API
- **GET** `/api/v1/posts/` - List all posts (paginated)
- **POST** `/api/v1/posts/` - Create a new post (authenticated)
- **GET** `/api/v1/posts/{id}/` - Get a specific post
- **PUT** `/api/v1/posts/{id}/` - Update a post (authenticated, author only)
- **PATCH** `/api/v1/posts/{id}/` - Partially update a post (authenticated, author only)
- **DELETE** `/api/v1/posts/{id}/` - Delete a post (authenticated, author only)

#### Custom Post Actions
- **POST** `/api/v1/posts/{id}/publish/` - Publish a post
- **POST** `/api/v1/posts/{id}/unpublish/` - Unpublish a post

### Comments API
- **GET** `/api/v1/comments/` - List all comments (paginated)
- **POST** `/api/v1/comments/` - Create a new comment (authenticated)
- **GET** `/api/v1/comments/{id}/` - Get a specific comment
- **PUT** `/api/v1/comments/{id}/` - Update a comment (authenticated, author only)
- **PATCH** `/api/v1/comments/{id}/` - Partially update a comment (authenticated, author only)
- **DELETE** `/api/v1/comments/{id}/` - Delete a comment (authenticated, author only)

### Users API
- **GET** `/api/v1/users/` - List all users (paginated)
- **GET** `/api/v1/users/{id}/` - Get a specific user

## Data Models

### Post
```json
{
  "id": 1,
  "title": "Sample Post",
  "content": "This is the post content...",
  "author": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User"
  },
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T10:00:00Z",
  "published": true,
  "comments": [
    {
      "id": 1,
      "content": "Great post!",
      "author": {...},
      "created_at": "2025-01-01T10:30:00Z"
    }
  ],
  "comments_count": 1
}
```

### Comment
```json
{
  "id": 1,
  "content": "This is a comment",
  "author": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User"
  },
  "created_at": "2025-01-01T10:30:00Z"
}
```

### User
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "first_name": "Test",
  "last_name": "User"
}
```

## Examples

### Create a Post
```bash
curl -X POST http://localhost:8000/api/v1/posts/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My New Post",
    "content": "This is the content of my post.",
    "author_id": 1,
    "published": true
  }'
```

### Get All Posts
```bash
curl http://localhost:8000/api/v1/posts/
```

### Get a Specific Post
```bash
curl http://localhost:8000/api/v1/posts/1/
```

### Create a Comment
```bash
curl -X POST http://localhost:8000/api/v1/comments/ \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Great post!",
    "post": 1,
    "author_id": 1
  }'
```

## Pagination

All list endpoints support pagination:

```json
{
  "count": 25,
  "next": "http://localhost:8000/api/v1/posts/?page=2",
  "previous": null,
  "results": [...]
}
```

## Error Handling

The API returns appropriate HTTP status codes:

- **200 OK**: Successful GET, PUT, PATCH
- **201 Created**: Successful POST
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Invalid data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Permission denied
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

## Browsable API

Visit `/api/v1/` in your browser to explore the API through Django REST Framework's browsable interface. This provides:

- Interactive API exploration
- Form-based testing
- Authentication interface
- Automatic documentation

## Permissions

- **Read operations**: Available to all users (authenticated or not)
- **Write operations**: Require authentication
- **Edit/Delete**: Only available to the author of the resource

## Next Steps

This is a basic API skeleton. You can extend it by:

1. Adding more models and endpoints
2. Implementing token authentication
3. Adding field validation
4. Creating custom permissions
5. Adding filtering and searching
6. Implementing API versioning
7. Adding rate limiting
8. Creating API tests
