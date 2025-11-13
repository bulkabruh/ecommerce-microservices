Quick steps to create MongoDB Atlas connection string:
1. Sign up at https://www.mongodb.com/cloud/atlas and create a free M0 cluster.
2. Under Database Access -> Create Database User: add username and password.
3. Under Network Access -> Add your IP (or 0.0.0.0/0 for quick testing).
4. Go to Clusters -> Connect -> Connect your application -> copy the connection string (mongodb+srv://...).
5. Replace <password> in the URI with the DB user password.

Local run:
1. Copy .env.example to .env and edit values.
2. docker compose up --build
3. Open:
   - http://localhost:8000/docs
   - http://localhost:8001/docs
   - http://localhost:8002/docs

Render:
1. Push repo to GitHub.
2. Create a Web Service on Render (Docker).
3. Set environment variables in Render: MONGO_URI, DB_NAME, JWT_SECRET.
4. Deploy and watch Live Logs.

Notes:
- Dockerfiles include ca-certificates and update-ca-certificates to avoid TLS issues.
- requirements.txt pins passlib/bcrypt compatible versions.
