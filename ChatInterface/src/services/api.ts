import axios from 'axios';
import { Platform } from 'react-native';
import Constants from 'expo-constants';
import io from 'socket.io-client';

// Dynamically determine the base URL based on the Expo packager's IP
const getBaseUrl = () => {
    const debuggerHost = Constants.expoConfig?.hostUri;

    if (debuggerHost) {
        // hostUri is in the format "ip:port" (e.g., "192.168.1.14:8081")
        const ip = debuggerHost.split(':')[0];
        return `http://${ip}:5000`;
    }

    // Fallback for Android Emulator (10.0.2.2 points to host machine)
    if (Platform.OS === 'android') {
        return 'http://10.0.2.2:5000';
    }

    // Default fallback
    return 'http://192.168.1.14:5000';
};

const BASE_URL = getBaseUrl();
console.log('Using API URL:', BASE_URL);

const api = axios.create({
    baseURL: `${BASE_URL}/api`,
});

// Socket.IO connection for real-time updates
let socket: any = null;

const getSocket = () => {
    if (!socket) {
        socket = io(BASE_URL, {
            transports: ['websocket'],
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionAttempts: 5,
        });

        socket.on('connect', () => {
            console.log('✅ Connected to server via WebSocket');
        });

        socket.on('disconnect', () => {
            console.log('❌ Disconnected from server');
        });

        socket.on('connect_error', (error: any) => {
            console.error('Connection error:', error);
        });
    }
    return socket;
};

// Permission request types
export interface PermissionRequest {
    requestId: string;
    operation: string;
    details: string;
    timestamp: number;
}

// Send permission response back to server
export const sendPermissionResponse = (requestId: string, approved: boolean) => {
    const socket = getSocket();
    socket.emit('permission_response', {
        requestId,
        approved,
        timestamp: Date.now(),
    });
    console.log(`📤 Permission response sent: ${requestId} - ${approved ? 'APPROVED' : 'DENIED'}`);
};

// Listen for permission requests
export const connectToPermissionRequests = (callback: (data: PermissionRequest) => void) => {
    const socket = getSocket();

    const handlePermissionRequest = (data: PermissionRequest) => {
        console.log('🔐 Permission request received:', data);
        callback(data);
    };

    socket.on('permission_request', handlePermissionRequest);

    return () => {
        socket.off('permission_request', handlePermissionRequest);
    };
};

// Abort the current task
export const abortTask = () => {
    const socket = getSocket();
    socket.emit('abort_task', {
        timestamp: Date.now(),
    });
    console.log('🛑 Abort task signal sent');
};

export const sendMessage = async (message) => {
    try {
        const response = await api.post('/process', { text: message });
        return response.data;
    } catch (error) {
        console.error('Error sending message:', error);
        throw error;
    }
};

export const uploadFile = async (fileUri, fileName, fileType) => {
    const formData = new FormData();
    formData.append('file', {
        uri: fileUri,
        name: fileName,
        type: fileType,
    } as any);

    try {
        const response = await api.post('/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        console.error('Error uploading file:', error);
        throw error;
    }
};

export const connectToStatusUpdates = (callback: (data: any) => void) => {
    const socket = getSocket();

    const handleStatus = (data: any) => {
        console.log('📱 Status update:', data);
        callback(data);
    };

    socket.on('jarvis_status', handleStatus);

    // Return cleanup function
    return () => {
        socket.off('jarvis_status', handleStatus);
    };
};
