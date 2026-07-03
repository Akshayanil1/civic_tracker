import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, Button, TextInput, StyleSheet } from 'react-native';
import NetInfo from '@react-native-community/netinfo';
import { fetchAssignedIssues, resolveIssue } from '../services/api';
import { queueResolutionOffline, syncOfflineQueue } from '../services/sync';

// Day 53: Field Worker Dashboard UI
export default function Dashboard({ token }) {
    const [issues, setIssues] = useState([]);
    const [isConnected, setIsConnected] = useState(true);

    useEffect(() => {
        const unsubscribe = NetInfo.addEventListener(state => {
            setIsConnected(state.isConnected);
            if (state.isConnected) {
                syncOfflineQueue(token);
            }
        });

        loadIssues();

        return () => unsubscribe();
    }, []);

    const loadIssues = async () => {
        if (isConnected) {
            try {
                const data = await fetchAssignedIssues(token);
                setIssues(data);
            } catch (error) {
                console.error(error);
            }
        }
    };

    const handleResolve = async (tracking_id, notes) => {
        const issueData = {
            tracking_id,
            resolution_notes: notes,
            image_b64: "base64_encoded_after_photo_string" // Mocked image
        };

        if (isConnected) {
            await resolveIssue(token, issueData.tracking_id, issueData.resolution_notes, issueData.image_b64);
            alert("Issue marked as resolved!");
            loadIssues();
        } else {
            await queueResolutionOffline(issueData);
            alert("No internet. Saved offline! Will sync when connected.");
            // Optimistically remove from list
            setIssues(issues.filter(i => i.tracking_id !== tracking_id));
        }
    };

    const renderItem = ({ item }) => (
        <View style={styles.card}>
            <Text style={styles.title}>{item.issue_title}</Text>
            <Text>Tracking ID: {item.tracking_id}</Text>
            <Text>Priority: {item.priority}</Text>
            <Text style={styles.warning}>SLA Deadline: {item.due_date}</Text>
            
            {/* In a real app, this would be a camera component */}
            <Button title="Take 'After' Photo" onPress={() => {}} />
            <Button 
                title="Mark Resolved" 
                color="#28a745"
                onPress={() => handleResolve(item.tracking_id, "Fixed the issue as per standard.")} 
            />
        </View>
    );

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.headerText}>Field Worker Dashboard</Text>
                <Text style={isConnected ? styles.online : styles.offline}>
                    {isConnected ? "Online" : "Offline Mode"}
                </Text>
            </View>
            <FlatList
                data={issues}
                keyExtractor={item => item.tracking_id}
                renderItem={renderItem}
            />
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#f4f4f4' },
    header: { padding: 20, backgroundColor: '#0056b3', flexDirection: 'row', justifyContent: 'space-between' },
    headerText: { color: 'white', fontSize: 18, fontWeight: 'bold' },
    online: { color: '#0f0', fontWeight: 'bold' },
    offline: { color: '#f00', fontWeight: 'bold' },
    card: { backgroundColor: 'white', padding: 15, margin: 10, borderRadius: 5, shadowOpacity: 0.1 },
    title: { fontSize: 16, fontWeight: 'bold', marginBottom: 5 },
    warning: { color: '#d9534f', marginBottom: 10 }
});
