import axios from 'axios';
import { Platform } from 'react-native';

// Use local IP for both Emulator and Physical Device
const BASE_URL = 'http://192.168.1.14:5000/api';

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
