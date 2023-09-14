# Compiling
FROM node:18.16.0-alpine AS build

WORKDIR /app
COPY package.json ./package.json
COPY yarn.lock ./yarn.lock

RUN yarn install --frozen-lockfile

COPY . .
RUN yarn build

ENV NODE_ENV=production

CMD ["node", "dist"]
