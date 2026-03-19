import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardTitle, CardDescription } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, Users, ArrowDown, Database, Cpu, Wrench, Globe, CloudRain, Newspaper, Clock, ScanLine, LineChart, GraduationCap, LogOut } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { googleLogout } from '@react-oauth/google';
import LandingPage, { type UserProfile } from '@/components/LandingPage';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tools_used?: string[];
}

type Tab = 'chat' | 'docs' | 'team';

const AVAILABLE_TOOLS = [
  { id: 'weather_tool', name: 'Global Weather', icon: CloudRain },
  { id: 'news_tool', name: 'Live News', icon: Newspaper },
  { id: 'search_tool', name: 'DuckDuckGo Search', icon: Globe },
  { id: 'time_tool', name: 'System Clock', icon: Clock },
  { id: 'scrape_webpage', name: 'Web Scraper', icon: ScanLine },
  { id: 'finance_tool', name: 'Finance / Crypto', icon: LineChart },
  { id: 'arxiv_tool', name: 'ArXiv Papers', icon: GraduationCap },
];

function App() {
  const [isStarted, setIsStarted] = useState(false);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>('chat');
  
  // Chat State
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: 'assistant',
      content: "Hi there! I'm EchoMind, your elite system assistant. I have live access to tools like **Weather**, **News**, and **Search**. How can I assist you today?"
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const handleLogout = () => {
    googleLogout();
    setUser(null);
    setIsStarted(false);
  };

  useEffect(() => {
    if (activeTab === 'chat' && scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isLoading, activeTab]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Gather last 3 messages for context awareness
      const last3Messages = messages.slice(-3).map(m => ({ role: m.role, content: m.content }));

      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: userMessage.content,
          history: last3Messages 
        }),
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const data = await response.json();
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || "No response generated.",
        tools_used: data.tools_used || [],
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error fetching chat response:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I encountered an error connecting to the backend. Please ensure the server is running on `http://localhost:8000`.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isStarted) {
    return <LandingPage onStart={(userData?: UserProfile) => {
      if (userData) setUser(userData);
      setIsStarted(true);
    }} />;
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-zinc-50 font-sans selection:bg-white/20 flex flex-col relative overflow-hidden">
      {/* Background Ambient Glows */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-500/10 blur-[140px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-indigo-500/10 blur-[140px] rounded-full pointer-events-none" />
      
      {/* Navbar: Ultra Minimalist Linear/Vercel style */}
      <nav className="sticky top-0 z-50 w-full border-b border-white/5 bg-[#0a0a0a]/60 backdrop-blur-xl">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <div 
            className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => setIsStarted(false)}
          >
            <img src="/avatar.png" alt="EchoMind Avatar" className="w-8 h-8 object-cover rounded shadow-sm" />
            <span className="text-lg font-bold tracking-tight text-white">
              EchoMind
            </span>
          </div>
          
          <div className="hidden md:flex flex-1 justify-center items-center gap-8">
            {(['chat', 'docs', 'team'] as Tab[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`text-sm font-semibold transition-all duration-300 capitalize tracking-wide ${
                  activeTab === tab 
                    ? 'text-white drop-shadow-[0_0_10px_rgba(255,255,255,0.4)]' 
                    : 'text-zinc-500 hover:text-zinc-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden sm:flex flex-col items-end justify-center">
              <span className="text-sm font-semibold text-zinc-200 tracking-tight leading-none mb-1">{user?.name || 'Guest User'}</span>
              <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-medium leading-none">{user?.email ? 'Authenticated' : 'Local Session'}</span>
            </div>
            {user?.picture ? (
              <img src={user.picture} alt="Profile" className="w-9 h-9 rounded-full border border-white/10 shadow-lg" />
            ) : (
              <div className="w-9 h-9 rounded-full bg-zinc-800 border border-white/10 flex items-center justify-center shadow-inner">
                <span className="text-xs text-zinc-400 font-bold">GU</span>
              </div>
            )}
            <button 
              onClick={handleLogout}
              className="p-2 ml-1 rounded-lg bg-zinc-900 md:bg-transparent hover:bg-white/10 text-zinc-400 hover:text-white transition-all duration-200 cursor-pointer shadow-sm border border-white/5 md:border-transparent md:hover:border-white/10 flex items-center gap-2"
              title="End Session"
            >
              <LogOut className="w-4 h-4" />
              <span className="sr-only">Logout</span>
            </button>
          </div>
        </div>
        
        {/* Mobile Tab Control */}
        <div className="flex md:hidden w-full border-t border-white/5 p-2 bg-black/40 justify-around">
           {(['chat', 'docs', 'team'] as Tab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`text-[11px] font-bold tracking-wider py-2 w-full text-center capitalize ${activeTab === tab ? 'text-white shadow-sm bg-white/5 rounded-md' : 'text-zinc-500'}`}
            >
              {tab}
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="flex-1 container mx-auto p-4 md:p-8 flex items-start justify-center">
        
        {/* Chat Tab */}
        <AnimatePresence mode="wait">
        {activeTab === 'chat' && (
          <motion.div 
            key="chat"
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -5 }}
            transition={{ duration: 0.2 }}
            className="w-full max-w-6xl h-[calc(100vh-8rem)] flex flex-col md:flex-row gap-6 relative"
          >
            {/* Sidebar Tools Panel */}
            <div className="hidden md:flex flex-col w-64 border border-white/5 bg-[#0a0a0a] rounded-xl p-4">
              <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-4">Plugin Ecosystem</h3>
              <div className="space-y-2 flex-1">
                {AVAILABLE_TOOLS.map((tool) => {
                  const Icon = tool.icon;
                  return (
                    <div 
                      key={tool.id} 
                      className="flex items-center gap-3 p-3 rounded-lg border border-white/5 bg-zinc-900/50 hover:bg-zinc-800/50 transition-colors"
                    >
                      <Icon className="w-4 h-4 text-zinc-400" />
                      <span className="text-sm font-medium text-zinc-300">{tool.name}</span>
                    </div>
                  );
                })}
              </div>
              <div className="mt-auto pt-4 border-t border-white/5 border-b border-transparent">
                <div className="flex items-center gap-3 px-2 py-1 bg-indigo-500/5 rounded-md border border-indigo-500/10">
                  <Cpu className="w-4 h-4 text-indigo-400" />
                  <span className="text-[11px] font-bold tracking-widest text-indigo-300/80 uppercase">Llama 3.1 8B Live</span>
                </div>
              </div>
            </div>

            {/* Chat Container */}
            <div className="flex-1 flex flex-col border border-white/5 bg-black/40 backdrop-blur-md rounded-xl overflow-hidden relative shadow-2xl">
              <ScrollArea className="flex-1 px-4 lg:px-6">
                <div className="flex flex-col gap-6 py-6">
                  <AnimatePresence initial={false}>
                    {messages.map((message) => (
                      <motion.div
                        key={message.id}
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={`flex items-start gap-4 ${
                          message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                        }`}
                      >
                        <div className={`mt-1 w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center overflow-hidden border ${
                          message.role === 'user' 
                            ? 'bg-zinc-100 border-zinc-200' 
                            : 'bg-black border-white/10'
                        }`}>
                          {message.role === 'user' ? (
                            user?.picture ? (
                              <img src={user.picture} alt="User" className="w-full h-full object-cover" />
                            ) : (
                              <div className="w-full h-full bg-zinc-800" />
                            )
                          ) : (
                            <img src="/avatar.png" alt="EchoMind" className="w-full h-full object-cover" />
                          )}
                        </div>
                        
                        <div className="flex flex-col gap-2 max-w-[85%]">
                          {/* Tool Usage Badge */}
                          {message.role === 'assistant' && message.tools_used && message.tools_used.length > 0 && (
                            <div className="flex flex-wrap gap-2 mb-1">
                              {message.tools_used.map(toolId => {
                                const toolInfo = AVAILABLE_TOOLS.find(t => t.id === toolId) || { name: toolId, icon: Wrench };
                                const Icon = toolInfo.icon;
                                return (
                                  <div key={toolId} className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-zinc-900 border border-white/10 text-xs font-medium text-zinc-300">
                                    <Icon className="w-3 h-3 text-zinc-400" />
                                    <span>Used {toolInfo.name}</span>
                                  </div>
                                );
                              })}
                            </div>
                          )}

                          <div
                            className={`px-5 py-3.5 text-[15px] leading-relaxed shadow-sm ${
                              message.role === 'user'
                                ? 'bg-zinc-100 text-black rounded-2xl rounded-tr-sm font-medium shadow-white/5'
                                : 'bg-black/80 backdrop-blur-md text-zinc-300 rounded-2xl rounded-tl-sm border border-white/5 prose prose-invert max-w-none prose-p:leading-relaxed prose-pre:bg-zinc-950 prose-pre:border prose-pre:border-white/10 prose-strong:text-zinc-100 placeholder:text-zinc-500'
                            }`}
                          >
                            {message.role === 'user' ? (
                              <p>{message.content}</p>
                            ) : (
                              <div className="markdown-body text-zinc-200">
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                  {message.content}
                                </ReactMarkdown>
                              </div>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                  
                  <div ref={scrollRef} />
                  
                  {isLoading && (
                    <motion.div 
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex items-start gap-4"
                    >
                      <div className="mt-1 w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center overflow-hidden border bg-black border-white/10">
                         <img src="/avatar.png" alt="EchoMind" className="w-full h-full object-cover opacity-50 pulse-anim" />
                      </div>
                      <div className="px-5 py-3.5 rounded-2xl bg-zinc-900 border border-white/5 rounded-tl-sm flex items-center gap-3">
                        <div className="flex gap-1">
                          <span className="w-1.5 h-1.5 rounded-full bg-zinc-600 animate-bounce" style={{ animationDelay: '0ms' }} />
                          <span className="w-1.5 h-1.5 rounded-full bg-zinc-600 animate-bounce" style={{ animationDelay: '150ms' }} />
                          <span className="w-1.5 h-1.5 rounded-full bg-zinc-600 animate-bounce" style={{ animationDelay: '300ms' }} />
                        </div>
                      </div>
                    </motion.div>
                  )}
                </div>
              </ScrollArea>
              
              <div className="p-4 bg-[#0a0a0a] border-t border-white/5">
                <form onSubmit={handleSubmit} className="flex items-center gap-3 max-w-4xl mx-auto">
                  <Input
                    value={input}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
                    placeholder="Message EchoMind..."
                    className="flex-1 h-12 px-5 rounded-lg border-white/10 bg-zinc-900 text-white placeholder:text-zinc-600 focus-visible:ring-1 focus-visible:ring-zinc-700 focus-visible:ring-offset-0 focus-visible:bg-zinc-800 text-[15px] transition-colors"
                    disabled={isLoading}
                  />
                  <Button
                    type="submit"
                    disabled={!input.trim() || isLoading}
                    className="h-12 w-12 rounded-lg bg-zinc-100 hover:bg-white text-black transition-colors shrink-0 p-0 flex items-center justify-center disabled:opacity-50"
                  >
                    <span className="sr-only">Send</span>
                    <Send className="w-5 h-5" />
                  </Button>
                </form>
              </div>
            </div>
          </motion.div>
        )}

        {/* Docs Tab: System Architecture Diagram */}
        {activeTab === 'docs' && (
          <motion.div 
            key="docs"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            className="w-full max-w-5xl py-8 flex flex-col gap-14"
          >
            <div className="space-y-4 text-center md:text-left">
              <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-2">Technical Documentation</h1>
              <p className="text-zinc-400 text-lg max-w-2xl">A deep dive into how EchoMind processes queries, leverages LLMs, and invokes real-world tools entirely within milliseconds.</p>
            </div>

            {/* Expanded Knowledge Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
               <div className="bg-zinc-900/60 backdrop-blur-sm border border-white/5 p-6 rounded-2xl">
                 <Database className="w-6 h-6 text-zinc-300 mb-4" />
                 <h3 className="text-xl font-bold text-white mb-2 tracking-tight">Stateful Context Memory</h3>
                 <p className="text-zinc-400 text-sm leading-relaxed">
                    By intercepting the payload across the `/api/chat` route, the React frontend isolates and constructs a rolling context window of the last 3 message turns. 
                    This ensures the LangChain agent running locally maintains absolute conversational permanence, allowing accurate follow-up logic.
                 </p>
               </div>
               
               <div className="bg-zinc-900/60 backdrop-blur-sm border border-white/5 p-6 rounded-2xl">
                 <Wrench className="w-6 h-6 text-zinc-300 mb-4" />
                 <h3 className="text-xl font-bold text-white mb-2 tracking-tight">Deterministic Parsing</h3>
                 <p className="text-zinc-400 text-sm leading-relaxed">
                    LLMs frequently hallucinate JSON objects when attempting to invoke specific code execution modules. EchoMind relies on an explicit Python validation 
                    `for _ in range(3)` execution loop, automatically catching, parsing, and feeding any exceptions back to the model for instantaneous auto-correction.
                 </p>
               </div>
            </div>

            {/* Visual Diagram */}
            <div className="w-full bg-[#050505] border border-white/10 rounded-3xl p-8 relative flex flex-col items-center gap-6 overflow-x-auto shadow-2xl">
              
              <div className="absolute top-0 bottom-0 left-1/2 w-px bg-gradient-to-b from-blue-500/0 via-indigo-500/30 to-blue-500/0 -translate-x-1/2 z-0 hidden md:block" />

              {/* Box 1: User / UI */}
              <div className="w-72 bg-zinc-900/90 backdrop-blur-xl border border-white/10 rounded-2xl p-5 flex flex-col items-center text-center shadow-lg relative z-10 transition-transform hover:-translate-y-1 duration-300">
                <Users className="w-6 h-6 text-indigo-400 mb-3" />
                <h4 className="font-bold text-white text-[15px]">Frontend (Vite + React)</h4>
                <p className="text-[13px] text-zinc-500 mt-2 leading-relaxed">Accepts user prompt, parses Markdown, renders tool badges.</p>
              </div>

              <ArrowDown className="w-6 h-6 text-zinc-600 animate-bounce" />

              {/* Box 3: LangChain core */}
              <div className="w-full max-w-3xl bg-black border border-indigo-500/40 rounded-2xl p-8 shadow-[0_0_40px_rgba(99,102,241,0.1)] relative z-10 flex flex-col items-center">
                <Cpu className="w-10 h-10 text-indigo-400 mb-4 animate-pulse" />
                <h4 className="text-xl font-bold text-white tracking-tight">LangChain Recursive Agent</h4>
                <p className="text-sm text-zinc-400 text-center mt-3 max-w-lg mb-8 leading-relaxed">
                  Powered by Llama 3. The LLM determines if it has native knowledge to answer the query, or if it must autonomously execute external functions.
                </p>
                
                {/* Tools Grid inside Agent */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full">
                   <div className="bg-zinc-900 border border-white/5 rounded-xl p-4 text-center flex flex-col items-center hover:bg-zinc-800 transition-colors">
                     <CloudRain className="w-6 h-6 text-blue-400 mb-2" />
                     <span className="text-xs font-semibold text-white">Weather</span>
                     <span className="text-[10px] text-zinc-500 mt-1">Open-Meteo</span>
                   </div>
                   <div className="bg-zinc-900 border border-white/5 rounded-xl p-4 text-center flex flex-col items-center hover:bg-zinc-800 transition-colors">
                     <Newspaper className="w-6 h-6 text-yellow-400 mb-2" />
                     <span className="text-xs font-semibold text-white">News</span>
                     <span className="text-[10px] text-zinc-500 mt-1">DuckDuckGo</span>
                   </div>
                   <div className="bg-zinc-900 border border-white/5 rounded-xl p-4 text-center flex flex-col items-center hover:bg-zinc-800 transition-colors">
                     <LineChart className="w-6 h-6 text-green-400 mb-2" />
                     <span className="text-xs font-semibold text-white">Stocks</span>
                     <span className="text-[10px] text-zinc-500 mt-1">Yahoo Finance</span>
                   </div>
                   <div className="bg-zinc-900 border border-white/5 rounded-xl p-4 text-center flex flex-col items-center hover:bg-zinc-800 transition-colors">
                     <GraduationCap className="w-6 h-6 text-purple-400 mb-2" />
                     <span className="text-xs font-semibold text-white">ArXiv</span>
                     <span className="text-[10px] text-zinc-500 mt-1">Universities</span>
                   </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Team Tab */}
        {activeTab === 'team' && (
          <motion.div 
            key="team"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            className="w-full max-w-6xl py-12 flex flex-col items-center text-center gap-12"
          >
            <div className="space-y-4">
              <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white">Project Authors</h1>
              <p className="text-zinc-400 text-lg">The core engineers constructing the intelligence behind EchoMind.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full px-4">
              {[
                { name: 'Rajcharan', role: 'Full Stack Engineer', desc: 'Expert in React, Vite frameworks, component systems, and UI execution.', image: '/rajcharan.jpg', linkedin: 'https://www.linkedin.com/in/raj-charan-vanga-05b249255' },
                { name: 'Bandi Naresh', role: 'AI & Systems Architect', desc: 'Specialist in Vector DB integrations, LangChain orchestration and core Python API logic.', image: '/naresh.jpg', linkedin: 'https://www.linkedin.com/in/bandi-naresh' },
                { name: 'Talah Hanuman', role: 'Lead Developer', desc: 'Overseeing global platform vision, highly-scalable backend structures, and Vercel routing.', image: '/talah.jpg', linkedin: 'https://www.linkedin.com/in/talaha-numan-4bb92a28b' }
              ].map((member, i) => (
                <motion.div
                  key={member.name}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="group relative h-full flex flex-col"
                >
                  <div className="absolute inset-0 bg-gradient-to-b from-indigo-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-3xl blur-xl" />
                  <Card className="bg-zinc-900/80 backdrop-blur-xl border-white/5 h-full flex flex-col p-8 hover:border-indigo-500/30 transition-all duration-300 relative z-10 rounded-3xl group-hover:-translate-y-2 shadow-2xl">
                    <div className="w-20 h-20 rounded-full bg-zinc-900 border-2 border-white/10 mb-6 flex items-center justify-center mx-auto shadow-lg shadow-indigo-500/20 overflow-hidden relative">
                      {/* Avatar Image Placeholder */}
                      <img src={member.image} alt={member.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500 relative z-10" 
                           onError={(e) => { e.currentTarget.style.display = 'none'; e.currentTarget.nextElementSibling?.classList.remove('hidden'); }} />
                      <span className="hidden absolute inset-0 flex items-center justify-center text-xl font-bold text-white tracking-widest bg-gradient-to-br from-indigo-500 to-blue-600">{member.name.charAt(0)}</span>
                    </div>
                    <CardTitle className="text-xl font-bold text-white mb-2">{member.name}</CardTitle>
                    <CardDescription className="text-indigo-400 text-[13px] font-bold tracking-widest uppercase mb-6">{member.role}</CardDescription>
                    <p className="text-sm text-zinc-400 mt-auto leading-relaxed">{member.desc}</p>
                    
                    <div className="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mt-8 mb-4" />
                    <div className="flex justify-center gap-4">
                       <a href={member.linkedin} target="_blank" rel="noopener noreferrer" className="text-[11px] font-bold tracking-widest uppercase text-zinc-500 hover:text-indigo-400 transition-colors">LinkedIn</a>
                    </div>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
        </AnimatePresence>

      </main>

      {/* Embedded CSS for Markdown and pulse animations */}
      <style>{`
        .markdown-body p:last-child { margin-bottom: 0; }
        .markdown-body p { margin-bottom: 0.75em; }
        .markdown-body strong { color: white; font-weight: 600; }
        .markdown-body ul { list-style-type: disc; padding-left: 1.5em; margin-bottom: 1em; }
        .markdown-body ol { list-style-type: decimal; padding-left: 1.5em; margin-bottom: 1em; }
        .markdown-body a { color: #e4e4e7; text-decoration: underline; text-underline-offset: 4px; }
        .markdown-body code { background: #18181b; padding: 0.2em 0.4em; border-radius: 4px; font-size: 0.85em; border: 1px solid rgba(255,255,255,0.1); }
        .markdown-body pre { background: #18181b; padding: 1rem; border-radius: 8px; overflow-x: auto; margin-bottom: 1em; border: 1px solid rgba(255,255,255,0.1); }
        .markdown-body pre code { background: none; padding: 0; border: none; font-size: 0.85em; }
      `}</style>
    </div>
  );
}

export default App;
