# AstroEyes Server Changelog

## 1.0.0 & 1.0.1 (2025-08-17)
### 🆕 Add API endpoints 
#### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
#### Token Management
- `POST /token/revoke` - Revoke access token
#### User Management
- `GET /user/me` - Get user profile
- `POST /user/update/profile` - Update user profile
- `POST /user/update/password` - Update user password
### WIP API endpoints
- `POST /token/refresh` - Refresh access token