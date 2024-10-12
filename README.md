# 🚀 LLM Connect: Connecting users through intelligent conversations!
This is a personal project to create a multi-user system that interacts with openAI api (for now) to mimic the experience of the chatgpt website, with lower cost and pay as you go plan tho.

## 💡 Description

This is a multi-user backend application where users can log in, view and manage conversations, and interact with language models! The frontend is built using Streamlit, and the backend is powered by Flask with a PostgreSQL database. Plus, we’ve got Alembic in the mix to handle all your database migrations. 🧙‍♂️

<img width="600" alt="image" src="https://github.com/user-attachments/assets/8a3b3d04-8fe4-493d-a424-714bd8f1232f">


## 🛠 Tech Stack

- Backend: **Flask** 🧪
- Frontend: **Streamlit** 🌐
- Database: **PostgreSQL** 🐘
- ORM & Migrations: **SQLAlchemy & Alembic** 🛠️
- Containerization: **Docker** 🐳
- AI Platform: **OpenAI** 🧠

## ⚡️ Features

- 👥 **Multi-user login/register** system
- 💬 **Manage conversations** with ease
- 📜 V**iew conversation threads** and interact in real-time
- 🔑 **Token-based authentication** (cookies, yum! 🍪)
- 🐳 **Dockerized environment** for smooth sailing 🚢
- 💾 **PostgreSQL integration** for all your database needs
- 🔄 **Database migrations** made easy with Alembic
- **+1 Cool factor** 😎

## 🎉 Getting Started

Follow these steps to set up and run the project on your local machine:

### 🐳 Prerequisites

Make sure you have the following installed:

- **Docker** 🐳
- **Docker Compose** 📦
- **Git** 🌱

### 🛠️ Setup Steps

1. Clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/yourproject.git
cd yourproject
```

2. Create your .env file. The template is available in `.env.example` file.
3. Build the containers and bring the project to life! 🌟

```bash
docker-compose up --build
```

4. **Voila!** Your backend is now running on http://localhost:5000 and the frontend on http://localhost:8501. 🎉

### 🔧 How to Use

- **Register/Login:** First things first, head to the login/register page (on the frontend) and create an account. No spam emails, we promise! 💌
- **View Conversations:** After logging in, you can browse through your conversations. Your last one is conveniently opened by default! 📂
- **Send New Messages:** Need to add something? Send a new message right from the conversation thread! 💬
- **Create New Conversations:** Start a new conversation with just a click! ✨

### 🧙 Database Migrations with Alembic

Alembic handles the database migrations, so you don’t have to. After setting up the Docker containers, run the following command to apply migrations:

```bash
docker exec -it flask-backend alembic upgrade head
```

## 🚨 Development Notes

1.	For a development environment, use the Dockerfile to spin up both the backend and frontend.
2.	Ensure the database credentials in your .env file match the ones in the docker-compose.yml.

## 🎉 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests if you have any feature ideas, improvements, or bug fixes.

1.	**Fork** this repository 🍴
2.	Create a **branch** for your feature/fix 🏗️
3.	**Commit** your changes 💾
4.	Open a **Pull Request** 📨
