FROM node:16-alpine

WORKDIR /app
COPY . .

# Install serve for static file serving
RUN npm install -g serve

EXPOSE 3000
CMD ["serve", "-s", "public", "-l", "3000"]
