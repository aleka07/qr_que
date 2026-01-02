FROM nginx:alpine

# Copy nginx configuration
COPY nginx/sites-available/qr_que.conf /etc/nginx/conf.d/default.conf

# Create directories for static files
RUN mkdir -p /var/www/staff /var/www/display /var/www/client

# Copy built frontend files (will be mounted in development)
# COPY frontend/staff/dist /var/www/staff
# COPY frontend/display/dist /var/www/display
# COPY frontend/client/dist /var/www/client

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
