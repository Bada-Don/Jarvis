import React, { useState } from 'react';
import { Send, User, Bot } from 'lucide-react';

const ChatPanel = () => {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([
        { id: 1, role: 'assistant', text: 'Good afternoon. All systems are operational. How can I assist you today?' }
    ]);

    const handleSend = (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        setMessages(prev => [...prev, { id: Date.now(), role: 'user', text: input }]);
        setInput('');

        // Mock response
        setTimeout(() => {
            setMessages(prev => [...prev, { id: Date.now() + 1, role: 'assistant', text: 'I am processing your command...' }]);
        }, 1000);
    };

    return (
        <div className="flex flex-col h-full gap-4">
            <div className="flex items-center gap-2 pb-4 border-b border-border/20">
                <h2 className="text-xs uppercase tracking-widest text-muted-foreground font-semibold">Communication Log</h2>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto space-y-4 pr-2 scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent">
                {messages.map((msg) => (
                    <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-primary/20 text-primary' : 'bg-secondary/30 text-foreground'}`}>
                            {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
                        </div>
                        <div className={`p-3 rounded-lg text-sm max-w-[85%] ${msg.role === 'user' ? 'bg-primary/10 border border-primary/20 text-foreground' : 'bg-card/30 border border-border/10 text-muted-foreground'}`}>
                            {msg.text}
                        </div>
                    </div>
                ))}
            </div>

            {/* Input Area */}
            <form onSubmit={handleSend} className="mt-auto relative">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Enter command..."
                    className="w-full bg-card/20 border border-border/20 rounded-full py-3 pl-4 pr-12 text-sm text-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all font-mono"
                />
                <button
                    type="submit"
                    disabled={!input.trim()}
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full text-primary hover:bg-primary/10 disabled:opacity-50 disabled:hover:bg-transparent transition-colors"
                >
                    <Send size={16} />
                </button>
            </form>
        </div>
    );
};

export default ChatPanel;
