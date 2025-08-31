import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
// main.tsx
import App from './components/App.tsx'  // Add components/

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
