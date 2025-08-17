# AstroEyes Server Changelog

## 1.0.0 & 1.0.1 (2025-08-17)
### 🆕 API endpoints 
#### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
#### Token Management
- `POST /token/revoke` - Revoke access token
- `POST /token/refresh` - Refresh access token
#### User Management
- `GET /user/profile` - Get user profile
- `POST /user/updateProfile` - Update user profile
- `POST /user/updatePassword` - Update user password