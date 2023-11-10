FROM alpine:latest AS stage
WORKDIR /data
COPY *.jar /data/mods/*
COPY DevOps_Yearn_for_the_Mines.zip /data/world/*

FROM itzg/minecraft-server:java17-alpine
COPY --from=stage /data/mods/* /data/mods/*