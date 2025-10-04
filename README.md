# Brand24-Inspired Modern Web Application

A modern, responsive web application built with Next.js 15, React 19, and shadcn/ui, featuring beautiful gradient graphics and animations inspired by Brand24's design language.

## 🚀 Features

- **Modern UI/UX**: Clean, professional design with gradient backgrounds and smooth animations
- **Responsive Design**: Works seamlessly across all device sizes
- **shadcn/ui Components**: Consistent, accessible component library
- **Framer Motion**: Smooth animations and micro-interactions
- **Tailwind CSS**: Utility-first CSS framework with custom gradient utilities
- **App Store Parser**: Built-in functionality to analyze App Store reviews
- **Dark/Light Mode**: CSS variables for easy theme switching

## 🛠️ Tech Stack

- **Framework**: Next.js 15+ with React 19+
- **Styling**: Tailwind CSS 4+ with custom gradient utilities
- **Components**: shadcn/ui for consistent, accessible components
- **Icons**: Lucide React for modern iconography
- **Animations**: Framer Motion for smooth transitions
- **TypeScript**: Type-safe development (optional)

## 📦 Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Run the development server**:
   ```bash
   npm run dev
   ```

3. **Open your browser** and navigate to [http://localhost:3000](http://localhost:3000)

## 🎨 Design System

### Color Palette
- **Primary**: Modern blues and purples with gradient variations
- **Secondary**: Complementary colors that enhance readability
- **Accent**: Vibrant colors for CTAs and highlights
- **Neutral**: Sophisticated grays for text and backgrounds

### Gradient Utilities
The application includes custom gradient utilities:
- `.gradient-text`: Gradient text effect
- `.gradient-bg`: Primary gradient background
- `.hero-gradient`: Animated hero section gradient
- `.glass-effect`: Glassmorphism effect

### Components
- **Navigation**: Fixed navigation with mobile menu
- **Hero Section**: Animated hero with gradient background
- **Feature Cards**: Interactive cards with hover effects
- **Testimonials**: Customer testimonials with ratings
- **Footer**: Comprehensive footer with newsletter signup

## 🎯 Key Features

### Hero Section
- Large, impactful headlines with gradient text
- Compelling value propositions
- Clear call-to-action buttons
- Animated background gradients
- Social proof elements

### Feature Cards
- Clean card designs with subtle shadows
- Icon integration with consistent styling
- Hover effects with smooth transitions
- Gradient borders and backgrounds
- Clear typography hierarchy

### App Store Parser
- Real-time App Store review analysis
- Multi-country support
- Modern form design with validation
- Loading states and error handling
- Responsive data display

## 🎨 Customization

### Adding New Gradients
Add custom gradients to `tailwind.config.js`:
```javascript
backgroundImage: {
  'gradient-custom': 'linear-gradient(135deg, #your-colors)',
}
```

### Creating New Components
Follow the established patterns:
1. Use shadcn/ui as the foundation
2. Add custom Tailwind classes for styling
3. Implement Framer Motion for animations
4. Maintain accessibility standards

### Theme Customization
Modify CSS variables in `globals.css`:
```css
:root {
  --primary: your-primary-color;
  --secondary: your-secondary-color;
}
```

## 📱 Responsive Design

The application is built with a mobile-first approach:
- **Mobile**: Optimized for touch interactions
- **Tablet**: Adapted layouts for medium screens
- **Desktop**: Full-featured experience with hover effects

## 🚀 Performance

- **Optimized Images**: Next.js Image component
- **Code Splitting**: Automatic code splitting
- **Lazy Loading**: Non-critical components
- **Bundle Optimization**: Minimal bundle size

## 🔧 Development

### Project Structure
```
src/
├── app/                 # Next.js app directory
├── components/          # Reusable components
│   ├── ui/             # shadcn/ui components
│   ├── HeroSection.js  # Hero section component
│   ├── FeaturesSection.js # Features grid
│   └── ...
├── lib/                # Utility functions
└── styles/             # Global styles
```

### Adding New Pages
1. Create a new file in `src/app/`
2. Follow the established component patterns
3. Use the design system components
4. Implement responsive design

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the established coding patterns
4. Test your changes
5. Submit a pull request

## 📞 Support

For support and questions, please contact the development team.

---

Built with ❤️ using Next.js, React, and shadcn/ui