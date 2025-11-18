# Trade Agent React Frontend

Modern, responsive React frontend for the AI-powered Trade Form Automation platform.

## 🚀 Features

- **Dashboard**: Overview of forms, templates, and AI status with real-time statistics
- **AI Form Filler**: Intelligent form filling using Groq LLM
- **Template Management**: Create and manage custom form templates
- **History**: View and search past form submissions
- **CRM Dashboard**: Manage companies, leads, and products
- **Export Options**: Export data to PDF, Excel, and JSON formats
- **Modern UI**: Beautiful, responsive design with TailwindCSS

## 🛠️ Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **React Router** - Client-side routing
- **Zustand** - Lightweight state management
- **TailwindCSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **Lucide React** - Beautiful icons
- **jsPDF & XLSX** - Export functionality
- **React Hot Toast** - Elegant notifications

## 📦 Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env
```

## 🏃 Running the Application

### Development Mode

```bash
npm run dev
```

The application will start on `http://localhost:3000`

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## 🔧 Configuration

### Environment Variables

`.env` file:

```env
VITE_API_URL=http://localhost:5000
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/         # Reusable UI components
│   ├── pages/              # Page components
│   ├── services/           # API services
│   ├── store/              # State management
│   ├── types/              # TypeScript types
│   ├── utils/              # Utility functions
│   ├── App.tsx             # Main app component
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
├── public/                 # Static assets
└── vite.config.ts          # Vite config
```

## 🔌 Backend Integration

Start the Flask backend first:

```bash
cd /home/user/trade-agent
python web_app.py
```

Then start the frontend:

```bash
cd frontend
npm run dev
```

---

Built with ❤️ using React, TypeScript, and TailwindCSS
