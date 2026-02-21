FROM node:18-alpine

WORKDIR /app

COPY package.json .
# No dependencies to install really, but good practice
RUN npm install || true

COPY . .


# We use the test script as the container entrypoint for this demo
ENV FIX_APPLIED=true
CMD ["npm", "test"]