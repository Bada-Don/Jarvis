import React, { useRef, useEffect } from 'react';
import { FlatList, StyleSheet, View } from 'react-native';
import { MessageItem } from './MessageItem';

interface MessageListProps {
    messages: any[];
}

export const MessageList: React.FC<MessageListProps> = ({ messages }) => {
    const flatListRef = useRef<FlatList>(null);

    useEffect(() => {
        if (flatListRef.current && messages.length > 0) {
            setTimeout(() => {
                flatListRef.current?.scrollToEnd({ animated: true });
            }, 100);
        }
    }, [messages]);

    return (
        <FlatList
            ref={flatListRef}
            data={messages}
            renderItem={({ item }) => <MessageItem message={item} />}
            keyExtractor={(item) => item.id}
            contentContainerStyle={styles.listContainer}
            showsVerticalScrollIndicator={false}
        />
    );
};

const styles = StyleSheet.create({
    listContainer: {
        padding: 16,
        paddingBottom: 24,
    },
});
