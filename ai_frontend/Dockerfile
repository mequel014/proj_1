# ai_frontend/Dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npx nuxi build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NITRO_PORT=3000
ENV PORT=3000
COPY --from=build /app/.output ./.output
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]