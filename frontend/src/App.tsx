import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { LoginPage } from './pages/LoginPage';
import { AuthorizePage } from './pages/AuthorizePage';

function App() {
  return (
    <MantineProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth" element={<AuthorizePage />} />
        </Routes>
      </Router>
    </MantineProvider>
  );
}

export default App;
