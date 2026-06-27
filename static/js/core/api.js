/**
 * @fileoverview Parent API Module
 * This module handles all network requests, JWT token injection, and error parsing.
 * It strictly adheres to the Parent-Child architecture principle.
 */

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

/**
 * Core parent function for executing API requests.
 * Automatically handles JSON parsing and generic error throwing.
 * 
 * @param {string} endpoint - The API endpoint relative path (e.g., '/auth/login').
 * @param {Object} [options={}] - Standard Fetch API options (method, headers, body).
 * @returns {Promise<Object>} The parsed JSON response from the backend.
 * @throws {Error} Will throw an error if the network request fails or returns >= 400.
 */
async function request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    // Default headers
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    // Auto-inject JWT if present
    const token = localStorage.getItem('access_token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(url, {
            ...options,
            headers
        });

        const data = await response.json().catch(() => null);

        if (!response.ok) {
            // Backend validation error (422) or domain error (400, 401, 403, 404, 409)
            let errorMessage = 'An unexpected error occurred';
            if (data) {
                if (data.detail && Array.isArray(data.detail)) {
                    errorMessage = data.detail.map(e => e.msg).join(', '); // FastAPI Validation
                } else if (data.detail) {
                    errorMessage = data.detail; // FastAPI string detail
                } else if (data.message) {
                    errorMessage = data.message; // Custom Domain Exception
                }
            }
            throw new Error(errorMessage);
        }

        return data;
    } catch (error) {
        console.error(`[API Error] ${options.method || 'GET'} ${endpoint}:`, error.message);
        throw error;
    }
}
