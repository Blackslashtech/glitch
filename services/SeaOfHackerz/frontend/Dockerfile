FROM node:20

WORKDIR /app

COPY . .

RUN npm i
RUN npm i serve
RUN npm run build
ENV NODE_ENV production

EXPOSE 3000

CMD [ "npx", "serve", "-s", "build" ]