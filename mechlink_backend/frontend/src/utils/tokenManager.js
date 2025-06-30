// src/utils/tokenManager.js
class TokenManager {
    constructor() {
      this.isRefreshing = false;
      this.failedQueue = [];
    }
  
    // Main interceptor for all requests
    async makeAuthenticatedRequest(url, options = {}) {
      const token = localStorage.getItem('token');
      
    // Add token to the headers
      const authOptions = {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      };
  
      try {
        const response = await fetch(url, authOptions);
        
        // If the response is 401, attempt refresh
        if (response.status === 401) {
          console.log('🔄 Token expired, attempting refresh...');
          
          const newToken = await this.refreshToken();
          if (newToken) {
            // Retry with the new token
            const retryOptions = {
              ...authOptions,
              headers: {
                ...authOptions.headers,
                'Authorization': `Bearer ${newToken}`,
              },
            };
            
            console.log('✅ Retrying request with new token...');
            return await fetch(url, retryOptions);
          } else {
            // If the token could not be refreshed, redirect to login
            this.redirectToLogin();
            throw new Error('Authentication failed');
          }
        }
  
        return response;
      } catch (error) {
        console.error('❌ Error en request autenticada:', error);
        throw error;
      }
    }
  
    // Function to refresh the token
    async refreshToken() {
      if (this.isRefreshing) {
        // If it's already refreshing, wait
        return new Promise((resolve, reject) => {
          this.failedQueue.push({ resolve, reject });
        });
      }
  
      console.log('🔄 Iniciando refresh de token...');
      this.isRefreshing = true;
  
      try {
        const response = await fetch('http://localhost:8000/api/v1/auth/login-json', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: 'testuser@mechlink.com',
            password: 'TestPassword123!'
          }),
        });
  
        if (response.ok) {
          const data = await response.json();
          const newToken = data.access_token;
          
          // Save new token
          localStorage.setItem('token', newToken);
          localStorage.setItem('user_id', data.user.id);
          localStorage.setItem('user_email', data.user.email);
          
          console.log('✅ Token refrescado exitosamente');
          
          // Process failed request queue
          this.processQueue(null, newToken);
          
          return newToken;
        } else {
          console.error('❌ Error refrescando token:', response.status);
          this.processQueue(new Error('Token refresh failed'), null);
          return null;
        }
      } catch (error) {
        console.error('❌ Error en refresh de token:', error);
        this.processQueue(error, null);
        return null;
      } finally {
        this.isRefreshing = false;
      }
    }
  
    // Process pending request queue
    processQueue(error, token = null) {
      this.failedQueue.forEach(({ resolve, reject }) => {
        if (error) {
          reject(error);
        } else {
          resolve(token);
        }
      });
      
      this.failedQueue = [];
    }
  
    // Redirect to login
    redirectToLogin() {
      console.log('🚪 Redirigiendo al login...');
      localStorage.clear();
      window.location.href = '/login';
    }
  
    // Helper method for GET requests
    async get(url) {
      return this.makeAuthenticatedRequest(url, { method: 'GET' });
    }
  
    // Helper method for POST requests
    async post(url, data) {
      return this.makeAuthenticatedRequest(url, {
        method: 'POST',
        body: JSON.stringify(data),
      });
    }
  
    // Helper method for PUT requests
    async put(url, data) {
      return this.makeAuthenticatedRequest(url, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    }
  
    // Helper method for DELETE requests
    async delete(url) {
      return this.makeAuthenticatedRequest(url, { method: 'DELETE' });
    }
  }
  
// Export singleton instance
  const tokenManager = new TokenManager();
  export default tokenManager;