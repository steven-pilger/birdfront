FROM  node:20.12.0-alpine as dev

WORKDIR /frontend
COPY yarn.lock package.json ./
RUN yarn install

COPY . /frontend

CMD ["yarn", "dev", "--host", "0.0.0.0", "--port", "3000"]

FROM dev as build
RUN yarn build

FROM caddy:2.7-alpine
COPY --from=build /frontend/dist /srv
CMD ["caddy", "file-server"]

