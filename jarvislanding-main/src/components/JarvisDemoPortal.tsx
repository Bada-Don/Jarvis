"use client";

import React, { useState, useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import { ShieldAlert, Send, Terminal, Monitor, Circle, CheckCircle2, XCircle } from 'lucide-react';
import PermissionOverlay from './PermissionOverlay';

interface Message {
  text: string;
  sender: 'user' | 'system' | 'bot';
  timestamp: number;
}

interface PendingPermission {
  requestId: string;
  operation: string;
  details: string;
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://13.218.156.16:5000';
const GUACAMOLE_URL = process.env.NEXT_PUBLIC_GUACAMOLE_URL || 'https://evaluate-needs-semiconductor-understood.trycloudflare.com/guacamole/';
const DEVICE_ID = process.env.NEXT_PUBLIC_DEVICE_ID || 'desktop_e054d2c4a0684c98';

export default function JarvisDemoPortal() {
  const [command, setCommand] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    { text: "System: Standing by for commands...", sender: "system", timestamp: Date.now() }
  ]);
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [pendingPermission, setPendingPermission] = useState<PendingPermission | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Establish Socket.IO connection
  useEffect(() => {
    const newSocket = io(BACKEND_URL, {
      transports: ['websocket'],
      reconnectionAttempts: 5,
    });

    newSocket.on('connect', () => {
      console.log('Connected to JARVIS Brain');
      setIsConnected(true);
      setMessages(prev => [...prev, {
        text: "System: Neural Link Established.",
        sender: "system",
        timestamp: Date.now()
      }]);
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from JARVIS Brain');
      setIsConnected(false);
      setMessages(prev => [...prev, {
        text: "System: Neural Link Severed.",
        sender: "system",
        timestamp: Date.now()
      }]);
    });

    newSocket.on('jarvis_status', (data) => {
      if (data.message) {
        setMessages(prev => [...prev, {
          text: `JARVIS: ${data.message}${data.progress ? ` (${data.progress}%)` : ''}`,
          sender: "bot",
          timestamp: Date.now()
        }]);
      }
    });

    newSocket.on('permission_request', (data) => {
      setPendingPermission({
        requestId: data.requestId,
        operation: data.operation,
        details: data.details
      });
      setMessages(prev => [...prev, {
        text: `SECURITY ALERT: AI requesting permission for ${data.operation}`,
        sender: "system",
        timestamp: Date.now()
      }]);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  const handleSendCommand = () => {
    if (!command.trim()) {
      console.log('⚠️ Command is empty');
      return;
    }
    
    if (!socket) {
      console.log('❌ Socket is null');
      return;
    }

    console.log('🔵 Socket connected:', socket.connected);
    console.log('🔵 Socket ID:', socket.id);
    console.log('🔵 Sending command:', command, 'to device:', DEVICE_ID);

    // Emit event to backend
    socket.emit('process_instruction', {
      text: command,
      deviceId: DEVICE_ID,
      timestamp: Date.now()
    }, (response: any) => {
      console.log('📨 Server acknowledged:', response);
    });

    console.log('✅ Command emitted via socket');

    setMessages(prev => [...prev, { text: command, sender: "user", timestamp: Date.now() }]);
    setCommand("");
  };

  const handlePermissionResponse = (approved: boolean) => {
    if (!socket || !pendingPermission) return;

    socket.emit('permission_response', {
      requestId: pendingPermission.requestId,
      approved,
      timestamp: Date.now()
    });

    setMessages(prev => [...prev, {
      text: `Security: Permission ${approved ? 'APPROVED' : 'DECLINED'}`,
      sender: "system",
      timestamp: Date.now()
    }]);

    setPendingPermission(null);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] bg-black text-white font-mono border-t border-zinc-800 overflow-hidden shadow-2xl w-full">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-3 bg-zinc-900/50 border-b border-zinc-800">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold tracking-tighter text-zinc-100 uppercase">
            JARVIS <span className="text-zinc-500 font-light text-sm">Portal v4.0</span>
          </h1>
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-800/50 border border-zinc-700">
            <Circle className={`w-2 h-2 fill-current ${isConnected ? 'text-emerald-500 animate-pulse' : 'text-red-500'}`} />
            <span className="text-[10px] uppercase tracking-widest text-zinc-400">
              {isConnected ? 'Neural Link Established' : 'Link Offline'}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-4 text-xs text-zinc-500 uppercase tracking-widest">
          <div className="flex items-center gap-1">
            <Monitor size={14} />
            <span>EC2-I-0X2349</span>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Left: Command Console - Fixed Width */}
        <aside className="w-80 lg:w-96 flex flex-col border-r border-zinc-800 bg-zinc-950/30 relative">
          {pendingPermission && (
            <PermissionOverlay
              operation={pendingPermission.operation}
              details={pendingPermission.details}
              onApprove={() => handlePermissionResponse(true)}
              onDecline={() => handlePermissionResponse(false)}
            />
          )}

          <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'
                  }`}
              >
                <div className={`max-w-[90%] px-3 py-2 rounded-lg text-sm ${msg.sender === 'user'
                  ? 'bg-zinc-100 text-black rounded-tr-none'
                  : msg.sender === 'system'
                    ? 'bg-zinc-800/50 text-zinc-400 border border-zinc-700 italic text-xs'
                    : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-tl-none'
                  }`}>
                  {msg.text}
                </div>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          <div className="p-4 border-t border-zinc-800 bg-zinc-900/20">
            <div className="relative group">
              <input
                type="text"
                placeholder="EXECUTE SEQUENCE..."
                className="w-full bg-zinc-900 border border-zinc-800 rounded-lg py-3 pl-4 pr-12 text-sm focus:outline-none focus:border-emerald-500/50 transition-all placeholder:text-zinc-600 uppercase tracking-wider"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendCommand()}
              />
              <button
                onClick={handleSendCommand}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-zinc-400 hover:text-emerald-400 transition-colors"
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        </aside>

        {/* Right: Live View - Flex Fill */}
        <main className="flex-1 flex flex-col bg-zinc-950 overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-2 bg-zinc-900/30 border-b border-zinc-800">
            <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-400">
              Live Feed - EC2 Puppet Control
            </span>
          </div>
          <div className="flex-1 relative group">
            <iframe
              src={GUACAMOLE_URL}
              className="w-full h-full border-none grayscale-[0.2] opacity-90 group-hover:grayscale-0 group-hover:opacity-100 transition-all duration-700"
              title="Puppet View"
            />
            {/* Scanline Overlay */}
            <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.1)_50%),linear-gradient(90deg,rgba(255,0,0,0.02),rgba(0,255,0,0.01),rgba(0,0,255,0.02))] bg-[length:100%_2px,3px_100%] z-10" />
          </div>
        </main>
      </div>
    </div>
  );
}
