import { Routes, Route } from 'react-router-dom';
import LandingPage from '@/components/LandingPage';
import ChatPage from '@/pages/ChatPage';
import DocsPage from '@/pages/DocsPage';
import TeamPage from '@/pages/TeamPage';
import Layout from '@/components/Layout';

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route element={<Layout />}>
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/docs" element={<DocsPage />} />
        <Route path="/team" element={<TeamPage />} />
      </Route>
    </Routes>
  );
}

export default App;
