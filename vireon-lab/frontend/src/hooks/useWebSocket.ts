import { useEffect, useRef, useState } from 'react';

export function useWebSocket(channel: string) {
  const [data, setData] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // In a real app, URL should be configured via environment variables
    const ws = new WebSocket(`ws://localhost:8001/ws/${channel}`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log(`Connected to WS channel: ${channel}`);
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        setData(payload);
      } catch (err) {
        console.error('Failed to parse WS message', err);
      }
    };

    ws.onclose = () => {
      console.log(`Disconnected from WS channel: ${channel}`);
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [channel]);

  const sendMessage = (message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  };

  return { data, isConnected, sendMessage };
}
