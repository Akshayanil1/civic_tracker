import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Day 52: Token-based authentication
const API_URL = 'https://civictracker.local/api/method';

export const login = async (usr, pwd) => {
    try {
        const response = await axios.post(`${API_URL}/login`, { usr, pwd });
        // Frappe returns cookies for session, but for REST we can use token auth
        // Assuming we have created API API_KEY and API_SECRET
        return response.data;
    } catch (error) {
        console.error("Login Error", error);
        throw error;
    }
};

export const fetchAssignedIssues = async (token) => {
    try {
        const response = await axios.get(`${API_URL}/civic_tracker.api.mobile.get_assigned_issues`, {
            headers: {
                'Authorization': `token ${token}`
            }
        });
        return response.data.message;
    } catch (error) {
        console.error("Fetch Error", error);
        throw error;
    }
};

export const resolveIssue = async (token, tracking_id, resolution_notes, image_b64) => {
    try {
        const response = await axios.post(`${API_URL}/civic_tracker.api.mobile.resolve_issue`, {
            tracking_id,
            resolution_notes,
            image_b64
        }, {
            headers: {
                'Authorization': `token ${token}`
            }
        });
        return response.data.message;
    } catch (error) {
        console.error("Resolve Error", error);
        throw error;
    }
};
