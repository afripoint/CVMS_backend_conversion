FROM nginx:1.25-alpine

# Remove default Nginx config
RUN rm -f /etc/nginx/conf.d/default.conf

# Copy the correct Nginx config
COPY ./nginx.conf /etc/nginx/nginx.conf

# Copy additional configuration (if any)
COPY ./conf.d/ /etc/nginx/conf.d/

# Expose port
EXPOSE 80
