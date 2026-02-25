import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Modal, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ArrowLeft, MoreVertical, RefreshCw } from 'lucide-react-native';
import JarvisLogo from './JarvisLogo';

interface ChatHeaderProps {
    title: string;
    subtitle?: string;
    onBack?: () => void;
    onUnpair?: () => void;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({ title, subtitle, onBack, onUnpair }) => {
    const [showMenu, setShowMenu] = useState(false);

    const handleUnpair = () => {
        setShowMenu(false);
        if (onUnpair) {
            onUnpair();
        }
    };

    return (
        <SafeAreaView edges={['top', 'left', 'right']} style={styles.headerContainer}>
            <View style={styles.headerContent}>
                <View style={styles.leftContainer}>
                    {onBack && (
                        <TouchableOpacity onPress={onBack} style={styles.backButton}>
                            <ArrowLeft size={24} color="#fafafa" />
                        </TouchableOpacity>
                    )}
                    <View style={styles.avatarContainer}>
                        <View style={styles.avatar}>
                            <JarvisLogo style={styles.logo} />
                        </View>
                        <View style={styles.onlineIndicator} />
                    </View>
                    <View style={styles.titleContainer}>
                        <Text style={styles.title}>{title}</Text>
                        {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
                    </View>
                </View>

                <View style={styles.rightContainer}>
                    <TouchableOpacity 
                        style={styles.iconButton}
                        onPress={() => setShowMenu(true)}
                    >
                        <MoreVertical size={20} color="#16e2d7" />
                    </TouchableOpacity>
                </View>
            </View>

            {/* Menu Modal */}
            <Modal
                visible={showMenu}
                transparent
                animationType="fade"
                onRequestClose={() => setShowMenu(false)}
            >
                <Pressable 
                    style={styles.modalOverlay}
                    onPress={() => setShowMenu(false)}
                >
                    <View style={styles.menuContainer}>
                        {onUnpair && (
                            <TouchableOpacity 
                                style={styles.menuItem}
                                onPress={handleUnpair}
                            >
                                <RefreshCw size={18} color="#16e2d7" />
                                <Text style={styles.menuItemText}>Unpair Device</Text>
                            </TouchableOpacity>
                        )}
                    </View>
                </Pressable>
            </Modal>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    headerContainer: {
        backgroundColor: '#0a0a0a',
        borderBottomWidth: 1,
        borderBottomColor: '#18181b',
    },
    headerContent: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingHorizontal: 16,
        paddingVertical: 10,
    },
    leftContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        flex: 1,
    },
    backButton: {
        marginRight: 12,
    },
    avatarContainer: {
        position: 'relative',
        marginRight: 12,
    },
    avatar: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: '#18181b',
        alignItems: 'center',
        justifyContent: 'center',
    },
    logo: {
        width: 28,
        height: 28,
        color: '#16e2d7',
    },
    onlineIndicator: {
        position: 'absolute',
        bottom: 0,
        right: 0,
        width: 12,
        height: 12,
        borderRadius: 6,
        backgroundColor: '#16e2d7',
        borderWidth: 2,
        borderColor: '#0a0a0a',
    },
    titleContainer: {
        justifyContent: 'center',
    },
    title: {
        fontSize: 16,
        fontWeight: '600',
        color: '#fafafa',
    },
    subtitle: {
        fontSize: 12,
        color: '#a1a1aa',
    },
    rightContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 16,
    },
    iconButton: {
        padding: 4,
    },
    modalOverlay: {
        flex: 1,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        justifyContent: 'flex-start',
        alignItems: 'flex-end',
        paddingTop: 60,
        paddingRight: 16,
    },
    menuContainer: {
        backgroundColor: '#18181b',
        borderRadius: 12,
        borderWidth: 1,
        borderColor: '#27272a',
        minWidth: 180,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 8,
        elevation: 8,
    },
    menuItem: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 12,
        paddingHorizontal: 16,
        paddingVertical: 14,
    },
    menuItemText: {
        fontSize: 15,
        color: '#fafafa',
        fontWeight: '500',
    },
});
