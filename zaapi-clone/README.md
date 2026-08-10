# Zaapi Clone - Enterprise Omnichannel Customer Support Platform

A production-ready, enterprise-grade clone of the Zaapi customer support platform built with Next.js 14, TypeScript, and Tailwind CSS.

## 🚀 Features Implemented

### Core Modules
- **Unified Inbox** - Centralized ticketing system for all customer conversations
- **AI Chatbot** - Knowledge base management, prompt configuration, personality settings
- **Analytics Dashboard** - Real-time metrics and performance tracking
- **Automations** - Custom workflow builder (prebuilt and custom flows)
- **Broadcasts** - LINE OA and WhatsApp campaign management
- **Contacts Management** - Customer database with custom fields
- **Settings** - Business information, team management, integrations

### Channel Integrations
- Website Chat Widget
- Facebook Messenger & Instagram Direct
- WhatsApp Business
- LINE Official Account
- Shopee & Lazada Marketplaces
- TikTok Shop
- Gmail & Outlook Email
- Shopify & HubSpot CRM

### Technical Features
- ✅ Next.js 14 with App Router
- ✅ TypeScript for type safety
- ✅ Tailwind CSS for styling
- ✅ Responsive design (mobile & desktop)
- ✅ Thai language localization
- ✅ Trial period countdown banner
- ✅ Empty states with CTAs
- ✅ Modular component architecture
- ✅ Production-ready build configuration

## 📁 Project Structure

```
zaapi-clone/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout
│   │   └── th/                 # Thai locale routes
│   │       ├── tickets/        # Unified inbox
│   │       ├── contacts/       # Contact management
│   │       ├── ai-bot/         # AI chatbot config
│   │       ├── analytics/      # Analytics dashboard
│   │       ├── automations/    # Workflow automations
│   │       ├── broadcasts/     # Broadcast campaigns
│   │       └── settings/       # Business settings
│   ├── components/             # Reusable React components
│   │   ├── Sidebar.tsx         # Main navigation
│   │   └── EmptyState.tsx      # Empty state component
│   ├── data/                   # Constants and mock data
│   │   └── constants.ts        # Channel configs, time options
│   ├── styles/                 # Global styles
│   │   └── globals.css         # Tailwind imports
│   ├── types/                  # TypeScript definitions
│   │   └── index.ts            # All interfaces
│   └── utils/                  # Utility functions
├── public/
│   └── images/                 # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.js
└── README.md
```

## 🛠️ Installation

```bash
# Navigate to project directory
cd /workspace/zaapi-clone

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## 🔧 Configuration

### Environment Variables
Create a `.env.local` file:
```env
NEXT_PUBLIC_API_URL=https://api.zaapi.com
NEXT_PUBLIC_APP_URL=https://app.zaapi.com
```

### Supported Channels
All channel configurations are in `src/data/constants.ts`:
- Website, Facebook, Instagram, WhatsApp
- LINE, Shopee, Lazada, TikTok Shop
- Gmail, Outlook, Shopify, HubSpot

## 📱 Pages Implemented

1. **Tickets** (`/th/tickets`) - Unified inbox with filters
2. **AI Bot** (`/th/ai-bot`) - Knowledge base management
3. **Analytics** (`/th/analytics`) - Real-time dashboard
4. **Automations** (`/th/automations`) - Workflow builder
5. **Broadcasts** (`/th/broadcasts`) - Campaign management
6. **Contacts** (`/th/contacts`) - Customer database
7. **Settings** (`/th/settings`) - Business configuration

## 🎨 Design System

### Colors
- Primary: `#0066FF` (Blue)
- Secondary: `#F3F4F6` (Gray)
- Success: `#10B981` (Green)
- Warning: `#F59E0B` (Amber)
- Danger: `#EF4444` (Red)

### Typography
- Font: Inter (Google Fonts)
- Base size: 16px
- Scale: sm, base, lg, xl, 2xl

## 🚀 Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker
```bash
# Build image
docker build -t zaapi-clone .

# Run container
docker run -p 3000:3000 zaapi-clone
```

### Manual Production Build
```bash
npm run build
npm start
```

## 📊 Key Metrics Displayed

- Trial days remaining countdown
- Open tickets count
- Unassigned tickets
- Response time metrics
- Agent performance
- Channel distribution
- SLA compliance

## 🔐 Security Considerations

This is a frontend clone for demonstration purposes. For production use:

1. Implement proper authentication (JWT/OAuth)
2. Add API rate limiting
3. Enable HTTPS only
4. Implement CSRF protection
5. Add input validation
6. Configure CORS properly
7. Use environment variables for secrets

## 📝 License

This project is for educational and demonstration purposes only. Zaapi® is a registered trademark of its respective owners.

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## 📞 Support

For questions or issues, please refer to the original Zaapi documentation at https://help.zaapi.com

---

**Built with ❤️ using Next.js 14, TypeScript, and Tailwind CSS**
