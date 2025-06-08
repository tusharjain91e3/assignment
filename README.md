# 🤖 AI Chatbot Project

A full-stack intelligent chatbot application built with Flask and Next.js, featuring user authentication, product management, and AI-powered conversations.

![Project Banner](https://via.placeholder.com/800x200/4F46E5/FFFFFF?text=AI+Chatbot+Project)

## ✨ Features

### 🔐 Authentication & Security
- **Secure User Registration** with email verification
- **NextAuth.js Integration** for robust authentication
- **Protected Routes** with middleware
- **Password Security** with hashing and salting

### 💬 AI-Powered Chat
- **Intelligent Responses** using AI services
- **Conversation History** persistence
- **Real-time Chat Interface** with responsive UI
- **Context-Aware** conversations

### 🛍️ Product Management
- **Product Catalog** with categorization
- **Advanced Search** functionality
- **CRUD Operations** for products
- **Category Management** system

### 🎨 Modern UI/UX
- **Responsive Design** with Tailwind CSS
- **shadcn/ui Components** for consistent styling
- **Type-Safe** development with TypeScript
- **Accessible** interface components

## 🏗️ Tech Stack

### Backend
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-FCA121?style=for-the-badge&logo=sqlalchemy&logoColor=white)

### Frontend
![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

### Tools & Services
![NextAuth](https://img.shields.io/badge/NextAuth-000000?style=for-the-badge&logo=next.js&logoColor=white)
![Zod](https://img.shields.io/badge/Zod-3E67B1?style=for-the-badge&logo=zod&logoColor=white)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn
- SQL Database (SQLite/PostgreSQL/MySQL)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-chatbot-project
   ```

2. **Set up Python virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install flask sqlalchemy flask-cors python-dotenv
   # Add other dependencies as needed
   ```

4. **Set up database**
   ```bash
   # Run the SQL schema file
   sqlite3 database.db < sqlfile.sql
   # Or configure your preferred database
   ```

5. **Seed the database**
   ```bash
   python utils/data_seeder.py
   ```

6. **Run the Flask server**
   ```bash
   python app.py
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Configure your environment variables
   ```

4. **Run the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. **Open your browser**
   Navigate to `http://localhost:3000`

## 📁 Project Structure

```
ai-chatbot-project/
├── backend/
│   ├── app.py                 # Flask application entry point
│   ├── database.py           # Database configuration
│   ├── models.py             # SQLAlchemy models
│   ├── sqlfile.sql          # Database schema
│   ├── utils/
│   │   └── data_seeder.py   # Mock data generation
│   ├── services/
│   │   └── ai_services.py   # AI chatbot logic
│   └── api/
│       ├── chat.py          # Chat endpoints
│       ├── categories.py    # Category management
│       ├── products.py      # Product endpoints
│       └── search.py        # Search functionality
└── frontend/
    ├── app/
    │   ├── page.tsx          # Home page
    │   ├── dashboard/        # Dashboard pages
    │   └── (auth)/          # Authentication pages
    ├── components/           # Reusable UI components
    ├── api/                 # API route handlers
    ├── lib/                 # Utility functions
    ├── models/              # TypeScript interfaces
    ├── types/               # Type definitions
    └── .env                 # Environment variables
```

## 🔧 Configuration

### Backend Environment Variables
```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database Configuration
DATABASE_URL=sqlite:///database.db

# AI Service Configuration
AI_API_KEY=your-ai-api-key
```

### Frontend Environment Variables
```bash
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:5000

# Email Service (Resend)
RESEND_API_KEY=your-resend-api-key
```

## 📚 API Documentation

### Authentication Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | User registration |
| POST | `/api/auth/signin` | User login |
| POST | `/api/auth/verify` | Email verification |

### Chat Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send message to chatbot |
| GET | `/api/chat/history` | Retrieve chat history |

### Product Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | List all products |
| GET | `/api/products/:id` | Get product details |
| POST | `/api/products` | Create new product |
| PUT | `/api/products/:id` | Update product |
| DELETE | `/api/products/:id` | Delete product |

### Search & Categories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/search?q=query` | Search products |
| GET | `/api/categories` | List categories |

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm run test
# or
yarn test
```

## 📦 Deployment

### Backend Deployment (Heroku/Railway)
1. Configure production database
2. Set environment variables
3. Deploy using platform-specific instructions

### Frontend Deployment (Vercel/Netlify)
1. Configure build settings
2. Set environment variables
3. Deploy from repository

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines
- Follow TypeScript best practices
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed

## 🐛 Troubleshooting

### Common Issues

**CORS Errors**
```bash
# Ensure Flask-CORS is properly configured
pip install flask-cors
```

**Database Connection Issues**
```bash
# Check database URL and permissions
python -c "from database import db; print('Database connected!')"
```

**Authentication Problems**
```bash
# Verify NextAuth configuration
# Check environment variables
```

## 📖 Documentation

- [Technical Documentation](./TECHNICAL_DOCS.md) - Detailed technical overview
- [API Reference](./API_DOCS.md) - Complete API documentation
- [Deployment Guide](./DEPLOYMENT.md) - Production deployment instructions

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Basic chatbot functionality
- ✅ User authentication
- ✅ Product management
- ✅ Search functionality

### Phase 2 (Next)
- [ ] Real-time messaging with WebSockets
- [ ] File upload in chat
- [ ] Advanced AI features
- [ ] Mobile responsiveness improvements

### Phase 3 (Future)
- [ ] Mobile app development
- [ ] Multi-language support
- [ ] Analytics dashboard
- [ ] Advanced AI model training

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Your Name** - *Full Stack Developer* - [GitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Micro web framework
- [Next.js](https://nextjs.org/) - React framework
- [shadcn/ui](https://ui.shadcn.com/) - UI components
- [NextAuth.js](https://next-auth.js.org/) - Authentication library

## 📞 Support

If you have any questions or need help, please:
- 📧 Email: support@yourproject.com
- 💬 Create an issue on GitHub
- 📝 Check the documentation

---

<div align="center">
  <strong>Built with ❤️ using Flask and Next.js</strong>
</div>
