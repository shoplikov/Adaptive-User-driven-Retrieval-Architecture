/**
 * Analytics Dashboard JavaScript
 *
 * This script handles:
 * 1. API client for analytics service
 * 2. Data fetching and display
 * 3. Chart rendering
 * 4. Real-time updates
 */

// Configuration
const API_BASE_URL = 'http://localhost:8001/api/v1';
const REFRESH_INTERVAL = 30000; // 30 seconds

// DOM Elements
const elements = {
    totalConversations: document.getElementById('total-conversations-value'),
    satisfactionValues: document.getElementById('satisfaction-values'),
    tokenUsageValues: document.getElementById('token-usage-values'),
    statusValues: document.getElementById('status-values'),
    satisfactionCanvas: document.getElementById('satisfaction-canvas'),
    statusCanvas: document.getElementById('status-canvas')
};

// Chart instances
let satisfactionChart = null;
let statusChart = null;

/**
 * Fetch data from analytics API
 * @param {string} endpoint - API endpoint
 * @returns {Promise<object>} - API response data
 */
async function fetchAnalyticsData(endpoint) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`);
        if (!response.ok) {
            throw new Error(`API error: ${response.status} ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching analytics data:', error);
        throw error;
    }
}

/**
 * Update total conversations display
 */
async function updateTotalConversations() {
    try {
        const data = await fetchAnalyticsData('/metrics/total_conversations');
        elements.totalConversations.textContent = data.total.toLocaleString();
    } catch (error) {
        elements.totalConversations.textContent = 'Error loading data';
    }
}

/**
 * Update satisfaction statistics display
 */
async function updateSatisfactionStats() {
    try {
        const data = await fetchAnalyticsData('/metrics/satisfaction');
        let html = '';
        for (const [satisfaction, count] of Object.entries(data)) {
            html += `<div>${satisfaction}: ${count}</div>`;
        }
        elements.satisfactionValues.innerHTML = html;
        renderSatisfactionChart(data);
    } catch (error) {
        elements.satisfactionValues.innerHTML = '<div>Error loading data</div>';
    }
}

/**
 * Update token usage display
 */
async function updateTokenUsage() {
    try {
        const data = await fetchAnalyticsData('/metrics/token_usage');
        elements.tokenUsageValues.innerHTML = `
            <div>Input Tokens: ${data.input_tokens.toLocaleString()}</div>
            <div>Output Tokens: ${data.output_tokens.toLocaleString()}</div>
        `;
    } catch (error) {
        elements.tokenUsageValues.innerHTML = '<div>Error loading data</div>';
    }
}

/**
 * Update status breakdown display
 */
async function updateStatusBreakdown() {
    try {
        const data = await fetchAnalyticsData('/metrics/status_breakdown');
        let html = '';
        for (const [status, count] of Object.entries(data)) {
            html += `<div>${status}: ${count}</div>`;
        }
        elements.statusValues.innerHTML = html;
        renderStatusChart(data);
    } catch (error) {
        elements.statusValues.innerHTML = '<div>Error loading data</div>';
    }
}

/**
 * Render satisfaction distribution chart
 * @param {object} data - Satisfaction statistics data
 */
function renderSatisfactionChart(data) {
    const labels = Object.keys(data);
    const counts = Object.values(data);

    const ctx = elements.satisfactionCanvas.getContext('2d');

    // Destroy previous chart instance if it exists
    if (satisfactionChart) {
        satisfactionChart.destroy();
    }

    satisfactionChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: [
                    '#2ecc71', // Good
                    '#3498db', // Neutral
                    '#e74c3c'  // Bad
                ],
                hoverBackgroundColor: [
                    '#27ae60',
                    '#2980b9',
                    '#c0392b'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                position: 'right'
            },
            animation: {
                animateScale: true
            }
        }
    });
}

/**
 * Render status distribution chart
 * @param {object} data - Status breakdown data
 */
function renderStatusChart(data) {
    const labels = Object.keys(data);
    const counts = Object.values(data);

    const ctx = elements.statusCanvas.getContext('2d');

    // Destroy previous chart instance if it exists
    if (statusChart) {
        statusChart.destroy();
    }

    statusChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: [
                    '#3498db', // Active
                    '#e67e22', // Completed
                    '#e74c3c'  // Failed
                ],
                hoverBackgroundColor: [
                    '#2980b9',
                    '#d35400',
                    '#c0392b'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                position: 'right'
            },
            animation: {
                animateScale: true
            }
        }
    });
}

/**
 * Initialize the dashboard
 */
async function initDashboard() {
    // Load initial data
    await Promise.all([
        updateTotalConversations(),
        updateSatisfactionStats(),
        updateTokenUsage(),
        updateStatusBreakdown()
    ]);

    // Set up periodic refresh
    setInterval(async () => {
        await Promise.all([
            updateTotalConversations(),
            updateSatisfactionStats(),
            updateTokenUsage(),
            updateStatusBreakdown()
        ]);
    }, REFRESH_INTERVAL);
}

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Load Chart.js library
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    script.onload = initDashboard;
    document.head.appendChild(script);
});