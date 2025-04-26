FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

# 2. Expose Vite preview port
EXPOSE 4173

# 3. Start the preview server
CMD ["npm", "start"]
