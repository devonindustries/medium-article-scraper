# Stage 1: Build frontend
FROM node:18-alpine as build-stage

WORKDIR /app

COPY package*.json ./
RUN npm install

# COPY the env file
COPY .env .env

# Copy all source code
COPY . .

# Now when we run build, Vite will correctly inject process.env.VUE_APP_API_URL
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:stable-alpine as production-stage

COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]