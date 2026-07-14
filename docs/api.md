# Quizly API Endpoint Documentation

## Authentication

Login and registration

---

### POST `/api/register/`

**Description:** Registers a new user.

**Request Body**

```json
{
  "username": "your_username",
  "password": "your_password",
  "confirmed_password": "your_confirmed_password",
  "email": "your_email@example.com"
}
```

**Success Response**

User was created successfully.

```json
{
  "detail": "User created successfully!"
}
```

**Status Codes**

- `201`: User created successfully.
- `400`: Invalid data.

**Rate Limits:** No limit

**Permissions required:** None

---

### POST `/api/login/`

**Description:** Logs in the user and sets auth cookies.

**Request Body**

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Success Response**

Login was successful. Cookies are set.

```json
{
  "detail": "Login successfully!",
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "your_email@example.com"
  }
}
```

**Status Codes**

- `200`: Login successful.
- `401`: Invalid credentials.

**Rate Limits:** No limit

**Permissions required:** None

**Extra Information:** Sets `access_token` and `refresh_token` as cookies.

---

### POST `/api/logout/`

**Description:** Logs out the user and deletes all tokens.

**Request Body**

```json
{}
```

**Success Response**

The user is logged out, all tokens are invalidated.

```json
{
  "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
}
```

**Status Codes**

- `200`: Logout successful.
- `401`: Not authenticated.

**Rate Limits:** No limit

**Permissions required:** Authentication required.

**Extra Information:** The `access_token` and `refresh_token` cookies are removed.

---

### POST `/api/token/refresh/`

**Description:** Refreshes the access token using the refresh token.

**Request Body**

```json
{}
```

**Success Response**

Returns a new access token.

```json
{
  "detail": "Token refreshed"
}
```

**Status Codes**

- `200`: Token refreshed successfully.
- `401`: Refresh token invalid or missing.

**Rate Limits:** No limit

**Permissions required:** Authentication via `refresh_token` cookie required.

**Extra Information:** Sets a new `access_token` cookie.

---

## Quiz Management

Creation, management and retrieval of quizzes

---

### POST `/api/quizzes/`

**Description:** Creates a new quiz based on a YouTube URL.

**Request Body**

```json
{
  "url": "https://www.youtube.com/watch?v=example"
}
```

**Success Response**

Returns the created quiz with all questions.

```json
{
  "id": 1,
  "title": "Quiz Title",
  "description": "Quiz Description",
  "created_at": "2023-07-29T12:34:56.789Z",
  "updated_at": "2023-07-29T12:34:56.789Z",
  "video_url": "https://www.youtube.com/watch?v=example",
  "questions": [
    {
      "id": 1,
      "question_title": "Question 1",
      "question_options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "answer": "Option A",
      "created_at": "2023-07-29T12:34:56.789Z",
      "updated_at": "2023-07-29T12:34:56.789Z"
    }
  ]
}
```

**Status Codes**

- `201`: Quiz created successfully.
- `400`: Invalid URL or request data.
- `401`: Not authenticated.

**Rate Limits:** No limit

**Permissions required:** Authentication required.

---

### GET `/api/quizzes/`

**Description:** Retrieves all quizzes of the authenticated user.

**Success Response**

List of all the user's quizzes with questions.

```json
[
  {
    "id": 1,
    "title": "Quiz Title",
    "description": "Quiz Description",
    "created_at": "2023-07-29T12:34:56.789Z",
    "updated_at": "2023-07-29T12:34:56.789Z",
    "video_url": "https://www.youtube.com/watch?v=example",
    "questions": [
      {
        "id": 1,
        "question_title": "Question 1",
        "question_options": [
          "Option A",
          "Option B",
          "Option C",
          "Option D"
        ],
        "answer": "Option A"
      }
    ]
  }
]
```

**Status Codes**

- `200`: Quizzes retrieved successfully.
- `401`: Not authenticated.

**Rate Limits:** No limit

**Permissions required:** Authentication required.

---

### GET `/api/quizzes/{id}/`

**Description:** Retrieves a specific quiz belonging to the user.

**URL Parameters**

| Name | Type | Description                              |
| ---- | ---- | ----------------------------------------- |
| `id` | -    | The ID of the quiz to retrieve.           |

**Success Response**

The specific quiz with all questions and details.

```json
{
  "id": 1,
  "title": "Quiz Title",
  "description": "Quiz Description",
  "created_at": "2023-07-29T12:34:56.789Z",
  "updated_at": "2023-07-29T12:34:56.789Z",
  "video_url": "https://www.youtube.com/watch?v=example",
  "questions": [
    {
      "id": 1,
      "question_title": "Question 1",
      "question_options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "answer": "Option A"
    }
  ]
}
```

**Status Codes**

- `200`: Quiz retrieved successfully.
- `401`: Not authenticated.
- `403`: Access denied - quiz does not belong to the user.
- `404`: Quiz not found.

**Rate Limits:** No limit

**Permissions required:** Authentication required. Users can only retrieve their own quizzes.

---

### PATCH `/api/quizzes/{id}/`

**Description:** Updates individual fields of a quiz (partial update).

**URL Parameters**

| Name | Type | Description                            |
| ---- | ---- | --------------------------------------- |
| `id` | -    | The ID of the quiz to update.           |

**Request Body**

```json
{
  "title": "Partially Updated Title",
  "description": "Partially Updated Description"
}
```

**Success Response**

The updated quiz with all details.

```json
{
  "id": 1,
  "title": "Partially Updated Title",
  "description": "Quiz Description",
  "created_at": "2023-07-29T12:34:56.789Z",
  "updated_at": "2023-07-29T14:45:12.345Z",
  "video_url": "https://www.youtube.com/watch?v=example",
  "questions": [
    {
      "id": 1,
      "question_title": "Question 1",
      "question_options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "answer": "Option A"
    }
  ]
}
```

**Status Codes**

- `200`: Quiz updated successfully.
- `400`: Invalid request data.
- `401`: Not authenticated.
- `403`: Access denied - quiz does not belong to the user.
- `404`: Quiz not found.

**Rate Limits:** No limit

**Permissions required:** Authentication required. Users can only update their own quizzes.

---

### DELETE `/api/quizzes/{id}/`

**Description:** Permanently deletes a quiz and all its associated questions.

**URL Parameters**

| Name | Type | Description                             |
| ---- | ---- | ----------------------------------------- |
| `id` | -    | The ID of the quiz to delete.             |

**Success Response**

No response data on successful deletion.

```
null
```

**Status Codes**

- `204`: Quiz deleted successfully.
- `401`: Not authenticated.
- `403`: Access denied - quiz does not belong to the user.
- `404`: Quiz not found.

**Rate Limits:** No limit

**Permissions required:** Authentication required. Users can only delete their own quizzes.

**Extra Information:** Warning: deletion is permanent and cannot be undone.
