FROM alpine:latest AS stage
WORKDIR /data
COPY *.jar /data/mods/*

FROM itzg/minecraft-server:java17-alpine
COPY --from=stage /data/mods/* /data/mods/*