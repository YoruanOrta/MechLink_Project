import React, { useState, useEffect } from 'react';
import tokenManager from '../utils/tokenManager';
import './NotificationWidget.css';

function NotificationWidget() {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showDropdown, setShowDropdown] = useState(false);
  const [loading, setLoading] = useState(false);

  // ✅ Dynamic URL that always points to the backend on port 8000
  const API_BASE_URL = 'http://localhost:8000/api/v1';

  useEffect(() => {
    fetchNotifications();
    
    // Fetch every 30 seconds to keep updated
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      console.log('🔔 Fetching notifications from:', `${API_BASE_URL}/notifications/`);
      
      const response = await tokenManager.get(`${API_BASE_URL}/notifications/`);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ All notifications from server:', data);
        
        const now = new Date();
        const visibleNotifications = (data || []).filter(notification => {
          if (notification.type === 'appointment_confirmation' || 
              notification.type === 'system_update' ||
              notification.type === 'review_request') {
            return true;
          }
          
          if (notification.type === 'appointment_reminder') {
            if (!notification.scheduled_for) {
              console.log('⚠️ Reminder without scheduled_for:', notification.title);
              return true;
            }
            
            const scheduledTime = new Date(notification.scheduled_for);
            const isTimeToShow = scheduledTime <= now;
            
            console.log(`⏰ Reminder: "${notification.title}"`);
            console.log(`   Scheduled for: ${scheduledTime.toLocaleString()}`);
            console.log(`   Current time: ${now.toLocaleString()}`);
            console.log(`   Should show: ${isTimeToShow ? '✅ YES' : '❌ NO (future)'}`);
            
            return isTimeToShow;
          }
          
          return true;
        });
        
        console.log(`📊 Filtered: ${data.length} total → ${visibleNotifications.length} visible notifications`);
        
        setNotifications(visibleNotifications);
        
        const unread = visibleNotifications.filter(notif => 
          !notif.read_at && notif.status !== 'read'
        ).length;
        console.log('🔢 Unread count (visible only):', unread);
        setUnreadCount(unread);
      } else {
        console.error('❌ Error fetching notifications:', response.status);
      }
    } catch (error) {
      console.error('🚫 Network error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      console.log('📖 Starting markAsRead for:', notificationId);
      console.log('🔗 URL:', `${API_BASE_URL}/notifications/${notificationId}/read`);
      
      const response = await tokenManager.patch(`${API_BASE_URL}/notifications/${notificationId}/read`);
      
      console.log('📡 Response status:', response.status);
      console.log('📡 Response ok:', response.ok);
      
      if (response.ok) {
        const responseData = await response.json();
        console.log('✅ Server response:', responseData);
        
        console.log('🔄 Updating local state...');
        setNotifications(prev => {
          console.log('📊 Previous notifications count:', prev.length);
          
          const updated = prev.map(notif => {
            if (notif.id === notificationId) {
              console.log(`🎯 Found notification to update: ${notif.title}`);
              return { ...notif, read_at: new Date().toISOString(), status: 'read' };
            }
            return notif;
          });
          
            // Recalculate the counter based on the updated notifications
          const newUnreadCount = updated.filter(notif => !notif.read_at).length;
          console.log('🔢 New unread count calculated:', newUnreadCount);
          setUnreadCount(newUnreadCount);
          
          return updated;
        });
        
      } else {
        const errorData = await response.text();
        console.error('❌ Error response:', errorData);
      }
    } catch (error) {
      console.error('🚫 Network error marking as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      console.log('📖 Marking all notifications as read');
      
      const response = await tokenManager.patch(`${API_BASE_URL}/notifications/mark-all-read`);
      
      if (response.ok) {
        console.log('✅ All notifications marked as read');
        
        // Update local state - mark all as read
        setNotifications(prev => {
          const updated = prev.map(notif => ({ 
            ...notif, 
            read_at: new Date().toISOString(), 
            status: 'read' 
          }));
          
            // Counter set to 0 because all are read
          setUnreadCount(0);
          
          return updated;
        });
        
      } else {
        console.error('❌ Error marking all as read:', response.status);
      }
    } catch (error) {
      console.error('🚫 Network error marking all as read:', error);
    }
  };

  const getNotificationIcon = (type) => {
    const icons = {
      'APPOINTMENT_REMINDER': '⏰',
      'APPOINTMENT_CONFIRMATION': '✅',
      'APPOINTMENT_CANCELLED': '❌',
      'MAINTENANCE_REMINDER': '🔧',
      'REVIEW_REQUEST': '⭐',
      'SYSTEM_UPDATE': '🔔',
      'PROMOTIONAL': '🎉'
    };
    return icons[type] || '📢';
  };

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  return (
    <div className="notification-widget">
      <button 
        className="notification-button"
        onClick={() => setShowDropdown(!showDropdown)}
        title="Notifications"
      >
        🔔
        {unreadCount > 0 && (
          <span className="notification-badge">{unreadCount}</span>
        )}
      </button>

      {showDropdown && (
        <>
          {/* Click outside to close */}
          <div 
            className="notification-overlay"
            onClick={() => setShowDropdown(false)}
          />
          
          <div className="notification-dropdown">
            <div className="notification-header">
              <h3>Notifications</h3>
              <div className="header-buttons">
                {unreadCount > 0 && (
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      console.log('🔍 Mark all read clicked. Current unread count:', unreadCount);
                      console.log('🔍 Current notifications:', notifications.map(n => ({
                        id: n.id.substring(0, 8),
                        read_at: n.read_at,
                        status: n.status
                      })));
                      markAllAsRead();
                    }}
                    className="mark-all-read-btn"
                    disabled={loading}
                  >
                    Mark all read ({unreadCount})
                  </button>
                )}
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowDropdown(false);
                  }}
                  className="close-btn"
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="notification-list">
              {loading ? (
                <div className="notification-item loading">
                  <div className="loading-spinner">⏳</div>
                  <p>Loading notifications...</p>
                </div>
              ) : notifications.length === 0 ? (
                <div className="notification-item empty">
                  <div className="empty-icon">🔔</div>
                  <p>No notifications yet</p>
                  <small>We'll notify you about appointments and updates</small>
                </div>
              ) : (
                notifications.slice(0, 10).map((notification) => (
                  <div 
                    key={notification.id}
                    className={`notification-item ${!notification.read_at ? 'unread' : 'read'}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      console.log('🔍 Clicked notification:', {
                        id: notification.id,
                        read_at: notification.read_at,
                        status: notification.status,
                        title: notification.title
                      });
                      
                      if (!notification.read_at) {
                        console.log('📖 Will mark as read...');
                        markAsRead(notification.id);
                      } else {
                        console.log('ℹ️ Already read, no action needed');
                      }
                    }}
                  >
                    <div className="notification-icon">
                      {getNotificationIcon(notification.type)}
                    </div>
                    <div className="notification-content">
                      <h4>{notification.title}</h4>
                      <p>{notification.message}</p>
                      <span className="notification-time">
                        {formatTimeAgo(notification.created_at)}
                      </span>
                    </div>
                    {!notification.read_at && (
                      <div className="unread-indicator"></div>
                    )}
                  </div>
                ))
              )}
            </div>

            {notifications.length > 10 && (
              <div className="notification-footer">
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowDropdown(false);
                    console.log('Navigate to full notifications page');
                  }}
                  className="view-all-btn"
                >
                  View All {notifications.length} Notifications
                </button>
              </div>
            )}

            {notifications.length > 0 && (
              <div className="notification-actions">
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    fetchNotifications();
                  }}
                  className="refresh-btn"
                  disabled={loading}
                >
                  🔄 Refresh
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default NotificationWidget;