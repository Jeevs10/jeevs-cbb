# Development Guide (Individual Developer)

This is a simplified setup focused on code quality and maintainability without heavy DevOps overhead.

## 🚀 Quick Start (Minimal)

### 1. Setup Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Setup Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## 🧪 Development Tools (Lightweight)

### Code Quality
```bash
# Frontend
npm run lint          # Check code style
npm run format        # Fix formatting
npm run type-check    # TypeScript validation

# Backend (optional - add if needed)
# Add basic linting later if desired
```

### Testing (Optional)
```bash
# Frontend - run when making changes
npm run test

# Backend - run when making API changes  
pytest tests/ -v
```

## 📁 Project Structure (What We Improved)

### ✅ Frontend Improvements
- **Modular Components**: Broke down the 354-line `page.tsx` monster
- **Custom Hooks**: Extracted data fetching logic
- **Type Safety**: Added comprehensive TypeScript types
- **Error Boundaries**: Proper error handling
- **API Client**: Centralized API calls with error handling

### ✅ Backend Improvements  
- **Service Layer**: Separated business logic from routes
- **Validation**: Added input validation with Pydantic
- **Error Handling**: Structured error responses
- **Configuration**: Environment-based settings
- **Clean Architecture**: Organized into logical modules

## 🎯 What to Use Daily

### Development Workflow
1. **Make changes** to components/services
2. **Run linting**: `npm run lint` + `npm run type-check`  
3. **Test manually**: Open app and test functionality
4. **Format code**: `npm run format` before commits

### Code Standards
- **TypeScript**: No `any` types, strict mode enabled
- **Components**: Keep them small and focused
- **API**: Use the new centralized API client
- **Error Handling**: Use error boundaries and proper validation

## 🐛 Debugging Tips

### Frontend Issues
- **Network errors**: Check API URL in `.env.local`
- **Type errors**: Run `npm run type-check` for details
- **Build issues**: Clear `.next` folder: `rm -rf .next`

### Backend Issues  
- **Import errors**: Check virtual environment is activated
- **Data issues**: Verify CSV files exist in `data/` folder
- **API errors**: Check browser network tab for response details

## 📦 Optional Enhancements (When Ready)

### When You Want More Features
- **Add database**: Replace CSV files with PostgreSQL
- **Add authentication**: User accounts and sessions  
- **Add caching**: Redis for performance
- **Add monitoring**: Basic logging and metrics

### When Scaling Up
- **Add CI/CD**: GitHub Actions for automated testing
- **Add Docker**: Containerize for deployment
- **Add testing**: Comprehensive test coverage
- **Add monitoring**: APM tools like Sentry

---

**Focus**: Clean code, good structure, and maintainable architecture.  
**Skip**: Heavy DevOps, complex testing, over-engineering.
