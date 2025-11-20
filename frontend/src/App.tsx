// src/App.tsx
import { GlobalProvider } from './contexts/GlobalContext';
import { NotificationProvider } from './contexts/NotificationContext';
import MainLayout from './components/layout/MainLayout';

function App() {
  return (
    <GlobalProvider>
      <NotificationProvider>
        <MainLayout />
      </NotificationProvider>
    </GlobalProvider>
  );
}

export default App;