import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import { resolveIssue } from './api';

// Day 54: Offline Syncing
// Store pending resolutions in SQLite/AsyncStorage
export const queueResolutionOffline = async (issueData) => {
    try {
        const queueStr = await AsyncStorage.getItem('OFFLINE_QUEUE');
        let queue = queueStr ? JSON.parse(queueStr) : [];
        queue.push(issueData);
        await AsyncStorage.setItem('OFFLINE_QUEUE', JSON.stringify(queue));
        console.log("Issue queued for offline sync:", issueData.tracking_id);
    } catch (error) {
        console.error("Failed to queue offline", error);
    }
};

export const syncOfflineQueue = async (token) => {
    try {
        const state = await NetInfo.fetch();
        if (!state.isConnected) {
            console.log("No internet. Skipping sync.");
            return;
        }

        const queueStr = await AsyncStorage.getItem('OFFLINE_QUEUE');
        if (!queueStr) return;
        
        let queue = JSON.parse(queueStr);
        if (queue.length === 0) return;

        console.log(`Syncing ${queue.length} items to Frappe backend...`);

        let remainingQueue = [];
        for (let item of queue) {
            try {
                await resolveIssue(token, item.tracking_id, item.resolution_notes, item.image_b64);
                console.log(`Successfully synced ${item.tracking_id}`);
            } catch (error) {
                console.error(`Failed to sync ${item.tracking_id}`, error);
                remainingQueue.push(item);
            }
        }

        await AsyncStorage.setItem('OFFLINE_QUEUE', JSON.stringify(remainingQueue));
    } catch (error) {
        console.error("Sync error", error);
    }
};
