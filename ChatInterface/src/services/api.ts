import axios from 'axios';
import { Platform } from 'react-native';
import Constants from 'expo-constants';

// Dynamically determine the base URL based on the Expo packager's IP
const getBaseUrl = () => {
    const debuggerHost = Constants.expoConfig?.hostUri;

    if (debuggerHost) {
        // hostUri is in the format "ip:port" (e.g., "192.168.1.14:8081")
        const ip = debuggerHost.split(':')[0];
        return `http://${ip}:5000/api`;
    }

    // Fallback for Android Emulator (10.0.2.2 points to host machine)
    if (Platform.OS === 'android') {
        return 'http://10.0.2.2:5000/api';
    }

    // Default fallback
    return 'http://192.168.1.14:5000/api';
};

const BASE_URL = getBaseUrl();
console.log('Using API URL:', BASE_URL);

const api = axios.create({
    baseURL: BASE_URL,
});

export const sendMessage = async (message) => {
    try {
        const response = await api.post('/chat', { message });
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
