# Padhai Check - AI Study Assistant Frontend

A modern, Mistral-inspired frontend for an AI-powered study assistant that helps students verify information, fact-check claims, and learn better with evidence-based responses.

## 🎯 Features

- **Landing Page**: Beautiful hero section with feature showcase
- **Floating Chat Button**: Mistral-style chatbot accessible from the lower-right corner
- **AI Chat Interface**: Natural conversation with file upload support
- **Fact-Checking**: Real-time verification with colored verdict badges (True/False/Misleading/Unverified)
- **Evidence Cards**: Source citations with snippets from trusted sources
- **Wellbeing Support**: Motivational messages for student mental health
- **Trending Claims**: See what other students are verifying
- **Verification History**: Track past fact-checks and queries
- **File Support**: Upload images, screenshots, and PDFs with OCR processing
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Smooth Animations**: Motion-powered transitions and interactions

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
# or
yarn install
```

### 2. Configure Backend URL

Open `/config/backend.config.ts` and update:

```typescript
BASE_URL: 'http://localhost:8000'  // Your FastAPI backend URL
```

Or use environment variables:

```bash
# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

### 3. Run Development Server

```bash
npm start
# or
yarn start
```

Visit `http://localhost:3000` to see the app.

## 🔌 Backend Integration

### Required FastAPI Endpoints

Your backend must implement these endpoints:

1. **POST /api/upload** - Upload files (images, PDFs)
2. **POST /api/verify** - Verify content and return fact-check results
3. **GET /api/trends** - Get trending claims
4. **GET /api/claim/{id}** - Get detailed claim information

See [BACKEND_SETUP.md](./BACKEND_SETUP.md) for complete integration guide with code examples.

### Backend Response Format

```typescript
// POST /api/verify response
{
  "verdict": "True" | "False" | "Misleading" | "Unverified",
  "explanation": "Detailed explanation...",
  "evidence": [
    {
      "source": "Source name",
      "snippet": "Evidence snippet",
      "url": "https://source-url.com"
    }
  ],
  "wellbeing_message": "Optional motivational message"
}
```

## 📁 Project Structure

```
/
├── App.tsx                      # Main app component
├── config/
│   └── backend.config.ts        # Backend configuration
├── services/
│   └── api.ts                   # API service layer
├── pages/
│   ├── LandingPage.tsx          # Landing/home page
│   ├── ChatPage.tsx             # Main chat interface
│   ├── TrendsPage.tsx           # Trending claims
│   ├── HistoryPage.tsx          # Verification history
│   └── ClaimDetailsPage.tsx     # Detailed claim view
├── components/
│   ├── Layout.tsx               # App layout with sidebar
│   ├── DashboardApp.tsx         # Dashboard wrapper
│   ├── FloatingChatButton.tsx   # Floating chat button
│   ├── ChatModal.tsx            # Chat modal/popup
│   ├── VerdictBadge.tsx         # Verdict display component
│   ├── EvidenceCard.tsx         # Evidence source card
│   ├── WellbeingMessage.tsx     # Wellbeing message display
│   ├── TrendItem.tsx            # Trending claim item
│   ├── HistoryItem.tsx          # History item
│   └── chat/
│       ├── ChatBubble.tsx       # Chat message bubble
│       ├── ChatInput.tsx        # Chat input with file upload
│       └── TypingIndicator.tsx  # AI typing animation
└── styles/
    └── globals.css              # Global styles
```

## 🎨 Design Features

- **Mistral-Inspired**: Clean, modern design similar to Mistral AI
- **Floating Chat**: Lower-right corner chatbot button
- **Landing First**: Users see landing page before accessing chat
- **Google-Style**: Minimal, clean interface with focus on usability
- **Color-Coded Verdicts**: Visual distinction for True/False/Misleading/Unverified
- **Smooth Animations**: Motion/Framer Motion for buttery transitions
- **Mobile-First**: Fully responsive on all devices

## 🛠️ Tech Stack

- **React** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Motion (Framer Motion)** - Animations
- **Lucide React** - Icons
- **Fetch API** - HTTP requests

## 📱 Pages & Features

### Landing Page
- Hero section with call-to-action
- Feature showcase
- How it works section
- Footer with links

### Floating Chat Button
- Always visible on landing page
- Lower-right corner position
- Pulse animation to attract attention
- Opens chat modal on click

### Chat Modal
- Minimizable/maximizable
- File upload with preview
- Real-time typing indicator
- Verdict badges
- Evidence cards
- Wellbeing messages

### Dashboard
- Full-screen app mode
- Sidebar navigation
- Chat, Trends, and History pages
- Exam track selector
- Profile section

### Trending Claims
- Popular verifications
- View counts and timestamps
- Click to see details

### Verification History
- Past queries and results
- File upload indicators
- Quick access to previous checks

## 🔧 Configuration

### Enable/Disable Mock Data

In `/config/backend.config.ts`:

```typescript
USE_MOCK_FALLBACK: false  // Set to false when backend is ready
```

### CORS Setup (FastAPI)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚢 Deployment

### Build for Production

```bash
npm run build
# or
yarn build
```

### Environment Variables

```bash
# Production
REACT_APP_API_URL=https://api.padhaicheck.com
```

## 🤝 Backend Integration Checklist

- [ ] FastAPI backend running
- [ ] CORS configured correctly
- [ ] All 4 endpoints implemented
- [ ] Response formats match TypeScript interfaces
- [ ] File upload working
- [ ] OCR processing for images/PDFs
- [ ] Fact-checking logic implemented
- [ ] Evidence sources configured

## 📝 Notes

- Mock data is included for development without backend
- History is stored in localStorage
- File uploads are handled with FormData
- All timestamps use ISO format
- Verdicts are strictly typed (True/False/Misleading/Unverified)

## 🆘 Troubleshooting

**Chat not opening?** Check console for errors and ensure React is running.

**Backend errors?** Verify CORS is enabled and BASE_URL is correct.

**File upload fails?** Check file size limits and allowed types in backend.

**Mock data showing?** Backend might be unreachable; check network tab.

## 📄 License

© 2025 Padhai Check. All rights reserved.

---

**Need help?** Check [BACKEND_SETUP.md](./BACKEND_SETUP.md) for detailed backend integration instructions.
