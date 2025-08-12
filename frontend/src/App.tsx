import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { LoginPage } from './pages/LoginPage';
import { AuthorizePage } from './pages/AuthorizePage';

function App() {
  return (
    <MantineProvider>
      <Router basename="/">
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth" element={<AuthorizePage />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </MantineProvider>
  );
}

export default App;
